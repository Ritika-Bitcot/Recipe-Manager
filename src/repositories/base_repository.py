"""Base repository implementation with common CRUD operations."""

from typing import Any, Dict, List, Optional, TypeVar

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from src.core.exceptions import ConflictError
from src.interfaces.repository.base_repository_interface import BaseRepositoryInterface

T = TypeVar("T")


class BaseRepository(BaseRepositoryInterface[T]):
    """Base repository implementation with common CRUD operations."""

    def __init__(self, model_class):
        self.model_class = model_class

    def create(self, session: Session, obj_in: Dict[str, Any]) -> T:
        """Create a new record."""
        try:
            db_obj = self.model_class(**obj_in)
            session.add(db_obj)
            session.commit()
            session.refresh(db_obj)
            return db_obj
        except SQLAlchemyError as e:
            session.rollback()
            if "unique constraint" in str(e).lower():
                raise ConflictError("Record already exists")
            raise e

    def get_by_id(self, session: Session, id: int) -> Optional[T]:
        """Get a record by ID."""
        return session.query(self.model_class).filter(self.model_class.id == id).first()

    def get_all(self, session: Session, skip: int = 0, limit: int = 100) -> List[T]:
        """Get all records with pagination."""
        return session.query(self.model_class).offset(skip).limit(limit).all()

    def update(self, session: Session, id: int, obj_in: Dict[str, Any]) -> Optional[T]:
        """Update a record by ID."""
        try:
            db_obj = self.get_by_id(session, id)
            if not db_obj:
                return None

            for field, value in obj_in.items():
                if hasattr(db_obj, field):
                    setattr(db_obj, field, value)

            session.commit()
            session.refresh(db_obj)
            return db_obj
        except SQLAlchemyError as e:
            session.rollback()
            raise e

    def delete(self, session: Session, id: int) -> bool:
        """Delete a record by ID."""
        try:
            db_obj = self.get_by_id(session, id)
            if not db_obj:
                return False

            session.delete(db_obj)
            session.commit()
            return True
        except SQLAlchemyError as e:
            session.rollback()
            raise e

    def count(self, session: Session) -> int:
        """Count total records."""
        return session.query(self.model_class).count()
