"""Base repository implementation with common CRUD operations."""

import logging
from typing import Any, Dict, List, Optional, TypeVar

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from src.core.exceptions import ConflictError, ResourceNotFoundError
from src.interfaces.repository.base_repository_interface import BaseRepositoryInterface

T = TypeVar("T")
logger = logging.getLogger(__name__)


class BaseRepository(BaseRepositoryInterface[T]):
    """Base repository implementation with common CRUD operations."""

    def __init__(self, model_class):
        self.model_class = model_class

    def create(self, session: Session, obj_in: Dict[str, Any]) -> T:
        """Create a new record with proper error handling and logging.

        Args:
            session: Database session
            obj_in: Dictionary containing record data

        Returns:
            Created record instance

        Raises:
            ConflictError: If record violates unique constraints
            SQLAlchemyError: For other database errors
        """
        try:
            logger.debug(f"Creating {self.model_class.__name__} with data: {obj_in}")
            db_obj = self.model_class(**obj_in)
            session.add(db_obj)
            session.commit()
            session.refresh(db_obj)
            logger.info(f"Successfully created {self.model_class.__name__} with ID: {getattr(db_obj, 'id', 'unknown')}")
            return db_obj
        except SQLAlchemyError as e:
            session.rollback()
            logger.error(f"Failed to create {self.model_class.__name__}: {str(e)}")
            if "unique constraint" in str(e).lower():
                raise ConflictError("Record already exists")
            raise e

    def get_by_id(self, session: Session, id: int) -> Optional[T]:
        """Get a record by ID with proper logging.

        Args:
            session: Database session
            id: Record ID to retrieve

        Returns:
            Record instance if found, None otherwise
        """
        logger.debug(f"Retrieving {self.model_class.__name__} with ID: {id}")
        result = session.query(self.model_class).filter(self.model_class.id == id).first()
        if result:
            logger.debug(f"Found {self.model_class.__name__} with ID: {id}")
        else:
            logger.debug(f"{self.model_class.__name__} with ID: {id} not found")
        return result

    def get_all(self, session: Session, skip: int = 0, limit: int = 100) -> List[T]:
        """Get all records with pagination and logging.

        Args:
            session: Database session
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of record instances
        """
        logger.debug(f"Retrieving {self.model_class.__name__} records (skip={skip}, limit={limit})")
        results = session.query(self.model_class).offset(skip).limit(limit).all()
        logger.debug(f"Retrieved {len(results)} {self.model_class.__name__} records")
        return results

    def update(self, session: Session, id: int, obj_in: Dict[str, Any]) -> Optional[T]:
        """Update a record by ID with proper error handling and logging.

        Args:
            session: Database session
            id: Record ID to update
            obj_in: Dictionary containing updated data

        Returns:
            Updated record instance if found, None otherwise

        Raises:
            ResourceNotFoundError: If record with given ID doesn't exist
            SQLAlchemyError: For database errors
        """
        try:
            logger.debug(f"Updating {self.model_class.__name__} with ID: {id}")
            db_obj = self.get_by_id(session, id)
            if not db_obj:
                logger.warning(f"{self.model_class.__name__} with ID: {id} not found for update")
                raise ResourceNotFoundError(f"{self.model_class.__name__} not found")

            # Track changes for logging
            changes = []
            for field, value in obj_in.items():
                if hasattr(db_obj, field):
                    old_value = getattr(db_obj, field)
                    setattr(db_obj, field, value)
                    changes.append(f"{field}: {old_value} -> {value}")

            session.commit()
            session.refresh(db_obj)
            logger.info(
                f"Successfully updated {self.model_class.__name__} with ID: {id}. Changes: {', '.join(changes)}"
            )
            return db_obj
        except SQLAlchemyError as e:
            session.rollback()
            logger.error(f"Failed to update {self.model_class.__name__} with ID: {id}: {str(e)}")
            raise e

    def delete(self, session: Session, id: int) -> bool:
        """Delete a record by ID with proper error handling and logging.

        Args:
            session: Database session
            id: Record ID to delete

        Returns:
            True if record was deleted, False if not found

        Raises:
            SQLAlchemyError: For database errors
        """
        try:
            logger.debug(f"Deleting {self.model_class.__name__} with ID: {id}")
            db_obj = self.get_by_id(session, id)
            if not db_obj:
                logger.warning(f"{self.model_class.__name__} with ID: {id} not found for deletion")
                return False

            session.delete(db_obj)
            session.commit()
            logger.info(f"Successfully deleted {self.model_class.__name__} with ID: {id}")
            return True
        except SQLAlchemyError as e:
            session.rollback()
            logger.error(f"Failed to delete {self.model_class.__name__} with ID: {id}: {str(e)}")
            raise e

    def count(self, session: Session) -> int:
        """Count total records with logging.

        Args:
            session: Database session

        Returns:
            Total number of records
        """
        count = session.query(self.model_class).count()
        logger.debug(f"Total {self.model_class.__name__} records: {count}")
        return count
