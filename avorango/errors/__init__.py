class InvalidFieldError(Exception):
    def __init__(self, message=None):
        if message is not None:
            self.message = message


class DefinitionError(Exception):
    def __init__(self, message=None):
        if message is not None:
            self.message = message
