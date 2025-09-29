"""Password service for password-related operations."""

from typing import Any, Dict

from src.core.exceptions import ValidationError
from src.utils.password_helper import PasswordHelper
from src.validators.password_validator import validate_password, validate_password_strength


class PasswordService:
    """Password service for password operations following Single Responsibility Principle."""

    def __init__(self, password_helper: PasswordHelper = None):
        """Initialize with dependency injection for better testability."""
        self.password_helper = password_helper or PasswordHelper()

    def validate_password_strength(self, password: str) -> bool:
        """Validate password strength requirements using centralized validators.

        Args:
            password: Password to validate

        Returns:
            True if password is valid

        Raises:
            ValidationError: If password doesn't meet requirements
        """
        validate_password(password)  # This will raise ValidationError if invalid
        return True

    def get_password_strength_analysis(self, password: str) -> Dict[str, Any]:
        """Get detailed password strength analysis.

        Args:
            password: Password to analyze

        Returns:
            Dictionary with strength analysis details

        Raises:
            ValidationError: If password doesn't meet basic requirements
        """
        return validate_password_strength(password)

    def hash_password(self, password: str) -> str:
        """Hash a password after validation.

        Args:
            password: Password to hash

        Returns:
            Hashed password string

        Raises:
            ValidationError: If password doesn't meet requirements
        """
        validate_password(password)  # Validate before hashing
        return self.password_helper.hash_password(password)

    def verify_password(self, password: str, hashed_password: str) -> bool:
        """Verify a password against its hash.

        Args:
            password: Plain text password
            hashed_password: Hashed password to compare against

        Returns:
            True if password matches hash, False otherwise
        """
        return self.password_helper.verify_password(password, hashed_password)

    def is_password_strong_enough(self, password: str, min_strength: str = "good") -> bool:
        """Check if password meets minimum strength requirement.

        Args:
            password: Password to check
            min_strength: Minimum required strength level

        Returns:
            True if password meets minimum strength requirement
        """
        try:
            strength_analysis = self.get_password_strength_analysis(password)
            strength_levels = ["very_weak", "weak", "fair", "good", "strong"]
            min_index = strength_levels.index(min_strength)
            current_index = strength_levels.index(strength_analysis["strength"])
            return current_index >= min_index
        except ValidationError:
            return False
