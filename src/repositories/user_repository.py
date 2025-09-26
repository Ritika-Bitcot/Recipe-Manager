"""User repository implementation."""

from typing import Optional

from sqlalchemy.orm import Session

from src.interfaces.repository.user_repository_interface import UserRepositoryInterface
from src.models.user_model import User

from .base_repository import BaseRepository


class UserRepository(BaseRepository[User], UserRepositoryInterface):
    """User repository implementation with user-specific operations."""

    def __init__(self):
        super().__init__(User)

    def get_by_email(self, session: Session, email: str) -> Optional[User]:
        """Get user by email address."""
        return session.query(User).filter(User.email == email.lower().strip()).first()

    def email_exists(self, session: Session, email: str) -> bool:
        """Check if email already exists."""
        user = self.get_by_email(session, email)
        return user is not None

    def get_active_user(self, session: Session, user_id: int) -> Optional[User]:
        """Get active user by ID."""
        return session.query(User).filter(User.id == user_id, User.is_active is True).first()
