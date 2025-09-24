"""Custom exceptions for the Recipe Manager API."""

from typing import Optional


class RecipeManagerException(Exception):
    """Base exception for Recipe Manager API."""

    def __init__(self, message: str, status_code: int = 500):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)


class ValidationError(RecipeManagerException):
    """Raised when validation fails."""

    def __init__(self, message: str, field: Optional[str] = None):
        self.field = field
        super().__init__(message, 400)


class AuthenticationError(RecipeManagerException):
    """Raised when authentication fails."""

    def __init__(self, message: str = "Authentication failed"):
        super().__init__(message, 401)


class AuthorizationError(RecipeManagerException):
    """Raised when authorization fails."""

    def __init__(self, message: str = "Access denied"):
        super().__init__(message, 403)


class NotFoundError(RecipeManagerException):
    """Raised when a resource is not found."""

    def __init__(self, message: str = "Resource not found"):
        super().__init__(message, 404)


class ConflictError(RecipeManagerException):
    """Raised when there's a conflict (e.g., duplicate email)."""

    def __init__(self, message: str = "Resource already exists"):
        super().__init__(message, 409)
