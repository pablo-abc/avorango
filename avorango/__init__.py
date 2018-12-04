from inspect import getmembers
from .types import types
from arango import ArangoClient


class Avorango:
    Integer = 'Integer'
    String = 'String'

    class Model:
        def __init__(self, data=None):
            model = self.__class__
            properties = \
                [p for p in
                 getmembers(model, lambda o: isinstance(o, property))]
            self._properties = dict(properties)

    def __init__(self):
        self.client = ArangoClient()
        test_db = self.client.db('test', username='root')
        characters = test_db.collection('characters')
        print(characters.all().batch())

    def Column(self, value_type):
        """Column definition

        A property of a model must be initalized with this function
        in order for it to be taken into account.

        property = Column(data_type)
        """
        type_instance = types[value_type]()
        return property(
            type_instance.getter,
            type_instance.setter,
        )
