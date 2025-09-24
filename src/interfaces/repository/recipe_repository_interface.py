"""Recipe repository interface."""

from abc import abstractmethod
from typing import List, Optional

from sqlalchemy.orm import Session

from src.models.recipe_model import Recipe

from .base_repository_interface import BaseRepositoryInterface


class RecipeRepositoryInterface(BaseRepositoryInterface[Recipe]):
    """Recipe repository interface defining recipe-specific operations."""

    @abstractmethod
    def get_by_owner(
        self, session: Session, owner_id: int, skip: int = 0, limit: int = 100
    ) -> List[Recipe]:
        """Get recipes by owner ID with pagination."""
        pass

    @abstractmethod
    def get_by_owner_and_id(
        self, session: Session, recipe_id: int, owner_id: int
    ) -> Optional[Recipe]:
        """Get recipe by ID and owner ID (for authorization)."""
        pass

    @abstractmethod
    def count_by_owner(self, session: Session, owner_id: int) -> int:
        """Count recipes by owner ID."""
        pass

    @abstractmethod
    def search_by_title(
        self,
        session: Session,
        title: str,
        owner_id: int,
        skip: int = 0,
        limit: int = 100,
    ) -> List[Recipe]:
        """Search recipes by title for a specific owner."""
        pass

    @abstractmethod
    def get_by_category(
        self,
        session: Session,
        category: str,
        owner_id: int,
        skip: int = 0,
        limit: int = 100,
    ) -> List[Recipe]:
        """Get recipes by category for a specific owner."""
        pass
