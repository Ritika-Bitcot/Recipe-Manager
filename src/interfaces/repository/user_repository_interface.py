"""User repository interface."""

from abc import abstractmethod
from typing import Optional

from sqlalchemy.orm import Session

from src.models.user_model import User

from .base_repository_interface import BaseRepositoryInterface


class UserRepositoryInterface(BaseRepositoryInterface[User]):
    """User repository interface defining user-specific operations."""

    @abstractmethod
    def get_by_email(self, session: Session, email: str) -> Optional[User]:
        """Get user by email address."""
        pass

    @abstractmethod
    def email_exists(self, session: Session, email: str) -> bool:
        """Check if email already exists."""
        pass

    @abstractmethod
    def get_active_user(self, session: Session, user_id: int) -> Optional[User]:
        """Get active user by ID."""
        pass
