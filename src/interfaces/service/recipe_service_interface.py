"""Recipe service interface."""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional

from src.schemas.recipe_schema import RecipeCreate, RecipeListResponse, RecipeUpdate


class RecipeServiceInterface(ABC):
    """Recipe service interface defining recipe operations."""

    @abstractmethod
    def create_recipe(self, recipe_data: RecipeCreate, user_id: int) -> Dict[str, Any]:
        """Create a new recipe for a user."""
        pass

    @abstractmethod
    def get_recipe(self, recipe_id: int, user_id: int) -> Dict[str, Any]:
        """Get a recipe by ID for a specific user."""
        pass

    @abstractmethod
    def get_user_recipes(
        self,
        user_id: int,
        page: int = 1,
        per_page: int = 10,
        search: Optional[str] = None,
        category: Optional[str] = None,
    ) -> RecipeListResponse:
        """Get all recipes for a user with pagination and filtering."""
        pass

    @abstractmethod
    def update_recipe(
        self, recipe_id: int, recipe_data: RecipeUpdate, user_id: int
    ) -> Dict[str, Any]:
        """Update a recipe for a specific user."""
        pass

    @abstractmethod
    def delete_recipe(self, recipe_id: int, user_id: int) -> bool:
        """Delete a recipe for a specific user."""
        pass

    @abstractmethod
    def validate_recipe_ownership(self, recipe_id: int, user_id: int) -> bool:
        """Validate that a recipe belongs to a specific user."""
        pass
