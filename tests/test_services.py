"""Tests for service layer functionality."""

from unittest.mock import Mock, patch

import pytest

from src.core.exceptions import (
    AuthenticationError,
    ConflictError,
    ResourceNotFoundError,
    UnauthorizedError,
    ValidationError,
)
from src.schemas.recipe_schema import RecipeCreate, RecipeUpdate
from src.schemas.user_schema import UserCreate, UserLogin
from src.services.authentication.auth_service import AuthService
from src.services.authentication.password_service import PasswordService
from src.services.recipe_management.recipe_service import RecipeService


class TestPasswordService:
    """Test password service functionality."""

    def test_validate_password_strength_valid(self):
        """Test password strength validation with valid password."""
        service = PasswordService()
        result = service.validate_password_strength("StrongPassword123")
        assert result is True

    def test_validate_password_strength_invalid(self):
        """Test password strength validation with invalid password."""
        service = PasswordService()
        with pytest.raises(ValidationError) as exc_info:
            service.validate_password_strength("weak")
        assert exc_info.value.field == "password"

    def test_hash_password(self):
        """Test password hashing."""
        service = PasswordService()
        password = "TestPassword123"
        hashed = service.hash_password(password)
        assert hashed != password
        assert isinstance(hashed, str)
        assert len(hashed) > 0

    def test_verify_password_correct(self):
        """Test password verification with correct password."""
        service = PasswordService()
        password = "TestPassword123"
        hashed = service.hash_password(password)
        result = service.verify_password(password, hashed)
        assert result is True

    def test_verify_password_incorrect(self):
        """Test password verification with incorrect password."""
        service = PasswordService()
        password = "TestPassword123"
        hashed = service.hash_password(password)
        result = service.verify_password("WrongPassword", hashed)
        assert result is False

    def test_hash_password_validation(self):
        """Test that hash_password validates password first."""
        service = PasswordService()
        with pytest.raises(ValidationError):
            service.hash_password("weak")

    def test_get_password_strength_analysis(self):
        """Test password strength analysis method."""
        service = PasswordService()
        result = service.get_password_strength_analysis("StrongPassword123!")

        assert "score" in result
        assert "strength" in result
        assert "warnings" in result
        assert isinstance(result["score"], int)
        assert isinstance(result["strength"], str)

    def test_is_password_strong_enough_good(self):
        """Test password strength check with good password."""
        service = PasswordService()
        result = service.is_password_strong_enough("StrongPassword123!", "good")
        assert result is True

    def test_is_password_strong_enough_strong(self):
        """Test password strength check with strong password."""
        service = PasswordService()
        result = service.is_password_strong_enough("VeryStrongPassword123!@#", "strong")
        assert result is True

    def test_is_password_strong_enough_weak(self):
        """Test password strength check with weak password."""
        service = PasswordService()
        result = service.is_password_strong_enough("weak", "good")
        assert result is False

    def test_is_password_strong_enough_validation_error(self):
        """Test password strength check with validation error."""
        service = PasswordService()
        result = service.is_password_strong_enough("", "good")
        assert result is False


class TestAuthService:
    """Test authentication service functionality."""

    def test_register_user_success(self, db_session, sample_user_data):
        """Test successful user registration."""
        service = AuthService()
        user_data = UserCreate(**sample_user_data)

        with patch.object(service.user_repository, "email_exists", return_value=False):
            with patch.object(service.user_repository, "create") as mock_create:
                mock_user = Mock()
                mock_user.id = 1
                mock_user.email = sample_user_data["email"]
                mock_user.to_dict.return_value = {
                    "id": 1,
                    "email": sample_user_data["email"],
                }
                mock_create.return_value = mock_user

                result = service.register_user(user_data)

                assert "user" in result
                assert "token" in result
                assert "message" in result
                assert result["message"] == "User registered successfully"

    def test_register_user_email_exists(self, db_session, sample_user_data):
        """Test user registration with existing email."""
        service = AuthService()
        user_data = UserCreate(**sample_user_data)

        with patch.object(service.user_repository, "email_exists", return_value=True):
            with pytest.raises(ConflictError) as exc_info:
                service.register_user(user_data)
            assert exc_info.value.field == "email"

    def test_login_user_success(self, db_session, sample_user_data):
        """Test successful user login."""
        service = AuthService()
        login_data = UserLogin(email=sample_user_data["email"], password=sample_user_data["password"])

        mock_user = Mock()
        mock_user.id = 1
        mock_user.email = sample_user_data["email"]
        mock_user.is_active = True
        mock_user.password_hash = "hashed_password"
        mock_user.to_dict.return_value = {"id": 1, "email": sample_user_data["email"]}

        with patch.object(service.user_repository, "get_by_email", return_value=mock_user):
            with patch.object(service.password_helper, "verify_password", return_value=True):
                result = service.login_user(login_data)

                assert "user" in result
                assert "token" in result
                assert "message" in result
                assert result["message"] == "Login successful"

    def test_login_user_invalid_credentials(self, db_session, sample_user_data):
        """Test login with invalid credentials."""
        service = AuthService()
        login_data = UserLogin(email=sample_user_data["email"], password="wrong_password")

        with patch.object(service.user_repository, "get_by_email", return_value=None):
            with pytest.raises(AuthenticationError) as exc_info:
                service.login_user(login_data)
            assert "Invalid email or password" in exc_info.value.message

    def test_login_user_inactive_account(self, db_session, sample_user_data):
        """Test login with inactive account."""
        service = AuthService()
        login_data = UserLogin(email=sample_user_data["email"], password=sample_user_data["password"])

        mock_user = Mock()
        mock_user.is_active = False

        with patch.object(service.user_repository, "get_by_email", return_value=mock_user):
            with pytest.raises(AuthenticationError) as exc_info:
                service.login_user(login_data)
            assert "Account is deactivated" in exc_info.value.message

    def test_verify_token_success(self, db_session):
        """Test successful token verification."""
        service = AuthService()
        token = "valid_token"

        mock_payload = {"user_id": 1, "email": "test@example.com"}
        mock_user = Mock()
        mock_user.id = 1
        mock_user.email = "test@example.com"
        mock_user.is_active = True

        with patch.object(service.jwt_helper, "verify_token", return_value=mock_payload):
            with patch.object(service.user_repository, "get_active_user", return_value=mock_user):
                result = service.verify_token(token)

                assert result["user_id"] == 1
                assert result["email"] == "test@example.com"
                assert result["is_active"] is True

    def test_verify_token_invalid(self, db_session):
        """Test token verification with invalid token."""
        service = AuthService()
        token = "invalid_token"

        with patch.object(service.jwt_helper, "verify_token", side_effect=Exception("Invalid token")):
            with pytest.raises(AuthenticationError) as exc_info:
                service.verify_token(token)
            assert "Token verification failed" in exc_info.value.message

    def test_verify_token_user_not_found(self, db_session):
        """Test token verification with user not found."""
        service = AuthService()
        token = "valid_token"

        mock_payload = {"user_id": 1, "email": "test@example.com"}

        with patch.object(service.jwt_helper, "verify_token", return_value=mock_payload):
            with patch.object(service.user_repository, "get_active_user", return_value=None):
                with pytest.raises(AuthenticationError) as exc_info:
                    service.verify_token(token)
                assert "User not found or inactive" in exc_info.value.message


class TestRecipeService:
    """Test recipe service functionality."""

    def test_create_recipe_success(self, db_session, sample_user, sample_recipe_data):
        """Test successful recipe creation."""
        service = RecipeService()
        recipe_data = RecipeCreate(**sample_recipe_data)

        with patch.object(service.recipe_repository, "create") as mock_create:
            mock_recipe = Mock()
            mock_recipe.id = 1
            mock_recipe.title = sample_recipe_data["title"]
            mock_recipe.to_dict.return_value = {
                "id": 1,
                "title": sample_recipe_data["title"],
            }
            mock_create.return_value = mock_recipe

            result = service.create_recipe(db_session, recipe_data, sample_user.id)

            assert "recipe" in result
            assert "message" in result
            assert result["message"] == "Recipe created successfully"

    def test_get_recipe_success(self, db_session, sample_recipe):
        """Test successful recipe retrieval."""
        service = RecipeService()

        with patch.object(service.recipe_repository, "get_by_id", return_value=sample_recipe):
            result = service.get_recipe(db_session, sample_recipe.id, sample_recipe.user_id)

            assert result["recipe"]["id"] == sample_recipe.id
            assert result["message"] == "Recipe retrieved successfully"

    def test_get_recipe_not_found(self, db_session, sample_user):
        """Test recipe retrieval with non-existent recipe."""
        service = RecipeService()

        with patch.object(service.recipe_repository, "get_by_id", return_value=None):
            with pytest.raises(ResourceNotFoundError) as exc_info:
                service.get_recipe(db_session, 999, sample_user.id)
            assert exc_info.value.resource_type == "Recipe"
            assert exc_info.value.resource_id == 999

    def test_update_recipe_success(self, db_session, sample_recipe, sample_recipe_data):
        """Test successful recipe update."""
        service = RecipeService()
        update_data = RecipeUpdate(**sample_recipe_data)

        with patch.object(service.recipe_repository, "get_by_id", return_value=sample_recipe):
            with patch.object(service.recipe_repository, "update") as mock_update:
                mock_updated_recipe = Mock()
                mock_updated_recipe.to_dict.return_value = {
                    "id": sample_recipe.id,
                    "title": "Updated Title",
                }
                mock_update.return_value = mock_updated_recipe

                result = service.update_recipe(db_session, sample_recipe.id, update_data, sample_recipe.user_id)

                assert "recipe" in result
                assert "message" in result
                assert result["message"] == "Recipe updated successfully"

    def test_update_recipe_not_found(self, db_session, sample_user, sample_recipe_data):
        """Test recipe update with non-existent recipe."""
        service = RecipeService()
        update_data = RecipeUpdate(**sample_recipe_data)

        with patch.object(service.recipe_repository, "get_by_owner_and_id", return_value=None):
            with pytest.raises(UnauthorizedError) as exc_info:
                service.update_recipe(db_session, 999, update_data, sample_user.id)
            assert "You can only update your own recipes" in str(exc_info.value)

    def test_delete_recipe_success(self, db_session, sample_recipe):
        """Test successful recipe deletion."""
        service = RecipeService()

        with patch.object(service.recipe_repository, "get_by_id", return_value=sample_recipe):
            with patch.object(service.recipe_repository, "delete") as mock_delete:
                mock_delete.return_value = True

                result = service.delete_recipe(db_session, sample_recipe.id, sample_recipe.user_id)

                assert "message" in result
                assert result["message"] == "Recipe deleted successfully"

    def test_delete_recipe_not_found(self, db_session, sample_user):
        """Test recipe deletion with non-existent recipe."""
        service = RecipeService()

        with patch.object(service.recipe_repository, "get_by_owner_and_id", return_value=None):
            with pytest.raises(UnauthorizedError) as exc_info:
                service.delete_recipe(db_session, 999, sample_user.id)
            assert "You can only delete your own recipes" in str(exc_info.value)

    def test_list_recipes_success(self, db_session, sample_user):
        """Test successful recipe listing."""
        service = RecipeService()
        mock_recipes = [Mock(), Mock()]
        mock_recipes[0].to_dict.return_value = {"id": 1, "title": "Recipe 1"}
        mock_recipes[1].to_dict.return_value = {"id": 2, "title": "Recipe 2"}

        with patch.object(service.recipe_repository, "get_all", return_value=mock_recipes):
            with patch.object(service.recipe_repository, "count_all", return_value=2):
                result = service.list_recipes(db_session, page=1, per_page=10)

                assert "recipes" in result
                assert "pagination" in result
                assert len(result["recipes"]) == 2
                assert result["pagination"]["total"] == 2

    def test_list_recipes_empty(self, db_session, sample_user):
        """Test recipe listing with no recipes."""
        service = RecipeService()

        with patch.object(service.recipe_repository, "get_all", return_value=[]):
            with patch.object(service.recipe_repository, "count_all", return_value=0):
                result = service.list_recipes(db_session, page=1, per_page=10)

                assert "recipes" in result
                assert "pagination" in result
                assert len(result["recipes"]) == 0
                assert result["pagination"]["total"] == 0

    def test_search_recipes_success(self, db_session, sample_user):
        """Test successful recipe search."""
        service = RecipeService()
        mock_recipes = [Mock()]
        mock_recipes[0].to_dict.return_value = {"id": 1, "title": "Test Recipe"}

        search_params = {
            "search": "test",
            "difficulty": "easy",
            "prep_time_max": 60,
            "cook_time_max": 120,
            "tags": ["test"],
        }

        with patch.object(service.recipe_repository, "search_recipes", return_value=mock_recipes):
            with patch.object(service.recipe_repository, "count_search_recipes", return_value=1):
                result = service.search_recipes(db_session, sample_user.id, search_params, page=1, per_page=10)

                assert "recipes" in result
                assert "pagination" in result
                assert len(result["recipes"]) == 1

    def test_recipe_authorization(self, db_session, sample_recipe, sample_user):
        """Test recipe authorization (users can read all recipes but only modify their own)."""
        service = RecipeService()
        other_user_id = 999

        with patch.object(service.recipe_repository, "get_by_id", return_value=sample_recipe):
            # Users can now read all recipes (multi-tenancy read access)
            result = service.get_recipe(db_session, sample_recipe.id, other_user_id)
            assert "recipe" in result
            assert result["recipe"]["id"] == sample_recipe.id

    def test_recipe_validation_error(self, db_session, sample_user, invalid_recipe_data):
        """Test recipe creation with invalid data."""
        service = RecipeService()

        with pytest.raises(ValidationError):
            service.create_recipe(db_session, invalid_recipe_data, sample_user.id)

    def test_recipe_pagination(self, db_session, sample_user):
        """Test recipe pagination."""
        service = RecipeService()
        mock_recipes = [Mock() for _ in range(5)]
        for i, recipe in enumerate(mock_recipes):
            recipe.to_dict.return_value = {"id": i + 1, "title": f"Recipe {i + 1}"}

        with patch.object(service.recipe_repository, "get_all", return_value=mock_recipes):
            with patch.object(service.recipe_repository, "count_all", return_value=25):
                result = service.list_recipes(db_session, page=2, per_page=10)

                assert "pagination" in result
                assert result["pagination"]["page"] == 2
                assert result["pagination"]["per_page"] == 10
                assert result["pagination"]["total"] == 25
                assert result["pagination"]["pages"] == 3
