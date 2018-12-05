from .errors import InvalidFieldError, RequiredError


class BaseType:
    _type = None
    _name = None

    def validate(self, value, required=False):
        if self._type is None:
            return self
        if value is None:
            if required:
                raise RequiredError()
            else:
                return None
        if not isinstance(value, self._type):
            raise InvalidFieldError(
                "Expected {}".format(
                    str(self._type) if self._name is None else self._name
                )
            )
        return value


class Integer(BaseType):
    _type = int
    _name = 'integer'


class String(BaseType):
    _type = str
    _name = 'string'
    _length = None

    def __init__(self, length=None):
        self._length = length

    def validate(self, value, *args, **kwargs):
        super(String, self).validate(value, *args, **kwargs)

        if self._length is not None and len(value) > self._length:
            raise InvalidFieldError(
                "Value length must be less than {}".format(self._length)
            )
        return value
