"""Password service for password-related operations."""

from typing import bool

from src.core.exceptions import ValidationError
from src.utils.password_helper import PasswordHelper


class PasswordService:
    """Password service for password operations."""

    def __init__(self):
        self.password_helper = PasswordHelper()

    def validate_password_strength(self, password: str) -> bool:
        """Validate password strength requirements."""
        if not password:
            raise ValidationError("Password is required", "password")

        if len(password) < 8:
            raise ValidationError("Password must be at least 8 characters long", "password")

        if len(password) > 128:
            raise ValidationError("Password must be less than 128 characters", "password")

        if not self.password_helper.is_password_strong(password):
            raise ValidationError(
                "Password must contain at least one uppercase letter, one lowercase letter, and one digit",
                "password",
            )

        return True

    def hash_password(self, password: str) -> str:
        """Hash a password."""
        self.validate_password_strength(password)
        return self.password_helper.hash_password(password)

    def verify_password(self, password: str, hashed_password: str) -> bool:
        """Verify a password against its hash."""
        return self.password_helper.verify_password(password, hashed_password)
