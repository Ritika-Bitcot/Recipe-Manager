"""Password service for password-related operations."""

from src.utils.password_helper import PasswordHelper
from src.validators.password_validator import validate_password


class PasswordService:
    """Password service for password operations."""

    def __init__(self):
        self.password_helper = PasswordHelper()

    def validate_password_strength(self, password: str) -> bool:
        """Validate password strength requirements using centralized validators."""
        validate_password(password)  # This will raise ValidationError if invalid
        return True

    def hash_password(self, password: str) -> str:
        """Hash a password."""
        validate_password(password)  # Validate before hashing
        return self.password_helper.hash_password(password)

    def verify_password(self, password: str, hashed_password: str) -> bool:
        """Verify a password against its hash."""
        return self.password_helper.verify_password(password, hashed_password)
