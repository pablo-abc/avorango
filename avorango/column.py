from inspect import isclass
from .errors import DefinitionError, RequiredError
from .types import BaseType


class Column:
    def __init__(
            self,
            value_type,
            required=False,
            primary_key=False,
            default=None):
        self._type = value_type() if isclass(value_type) else value_type
        if not isinstance(self._type, BaseType):
            raise DefinitionError("Invalid type given")
        self._required = required
        self._primary_key = primary_key
        self._default = {'value': default, 'set': False}

    def __get__(self, obj, objtype):
        if obj is None:
            return self
        if self.name in obj.__dict__ and self._default['set']:
            return obj.__dict__[self.name]
        obj.__dict__[self.name] = self._type.validate(
            self._default['value']
        )
        self._default['set'] = True
        return self._default['value']

    def __set__(self, obj, val):
        obj.__dict__[self.name] = self._type.validate(
            val, self._required,
        )
        self._default['set'] = True

    def __delete__(self, obj):
        if self._required:
            raise RequiredError("The field can not be deleted")
        del obj.__dict__[self.name]

    def __set_name__(self, objtype, name):
        self.name = name
