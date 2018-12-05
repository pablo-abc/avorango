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
        print(self.Collection.__subclasses__()[0].__name__)
        collections = [collection._collection_name
                       if collection._collection_name is not None
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
