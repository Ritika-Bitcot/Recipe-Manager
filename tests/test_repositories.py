"""Tests for repository layer functionality."""

from unittest.mock import Mock, patch

import pytest
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from src.core.exceptions import ConflictError, ResourceNotFoundError
from src.models.user_model import User
from src.repositories.base_repository import BaseRepository
from src.repositories.recipe_repository import RecipeRepository
from src.repositories.user_repository import UserRepository


class TestBaseRepository:
    """Test base repository functionality."""

    @pytest.fixture
    def mock_session(self):
        """Create a mock database session."""
        session = Mock()
        session.add = Mock()
        session.commit = Mock()
        session.rollback = Mock()
        session.refresh = Mock()
        session.query = Mock()
        return session

    @pytest.fixture
    def base_repo(self):
        """Create base repository instance."""
        return BaseRepository(User)

    def test_create_success(self, base_repo, mock_session):
        """Test successful record creation."""
        # Setup
        user_data = {"email": "test@example.com", "password_hash": "hashed"}
        mock_user = Mock()
        mock_user.id = 1
        mock_session.refresh.return_value = mock_user

        with patch.object(base_repo, "model_class") as mock_model_class:
            mock_model_class.return_value = mock_user
            mock_model_class.__name__ = "User"
            # Execute
            result = base_repo.create(mock_session, user_data)

            # Assert
            assert result == mock_user
            mock_session.add.assert_called_once()
            mock_session.commit.assert_called_once()
            mock_session.refresh.assert_called_once_with(mock_user)

    def test_create_integrity_error(self, base_repo, mock_session):
        """Test creation with integrity error (unique constraint)."""
        # Setup
        user_data = {"email": "test@example.com", "password_hash": "hashed"}
        mock_session.commit.side_effect = IntegrityError("unique constraint", None, None)

        # Execute & Assert
        with pytest.raises(ConflictError, match="Record already exists"):
            base_repo.create(mock_session, user_data)

        mock_session.rollback.assert_called_once()

    def test_create_sqlalchemy_error(self, base_repo, mock_session):
        """Test creation with general SQLAlchemy error."""
        # Setup
        user_data = {"email": "test@example.com", "password_hash": "hashed"}
        mock_session.commit.side_effect = SQLAlchemyError("Database error")

        # Execute & Assert
        with pytest.raises(SQLAlchemyError):
            base_repo.create(mock_session, user_data)

        mock_session.rollback.assert_called_once()

    def test_get_by_id_found(self, base_repo, mock_session):
        """Test getting record by ID when found."""
        # Setup
        mock_user = Mock()
        mock_query = Mock()
        mock_query.filter.return_value.first.return_value = mock_user
        mock_session.query.return_value = mock_query

        # Execute
        result = base_repo.get_by_id(mock_session, 1)

        # Assert
        assert result == mock_user
        mock_session.query.assert_called_once_with(User)

    def test_get_by_id_not_found(self, base_repo, mock_session):
        """Test getting record by ID when not found."""
        # Setup
        mock_query = Mock()
        mock_query.filter.return_value.first.return_value = None
        mock_session.query.return_value = mock_query

        # Execute
        result = base_repo.get_by_id(mock_session, 999)

        # Assert
        assert result is None

    def test_get_all_with_pagination(self, base_repo, mock_session):
        """Test getting all records with pagination."""
        # Setup
        mock_users = [Mock(), Mock()]
        mock_query = Mock()
        mock_query.offset.return_value.limit.return_value.all.return_value = mock_users
        mock_session.query.return_value = mock_query

        # Execute
        result = base_repo.get_all(mock_session, skip=10, limit=5)

        # Assert
        assert result == mock_users
        mock_query.offset.assert_called_once_with(10)
        # Check that limit was called on the result of offset
        mock_query.offset.return_value.limit.assert_called_once_with(5)

    def test_update_success(self, base_repo, mock_session):
        """Test successful record update."""
        # Setup
        mock_user = Mock()
        mock_user.id = 1
        mock_user.email = "old@example.com"
        mock_user.password_hash = "old_hash"

        with patch.object(base_repo, "get_by_id", return_value=mock_user):
            update_data = {"email": "new@example.com"}

            # Execute
            result = base_repo.update(mock_session, 1, update_data)

            # Assert
            assert result == mock_user
            assert mock_user.email == "new@example.com"
            mock_session.commit.assert_called_once()
            mock_session.refresh.assert_called_once_with(mock_user)

    def test_update_not_found(self, base_repo, mock_session):
        """Test update when record not found."""
        # Setup
        with patch.object(base_repo, "get_by_id", return_value=None):
            update_data = {"email": "new@example.com"}

            # Execute & Assert
            with pytest.raises(ResourceNotFoundError, match="User not found"):
                base_repo.update(mock_session, 999, update_data)

    def test_update_sqlalchemy_error(self, base_repo, mock_session):
        """Test update with SQLAlchemy error."""
        # Setup
        mock_user = Mock()
        with patch.object(base_repo, "get_by_id", return_value=mock_user):
            mock_session.commit.side_effect = SQLAlchemyError("Database error")
            update_data = {"email": "new@example.com"}

            # Execute & Assert
            with pytest.raises(SQLAlchemyError):
                base_repo.update(mock_session, 1, update_data)

            mock_session.rollback.assert_called_once()

    def test_delete_success(self, base_repo, mock_session):
        """Test successful record deletion."""
        # Setup
        mock_user = Mock()
        with patch.object(base_repo, "get_by_id", return_value=mock_user):
            # Execute
            result = base_repo.delete(mock_session, 1)

            # Assert
            assert result is True
            mock_session.delete.assert_called_once_with(mock_user)
            mock_session.commit.assert_called_once()

    def test_delete_not_found(self, base_repo, mock_session):
        """Test delete when record not found."""
        # Setup
        with patch.object(base_repo, "get_by_id", return_value=None):
            # Execute
            result = base_repo.delete(mock_session, 999)

            # Assert
            assert result is False
            mock_session.delete.assert_not_called()

    def test_delete_sqlalchemy_error(self, base_repo, mock_session):
        """Test delete with SQLAlchemy error."""
        # Setup
        mock_user = Mock()
        with patch.object(base_repo, "get_by_id", return_value=mock_user):
            mock_session.commit.side_effect = SQLAlchemyError("Database error")

            # Execute & Assert
            with pytest.raises(SQLAlchemyError):
                base_repo.delete(mock_session, 1)

            mock_session.rollback.assert_called_once()

    def test_count(self, base_repo, mock_session):
        """Test counting records."""
        # Setup
        mock_query = Mock()
        mock_query.count.return_value = 42
        mock_session.query.return_value = mock_query

        # Execute
        result = base_repo.count(mock_session)

        # Assert
        assert result == 42
        mock_session.query.assert_called_once_with(User)


class TestRecipeRepository:
    """Test recipe repository specific functionality."""

    @pytest.fixture
    def recipe_repo(self):
        """Create recipe repository instance."""
        return RecipeRepository()

    @pytest.fixture
    def mock_session(self):
        """Create a mock database session."""
        session = Mock()
        session.query = Mock()
        return session

    def test_get_by_owner(self, recipe_repo, mock_session):
        """Test getting recipes by owner."""
        # Setup
        mock_recipes = [Mock(), Mock()]
        mock_query = Mock()
        mock_filtered = Mock()
        mock_offset = Mock()
        mock_limit = Mock()

        mock_query.filter.return_value = mock_filtered
        mock_filtered.offset.return_value = mock_offset
        mock_offset.limit.return_value = mock_limit
        mock_limit.all.return_value = mock_recipes
        mock_session.query.return_value = mock_query

        # Execute
        result = recipe_repo.get_by_owner(mock_session, owner_id=1, skip=0, limit=10)

        # Assert
        assert result == mock_recipes
        mock_query.filter.assert_called_once()
        mock_filtered.offset.assert_called_once_with(0)
        mock_offset.limit.assert_called_once_with(10)

    def test_get_by_owner_and_id(self, recipe_repo, mock_session):
        """Test getting recipe by owner and ID."""
        # Setup
        mock_recipe = Mock()
        mock_query = Mock()
        mock_query.filter.return_value.first.return_value = mock_recipe
        mock_session.query.return_value = mock_query

        # Execute
        result = recipe_repo.get_by_owner_and_id(mock_session, recipe_id=1, owner_id=1)

        # Assert
        assert result == mock_recipe

    def test_count_by_owner(self, recipe_repo, mock_session):
        """Test counting recipes by owner."""
        # Setup
        mock_query = Mock()
        mock_query.filter.return_value.count.return_value = 5
        mock_session.query.return_value = mock_query

        # Execute
        result = recipe_repo.count_by_owner(mock_session, owner_id=1)

        # Assert
        assert result == 5

    def test_search_by_title(self, recipe_repo, mock_session):
        """Test searching recipes by title."""
        # Setup
        mock_recipes = [Mock()]
        mock_query = Mock()
        mock_query.filter.return_value.offset.return_value.limit.return_value.all.return_value = mock_recipes
        mock_session.query.return_value = mock_query

        # Execute
        result = recipe_repo.search_by_title(mock_session, title="pasta", owner_id=1, skip=0, limit=10)

        # Assert
        assert result == mock_recipes

    def test_get_all_recipes(self, recipe_repo, mock_session):
        """Test getting all recipes (multi-tenancy read access)."""
        # Setup
        mock_recipes = [Mock(), Mock()]
        mock_query = Mock()
        mock_query.offset.return_value.limit.return_value.all.return_value = mock_recipes
        mock_session.query.return_value = mock_query

        # Execute
        result = recipe_repo.get_all(mock_session, skip=0, limit=10)

        # Assert
        assert result == mock_recipes

    def test_count_all_recipes(self, recipe_repo, mock_session):
        """Test counting all recipes."""
        # Setup
        mock_query = Mock()
        mock_query.count.return_value = 15
        mock_session.query.return_value = mock_query

        # Execute
        result = recipe_repo.count_all(mock_session)

        # Assert
        assert result == 15

    def test_get_user_recipes(self, recipe_repo, mock_session):
        """Test getting recipes by user ID (alias method)."""
        # Setup
        mock_recipes = [Mock(), Mock()]
        mock_query = Mock()
        mock_query.filter.return_value.offset.return_value.limit.return_value.all.return_value = mock_recipes
        mock_session.query.return_value = mock_query

        # Execute
        result = recipe_repo.get_user_recipes(mock_session, user_id=1, skip=0, limit=10)

        # Assert
        assert result == mock_recipes

    def test_count_user_recipes(self, recipe_repo, mock_session):
        """Test counting recipes by user ID (alias method)."""
        # Setup
        mock_query = Mock()
        mock_query.filter.return_value.count.return_value = 5
        mock_session.query.return_value = mock_query

        # Execute
        result = recipe_repo.count_user_recipes(mock_session, user_id=1)

        # Assert
        assert result == 5

    def test_count_search_recipes(self, recipe_repo, mock_session):
        """Test counting search results."""
        # Setup
        mock_query = Mock()
        mock_query.filter.return_value = mock_query  # Return self for chaining
        mock_query.count.return_value = 3
        mock_session.query.return_value = mock_query

        # Execute
        search_params = {"search": "pasta"}
        result = recipe_repo.count_search_recipes(mock_session, user_id=1, search_params=search_params)

        # Assert
        assert result == 3

    def test_count_search_recipes_with_filters(self, recipe_repo, mock_session):
        """Test counting search results with multiple filters."""
        # Setup
        mock_query = Mock()
        mock_query.filter.return_value = mock_query  # Return self for chaining
        mock_query.count.return_value = 2
        mock_session.query.return_value = mock_query

        # Execute
        search_params = {"search": "pasta", "difficulty": "easy", "prep_time_max": 30}
        result = recipe_repo.count_search_recipes(mock_session, user_id=1, search_params=search_params)

        # Assert
        assert result == 2


class TestUserRepository:
    """Test user repository specific functionality."""

    @pytest.fixture
    def user_repo(self):
        """Create user repository instance."""
        return UserRepository()

    @pytest.fixture
    def mock_session(self):
        """Create a mock database session."""
        session = Mock()
        session.query = Mock()
        return session

    def test_get_by_email(self, user_repo, mock_session):
        """Test getting user by email."""
        # Setup
        mock_user = Mock()
        mock_query = Mock()
        mock_query.filter.return_value.first.return_value = mock_user
        mock_session.query.return_value = mock_query

        # Execute
        result = user_repo.get_by_email(mock_session, "test@example.com")

        # Assert
        assert result == mock_user

    def test_email_exists_true(self, user_repo, mock_session):
        """Test email exists when user found."""
        # Setup
        mock_query = Mock()
        mock_query.filter.return_value.first.return_value = Mock()  # User found
        mock_session.query.return_value = mock_query

        # Execute
        result = user_repo.email_exists(mock_session, "test@example.com")

        # Assert
        assert result is True

    def test_email_exists_false(self, user_repo, mock_session):
        """Test email exists when user not found."""
        # Setup
        mock_query = Mock()
        mock_query.filter.return_value.first.return_value = None  # User not found
        mock_session.query.return_value = mock_query

        # Execute
        result = user_repo.email_exists(mock_session, "nonexistent@example.com")

        # Assert
        assert result is False

    def test_get_active_user(self, user_repo, mock_session):
        """Test getting active user by ID."""
        # Setup
        mock_user = Mock()
        mock_user.is_active = True
        mock_query = Mock()
        mock_query.filter.return_value.first.return_value = mock_user
        mock_session.query.return_value = mock_query

        # Execute
        result = user_repo.get_active_user(mock_session, user_id=1)

        # Assert
        assert result == mock_user
