from inspect import getmembers, isroutine
from stringcase import snakecase
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


class CollectionMeta(type):
    def __init__(cls, name, bases, attrs, **kwargs):
        if cls._session is not None:
            cls._collection = cls._session.collection(cls.collection_name)
        return super().__init__(name, bases, attrs)

    @property
    def collection_name(self):
        return self._collectionname if self._collectionname is not None \
            else snakecase(self.__name__)


class Collection(metaclass=CollectionMeta):
    _collectionname = None
    _session = None
    _collection = None
    key = Column(String)

    def __init__(self, data=None):
        self._collectionname = type(self).collection_name
        self._collection = self._session.collection(self._collectionname)
        if data is None:
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
    def _properties(self):
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
    def find(cls, filter_={}):
        return cls._collection.find(filter_)

    @classmethod
    @check_session
    def findByKey(cls, key):
        String().validate(key)
        return cls._collection.get(cls._make_id(key))

    @classmethod
    @check_session
    def findOne(cls, filter_={}):
        return cls._collection.find(filter_, limit=1).next()

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
        properties = dict(self._properties)
        self._check_required(properties)
        result = None

        if self.key is None:
            result = self._collection.insert(
                properties, return_new=True
            )
        else:
            properties['_key'] = self.key
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

        result['new']['key'] = result['new'].pop('_key')
        return type(self)(result['new'])

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
