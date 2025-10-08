"""Centralized error handling for the Recipe Manager API."""

import logging
import traceback
from typing import Any, Dict, Optional

from flask import Flask, jsonify
from werkzeug.exceptions import HTTPException

from .exceptions import BaseAppException, ValidationError

# Import Pydantic validation error if available
try:
    from pydantic import ValidationError as PydanticValidationError
except ImportError:
    PydanticValidationError = None

logger = logging.getLogger(__name__)


def create_error_response(
    error_code: str,
    message: str,
    status_code: int,
    details: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """Create standardized error response following consistent API contract.

    Args:
        error_code: Machine-readable error code (e.g., "VALIDATION_ERROR", "NOT_FOUND")
        message: Human-readable error message for end users
        status_code: HTTP status code (400, 401, 404, 500, etc.)
        details: Additional error details (field errors, traceback, etc.)

    Returns:
        Standardized error response dictionary with consistent structure:
        {
            "error": {
                "code": str,
                "message": str,
                "status_code": int,
                "details": dict (optional)
            }
        }
    """
    response = {
        "error": {
            "code": error_code,
            "message": message,
            "status_code": status_code,
        }
    }

    if details:
        response["error"]["details"] = details

    return response


def handle_validation_error(error: ValidationError) -> tuple[Dict[str, Any], int]:
    """Handle validation errors with detailed field information.

    Args:
        error: ValidationError instance

    Returns:
        Error response tuple (response, status_code)
    """
    field_errors = []

    # Add field-specific error if available
    if hasattr(error, "field") and error.field:
        field_errors.append({"field": error.field, "message": error.message, "type": "validation_error"})

    # Add additional field errors if available
    if error.details.get("field_errors"):
        field_errors.extend(error.details["field_errors"])

    details = {}
    if field_errors:
        details["field_errors"] = field_errors

    response = create_error_response(
        error_code=error.error_code,
        message=error.message,
        status_code=error.status_code,
        details=details if details else None,
    )

    field = getattr(error, "field", None)
    logger.warning(f"Validation error: {error.message}", extra={"field": field})
    return response, error.status_code


def handle_pydantic_validation_error(error: Exception) -> tuple[Dict[str, Any], int]:
    """Handle Pydantic validation errors.

    Args:
        error: Pydantic validation error

    Returns:
        Error response tuple (response, status_code)
    """
    field_errors = []

    # Extract field errors from Pydantic error
    if hasattr(error, "errors"):
        for err in error.errors():
            field_path = " -> ".join(str(loc) for loc in err.get("loc", []))
            field_errors.append(
                {
                    "field": field_path,
                    "message": err.get("msg", "Validation error"),
                    "type": err.get("type", "validation_error"),
                }
            )

    details = {}
    if field_errors:
        details["field_errors"] = field_errors

    response = create_error_response(
        error_code="VALIDATION_ERROR",
        message="Request validation failed",
        status_code=400,
        details=details,
    )

    logger.warning(f"Pydantic validation error: {error}")
    return response, 400


def handle_app_exception(error: BaseAppException) -> tuple[Dict[str, Any], int]:
    """Handle custom application exceptions.

    Args:
        error: BaseAppException instance

    Returns:
        Error response tuple (response, status_code)
    """
    # Log error based on severity
    if error.status_code >= 500:
        logger.error(
            f"Server error: {error.message}",
            extra={"error_code": error.error_code, "details": error.details},
        )
    else:
        logger.warning(
            f"Client error: {error.message}",
            extra={"error_code": error.error_code, "details": error.details},
        )

    response = create_error_response(
        error_code=error.error_code,
        message=error.message,
        status_code=error.status_code,
        details=error.details,
    )

    return response, error.status_code


def handle_http_exception(error: HTTPException) -> tuple[Dict[str, Any], int]:
    """Handle Werkzeug HTTP exceptions.

    Args:
        error: HTTPException instance

    Returns:
        Error response tuple (response, status_code)
    """
    # Map common HTTP status codes to error codes
    error_code_map = {
        400: "BAD_REQUEST",
        401: "UNAUTHORIZED",
        403: "FORBIDDEN",
        404: "NOT_FOUND",
        405: "METHOD_NOT_ALLOWED",
        409: "CONFLICT",
        422: "UNPROCESSABLE_ENTITY",
        429: "TOO_MANY_REQUESTS",
        500: "INTERNAL_SERVER_ERROR",
        502: "BAD_GATEWAY",
        503: "SERVICE_UNAVAILABLE",
    }

    error_code = error_code_map.get(error.code, "HTTP_ERROR")
    message = error.description or "An error occurred"

    response = create_error_response(error_code=error_code, message=message, status_code=error.code)

    logger.warning(f"HTTP error {error.code}: {message}")
    return response, error.code


def handle_generic_exception(error: Exception) -> tuple[Dict[str, Any], int]:
    """Handle unexpected exceptions.

    Args:
        error: Generic exception

    Returns:
        Error response tuple (response, status_code)
    """
    # Log the full traceback for debugging
    logger.error(f"Unexpected error: {str(error)}", exc_info=True)

    # Don't expose internal details in production
    message = "An unexpected error occurred"
    details = {}

    # In development, include more details
    if logger.level <= logging.DEBUG:
        details["traceback"] = traceback.format_exc()
        message = f"Unexpected error: {str(error)}"

    response = create_error_response(
        error_code="INTERNAL_SERVER_ERROR",
        message=message,
        status_code=500,
        details=details,
    )

    return response, 500


def register_exception_handlers(app: Flask) -> None:
    """Register centralized exception handlers with Flask app.

    Args:
        app: Flask application instance
    """

    @app.errorhandler(ValidationError)
    def handle_validation_error_handler(error: ValidationError):
        """Handle validation errors."""
        return (
            jsonify(handle_validation_error(error)[0]),
            handle_validation_error(error)[1],
        )

    @app.errorhandler(BaseAppException)
    def handle_app_exception_handler(error: BaseAppException):
        """Handle custom application exceptions."""
        return jsonify(handle_app_exception(error)[0]), handle_app_exception(error)[1]

    @app.errorhandler(HTTPException)
    def handle_http_exception_handler(error: HTTPException):
        """Handle Werkzeug HTTP exceptions."""
        return jsonify(handle_http_exception(error)[0]), handle_http_exception(error)[1]

    @app.errorhandler(Exception)
    def handle_generic_exception_handler(error: Exception):
        """Handle unexpected exceptions."""
        return (
            jsonify(handle_generic_exception(error)[0]),
            handle_generic_exception(error)[1],
        )

    # Handle Pydantic validation errors if Pydantic is used
    if PydanticValidationError is not None:

        @app.errorhandler(PydanticValidationError)
        def handle_pydantic_validation_error_handler(error: PydanticValidationError):
            """Handle Pydantic validation errors."""
            return (
                jsonify(handle_pydantic_validation_error(error)[0]),
                handle_pydantic_validation_error(error)[1],
            )


def log_request_error(request, error: Exception) -> None:
    """Log request context with error.

    Args:
        request: Flask request object
        error: Exception that occurred
    """
    logger.error(
        f"Request error: {str(error)}",
        extra={
            "method": request.method,
            "url": request.url,
            "user_agent": request.headers.get("User-Agent"),
            "remote_addr": request.remote_addr,
            "traceback": traceback.format_exc(),
        },
    )


def create_error_response_from_exception(
    error: Exception,
) -> tuple[Dict[str, Any], int]:
    """Create error response from any exception type.

    Args:
        error: Exception instance

    Returns:
        Error response tuple (response, status_code)
    """
    if isinstance(error, ValidationError):
        return handle_validation_error(error)
    elif isinstance(error, BaseAppException):
        return handle_app_exception(error)
    elif isinstance(error, HTTPException):
        return handle_http_exception(error)
    else:
        return handle_generic_exception(error)
