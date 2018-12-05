from inspect import isclass
from .errors import DefinitionError
from .types import BaseType


class Column:
    def __init__(self, value_type, required=False, primary_key=False):
        self._type = value_type() if isclass(value_type) else value_type
        if not isinstance(self._type, BaseType):
            raise DefinitionError("Invalid type given")
        self._required = required
        self._primary_key = primary_key

    def __get__(self, obj, objtype):
        return self._type.getter()

    def __set__(self, obj, val):
        self._type.setter(val)
