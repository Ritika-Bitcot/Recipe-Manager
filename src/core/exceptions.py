"""Custom exceptions for the Recipe Manager API."""

from typing import Any, Dict, List, Optional


class BaseAppException(Exception):
    """Base exception for all application exceptions."""

    def __init__(
        self,
        message: str,
        status_code: int = 500,
        error_code: str = "INTERNAL_SERVER_ERROR",
        details: Optional[Dict[str, Any]] = None,
    ):
        self.message = message
        self.status_code = status_code
        self.error_code = error_code
        self.details = details or {}
        super().__init__(self.message)


class ValidationError(BaseAppException):
    """Raised when input validation fails."""

    def __init__(
        self,
        message: str,
        field: Optional[str] = None,
        field_errors: Optional[List[Dict[str, str]]] = None,
    ):
        details = {}
        if field:
            details["field"] = field
        if field_errors:
            details["field_errors"] = field_errors

        super().__init__(
            message=message,
            status_code=400,
            error_code="VALIDATION_ERROR",
            details=details,
        )

        # Store field as instance attribute for easy access
        self.field = field


class AuthenticationError(BaseAppException):
    """Raised when authentication fails."""

    def __init__(self, message: str = "Authentication failed"):
        super().__init__(message=message, status_code=401, error_code="AUTHENTICATION_ERROR")


class AuthorizationError(BaseAppException):
    """Raised when authorization fails."""

    def __init__(self, message: str = "Access denied"):
        super().__init__(message=message, status_code=403, error_code="AUTHORIZATION_ERROR")


class ResourceNotFoundError(BaseAppException):
    """Raised when a resource is not found."""

    def __init__(self, resource_type: str, resource_id: Any = None):
        if resource_id is not None:
            message = f"{resource_type} with ID '{resource_id}' not found"
        else:
            message = f"{resource_type} not found"

        super().__init__(
            message=message,
            status_code=404,
            error_code="RESOURCE_NOT_FOUND",
            details={"resource_type": resource_type, "resource_id": resource_id},
        )

        # Store resource_type as instance attribute for easy access
        self.resource_type = resource_type
        self.resource_id = resource_id


class ConflictError(BaseAppException):
    """Raised when there's a data conflict."""

    def __init__(self, message: str = "Resource already exists", field: Optional[str] = None):
        details = {}
        if field:
            details["field"] = field

        super().__init__(
            message=message,
            status_code=409,
            error_code="CONFLICT_ERROR",
            details=details,
        )

        # Store field as instance attribute for easy access
        self.field = field


class RateLimitError(BaseAppException):
    """Raised when rate limit is exceeded."""

    def __init__(self, message: str = "Rate limit exceeded", retry_after: Optional[int] = None):
        details = {}
        if retry_after:
            details["retry_after"] = retry_after

        super().__init__(
            message=message,
            status_code=429,
            error_code="RATE_LIMIT_ERROR",
            details=details,
        )


class DatabaseError(BaseAppException):
    """Raised when database operation fails."""

    def __init__(
        self,
        message: str = "Database operation failed",
        operation: Optional[str] = None,
    ):
        details = {}
        if operation:
            details["operation"] = operation

        super().__init__(
            message=message,
            status_code=500,
            error_code="DATABASE_ERROR",
            details=details,
        )


class ExternalServiceError(BaseAppException):
    """Raised when external service fails."""

    def __init__(self, message: str = "External service failed", service: Optional[str] = None):
        details = {}
        if service:
            details["service"] = service

        super().__init__(
            message=message,
            status_code=502,
            error_code="EXTERNAL_SERVICE_ERROR",
            details=details,
        )


class InternalServerError(BaseAppException):
    """Raised when an unexpected server error occurs."""

    def __init__(self, message: str = "Internal server error"):
        super().__init__(message=message, status_code=500, error_code="INTERNAL_SERVER_ERROR")


# Legacy aliases for backward compatibility
RecipeManagerException = BaseAppException
NotFoundError = ResourceNotFoundError
UnauthorizedError = AuthorizationError
