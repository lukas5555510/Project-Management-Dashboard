class PermissionDenied(Exception):
    """Raised when a user tries an unauthorized action."""


class NotFoundError(Exception):
    """Raised when an entity is not found."""


class ValidationError(Exception):
    """Raised for validation errors."""