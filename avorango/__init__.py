from inspect import getmembers
from .types import Integer, String, BaseType
from arango import ArangoClient
from stringcase import snakecase
from inspect import isclass, isroutine
from .errors import DefinitionError


class Avorango:
    Integer = Integer
    String = String

    class Model:
        def __init__(self, data=None):
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
            if 'id' in self._properties:
                self._properties['_key'] = self._properties.pop('id')
            print(self._properties)

    class Column:
        def __init__(self, value_type, required=False, primary_key=False):
            self.type_ = value_type() if isclass(value_type) else value_type
            if not isinstance(self.type_, BaseType):
                raise DefinitionError("Invalid type given")
            self._required = required
            self._primary_key = primary_key
            self._set_rules()

        def __get__(self, obj, objtype):
            return self.type_.getter()

        def __set__(self, obj, val):
            self.type_.setter(val)

        def _set_rules(self):
            try:
                self.length = self.type_.length
            except AttributeError:
                pass

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
