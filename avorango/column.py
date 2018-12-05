from inspect import isclass
from .errors import DefinitionError, RequiredError
from .types import BaseType


class Column:
    def __init__(self, value_type, required=False, primary_key=False):
        self._type = value_type() if isclass(value_type) else value_type
        if not isinstance(self._type, BaseType):
            raise DefinitionError("Invalid type given")
        self._required = required
        self._primary_key = primary_key

    def __get__(self, obj, objtype):
        if obj is None:
            return self
        return obj.__dict__[self.name]

    def __set__(self, obj, val):
        obj.__dict__[self.name] = self._type.validate(val, self._required)

    def __delete__(self, obj):
        if self._required:
            raise RequiredError("The field can not be deleted")
        del obj.__dict__[self.name]

    def __set_name__(self, objtype, name):
        self.name = name
