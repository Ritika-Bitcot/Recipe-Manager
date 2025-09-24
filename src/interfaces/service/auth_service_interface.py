"""Authentication service interface."""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional

from src.schemas.user_schema import UserCreate, UserLogin


class AuthServiceInterface(ABC):
    """Authentication service interface defining auth operations."""

    @abstractmethod
    def register_user(self, user_data: UserCreate) -> Dict[str, Any]:
        """Register a new user and return user data with token."""
        pass

    @abstractmethod
    def login_user(self, login_data: UserLogin) -> Dict[str, Any]:
        """Authenticate user and return user data with token."""
        pass

    @abstractmethod
    def verify_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Verify JWT token and return user data."""
        pass

    @abstractmethod
    def hash_password(self, password: str) -> str:
        """Hash a password using bcrypt."""
        pass

    @abstractmethod
    def verify_password(self, password: str, hashed_password: str) -> bool:
        """Verify a password against its hash."""
        pass
