from inspect import getmembers
from .types import Integer, String, BaseType
from arango import ArangoClient
from stringcase import snakecase
from inspect import isclass
from .errors import DefinitionError


class Avorango:
    Integer = Integer
    String = String

    class Model:
        def __init__(self, data=None):
            model = self.__class__
            properties = \
                [p for p in
                 getmembers(model, lambda o: isinstance(o, property))]
            self._properties = dict(properties)

    class Column:
        def __init__(self, value_type, required=False, primary_key=False):
            self.type_ = value_type() if isclass(value_type) else value_type
            if not isinstance(self.type_, BaseType):
                raise DefinitionError("Invalid type given")
            self._required = required
            self._primary_key = primary_key

        def __get__(self, obj, objtype):
            return self.type_.getter()

        def __set__(self, obj, val):
            self.type_.setter(val)

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

    def create_all(self):
        models = [model.__collectionname__
                  if hasattr(model, '__collectionname__')
                  else snakecase(model.__name__)
                  for model in self.Model.__subclasses__()]
        for model in models:
            if not self.session.has_collection(model):
                self.session.create_collection(model)
                print("Created collection: {}".format(model))
