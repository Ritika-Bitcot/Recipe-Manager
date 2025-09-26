"""Test configuration and fixtures for Recipe Manager API."""

import os
from typing import Generator
from unittest.mock import Mock

import pytest
from flask import Flask

# Set test environment variables before importing the app
os.environ["DATABASE_URL"] = "sqlite:///:memory:"
os.environ["SECRET_KEY"] = "test-secret-key"
os.environ["ALLOWED_ORIGINS"] = '["*"]'
os.environ["ENVIRONMENT"] = "test"

from src.api.app import create_app  # noqa: E402
from src.core.database import db, get_db_session  # noqa: E402
from src.models.recipe_model import Recipe  # noqa: E402
from src.models.user_model import User  # noqa: E402


@pytest.fixture(scope="session")
def test_config():
    """Test configuration."""
    return {
        "TESTING": True,
        "SECRET_KEY": "test-secret-key",
        "JWT_SECRET_KEY": "test-jwt-secret-key",
        "JWT_ACCESS_TOKEN_EXPIRES": 3600,
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
        "SQLALCHEMY_TRACK_MODIFICATIONS": False,
    }


@pytest.fixture(scope="function")
def app(test_config) -> Generator[Flask, None, None]:
    """Create and configure a test Flask application."""
    app = create_app()
    app.config.update(test_config)

    with app.app_context():
        db.drop_all()  # Clean up first
        db.create_all()
        # Clear any existing data
        from sqlalchemy import text

        db.session.execute(text("DELETE FROM recipes"))
        db.session.execute(text("DELETE FROM users"))
        db.session.commit()
        yield app
        db.session.remove()
        db.drop_all()
        db.session.close_all()


@pytest.fixture(scope="function")
def client(app: Flask):
    """Create a test client for the Flask application."""
    return app.test_client()


@pytest.fixture(scope="function")
def db_session(app: Flask):
    """Create a database session for testing."""
    with app.app_context():
        session = get_db_session()
        yield session
        session.rollback()
        session.close()


@pytest.fixture(scope="function")
def sample_user_data():
    """Sample user data for testing."""
    import uuid

    return {
        "email": f"test-{uuid.uuid4().hex[:8]}@example.com",
        "password": "TestPassword123",
        "first_name": "Test",
        "last_name": "User",
    }


@pytest.fixture
def sample_user(db_session, sample_user_data):
    """Create a sample user in the database."""
    from sqlalchemy import text

    # Clear any existing users to prevent conflicts
    db_session.execute(text("DELETE FROM recipes"))
    db_session.execute(text("DELETE FROM users"))
    db_session.commit()

    user = User(
        email=sample_user_data["email"],
        password_hash="hashed_password",
        first_name=sample_user_data["first_name"],
        last_name=sample_user_data["last_name"],
        is_active=True,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def sample_recipe_data():
    """Sample recipe data for testing."""
    return {
        "title": "Test Recipe",
        "description": "A test recipe",
        "ingredients": ["ingredient1", "ingredient2"],
        "instructions": ["step1", "step2"],
        "prep_time_minutes": 30,
        "cook_time_minutes": 45,
        "servings": 4,
        "difficulty": "medium",
        "tags": ["test", "recipe"],
    }


@pytest.fixture
def sample_recipe(db_session, sample_user, sample_recipe_data):
    """Create a sample recipe in the database."""
    recipe = Recipe(
        title=sample_recipe_data["title"],
        description=sample_recipe_data["description"],
        ingredients=sample_recipe_data["ingredients"],
        instructions=sample_recipe_data["instructions"],
        prep_time_minutes=sample_recipe_data["prep_time_minutes"],
        cook_time_minutes=sample_recipe_data["cook_time_minutes"],
        servings=sample_recipe_data["servings"],
        difficulty=sample_recipe_data["difficulty"],
        tags=sample_recipe_data["tags"],
        owner_id=sample_user.id,
    )
    db_session.add(recipe)
    db_session.commit()
    db_session.refresh(recipe)
    return recipe


@pytest.fixture
def auth_headers(client, sample_user_data):
    """Get authentication headers for testing."""
    # Register a new user to get token
    response = client.post(
        "/api/auth/register",
        json=sample_user_data,
    )

    if response.status_code == 201:
        token = response.json["token"]["access_token"]
        return {"Authorization": f"Bearer {token}"}

    # If registration fails, try login
    response = client.post(
        "/api/auth/login",
        json={
            "email": sample_user_data["email"],
            "password": sample_user_data["password"],
        },
    )

    if response.status_code == 200:
        token = response.json["token"]["access_token"]
        return {"Authorization": f"Bearer {token}"}

    return {}


@pytest.fixture
def mock_jwt_token():
    """Mock JWT token for testing."""
    return "mock.jwt.token"


@pytest.fixture
def mock_user_id():
    """Mock user ID for testing."""
    return 1


@pytest.fixture
def mock_email():
    """Mock email for testing."""
    return "test@example.com"


@pytest.fixture
def invalid_email():
    """Invalid email for testing."""
    return "invalid-email"


@pytest.fixture
def weak_password():
    """Weak password for testing."""
    return "weak"


@pytest.fixture
def strong_password():
    """Strong password for testing."""
    return "StrongPassword123!"


@pytest.fixture
def invalid_recipe_data():
    """Invalid recipe data for testing."""
    return {
        "title": "",  # Empty title
        "ingredients": [],  # Empty ingredients
        "instructions": [],  # Empty instructions
    }


@pytest.fixture
def invalid_user_data():
    """Invalid user data for testing."""
    return {
        "email": "invalid-email",  # Invalid email format
        "password": "weak",  # Too short password
        "first_name": "",  # Empty first name
        "last_name": "",  # Empty last name
    }


@pytest.fixture
def mock_repository():
    """Mock repository for testing."""
    return Mock()


@pytest.fixture
def mock_service():
    """Mock service for testing."""
    return Mock()


@pytest.fixture
def mock_validator():
    """Mock validator for testing."""
    return Mock()


@pytest.fixture(autouse=True)
def cleanup_database():
    """Clean up database after each test."""
    yield
    # Cleanup is handled by the db_session fixture
    pass


@pytest.fixture
def mock_external_service():
    """Mock external service for testing."""
    return Mock()


@pytest.fixture
def sample_pagination_params():
    """Sample pagination parameters for testing."""
    return {"page": 1, "per_page": 10}


@pytest.fixture
def sample_search_params():
    """Sample search parameters for testing."""
    return {
        "search": "test recipe",
        "difficulty": "easy",
        "prep_time_max": 60,
        "cook_time_max": 120,
        "tags": "test,recipe",
    }


@pytest.fixture
def sample_sort_params():
    """Sample sort parameters for testing."""
    return {"sort_by": "title", "sort_order": "asc"}


@pytest.fixture
def mock_database_error():
    """Mock database error for testing."""
    from sqlalchemy.exc import SQLAlchemyError

    return SQLAlchemyError("Database connection failed")


@pytest.fixture
def mock_validation_error():
    """Mock validation error for testing."""
    from src.core.exceptions import ValidationError

    return ValidationError("Validation failed", "test_field")


@pytest.fixture
def mock_authentication_error():
    """Mock authentication error for testing."""
    from src.core.exceptions import AuthenticationError

    return AuthenticationError("Authentication failed")


@pytest.fixture
def mock_conflict_error():
    """Mock conflict error for testing."""
    from src.core.exceptions import ConflictError

    return ConflictError("Resource already exists", "email")


@pytest.fixture
def mock_not_found_error():
    """Mock not found error for testing."""
    from src.core.exceptions import ResourceNotFoundError

    return ResourceNotFoundError("User", 1)


@pytest.fixture
def sample_error_response():
    """Sample error response for testing."""
    return {
        "error": {
            "code": "VALIDATION_ERROR",
            "message": "Validation failed",
            "status_code": 400,
            "details": {"field": "test_field"},
        }
    }
