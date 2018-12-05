from weakref import WeakKeyDictionary
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
        self._values = WeakKeyDictionary()

    def __get__(self, obj, objtype):
        if obj is None:
            return self
        return self._values.get(obj, None)

    def __set__(self, obj, val):
        self._values[obj] = self._type.validate(val, self._required)

    def __delete__(self, obj):
        if self._required:
            raise RequiredError("The field can not be deleted")
        del self._values[obj]
