from inspect import getmembers, isroutine
from avorango.collection import Collection


class Vertex(Collection):
    def __init__(self, **data):
        self._collectionname = type(self).collection_name
        if self._graphname is not None:
            self._graph = self._session.graph(self._graphname)
            self._collection = \
                self._graph.vertex_collection(self._collectionname)
        else:
            self._collection = \
                self._session.collection(self._collectionname)
        if data is None or data == {}:
            return
        # Assign data to object
        [setattr(self, p[0], data[p[0]])
         for p in getmembers(type(self), lambda o: not isroutine(o))
         if p[0] in data and (not p[0].startswith('_') or p[0] == '_key')]
