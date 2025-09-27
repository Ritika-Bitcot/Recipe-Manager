"""Recipe repository implementation."""

from typing import Any, Dict, List, Optional

from sqlalchemy import and_
from sqlalchemy.orm import Session

from src.interfaces.repository.recipe_repository_interface import RecipeRepositoryInterface
from src.models.recipe_model import Recipe

from .base_repository import BaseRepository


class RecipeRepository(BaseRepository[Recipe], RecipeRepositoryInterface):
    """Recipe repository implementation with recipe-specific operations."""

    def __init__(self):
        super().__init__(Recipe)

    def get_by_owner(self, session: Session, owner_id: int, skip: int = 0, limit: int = 100) -> List[Recipe]:
        """Get recipes by owner ID with pagination."""
        return session.query(Recipe).filter(Recipe.owner_id == owner_id).offset(skip).limit(limit).all()

    def get_by_owner_and_id(self, session: Session, recipe_id: int, owner_id: int) -> Optional[Recipe]:
        """Get recipe by ID and owner ID (for authorization)."""
        return session.query(Recipe).filter(and_(Recipe.id == recipe_id, Recipe.owner_id == owner_id)).first()

    def count_by_owner(self, session: Session, owner_id: int) -> int:
        """Count recipes by owner ID."""
        return session.query(Recipe).filter(Recipe.owner_id == owner_id).count()

    def search_by_title(
        self,
        session: Session,
        title: str,
        owner_id: int,
        skip: int = 0,
        limit: int = 100,
    ) -> List[Recipe]:
        """Search recipes by title for a specific owner."""
        return (
            session.query(Recipe)
            .filter(and_(Recipe.owner_id == owner_id, Recipe.title.ilike(f"%{title}%")))
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_by_category(
        self,
        session: Session,
        category: str,
        owner_id: int,
        skip: int = 0,
        limit: int = 100,
    ) -> List[Recipe]:
        """Get recipes by category for a specific owner."""
        return (
            session.query(Recipe)
            .filter(and_(Recipe.owner_id == owner_id, Recipe.category == category))
            .offset(skip)
            .limit(limit)
            .all()
        )

    # Additional sync methods expected by tests
    def get_user_recipes(self, session: Session, user_id: int, skip: int = 0, limit: int = 100) -> List[Recipe]:
        """Get recipes by user ID with pagination (alias for get_by_owner)."""
        return self.get_by_owner(session, user_id, skip, limit)

    def search_recipes(
        self,
        session: Session,
        user_id: int,
        search_params: Dict[str, Any],
        skip: int = 0,
        limit: int = 100,
    ) -> List[Recipe]:
        """Search recipes with various filters."""
        query = session.query(Recipe).filter(Recipe.owner_id == user_id)

        if search_params.get("search"):
            query = query.filter(Recipe.title.ilike(f"%{search_params['search']}%"))

        if search_params.get("difficulty"):
            query = query.filter(Recipe.difficulty == search_params["difficulty"])

        if search_params.get("prep_time_max"):
            query = query.filter(Recipe.prep_time_minutes <= search_params["prep_time_max"])

        if search_params.get("cook_time_max"):
            query = query.filter(Recipe.cook_time_minutes <= search_params["cook_time_max"])

        if search_params.get("tags"):
            tags = search_params["tags"]
            if isinstance(tags, list):
                for tag in tags:
                    query = query.filter(Recipe.tags.contains([tag]))

        return query.offset(skip).limit(limit).all()

    # Async methods expected by tests
    async def create_async(self, session: Session, obj_in: Dict[str, Any]) -> Recipe:
        """Create a new record asynchronously."""
        return self.create(session, obj_in)

    async def get_by_id_async(self, session: Session, id: int) -> Optional[Recipe]:
        """Get a record by ID asynchronously."""
        return self.get_by_id(session, id)

    async def update_async(self, session: Session, id: int, obj_in: Dict[str, Any]) -> Optional[Recipe]:
        """Update a record by ID asynchronously."""
        return self.update(session, id, obj_in)

    async def delete_async(self, session: Session, id: int) -> bool:
        """Delete a record by ID asynchronously."""
        return self.delete(session, id)

    async def get_user_recipes_async(
        self,
        session: Session,
        user_id: int,
        page: int = 1,
        per_page: int = 10,
        sort_by: str = "created_at",
        sort_order: str = "desc",
    ) -> List[Recipe]:
        """Get recipes by user ID asynchronously with pagination."""
        skip = (page - 1) * per_page
        query = session.query(Recipe).filter(Recipe.owner_id == user_id)

        # Add sorting
        if hasattr(Recipe, sort_by):
            if sort_order.lower() == "desc":
                query = query.order_by(getattr(Recipe, sort_by).desc())
            else:
                query = query.order_by(getattr(Recipe, sort_by).asc())

        return query.offset(skip).limit(per_page).all()

    async def count_user_recipes_async(self, session: Session, user_id: int) -> int:
        """Count recipes by user ID asynchronously."""
        return self.count_by_owner(session, user_id)

    async def search_recipes_async(
        self,
        session: Session,
        user_id: int,
        search_params: Dict[str, Any],
        page: int = 1,
        per_page: int = 10,
    ) -> List[Recipe]:
        """Search recipes asynchronously with various filters."""
        skip = (page - 1) * per_page
        return self.search_recipes(session, user_id, search_params, skip, per_page)

    async def count_search_recipes_async(self, session: Session, user_id: int, search_params: Dict[str, Any]) -> int:
        """Count search results asynchronously."""
        query = session.query(Recipe).filter(Recipe.owner_id == user_id)

        if search_params.get("search"):
            query = query.filter(Recipe.title.ilike(f"%{search_params['search']}%"))

        if search_params.get("difficulty"):
            query = query.filter(Recipe.difficulty == search_params["difficulty"])

        if search_params.get("prep_time_max"):
            query = query.filter(Recipe.prep_time_minutes <= search_params["prep_time_max"])

        if search_params.get("cook_time_max"):
            query = query.filter(Recipe.cook_time_minutes <= search_params["cook_time_max"])

        if search_params.get("tags"):
            tags = search_params["tags"]
            if isinstance(tags, list):
                for tag in tags:
                    query = query.filter(Recipe.tags.contains([tag]))

        return query.count()

    # Additional sync methods expected by tests
    def count_user_recipes(self, session: Session, user_id: int) -> int:
        """Count recipes by user ID (alias for count_by_owner)."""
        return self.count_by_owner(session, user_id)

    def count_search_recipes(self, session: Session, user_id: int, search_params: Dict[str, Any]) -> int:
        """Count search results."""
        query = session.query(Recipe).filter(Recipe.owner_id == user_id)

        if search_params.get("search"):
            query = query.filter(Recipe.title.ilike(f"%{search_params['search']}%"))

        if search_params.get("difficulty"):
            query = query.filter(Recipe.difficulty == search_params["difficulty"])

        if search_params.get("prep_time_max"):
            query = query.filter(Recipe.prep_time_minutes <= search_params["prep_time_max"])

        if search_params.get("cook_time_max"):
            query = query.filter(Recipe.cook_time_minutes <= search_params["cook_time_max"])

        if search_params.get("tags"):
            tags = search_params["tags"]
            if isinstance(tags, list):
                for tag in tags:
                    query = query.filter(Recipe.tags.contains([tag]))

        return query.count()

    def get_all(self, session: Session, skip: int = 0, limit: int = 100) -> List[Recipe]:
        """Get all recipes with pagination (for multi-tenancy read access)."""
        return session.query(Recipe).offset(skip).limit(limit).all()

    def count_all(self, session: Session) -> int:
        """Count all recipes."""
        return session.query(Recipe).count()
