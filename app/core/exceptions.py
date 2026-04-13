class PermissionDenied(Exception):
    """Raised when a user tries an unauthorized action."""


class NotFoundError(Exception):
    """Raised when an entity is not found."""


class ValidationError(Exception):
    """Raised for validation errors."""


class ConflictException(Exception):
    """Raised when there data conflict (sth already exists)."""


class DatabaseRequestError(Exception):
    """Raised when database request fails."""


class InvalidCredentialsError(Exception):
    """Raised when invalid credentials are provided."""

