class BaseError(Exception):
    def __init__(self, message=None):
        if message is not None:
            self.message = message


class InvalidFieldError(BaseError):
    message = "The field is invalid"


class DefinitionError(BaseError):
    message = "The defiition is invalid"


class RequiredError(BaseError):
    message = "The field is required"


class SessionError(BaseError):
    message = "No session defined"
