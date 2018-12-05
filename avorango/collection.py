from inspect import getmembers, isroutine
from stringcase import snakecase


class Collection:
    _collection_name = None
    _session = None
    _collection = None
    key = None

    def __init__(self, data=None):
        if self._collection_name is None:
            self._collection_name = snakecase(type(self).__name__)
        self._collection = self._session.collection(self._collection_name)
        if data is None:
            return
        [setattr(self, p[0], data[p[0]])
         for p in getmembers(type(self), lambda o: not isroutine(o))
         if p[0] in data and not p[0].startswith('_')]

    def save(self):
        properties = \
            [p for p in
             getmembers(type(self), lambda o: not isroutine(o))
             if not p[0].startswith('_')]
        self._properties = dict(properties)

        result = None
        if 'key' in self._properties and self._properties['key'] is None:
            del self._properties['key']
        if 'key' not in self._properties:
            result = self._collection.insert(
                self._properties, return_new=True
            )
        else:
            self._properties['_key'] = self._properties.pop('key')
            id = '{}/{}'.format(
                self._collection_name,
                self._properties['_key'],
            )
            self._properties['_id'] = id
            collection = self._collection.get(id)

            if collection is None:
                result = self._collection.insert(
                    self._properties, return_new=True
                )
            else:
                result = self._collection.update(
                    self._properties, return_new=True,
                )
        result['new']['key'] = result['new'].pop('_key')
        return type(self)(result['new'])

    @property
    def _id(self):
        if self.key is None:
            return None
        return "{}/{}".format(
            self._collection_name,
            self.key,
        )
