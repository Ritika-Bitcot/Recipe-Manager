"""Recipe repository implementation."""

from typing import List, Optional

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
