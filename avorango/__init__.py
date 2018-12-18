from .types import Integer, String
from arango import ArangoClient
from .errors import RequiredError
from .collection import Collection
from .column import Column
from .edge import Edge
from .vertex import Vertex


class Avorango:
    Integer = Integer
    String = String
    Vertex = Vertex
    Edge = Edge
    Column = Column

    def __init__(self,
                 protocol='http',
                 host='127.0.0.1',
                 port=8529,
                 database='_system',
                 username='root',
                 password=''):
        """Connect to database

        Initializes the client of python-arango and connects
        to the database ussing its db() method. This is exposed
        in the 'session' attribute of the instance and injected
        into the 'Collection' class attribute.
        """
        self.client = ArangoClient(
            protocol=protocol,
            host=host,
            port=port,
        )
        self.session = self.client.db(
            database, username=username, password=password,
        )
        Collection._session = self.session

    def _get_or_create_graph(self, graph_name):
        if self.session.has_graph(graph_name):
            graph = self.session.graph(graph_name)
        else:
            graph = self.session \
                        .create_graph(graph_name)
        return graph

    def _create_collections(self,
                            graph_name,
                            collection_name,
                            collection_type,
                            from_vertices=None,
                            to_vertices=None):
        is_vertex = collection_type == "vertex"
        message_type = "collection" if is_vertex else "graphless edge"
        create_type = "collection" if is_vertex else "definition"
        if graph_name is not None:
            graph = self._get_or_create_graph(graph_name)
            collection_has = getattr(
                graph, "has_{}_collection".format(collection_type)
            )
            collection_create = getattr(
                graph,
                "create_{}_{}".format(collection_type, create_type)
            )
            if not collection_has(collection_name):
                if is_vertex:
                    collection_create(collection_name)
                elif from_vertices is not None and to_vertices is not None:
                    collection_create(
                        collection_name, from_vertices, to_vertices
                    )
                else:
                    raise RequiredError(
                        "from_vertices and to_vertices required"
                    )
                print(
                    "Created {}: {}"
                    .format(collection_type, collection_name)
                )
            else:
                print(
                    "The {} '{}' already exists. "
                    "Nothing changed"
                    .format(collection_type, collection_name)
                )
        elif not self.session.has_collection(collection_name):
            self.session.create_collection(collection_name)
            print(
                "Created {}: {}"
                .format(message_type, collection_name)
            )
        else:
            print(
                "The {} '{}' already exists. "
                "Nothing changed"
                .format(message_type, collection_name)
            )

    def create_all(self):
        """Create all collections defined in package

        Implemented by using Vertex.__subclasses__()
        and Edge.__subclasses__()
        """
        for vertex in self.Vertex.__subclasses__():
            name = vertex.collection_name
            self._create_collections(
                vertex._graphname, name, 'vertex'
            )

        for edge in self.Edge.__subclasses__():
            self._create_collections(
                edge._graphname,
                edge.collection_name,
                'edge',
                edge._from_vertices,
                edge._to_vertices,
            )
