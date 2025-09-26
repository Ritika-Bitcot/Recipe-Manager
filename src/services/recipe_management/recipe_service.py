"""Recipe service implementation."""

import math
from typing import Any, Dict, Optional

from src.core.database import get_db_session
from src.core.exceptions import NotFoundError
from src.interfaces.repository.recipe_repository_interface import RecipeRepositoryInterface
from src.interfaces.service.recipe_service_interface import RecipeServiceInterface
from src.repositories.recipe_repository import RecipeRepository
from src.schemas.recipe_schema import RecipeCreate, RecipeListResponse, RecipeUpdate


class RecipeService(RecipeServiceInterface):
    """Recipe service implementation."""

    def __init__(self, recipe_repository: RecipeRepositoryInterface = None):
        self.recipe_repository = recipe_repository or RecipeRepository()

    def create_recipe(self, recipe_data: RecipeCreate, user_id: int) -> Dict[str, Any]:
        """Create a new recipe for a user."""
        session = get_db_session()

        try:
            # Prepare recipe data
            recipe_dict = {
                "title": recipe_data.title.strip(),
                "description": (recipe_data.description.strip() if recipe_data.description else None),
                "ingredients": recipe_data.ingredients,  # Already a list of strings
                "instructions": recipe_data.instructions,  # Already a list of strings
                "prep_time_minutes": recipe_data.prep_time,
                "cook_time_minutes": recipe_data.cook_time,
                "servings": recipe_data.servings,
                "difficulty": recipe_data.difficulty,
                "cuisine": (recipe_data.cuisine.strip() if recipe_data.cuisine else None),
                "tags": recipe_data.tags,
                "image_url": (recipe_data.image_url.strip() if recipe_data.image_url else None),
                "is_public": recipe_data.is_public,
                "owner_id": user_id,
            }

            # Create recipe
            recipe = self.recipe_repository.create(session, recipe_dict)

            return {
                "recipe": recipe.to_dict(),
                "message": "Recipe created successfully",
            }

        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()

    def get_recipe(self, recipe_id: int, user_id: int) -> Dict[str, Any]:
        """Get a recipe by ID for a specific user."""
        session = get_db_session()

        try:
            recipe = self.recipe_repository.get_by_owner_and_id(session, recipe_id, user_id)
            if not recipe:
                raise NotFoundError("Recipe not found")

            return {
                "recipe": recipe.to_dict(),
                "message": "Recipe retrieved successfully",
            }

        except Exception as e:
            raise e
        finally:
            session.close()

    def get_user_recipes(
        self,
        user_id: int,
        page: int = 1,
        per_page: int = 10,
        search: Optional[str] = None,
        category: Optional[str] = None,
    ) -> RecipeListResponse:
        """Get all recipes for a user with pagination and filtering."""
        session = get_db_session()

        try:
            skip = (page - 1) * per_page

            # Get recipes based on filters
            if search:
                recipes = self.recipe_repository.search_by_title(session, search, user_id, skip, per_page)
                total = len(self.recipe_repository.search_by_title(session, search, user_id, 0, 1000))
            elif category:
                recipes = self.recipe_repository.get_by_category(session, category, user_id, skip, per_page)
                total = len(self.recipe_repository.get_by_category(session, category, user_id, 0, 1000))
            else:
                recipes = self.recipe_repository.get_by_owner(session, user_id, skip, per_page)
                total = self.recipe_repository.count_by_owner(session, user_id)

            # Calculate pagination info
            total_pages = math.ceil(total / per_page) if total > 0 else 1

            return RecipeListResponse(
                recipes=[recipe.to_dict() for recipe in recipes],
                total=total,
                page=page,
                per_page=per_page,
                total_pages=total_pages,
            )

        except Exception as e:
            raise e
        finally:
            session.close()

    def update_recipe(self, recipe_id: int, recipe_data: RecipeUpdate, user_id: int) -> Dict[str, Any]:
        """Update a recipe for a specific user."""
        session = get_db_session()

        try:
            # Check if recipe exists and belongs to user
            existing_recipe = self.recipe_repository.get_by_owner_and_id(session, recipe_id, user_id)
            if not existing_recipe:
                raise NotFoundError("Recipe not found")

            # Prepare update data (only include non-None values)
            update_dict = {}
            for field, value in recipe_data.dict(exclude_unset=True).items():
                if value is not None:
                    if field in ["ingredients", "instructions", "tags"]:
                        update_dict[field] = value  # Already lists
                    elif field in [
                        "title",
                        "description",
                        "cuisine",
                        "image_url",
                    ]:
                        update_dict[field] = value.strip() if value else None
                    elif field == "prep_time":
                        update_dict["prep_time_minutes"] = value
                    elif field == "cook_time":
                        update_dict["cook_time_minutes"] = value
                    else:
                        update_dict[field] = value

            # Update recipe
            updated_recipe = self.recipe_repository.update(session, recipe_id, update_dict)

            return {
                "recipe": updated_recipe.to_dict(),
                "message": "Recipe updated successfully",
            }

        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()

    def delete_recipe(self, recipe_id: int, user_id: int) -> bool:
        """Delete a recipe for a specific user."""
        session = get_db_session()

        try:
            # Check if recipe exists and belongs to user
            existing_recipe = self.recipe_repository.get_by_owner_and_id(session, recipe_id, user_id)
            if not existing_recipe:
                raise NotFoundError("Recipe not found")

            # Delete recipe
            success = self.recipe_repository.delete(session, recipe_id)

            return success

        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()

    def validate_recipe_ownership(self, recipe_id: int, user_id: int) -> bool:
        """Validate that a recipe belongs to a specific user."""
        session = get_db_session()

        try:
            recipe = self.recipe_repository.get_by_owner_and_id(session, recipe_id, user_id)
            return recipe is not None
        except Exception:
            return False
        finally:
            session.close()
