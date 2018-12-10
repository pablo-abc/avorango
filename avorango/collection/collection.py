from inspect import getmembers, isroutine
from .meta import CollectionMeta
from .column import Column
from .types import String
from .errors import SessionError, RequiredError
from functools import wraps


def check_session(f):
    @wraps(f)
    def wrapper(self, *args, **kwargs):
        if self._session is None:
            raise SessionError()
        return f(self, *args, **kwargs)
    return wrapper


class Collection(metaclass=CollectionMeta):
    _collectionname = None
    _session = None
    _collection = None
    key = Column(String)

    def __init__(self, **data):
        self._collectionname = type(self).collection_name
        self._collection = self._session.collection(self._collectionname)
        if data is None or data == {}:
            return
        # Assign data to object
        [setattr(self, p[0], data[p[0]])
         for p in getmembers(type(self), lambda o: not isroutine(o))
         if p[0] in data and not p[0].startswith('_')]

    @property
    def id(self):
        if self.key is None:
            return None
        return '{}/{}'.format(
            self._collectionname,
            self.key,
        )

    @property
    def attributes(self):
        """Return attributes of the instance as a dictionary."""
        return {
            p[0]: p[1].__get__(self, type(self)) for p in
            getmembers(
                type(self), lambda o: not isroutine(o)
                and not isinstance(o, property)
            )
            if not p[0].startswith('_')
        }

    @property
    def _descriptors(self):
        return {
            p[0]: p[1] for p in
            getmembers(
                type(self), lambda o: not isroutine(o)
                and not isinstance(o, property)
            )
            if not p[0].startswith('_')
        }

    @classmethod
    @check_session
    def find(cls, **filter_):
        cursor = cls._collection.find(filter_)
        results = []
        while not cursor.empty():
            results.append(cls._prepare_result(cursor))
        return results

    @classmethod
    @check_session
    def find_like(cls,
                  case_sensitive=False,
                  limit=None,
                  skip=None,
                  **filter_):
        if filter_ == {}:
            return cls.find(limit=limit, skip=skip)
        query = ""
        ci = "false" if case_sensitive else "true"
        pagination = "LIMIT {}".format(limit) if limit is not None else ""
        pagination = "LIMIT {}, {}".format(skip, limit) \
            if limit is not None and skip is not None else pagination
        for key in filter_:
            query += "FILTER LIKE(r.{}, @{}, {}) ".format(key, key, ci)
        cursor = cls._session.aql.execute(
            "FOR r IN {} ".format(cls.collection_name)
            + query
            + pagination
            + "RETURN r",
            bind_vars=filter_,
        )
        results = []
        while not cursor.empty():
            results.append(cls._prepare_result(cursor))
        return results

    @classmethod
    @check_session
    def get(cls, key):
        String().validate(key)
        result = cls._collection.get(cls._make_id(key))
        return cls._prepare_result(result)

    @classmethod
    @check_session
    def find_one(cls, **filter_):
        cursor = cls._collection.find(filter_, limit=1)
        if cursor.empty():
            return None
        return cls._prepare_result(cursor)

    @classmethod
    @check_session
    def execute(cls, query, **kwargs):
        return cls._session.aql.execute(query, **kwargs)

    def save(self):
        """Save or update a collection.

        If a key is defined on the instance, it will check if an instance
        with the same key is defined in the database. If it does, it will
        execute an update. In every other situation, it will create a new
        document.
        """
        properties = dict(self.attributes)
        self._check_required(properties)
        result = None

        if self.key is None:
            properties.pop('key')
            result = self._collection.insert(
                properties, return_new=True
            )
        else:
            properties['_key'] = properties.pop('key')
            properties['_id'] = self.id

            collection = self._collection.get(self.id)
            if collection is None:
                result = self._collection.insert(
                    properties, return_new=True
                )
            else:
                result = self._collection.update(
                    properties, return_new=True,
                )
        return type(self)._prepare_result(result['new'])

    def delete(self):
        id = self.id
        if id is None:
            raise RequiredError("Key is not defined in instance")
        self._collection.delete(id)

    @classmethod
    def _make_id(cls, key):
        return '{}/{}'.format(
            cls.collection_name,
            key,
        )

    def _check_required(self, properties):
        for p, value in self._descriptors.items():
            if properties[p] is None and value._required is True:
                raise RequiredError(
                    "The attribute '{}' is required".format(p)
                )

    @classmethod
    def _prepare_result(cls, result):
        if not isinstance(result, dict):
            result = result.next()
        result['key'] = result.pop('_key')
        return cls(**result)
