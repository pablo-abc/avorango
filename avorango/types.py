from .errors import InvalidFieldError


class BaseType:
    _value = None

    def getter(self):
        return self._value


class Integer(BaseType):
    def setter(self, value):
        if not isinstance(value, int):
            raise InvalidFieldError("Integer expected")
        self._value = value


class String(BaseType):
    def __init__(self, length):
        self.length = length

    def setter(self, value):
        if not isinstance(value, str):
            raise InvalidFieldError("String expected")
        if len(value) > self.length:
            raise InvalidFieldError(
                "Value length must be less than {}".format(self.length)
            )
        self._value = value
