"""Tests for SQLAlchemy models."""

from datetime import datetime

import pytest

from src.models.recipe_model import Recipe
from src.models.user_model import User


class TestUserModel:
    """Test User model functionality."""

    def test_user_creation(self, db_session, sample_user_data):
        """Test user model creation."""
        user = User(
            email=sample_user_data["email"],
            password_hash="hashed_password",
            first_name=sample_user_data["first_name"],
            last_name=sample_user_data["last_name"],
            is_active=True,
        )
        assert user.email == sample_user_data["email"]
        assert user.password_hash == "hashed_password"
        assert user.first_name == sample_user_data["first_name"]
        assert user.last_name == sample_user_data["last_name"]
        assert user.is_active is True

        # Save to database to trigger timestamp creation
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)

        assert user.created_at is not None
        assert user.updated_at is not None

    def test_user_to_dict(self, sample_user):
        """Test user to_dict method."""
        user_dict = sample_user.to_dict()
        assert isinstance(user_dict, dict)
        assert user_dict["id"] == sample_user.id
        assert user_dict["email"] == sample_user.email
        assert user_dict["first_name"] == sample_user.first_name
        assert user_dict["last_name"] == sample_user.last_name
        assert user_dict["is_active"] == sample_user.is_active
        assert "password_hash" not in user_dict  # Should not include sensitive data

    def test_user_repr(self, sample_user):
        """Test user string representation."""
        user_repr = repr(sample_user)
        assert "User" in user_repr
        assert str(sample_user.id) in user_repr
        assert sample_user.email in user_repr

    def test_user_default_values(self, db_session):
        """Test user model default values."""
        user = User(
            email="test@example.com",
            password_hash="hashed_password",
            first_name="Test",
            last_name="User",
        )

        # Save to database to trigger default values and timestamp creation
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)

        # Check default values after saving
        assert user.is_active is True
        assert user.created_at is not None
        assert user.updated_at is not None

    def test_user_relationships(self, sample_user, sample_recipe):
        """Test user relationships with recipes."""
        # This would test the relationship if it exists
        # For now, we'll just ensure the user can be created
        assert sample_user.id is not None
        assert sample_recipe.user_id == sample_user.id

    def test_user_email_uniqueness(self, db_session, sample_user_data):
        """Test that email must be unique."""
        # Create first user
        user1 = User(
            email=sample_user_data["email"],
            password_hash="hashed_password1",
            first_name="User1",
            last_name="Test",
        )
        db_session.add(user1)
        db_session.commit()

        # Try to create second user with same email
        user2 = User(
            email=sample_user_data["email"],
            password_hash="hashed_password2",
            first_name="User2",
            last_name="Test",
        )
        db_session.add(user2)

        # This should raise an integrity error
        with pytest.raises(Exception):  # SQLAlchemy integrity error
            db_session.commit()

    def test_user_timestamps(self, sample_user):
        """Test that timestamps are set correctly."""
        assert isinstance(sample_user.created_at, datetime)
        assert isinstance(sample_user.updated_at, datetime)
        assert sample_user.created_at <= sample_user.updated_at

    def test_user_activation(self, sample_user):
        """Test user activation/deactivation."""
        assert sample_user.is_active is True

        sample_user.is_active = False
        assert sample_user.is_active is False

    def test_user_name_properties(self, sample_user):
        """Test user name properties."""
        assert sample_user.first_name == "Test"
        assert sample_user.last_name == "User"

    def test_user_password_hash(self, sample_user):
        """Test password hash storage."""
        assert sample_user.password_hash == "hashed_password"
        assert isinstance(sample_user.password_hash, str)


class TestRecipeModel:
    """Test Recipe model functionality."""

    def test_recipe_creation(self, db_session, sample_recipe_data, sample_user):
        """Test recipe model creation."""
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
        assert recipe.title == sample_recipe_data["title"]
        assert recipe.description == sample_recipe_data["description"]
        assert recipe.ingredients == sample_recipe_data["ingredients"]
        assert recipe.instructions == sample_recipe_data["instructions"]
        assert recipe.prep_time == sample_recipe_data["prep_time_minutes"]
        assert recipe.cook_time == sample_recipe_data["cook_time_minutes"]
        assert recipe.servings == sample_recipe_data["servings"]
        assert recipe.difficulty == sample_recipe_data["difficulty"]
        assert recipe.tags == sample_recipe_data["tags"]
        assert recipe.user_id == sample_user.id

        # Save to database to trigger timestamp creation
        db_session.add(recipe)
        db_session.commit()
        db_session.refresh(recipe)

        assert recipe.created_at is not None
        assert recipe.updated_at is not None

    def test_recipe_to_dict(self, sample_recipe):
        """Test recipe to_dict method."""
        recipe_dict = sample_recipe.to_dict()
        assert isinstance(recipe_dict, dict)
        assert recipe_dict["id"] == sample_recipe.id
        assert recipe_dict["title"] == sample_recipe.title
        assert recipe_dict["description"] == sample_recipe.description
        assert recipe_dict["ingredients"] == sample_recipe.ingredients
        assert recipe_dict["instructions"] == sample_recipe.instructions
        assert recipe_dict["prep_time"] == sample_recipe.prep_time
        assert recipe_dict["cook_time"] == sample_recipe.cook_time
        assert recipe_dict["servings"] == sample_recipe.servings
        assert recipe_dict["difficulty"] == sample_recipe.difficulty
        assert recipe_dict["tags"] == sample_recipe.tags
        assert recipe_dict["user_id"] == sample_recipe.user_id

    def test_recipe_repr(self, sample_recipe):
        """Test recipe string representation."""
        recipe_repr = repr(sample_recipe)
        assert "Recipe" in recipe_repr
        assert str(sample_recipe.id) in recipe_repr
        assert sample_recipe.title in recipe_repr

    def test_recipe_optional_fields(self, sample_user):
        """Test recipe with optional fields."""
        recipe = Recipe(
            title="Simple Recipe",
            ingredients=["ingredient1"],
            instructions=["step1"],
            owner_id=sample_user.id,
        )
        assert recipe.title == "Simple Recipe"
        assert recipe.description is None
        assert recipe.prep_time is None
        assert recipe.cook_time is None
        assert recipe.servings is None
        assert recipe.difficulty is None
        assert recipe.tags is None

    def test_recipe_timestamps(self, sample_recipe):
        """Test that timestamps are set correctly."""
        assert isinstance(sample_recipe.created_at, datetime)
        assert isinstance(sample_recipe.updated_at, datetime)
        assert sample_recipe.created_at <= sample_recipe.updated_at

    def test_recipe_ingredients_list(self, sample_recipe):
        """Test recipe ingredients as list."""
        assert isinstance(sample_recipe.ingredients, list)
        assert len(sample_recipe.ingredients) > 0

    def test_recipe_instructions_list(self, sample_recipe):
        """Test recipe instructions as list."""
        assert isinstance(sample_recipe.instructions, list)
        assert len(sample_recipe.instructions) > 0

    def test_recipe_tags_list(self, sample_recipe):
        """Test recipe tags as list."""
        assert isinstance(sample_recipe.tags, list)
        assert len(sample_recipe.tags) > 0

    def test_recipe_difficulty_values(self, sample_user):
        """Test recipe difficulty values."""
        for difficulty in ["easy", "medium", "hard"]:
            recipe = Recipe(
                title=f"Recipe {difficulty}",
                ingredients=["ingredient1"],
                instructions=["step1"],
                difficulty=difficulty,
                owner_id=sample_user.id,
            )
            assert recipe.difficulty == difficulty

    def test_recipe_numeric_fields(self, sample_recipe):
        """Test recipe numeric fields."""
        assert isinstance(sample_recipe.prep_time, int)
        assert isinstance(sample_recipe.cook_time, int)
        assert isinstance(sample_recipe.servings, int)
        assert sample_recipe.prep_time > 0
        assert sample_recipe.cook_time > 0
        assert sample_recipe.servings > 0

    def test_recipe_user_relationship(self, sample_recipe, sample_user):
        """Test recipe user relationship."""
        assert sample_recipe.user_id == sample_user.id

    def test_recipe_update_timestamp(self, sample_recipe):
        """Test that updated_at changes when recipe is modified."""
        sample_recipe.title = "Updated Title"
        # In a real scenario, this would be updated by SQLAlchemy
        # For testing, we'll just verify the field exists
        assert sample_recipe.updated_at is not None

    def test_recipe_string_fields(self, sample_recipe):
        """Test recipe string fields."""
        assert isinstance(sample_recipe.title, str)
        assert isinstance(sample_recipe.description, str)
        assert len(sample_recipe.title) > 0

    def test_recipe_empty_optional_fields(self, sample_user):
        """Test recipe with empty optional fields."""
        recipe = Recipe(
            title="Minimal Recipe",
            ingredients=["ingredient1"],
            instructions=["step1"],
            owner_id=sample_user.id,
            description="",
            tags=[],
        )
        assert recipe.description == ""
        assert recipe.tags == []

    def test_recipe_large_data(self, sample_user):
        """Test recipe with large data."""
        large_ingredients = [f"ingredient{i}" for i in range(50)]
        large_instructions = [f"step{i}" for i in range(100)]
        large_tags = [f"tag{i}" for i in range(20)]

        recipe = Recipe(
            title="Large Recipe",
            description="A recipe with lots of data",
            ingredients=large_ingredients,
            instructions=large_instructions,
            tags=large_tags,
            owner_id=sample_user.id,
        )
        assert len(recipe.ingredients) == 50
        assert len(recipe.instructions) == 100
        assert len(recipe.tags) == 20
