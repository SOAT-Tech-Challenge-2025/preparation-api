"""The domain exeptions"""


class DomainException(Exception):
    """The domain base exception"""

    def __init__(self, message="An error occurred"):
        super().__init__(message)


class NotFound(DomainException):
    """The not found exception."""

    def __init__(self, message="Not found"):
        super().__init__(message)


class PersistenceError(DomainException):
    """If an error occurs trying to persist or retrieve data"""

    def __init__(
        self, message="An error occurred while trying to persist or retrieve data"
    ):
        super().__init__(message)
