"""Tests for centralized error handling system."""

from unittest.mock import patch

from werkzeug.exceptions import HTTPException

from src.core.error_handler import (
    create_error_response,
    create_error_response_from_exception,
    handle_app_exception,
    handle_generic_exception,
    handle_http_exception,
    handle_pydantic_validation_error,
    handle_validation_error,
)
from src.core.exceptions import (
    AuthenticationError,
    AuthorizationError,
    ConflictError,
    DatabaseError,
    ExternalServiceError,
    InternalServerError,
    RateLimitError,
    ResourceNotFoundError,
    ValidationError,
)


class TestErrorResponseCreation:
    """Test error response creation functions."""

    def test_create_error_response_basic(self):
        """Test basic error response creation."""
        response = create_error_response(error_code="TEST_ERROR", message="Test error message", status_code=400)

        assert "error" in response
        assert response["error"]["code"] == "TEST_ERROR"
        assert response["error"]["message"] == "Test error message"
        assert response["error"]["status_code"] == 400

    def test_create_error_response_with_details(self):
        """Test error response creation with details."""
        details = {"field": "test_field", "value": "test_value"}
        response = create_error_response(
            error_code="TEST_ERROR",
            message="Test error message",
            status_code=400,
            details=details,
        )

        assert "error" in response
        assert response["error"]["details"] == details

    def test_create_error_response_no_details(self):
        """Test error response creation without details."""
        response = create_error_response(error_code="TEST_ERROR", message="Test error message", status_code=400)

        assert "error" in response
        assert "details" not in response["error"]


class TestValidationErrorHandling:
    """Test validation error handling."""

    def test_handle_validation_error_with_field(self):
        """Test validation error handling with field."""
        error = ValidationError("Invalid input", "test_field")
        response, status_code = handle_validation_error(error)

        assert status_code == 400
        assert response["error"]["code"] == "VALIDATION_ERROR"
        assert response["error"]["message"] == "Invalid input"
        assert response["error"]["status_code"] == 400
        assert "field_errors" in response["error"]["details"]
        assert len(response["error"]["details"]["field_errors"]) == 1
        assert response["error"]["details"]["field_errors"][0]["field"] == "test_field"

    def test_handle_validation_error_with_field_errors(self):
        """Test validation error handling with field errors."""
        field_errors = [
            {"field": "field1", "message": "Error 1", "type": "validation_error"},
            {"field": "field2", "message": "Error 2", "type": "validation_error"},
        ]
        error = ValidationError("Multiple errors", field_errors=field_errors)
        response, status_code = handle_validation_error(error)

        assert status_code == 400
        assert len(response["error"]["details"]["field_errors"]) == 2

    def test_handle_validation_error_no_field(self):
        """Test validation error handling without field."""
        error = ValidationError("General validation error")
        response, status_code = handle_validation_error(error)

        assert status_code == 400
        assert response["error"]["code"] == "VALIDATION_ERROR"
        assert "details" not in response["error"]

    def test_handle_pydantic_validation_error(self):
        """Test Pydantic validation error handling."""

        class MockPydanticError:
            def __init__(self):
                self.errors = lambda: [
                    {"loc": ("field1",), "msg": "Error 1", "type": "value_error"},
                    {
                        "loc": ("field2", "subfield"),
                        "msg": "Error 2",
                        "type": "type_error",
                    },
                ]

        error = MockPydanticError()
        response, status_code = handle_pydantic_validation_error(error)

        assert status_code == 400
        assert response["error"]["code"] == "VALIDATION_ERROR"
        assert "field_errors" in response["error"]["details"]
        assert len(response["error"]["details"]["field_errors"]) == 2
        assert response["error"]["details"]["field_errors"][0]["field"] == "field1"
        assert response["error"]["details"]["field_errors"][1]["field"] == "field2 -> subfield"

    def test_handle_pydantic_validation_error_no_errors(self):
        """Test Pydantic validation error handling without errors."""

        class MockPydanticError:
            def __init__(self):
                self.errors = lambda: []

        error = MockPydanticError()
        response, status_code = handle_pydantic_validation_error(error)

        assert status_code == 400
        assert response["error"]["code"] == "VALIDATION_ERROR"
        assert "details" not in response["error"]


class TestAppExceptionHandling:
    """Test application exception handling."""

    def test_handle_authentication_error(self):
        """Test authentication error handling."""
        error = AuthenticationError("Invalid credentials")
        response, status_code = handle_app_exception(error)

        assert status_code == 401
        assert response["error"]["code"] == "AUTHENTICATION_ERROR"
        assert response["error"]["message"] == "Invalid credentials"

    def test_handle_authorization_error(self):
        """Test authorization error handling."""
        error = AuthorizationError("Access denied")
        response, status_code = handle_app_exception(error)

        assert status_code == 403
        assert response["error"]["code"] == "AUTHORIZATION_ERROR"
        assert response["error"]["message"] == "Access denied"

    def test_handle_resource_not_found_error(self):
        """Test resource not found error handling."""
        error = ResourceNotFoundError("User", 123)
        response, status_code = handle_app_exception(error)

        assert status_code == 404
        assert response["error"]["code"] == "RESOURCE_NOT_FOUND"
        assert "User with ID '123' not found" in response["error"]["message"]
        assert response["error"]["details"]["resource_type"] == "User"
        assert response["error"]["details"]["resource_id"] == 123

    def test_handle_conflict_error(self):
        """Test conflict error handling."""
        error = ConflictError("Email already exists", "email")
        response, status_code = handle_app_exception(error)

        assert status_code == 409
        assert response["error"]["code"] == "CONFLICT_ERROR"
        assert response["error"]["message"] == "Email already exists"
        assert response["error"]["details"]["field"] == "email"

    def test_handle_rate_limit_error(self):
        """Test rate limit error handling."""
        error = RateLimitError("Too many requests", retry_after=60)
        response, status_code = handle_app_exception(error)

        assert status_code == 429
        assert response["error"]["code"] == "RATE_LIMIT_ERROR"
        assert response["error"]["message"] == "Too many requests"
        assert response["error"]["details"]["retry_after"] == 60

    def test_handle_database_error(self):
        """Test database error handling."""
        error = DatabaseError("Connection failed", "SELECT")
        response, status_code = handle_app_exception(error)

        assert status_code == 500
        assert response["error"]["code"] == "DATABASE_ERROR"
        assert response["error"]["message"] == "Connection failed"
        assert response["error"]["details"]["operation"] == "SELECT"

    def test_handle_external_service_error(self):
        """Test external service error handling."""
        error = ExternalServiceError("API timeout", "payment_service")
        response, status_code = handle_app_exception(error)

        assert status_code == 502
        assert response["error"]["code"] == "EXTERNAL_SERVICE_ERROR"
        assert response["error"]["message"] == "API timeout"
        assert response["error"]["details"]["service"] == "payment_service"

    def test_handle_internal_server_error(self):
        """Test internal server error handling."""
        error = InternalServerError("Unexpected error")
        response, status_code = handle_app_exception(error)

        assert status_code == 500
        assert response["error"]["code"] == "INTERNAL_SERVER_ERROR"
        assert response["error"]["message"] == "Unexpected error"


class TestHTTPExceptionHandling:
    """Test HTTP exception handling."""

    def test_handle_http_exception_400(self):
        """Test HTTP 400 exception handling."""
        error = HTTPException(description="Bad Request")
        error.code = 400
        response, status_code = handle_http_exception(error)

        assert status_code == 400
        assert response["error"]["code"] == "BAD_REQUEST"
        assert response["error"]["message"] == "Bad Request"

    def test_handle_http_exception_404(self):
        """Test HTTP 404 exception handling."""
        error = HTTPException(description="Not Found")
        error.code = 404
        response, status_code = handle_http_exception(error)

        assert status_code == 404
        assert response["error"]["code"] == "NOT_FOUND"
        assert response["error"]["message"] == "Not Found"

    def test_handle_http_exception_500(self):
        """Test HTTP 500 exception handling."""
        error = HTTPException(description="Internal Server Error")
        error.code = 500
        response, status_code = handle_http_exception(error)

        assert status_code == 500
        assert response["error"]["code"] == "INTERNAL_SERVER_ERROR"
        assert response["error"]["message"] == "Internal Server Error"

    def test_handle_http_exception_unknown_code(self):
        """Test HTTP exception with unknown code."""
        error = HTTPException(description="Unknown Error")
        error.code = 999
        response, status_code = handle_http_exception(error)

        assert status_code == 999
        assert response["error"]["code"] == "HTTP_ERROR"
        assert response["error"]["message"] == "Unknown Error"

    def test_handle_http_exception_no_description(self):
        """Test HTTP exception without description."""
        error = HTTPException()
        error.code = 400
        response, status_code = handle_http_exception(error)

        assert status_code == 400
        assert response["error"]["message"] == "An error occurred"


class TestGenericExceptionHandling:
    """Test generic exception handling."""

    def test_handle_generic_exception(self):
        """Test generic exception handling."""
        with patch("src.core.error_handler.logger") as mock_logger:
            mock_logger.level = 30  # WARNING level (not DEBUG)
            error = Exception("Generic error")
            response, status_code = handle_generic_exception(error)

            assert status_code == 500
            assert response["error"]["code"] == "INTERNAL_SERVER_ERROR"
            assert response["error"]["message"] == "An unexpected error occurred"

    def test_handle_generic_exception_with_debug(self):
        """Test generic exception handling in debug mode."""
        with patch("src.core.error_handler.logger") as mock_logger:
            mock_logger.level = 10  # DEBUG level
            error = Exception("Debug error")
            response, status_code = handle_generic_exception(error)

            assert status_code == 500
            assert response["error"]["code"] == "INTERNAL_SERVER_ERROR"
            assert "Debug error" in response["error"]["message"]
            assert "traceback" in response["error"]["details"]


class TestErrorResponseFromException:
    """Test error response creation from any exception."""

    def test_create_error_response_from_validation_error(self):
        """Test error response creation from ValidationError."""
        error = ValidationError("Test validation error", "test_field")
        response, status_code = create_error_response_from_exception(error)

        assert status_code == 400
        assert response["error"]["code"] == "VALIDATION_ERROR"

    def test_create_error_response_from_app_exception(self):
        """Test error response creation from BaseAppException."""
        error = AuthenticationError("Test auth error")
        response, status_code = create_error_response_from_exception(error)

        assert status_code == 401
        assert response["error"]["code"] == "AUTHENTICATION_ERROR"

    def test_create_error_response_from_http_exception(self):
        """Test error response creation from HTTPException."""
        error = HTTPException(description="Test HTTP error")
        error.code = 400
        response, status_code = create_error_response_from_exception(error)

        assert status_code == 400
        assert response["error"]["code"] == "BAD_REQUEST"

    def test_create_error_response_from_generic_exception(self):
        """Test error response creation from generic Exception."""
        error = Exception("Test generic error")
        response, status_code = create_error_response_from_exception(error)

        assert status_code == 500
        assert response["error"]["code"] == "INTERNAL_SERVER_ERROR"


class TestErrorHandlingIntegration:
    """Test error handling integration scenarios."""

    def test_error_handling_chain(self):
        """Test error handling chain with different exception types."""
        # Test ValidationError
        validation_error = ValidationError("Validation failed", "field1")
        response, status_code = create_error_response_from_exception(validation_error)
        assert status_code == 400

        # Test AuthenticationError
        auth_error = AuthenticationError("Auth failed")
        response, status_code = create_error_response_from_exception(auth_error)
        assert status_code == 401

        # Test ResourceNotFoundError
        not_found_error = ResourceNotFoundError("Resource", 123)
        response, status_code = create_error_response_from_exception(not_found_error)
        assert status_code == 404

        # Test generic Exception
        generic_error = Exception("Generic error")
        response, status_code = create_error_response_from_exception(generic_error)
        assert status_code == 500

    def test_error_response_consistency(self):
        """Test that all error responses have consistent structure."""
        error_types = [
            ValidationError("Test", "field"),
            AuthenticationError("Test"),
            ResourceNotFoundError("Resource", 1),
            ConflictError("Test", "field"),
            DatabaseError("Test", "operation"),
            Exception("Test"),
        ]

        for error in error_types:
            response, status_code = create_error_response_from_exception(error)

            # Check basic structure
            assert "error" in response
            assert "code" in response["error"]
            assert "message" in response["error"]
            assert "status_code" in response["error"]

            # Check data types
            assert isinstance(response["error"]["code"], str)
            assert isinstance(response["error"]["message"], str)
            assert isinstance(response["error"]["status_code"], int)
            assert isinstance(status_code, int)

            # Check status code consistency
            assert response["error"]["status_code"] == status_code
