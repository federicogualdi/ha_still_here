"""Common exceptions module."""


class StillHereBackendBaseError(Exception):
    """Base exception.

    All exceptions should be created from this.
    """


class NotFoundError(StillHereBackendBaseError):
    """Raised when database object does not exist."""


class NotDeletableError(StillHereBackendBaseError):
    """Raised when an object cannot be deleted because of some constrains."""


class NotUpdatableError(StillHereBackendBaseError):
    """Raised when an object cannot be updated because of some constrains."""


class InvalidArgumentError(StillHereBackendBaseError):
    """Raised when an invalid argument is passed to a function."""


class ExecutionError(StillHereBackendBaseError):
    """Raised when an unexpected behavior happens."""


class AuthenticationError(StillHereBackendBaseError):
    """Raised when Authentication error happens."""
