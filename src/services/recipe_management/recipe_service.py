"""Recipe service implementation with caching and multi-tenancy."""

import logging
import math
from typing import Any, Dict, Optional

from src.core.database import get_db_session
from src.core.exceptions import ResourceNotFoundError, UnauthorizedError
from src.interfaces.repository.recipe_repository_interface import RecipeRepositoryInterface
from src.interfaces.service.recipe_service_interface import RecipeServiceInterface
from src.repositories.recipe_repository import RecipeRepository
from src.schemas.recipe_schema import RecipeListResponse, RecipeUpdate
from src.services.caching.cache_service import cache_key, cache_service, invalidate_cache
from src.validators.query_validators import validate_pagination_params, validate_search_params
from src.validators.recipe_validator import validate_recipe_data

logger = logging.getLogger(__name__)


class RecipeService(RecipeServiceInterface):
    """Recipe service implementation."""

    def __init__(self, recipe_repository: RecipeRepositoryInterface = None):
        self.recipe_repository = recipe_repository or RecipeRepository()

    @invalidate_cache("recipe:*")
    def create_recipe(self, db_session, recipe_data, user_id: int) -> Dict[str, Any]:
        """Create a new recipe for a user."""
        session = db_session

        try:
            # Handle both dict and RecipeCreate objects
            if isinstance(recipe_data, dict):
                # Validate recipe data if it's a dict
                validated_data = validate_recipe_data(recipe_data)
                recipe_dict = {
                    "title": validated_data["title"].strip(),
                    "description": (
                        validated_data["description"].strip() if validated_data.get("description") else None
                    ),
                    "ingredients": validated_data["ingredients"],
                    "instructions": validated_data["instructions"],
                    "prep_time_minutes": validated_data.get("prep_time"),
                    "cook_time_minutes": validated_data.get("cook_time"),
                    "servings": validated_data.get("servings"),
                    "difficulty": validated_data.get("difficulty"),
                    "cuisine": (validated_data["cuisine"].strip() if validated_data.get("cuisine") else None),
                    "tags": validated_data.get("tags"),
                    "image_url": (validated_data["image_url"].strip() if validated_data.get("image_url") else None),
                    "is_public": validated_data.get("is_public", "private"),
                    "owner_id": user_id,
                }
            else:
                # Handle RecipeCreate object
                recipe_dict = {
                    "title": recipe_data.title.strip(),
                    "description": (recipe_data.description.strip() if recipe_data.description else None),
                    "ingredients": recipe_data.ingredients,
                    "instructions": recipe_data.instructions,
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

            logger.info(f"Recipe {recipe.id} created for user {user_id}")

            return {
                "recipe": recipe.to_dict(),
                "message": "Recipe created successfully",
            }

        except Exception as e:
            session.rollback()
            raise e

    def get_recipe(self, db_session, recipe_id: int, user_id: int) -> Dict[str, Any]:
        """Get a recipe by ID with multi-tenancy support (users can read all recipes)."""
        session = db_session

        try:
            # First try to get from cache
            cache_key_str = cache_key("recipe", recipe_id)
            cached_result = cache_service.get(cache_key_str)
            if cached_result:
                logger.debug(f"Recipe {recipe_id} retrieved from cache")
                return cached_result

            # Get recipe from database (allow reading any recipe)
            recipe = self.recipe_repository.get_by_id(session, recipe_id)
            if not recipe:
                raise ResourceNotFoundError("Recipe", recipe_id)

            result = {
                "recipe": recipe.to_dict(),
                "message": "Recipe retrieved successfully",
            }

            # Cache the result
            cache_service.set(cache_key_str, result)
            logger.info(f"Recipe {recipe_id} retrieved for user {user_id}")

            return result

        except Exception as e:
            raise e

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

    @invalidate_cache("recipe:*")
    def update_recipe(self, db_session, recipe_id: int, recipe_data: RecipeUpdate, user_id: int) -> Dict[str, Any]:
        """Update a recipe for a specific user (enforce ownership)."""
        session = db_session

        try:
            # Check if recipe exists and belongs to user (enforce ownership)
            existing_recipe = self.recipe_repository.get_by_owner_and_id(session, recipe_id, user_id)
            if not existing_recipe:
                logger.warning(f"User {user_id} attempted to update recipe {recipe_id} they don't own")
                raise UnauthorizedError("You can only update your own recipes")

            # Prepare update data (only include non-None values)
            update_dict = {}
            for field, value in recipe_data.model_dump(exclude_unset=True).items():
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

            logger.info(f"Recipe {recipe_id} updated by user {user_id}")

            return {
                "recipe": updated_recipe.to_dict(),
                "message": "Recipe updated successfully",
            }

        except Exception as e:
            session.rollback()
            raise e

    @invalidate_cache("recipe:*")
    def delete_recipe(self, db_session, recipe_id: int, user_id: int) -> Dict[str, Any]:
        """Delete a recipe for a specific user (enforce ownership)."""
        session = db_session

        try:
            # Check if recipe exists and belongs to user (enforce ownership)
            existing_recipe = self.recipe_repository.get_by_owner_and_id(session, recipe_id, user_id)
            if not existing_recipe:
                logger.warning(f"User {user_id} attempted to delete recipe {recipe_id} they don't own")
                raise UnauthorizedError("You can only delete your own recipes")

            # Delete recipe
            success = self.recipe_repository.delete(session, recipe_id)

            logger.info(f"Recipe {recipe_id} deleted by user {user_id}")

            return {"message": "Recipe deleted successfully", "success": success}

        except Exception as e:
            session.rollback()
            raise e

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

    # Additional sync methods expected by tests
    def list_recipes(self, db_session, user_id: int = None, page: int = 1, per_page: int = 10) -> Dict[str, Any]:
        """List all recipes with pagination and caching (multi-tenancy read access)."""
        session = db_session

        try:
            # Try to get from cache first
            cache_key_str = cache_key("all_recipes", page, per_page)
            cached_result = cache_service.get(cache_key_str)
            if cached_result:
                logger.debug(f"All recipes page {page} retrieved from cache")
                return cached_result

            skip = (page - 1) * per_page
            recipes = self.recipe_repository.get_all(session, skip, per_page)
            total = self.recipe_repository.count_all(session)

            total_pages = math.ceil(total / per_page) if total > 0 else 1

            result = {
                "recipes": [recipe.to_dict() for recipe in recipes],
                "pagination": {
                    "page": page,
                    "per_page": per_page,
                    "total": total,
                    "pages": total_pages,
                },
            }

            # Cache the result
            cache_service.set(cache_key_str, result)
            logger.info(f"All recipes page {page} retrieved")

            return result
        except Exception as e:
            raise e

    def get_all_recipes(self, db_session, page: int = 1, per_page: int = 10) -> Dict[str, Any]:
        """Get all recipes (multi-tenancy read access)."""
        session = db_session

        try:
            # Try to get from cache first
            cache_key_str = cache_key("all_recipes", page, per_page)
            cached_result = cache_service.get(cache_key_str)
            if cached_result:
                logger.debug(f"All recipes page {page} retrieved from cache")
                return cached_result

            skip = (page - 1) * per_page
            recipes = self.recipe_repository.get_all(session, skip, per_page)
            total = self.recipe_repository.count_all(session)

            total_pages = math.ceil(total / per_page) if total > 0 else 1

            result = {
                "recipes": [recipe.to_dict() for recipe in recipes],
                "pagination": {
                    "page": page,
                    "per_page": per_page,
                    "total": total,
                    "pages": total_pages,
                },
            }

            # Cache the result
            cache_service.set(cache_key_str, result)
            logger.info(f"All recipes page {page} retrieved")

            return result
        except Exception as e:
            raise e

    def search_recipes(
        self,
        db_session,
        user_id: int,
        search_params: Dict[str, Any],
        page: int = 1,
        per_page: int = 10,
    ) -> Dict[str, Any]:
        """Search recipes with various filters."""
        session = db_session

        try:
            skip = (page - 1) * per_page
            recipes = self.recipe_repository.search_recipes(session, user_id, search_params, skip, per_page)
            total = self.recipe_repository.count_search_recipes(session, user_id, search_params)

            return {
                "recipes": [recipe.to_dict() for recipe in recipes],
                "pagination": {
                    "page": page,
                    "per_page": per_page,
                    "total": total,
                    "pages": math.ceil(total / per_page) if total > 0 else 1,
                },
            }
        except Exception as e:
            raise e

    # Async methods for asynchronous operations
    async def create_recipe_async(self, session, recipe_data: Dict[str, Any], user_id: int) -> Dict[str, Any]:
        """Create a new recipe asynchronously."""
        # Validate recipe data
        validated_data = validate_recipe_data(recipe_data)

        # Add user_id to validated data
        validated_data["user_id"] = user_id

        # Create recipe
        recipe = await self.recipe_repository.create_async(session, validated_data)

        return {
            "recipe": recipe.to_dict(),
            "message": "Recipe created successfully",
        }

    async def get_recipe_async(self, session, recipe_id: int, user_id: int) -> Dict[str, Any]:
        """Get a recipe by ID asynchronously."""
        recipe = await self.recipe_repository.get_by_id_async(session, recipe_id)

        if not recipe:
            raise ResourceNotFoundError("Recipe", recipe_id)

        # Check if user owns the recipe
        if recipe.user_id != user_id:
            raise ResourceNotFoundError("Recipe", recipe_id)

        return {
            "recipe": recipe.to_dict(),
            "message": "Recipe retrieved successfully",
        }

    async def update_recipe_async(
        self, session, recipe_id: int, recipe_data: Dict[str, Any], user_id: int
    ) -> Dict[str, Any]:
        """Update a recipe asynchronously."""
        # Get existing recipe
        recipe = await self.recipe_repository.get_by_id_async(session, recipe_id)

        if not recipe:
            raise ResourceNotFoundError("Recipe", recipe_id)

        # Check if user owns the recipe
        if recipe.user_id != user_id:
            raise ResourceNotFoundError("Recipe", recipe_id)

        # Validate update data
        validated_data = validate_recipe_data(recipe_data)

        # Update recipe
        updated_recipe = await self.recipe_repository.update_async(session, recipe_id, validated_data)

        return {
            "recipe": updated_recipe.to_dict(),
            "message": "Recipe updated successfully",
        }

    async def delete_recipe_async(self, session, recipe_id: int, user_id: int) -> Dict[str, Any]:
        """Delete a recipe asynchronously."""
        # Get existing recipe
        recipe = await self.recipe_repository.get_by_id_async(session, recipe_id)

        if not recipe:
            raise ResourceNotFoundError("Recipe", recipe_id)

        # Check if user owns the recipe
        if recipe.user_id != user_id:
            raise ResourceNotFoundError("Recipe", recipe_id)

        # Delete recipe
        await self.recipe_repository.delete_async(session, recipe_id)

        return {"message": "Recipe deleted successfully"}

    async def list_recipes_async(
        self,
        session,
        user_id: int,
        page: int = 1,
        per_page: int = 10,
        sort_by: str = "created_at",
        sort_order: str = "desc",
    ) -> Dict[str, Any]:
        """List user's recipes asynchronously with pagination."""
        # Validate pagination parameters
        pagination_params = validate_pagination_params(page, per_page)

        # Get recipes
        recipes = await self.recipe_repository.get_user_recipes_async(
            session,
            user_id,
            page=pagination_params["page"],
            per_page=pagination_params["per_page"],
            sort_by=sort_by,
            sort_order=sort_order,
        )

        # Get total count
        total = await self.recipe_repository.count_user_recipes_async(session, user_id)

        # Calculate pagination info
        pages = (total + per_page - 1) // per_page

        return {
            "recipes": [recipe.to_dict() for recipe in recipes],
            "pagination": {
                "page": pagination_params["page"],
                "per_page": pagination_params["per_page"],
                "total": total,
                "pages": pages,
            },
        }

    async def search_recipes_async(
        self,
        session,
        user_id: int,
        search_params: Dict[str, Any],
        page: int = 1,
        per_page: int = 10,
    ) -> Dict[str, Any]:
        """Search recipes asynchronously."""
        # Validate search parameters
        validated_params = validate_search_params(**search_params)

        # Validate pagination parameters
        pagination_params = validate_pagination_params(page, per_page)

        # Search recipes
        recipes = await self.recipe_repository.search_recipes_async(
            session,
            user_id,
            validated_params,
            page=pagination_params["page"],
            per_page=pagination_params["per_page"],
        )

        # Get total count for search
        total = await self.recipe_repository.count_search_recipes_async(session, user_id, validated_params)

        # Calculate pagination info
        pages = (total + per_page - 1) // per_page

        return {
            "recipes": [recipe.to_dict() for recipe in recipes],
            "pagination": {
                "page": pagination_params["page"],
                "per_page": pagination_params["per_page"],
                "total": total,
                "pages": pages,
            },
        }
