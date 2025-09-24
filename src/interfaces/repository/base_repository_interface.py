"""Base repository interface following SOLID principles."""

from abc import ABC, abstractmethod
from typing import Any, Dict, Generic, List, Optional, TypeVar

from sqlalchemy.orm import Session

T = TypeVar("T")


class BaseRepositoryInterface(Generic[T], ABC):
    """Base repository interface defining common CRUD operations."""

    @abstractmethod
    def create(self, session: Session, obj_in: Dict[str, Any]) -> T:
        """Create a new record."""
        pass

    @abstractmethod
    def get_by_id(self, session: Session, id: int) -> Optional[T]:
        """Get a record by ID."""
        pass

    @abstractmethod
    def get_all(self, session: Session, skip: int = 0, limit: int = 100) -> List[T]:
        """Get all records with pagination."""
        pass

    @abstractmethod
    def update(self, session: Session, id: int, obj_in: Dict[str, Any]) -> Optional[T]:
        """Update a record by ID."""
        pass

    @abstractmethod
    def delete(self, session: Session, id: int) -> bool:
        """Delete a record by ID."""
        pass

    @abstractmethod
    def count(self, session: Session) -> int:
        """Count total records."""
        pass
