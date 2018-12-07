from .types import Integer, String
from arango import ArangoClient
from stringcase import snakecase
from .collection import Collection
from .column import Column


class Avorango:
    Integer = Integer
    String = String
    Collection = Collection
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

    def create_all(self):
        """Create all collections defined in package

        Implemented by using Collection.__subclasses__()
        """
        collections = [collection.collection_name
                       if collection.collection_name is not None
                       else snakecase(collection.__name__)
                       for collection in self.Collection.__subclasses__()]
        for collection in collections:
            if not self.session.has_collection(collection):
                self.session.create_collection(collection)
                print("Created collection: {}".format(collection))
            else:
                print(
                    "Collection '{}' already exists. "
                    "Nothing changed".format(collection)
                )
