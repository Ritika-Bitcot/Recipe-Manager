"""Simple tests that don't require Flask dependencies."""

import os
import sys

import pytest

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from src.core.exceptions import AuthenticationError, ValidationError  # noqa: E402
from src.validators.email_validator import validate_email, validate_email_optional  # noqa: E402
from src.validators.password_validator import validate_password, validate_password_strength  # noqa: E402
from src.validators.query_validators import (  # noqa: E402
    validate_pagination_params,
    validate_search_params,
    validate_sort_params,
)
from src.validators.recipe_validator import (  # noqa: E402
    validate_difficulty,
    validate_optional_string,
    validate_positive_integer,
    validate_recipe_data,
    validate_string_length,
)
from src.validators.token_validator import validate_bearer_token, validate_token, validate_token_optional  # noqa: E402


class TestEmailValidator:
    """Test email validation functions."""

    def test_validate_email_valid(self):
        """Test valid email validation."""
        result = validate_email("test@example.com")
        assert result == "test@example.com"

    def test_validate_email_normalize(self):
        """Test email normalization."""
        result = validate_email("  TEST@EXAMPLE.COM  ")
        assert result == "test@example.com"

    def test_validate_email_empty(self):
        """Test empty email validation."""
        with pytest.raises(ValidationError) as exc_info:
            validate_email("")
        assert exc_info.value.field == "email"
        assert "required" in exc_info.value.message

    def test_validate_email_invalid_format(self):
        """Test invalid email format."""
        with pytest.raises(ValidationError) as exc_info:
            validate_email("invalid-email")
        assert exc_info.value.field == "email"
        assert "Invalid email format" in exc_info.value.message

    def test_validate_email_optional_valid(self):
        """Test optional email validation with valid email."""
        result = validate_email_optional("test@example.com")
        assert result == "test@example.com"

    def test_validate_email_optional_none(self):
        """Test optional email validation with None."""
        result = validate_email_optional(None)
        assert result is None


class TestPasswordValidator:
    """Test password validation functions."""

    def test_validate_password_valid(self):
        """Test valid password validation."""
        result = validate_password("StrongPassword123")
        assert result == "StrongPassword123"

    def test_validate_password_empty(self):
        """Test empty password validation."""
        with pytest.raises(ValidationError) as exc_info:
            validate_password("")
        assert exc_info.value.field == "password"
        assert "required" in exc_info.value.message

    def test_validate_password_too_short(self):
        """Test password too short."""
        with pytest.raises(ValidationError) as exc_info:
            validate_password("short")
        assert exc_info.value.field == "password"
        assert "at least 8 characters" in exc_info.value.message

    def test_validate_password_weak_common(self):
        """Test weak common password."""
        with pytest.raises(ValidationError) as exc_info:
            validate_password("password")
        assert exc_info.value.field == "password"
        assert "too common" in exc_info.value.message

    def test_validate_password_strength_strong(self):
        """Test password strength validation for strong password."""
        result = validate_password_strength("StrongPassword123!")
        assert result["score"] >= 4
        assert result["strength"] in ["good", "strong"]


class TestRecipeValidator:
    """Test recipe validation functions."""

    def test_validate_recipe_data_valid(self):
        """Test valid recipe data validation."""
        data = {
            "title": "Test Recipe",
            "description": "A test recipe",
            "ingredients": ["ingredient1", "ingredient2"],
            "instructions": ["step1", "step2"],
            "prep_time": 30,
            "cook_time": 45,
            "servings": 4,
            "difficulty": "medium",
            "tags": ["test", "recipe"],
        }
        result = validate_recipe_data(data)
        assert result["title"] == "Test Recipe"
        assert result["ingredients"] == ["ingredient1", "ingredient2"]

    def test_validate_recipe_data_missing_title(self):
        """Test recipe data without title."""
        data = {
            "ingredients": ["ingredient1"],
            "instructions": ["step1"],
        }
        with pytest.raises(ValidationError) as exc_info:
            validate_recipe_data(data)
        assert exc_info.value.field == "title"

    def test_validate_difficulty_valid(self):
        """Test valid difficulty validation."""
        for difficulty in ["easy", "medium", "hard"]:
            result = validate_difficulty(difficulty)
            assert result == difficulty

    def test_validate_difficulty_invalid(self):
        """Test invalid difficulty validation."""
        with pytest.raises(ValidationError) as exc_info:
            validate_difficulty("invalid")
        assert exc_info.value.field == "difficulty"

    def test_validate_string_length_valid(self):
        """Test valid string length validation."""
        result = validate_string_length("test", "field", 1, 10)
        assert result == "test"

    def test_validate_string_length_empty(self):
        """Test empty string length validation."""
        with pytest.raises(ValidationError) as exc_info:
            validate_string_length("", "field", 1, 10)
        assert exc_info.value.field == "field"

    def test_validate_positive_integer_valid(self):
        """Test valid positive integer validation."""
        result = validate_positive_integer(5, "field")
        assert result == 5

    def test_validate_positive_integer_zero(self):
        """Test zero positive integer validation."""
        with pytest.raises(ValidationError) as exc_info:
            validate_positive_integer(0, "field")
        assert exc_info.value.field == "field"

    def test_validate_optional_string_valid(self):
        """Test valid optional string validation."""
        result = validate_optional_string("test", "field", 10)
        assert result == "test"

    def test_validate_optional_string_none(self):
        """Test None optional string validation."""
        result = validate_optional_string(None, "field", 10)
        assert result is None


class TestQueryValidators:
    """Test query parameter validation functions."""

    def test_validate_pagination_params_valid(self):
        """Test valid pagination parameters validation."""
        result = validate_pagination_params(1, 10)
        assert result["page"] == 1
        assert result["per_page"] == 10

    def test_validate_pagination_params_defaults(self):
        """Test pagination parameters with defaults."""
        result = validate_pagination_params()
        assert result["page"] == 1
        assert result["per_page"] == 10

    def test_validate_pagination_params_invalid_page(self):
        """Test invalid page parameter."""
        with pytest.raises(ValidationError) as exc_info:
            validate_pagination_params(0, 10)
        assert exc_info.value.field == "page"

    def test_validate_search_params_valid(self):
        """Test valid search parameters validation."""
        result = validate_search_params(
            search="test",
            difficulty="easy",
            prep_time_max=60,
            cook_time_max=120,
            tags="test,recipe",
        )
        assert result["search"] == "test"
        assert result["difficulty"] == "easy"
        assert result["prep_time_max"] == 60
        assert result["cook_time_max"] == 120
        assert result["tags"] == ["test", "recipe"]

    def test_validate_sort_params_valid(self):
        """Test valid sort parameters validation."""
        result = validate_sort_params("title", "asc")
        assert result["sort_by"] == "title"
        assert result["sort_order"] == "asc"


class TestTokenValidator:
    """Test token validation functions."""

    def test_validate_token_valid(self):
        """Test valid token validation."""
        token = (
            "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9."
            "eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ."
            "SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c"
        )
        result = validate_token(token)
        assert result == token

    def test_validate_token_empty(self):
        """Test empty token validation."""
        with pytest.raises(AuthenticationError) as exc_info:
            validate_token("")
        assert "required" in exc_info.value.message

    def test_validate_bearer_token_valid(self):
        """Test valid bearer token validation."""
        token = (
            "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9."
            "eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ."
            "SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c"
        )
        result = validate_bearer_token(f"Bearer {token}")
        assert result == token

    def test_validate_bearer_token_invalid_format(self):
        """Test invalid bearer token format."""
        with pytest.raises(AuthenticationError) as exc_info:
            validate_bearer_token("Invalid token")
        assert "must start with 'Bearer '" in exc_info.value.message

    def test_validate_token_optional_valid(self):
        """Test valid optional token validation."""
        token = (
            "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9."
            "eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ."
            "SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c"
        )
        result = validate_token_optional(token)
        assert result == token

    def test_validate_token_optional_none(self):
        """Test optional token validation with None."""
        result = validate_token_optional(None)
        assert result is None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
