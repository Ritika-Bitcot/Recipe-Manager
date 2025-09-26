"""Tests for validation functions."""

import pytest

from src.core.exceptions import AuthenticationError, ValidationError
from src.validators.email_validator import validate_email, validate_email_optional
from src.validators.password_validator import validate_password, validate_password_strength
from src.validators.query_validators import validate_pagination_params, validate_search_params, validate_sort_params
from src.validators.recipe_validator import (
    validate_difficulty,
    validate_ingredients_list,
    validate_optional_string,
    validate_positive_integer,
    validate_recipe_data,
    validate_string_length,
)
from src.validators.token_validator import (
    validate_bearer_token,
    validate_refresh_token,
    validate_token,
    validate_token_optional,
)


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

    def test_validate_email_none(self):
        """Test None email validation."""
        with pytest.raises(ValidationError) as exc_info:
            validate_email(None)
        assert exc_info.value.field == "email"

    def test_validate_email_invalid_format(self):
        """Test invalid email format."""
        with pytest.raises(ValidationError) as exc_info:
            validate_email("invalid-email")
        assert exc_info.value.field == "email"
        assert "Invalid email format" in exc_info.value.message

    def test_validate_email_too_long(self):
        """Test email too long."""
        long_email = "a" * 250 + "@example.com"
        with pytest.raises(ValidationError) as exc_info:
            validate_email(long_email)
        assert exc_info.value.field == "email"
        assert "too long" in exc_info.value.message

    def test_validate_email_consecutive_dots(self):
        """Test email with consecutive dots."""
        with pytest.raises(ValidationError) as exc_info:
            validate_email("test..user@example.com")
        assert exc_info.value.field == "email"
        assert "consecutive dots" in exc_info.value.message

    def test_validate_email_optional_valid(self):
        """Test optional email validation with valid email."""
        result = validate_email_optional("test@example.com")
        assert result == "test@example.com"

    def test_validate_email_optional_none(self):
        """Test optional email validation with None."""
        result = validate_email_optional(None)
        assert result is None

    def test_validate_email_optional_invalid(self):
        """Test optional email validation with invalid email."""
        with pytest.raises(ValidationError):
            validate_email_optional("invalid-email")


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

    def test_validate_password_too_long(self):
        """Test password too long."""
        long_password = "a" * 129
        with pytest.raises(ValidationError) as exc_info:
            validate_password(long_password)
        assert exc_info.value.field == "password"
        assert "less than 128 characters" in exc_info.value.message

    def test_validate_password_weak_common(self):
        """Test weak common password."""
        with pytest.raises(ValidationError) as exc_info:
            validate_password("password")
        assert exc_info.value.field == "password"
        assert "too common" in exc_info.value.message

    def test_validate_password_no_letters(self):
        """Test password without letters."""
        with pytest.raises(ValidationError) as exc_info:
            validate_password("12345678")
        assert exc_info.value.field == "password"
        assert "at least one letter" in exc_info.value.message

    def test_validate_password_no_numbers(self):
        """Test password without numbers."""
        with pytest.raises(ValidationError) as exc_info:
            validate_password("PasswordTest")
        assert exc_info.value.field == "password"
        assert "at least one number" in exc_info.value.message

    def test_validate_password_strength_strong(self):
        """Test password strength validation for strong password."""
        result = validate_password_strength("StrongPassword123!")
        assert result["score"] >= 4
        assert result["strength"] in ["good", "strong"]

    def test_validate_password_strength_weak(self):
        """Test password strength validation for weak password."""
        with pytest.raises(ValidationError):
            validate_password_strength("weak")


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

    def test_validate_recipe_data_empty_ingredients(self):
        """Test recipe data with empty ingredients."""
        data = {
            "title": "Test Recipe",
            "ingredients": [],
            "instructions": ["step1"],
        }
        with pytest.raises(ValidationError) as exc_info:
            validate_recipe_data(data)
        assert exc_info.value.field == "ingredients"

    def test_validate_ingredients_list_valid(self):
        """Test valid ingredients list validation."""
        ingredients = ["ingredient1", "ingredient2"]
        result = validate_ingredients_list(ingredients)
        assert result == ingredients

    def test_validate_ingredients_list_empty(self):
        """Test empty ingredients list validation."""
        with pytest.raises(ValidationError) as exc_info:
            validate_ingredients_list([])
        assert exc_info.value.field == "ingredients"

    def test_validate_ingredients_list_too_many(self):
        """Test ingredients list with too many items."""
        ingredients = ["ingredient"] * 51
        with pytest.raises(ValidationError) as exc_info:
            validate_ingredients_list(ingredients)
        assert exc_info.value.field == "ingredients"

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

    def test_validate_string_length_too_short(self):
        """Test string too short validation."""
        with pytest.raises(ValidationError) as exc_info:
            validate_string_length("a", "field", 2, 10)
        assert exc_info.value.field == "field"

    def test_validate_string_length_too_long(self):
        """Test string too long validation."""
        with pytest.raises(ValidationError) as exc_info:
            validate_string_length("a" * 11, "field", 1, 10)
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

    def test_validate_positive_integer_negative(self):
        """Test negative positive integer validation."""
        with pytest.raises(ValidationError) as exc_info:
            validate_positive_integer(-1, "field")
        assert exc_info.value.field == "field"

    def test_validate_positive_integer_invalid(self):
        """Test invalid positive integer validation."""
        with pytest.raises(ValidationError) as exc_info:
            validate_positive_integer("invalid", "field")
        assert exc_info.value.field == "field"

    def test_validate_optional_string_valid(self):
        """Test valid optional string validation."""
        result = validate_optional_string("test", "field", 10)
        assert result == "test"

    def test_validate_optional_string_none(self):
        """Test None optional string validation."""
        result = validate_optional_string(None, "field", 10)
        assert result is None

    def test_validate_optional_string_too_long(self):
        """Test optional string too long validation."""
        with pytest.raises(ValidationError) as exc_info:
            validate_optional_string("a" * 11, "field", 10)
        assert exc_info.value.field == "field"


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

    def test_validate_pagination_params_invalid_per_page(self):
        """Test invalid per_page parameter."""
        with pytest.raises(ValidationError) as exc_info:
            validate_pagination_params(1, 101)
        assert exc_info.value.field == "per_page"

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

    def test_validate_search_params_invalid_difficulty(self):
        """Test invalid difficulty parameter."""
        with pytest.raises(ValidationError) as exc_info:
            validate_search_params(difficulty="invalid")
        assert exc_info.value.field == "difficulty"

    def test_validate_search_params_invalid_prep_time(self):
        """Test invalid prep_time_max parameter."""
        with pytest.raises(ValidationError) as exc_info:
            validate_search_params(prep_time_max=-1)
        assert exc_info.value.field == "prep_time_max"

    def test_validate_sort_params_valid(self):
        """Test valid sort parameters validation."""
        result = validate_sort_params("title", "asc")
        assert result["sort_by"] == "title"
        assert result["sort_order"] == "asc"

    def test_validate_sort_params_invalid_field(self):
        """Test invalid sort field."""
        with pytest.raises(ValidationError) as exc_info:
            validate_sort_params("invalid", "asc")
        assert exc_info.value.field == "sort_by"

    def test_validate_sort_params_invalid_order(self):
        """Test invalid sort order."""
        with pytest.raises(ValidationError) as exc_info:
            validate_sort_params("title", "invalid")
        assert exc_info.value.field == "sort_order"


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

    def test_validate_token_invalid_format(self):
        """Test invalid token format."""
        with pytest.raises(AuthenticationError) as exc_info:
            validate_token("invalid.token")
        assert "Invalid token format" in exc_info.value.message

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

    def test_validate_refresh_token_valid(self):
        """Test valid refresh token validation."""
        token = "refresh_token_1234567890abcdef"
        result = validate_refresh_token(token)
        assert result == token

    def test_validate_refresh_token_too_short(self):
        """Test refresh token too short."""
        with pytest.raises(AuthenticationError) as exc_info:
            validate_refresh_token("short")
        assert "too short" in exc_info.value.message

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
