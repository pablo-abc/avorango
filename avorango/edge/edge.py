from avorango.collection import Collection
from avorango.errors import InvalidFieldError


class Edge(Collection):
    _from_vertices = None
    _to_vertices = None
    _required = False

    def __init__(self,
                 from_vertices=None,
                 to_vertices=None,
                 collection_name=None):
        self._collectionname = type(self).collection_name
        if self._graphname is not None:
            self._graph = self._session.graph(self._graphname)
            self._collection = self._graph.edge_collection(
                self._collectionname)
        else:
            self._collection = \
                self._session.collection(self._collectionname)
        if collection_name is not None:
            self._collectionname = collection_name
        if from_vertices is not None:
            if type(self)._from_vertices is None:
                type(self)._from_vertices = []
            type(self)._from_vertices = \
                type(self)._from_vertices + from_vertices
        if to_vertices is not None:
            if type(self)._to_vertices is None:
                type(self)._to_vertices = []
            type(self)._to_vertices = type(self)._to_vertices + to_vertices

    def __get__(self, obj, objtype):
        if obj is None:
            return self
        if self.name not in obj.__dict__:
            return None
        return obj.__dict__[self.name]

    def __set__(self, obj, val):
        obj.__dict__[self.name] = self._validate(val)

    def __set_name__(self, objtype, name):
        self._graph = objtype._graph
        self._graphname = objtype._graphname
        self.name = name
        if self._graph is not None:
            self._collection = self._graph.edge_collection(name)
        else:
            self._collection = self._session.collection(name)
        if type(self)._from_vertices is None:
            type(self)._from_vertices = []
        if objtype not in type(self)._from_vertices:
            type(self)._from_vertices.append(objtype.collection_name)

    def _validate(self, val):
        for vertex in self._to_vertices:
            if isinstance(val, list):
                for v in val:
                    self._validate(v)
                return val
            if type(val).collection_name == vertex:
                return val
        raise InvalidFieldError()
