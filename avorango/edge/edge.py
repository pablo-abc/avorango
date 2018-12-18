from avorango.collection import Collection


class Edge(Collection):
    _from_vertices = None
    _to_vertices = None
    _to = None
    _from = None

    def __init__(self,
                 collectionname=None,
                 from_vertices=None,
                 to_vertices=None):
        self._collectionname = type(self).collection_name
        if self._graphname is not None:
            self._graph = self._session.graph(self._graphname)
            self._collection = self._graph.edge_collection(
                self._collectionname)
        else:
            self._collection = \
                self._session.collection(self._collectionname)
        if collectionname is not None:
            self._collectionname = collectionname
        if from_vertices is not None:
            self._from_vertices = from_vertices
        if to_vertices is not None:
            self._to_vertices = to_vertices

    def __get__(self, obj, objtype):
        if obj is None:
            return self
        return obj.__dict__[self.name]

    def __set__(self, obj, val):
        pass

    def __set_name__(self, objtype, name):
        self._graph = objtype._graph
        self._graphname = objtype._graphname
        self.name = name
        if self._graph is not None:
            self._collection = self._graph.edge_collection(name)
        else:
            self._collection = self._session.collection(name)
