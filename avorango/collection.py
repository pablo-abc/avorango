from inspect import getmembers, isroutine
from stringcase import snakecase
from .column import Column
from .types import String


class Collection:
    _collection_name = None
    _session = None
    _collection = None
    key = Column(String)

    def __init__(self, data=None):
        if self._collection_name is None:
            self._collection_name = snakecase(type(self).__name__)
        self._collection = self._session.collection(self._collection_name)
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
            self._collection_name,
            self.key,
        )

    @property
    def _properties(self):
        """Attributes of the instance as a dictionary"""
        return dict([p for p in
                     getmembers(
                         type(self), lambda o: not isroutine(o)
                         and not isinstance(o, property)
                     )
                     if not p[0].startswith('_')])

    def save(self):
        """Saves or updates a collection

        If a key is defined on the instance, it will check if an instance
        with the same key is defined in the database. If it does, it will
        execute an update. In every other situation, it will create a new
        document.
        """
        properties = dict(self._properties)
        result = None

        if properties['key'] is None:
            del properties['key']
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

        result['new']['key'] = result['new'].pop('_key')
        return type(self)(result['new'])
