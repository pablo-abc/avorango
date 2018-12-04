from .errors import InvalidFieldError


class BaseType:
    _value = None

    def getter(self, outer):
        return self._value


class Integer(BaseType):
    def setter(self, outer, value):
        if not isinstance(value, int):
            raise InvalidFieldError("Integer expected")
        self._value = value


class String(BaseType):
    def setter(self, outer, value):
        if not isinstance(value, str):
            raise InvalidFieldError("String expected")
        self._value = value


types = {
    'Integer': Integer,
    'String': String,
}
