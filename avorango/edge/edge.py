from .meta import EdgeMeta


class Edge(metaclass=EdgeMeta):
    _edgename = None
    _graphname = None
    _session = None
    _edge = None
    _graph = None
    _from_vertex = None
    _to_vertex = None
    _to = None
    _from = None
