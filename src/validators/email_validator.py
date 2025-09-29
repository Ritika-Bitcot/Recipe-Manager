"""Email validation for the Recipe Manager API."""

import re
from typing import Optional

from src.core.exceptions import ValidationError


def validate_email(email: str) -> str:
    """Validate email format and return normalized email.

    Args:
        email: Email address to validate

    Returns:
        Normalized email address (lowercase, trimmed)

    Raises:
        ValidationError: If email is invalid
    """
    if not email:
        raise ValidationError("Email is required", "email")

    # Normalize email first (trim whitespace)
    normalized_email = email.strip()

    # Additional validation for length
    if len(normalized_email) > 254:  # RFC 5321 limit
        raise ValidationError("Email is too long", "email")

    # Basic email format validation
    email_pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    if not re.match(email_pattern, normalized_email):
        raise ValidationError("Invalid email format", "email")

    # Convert to lowercase
    normalized_email = normalized_email.lower()

    # Check for consecutive dots
    if ".." in normalized_email:
        raise ValidationError("Email cannot contain consecutive dots", "email")

    # Check for leading/trailing dots in local part
    local_part = normalized_email.split("@")[0]
    if local_part.startswith(".") or local_part.endswith("."):
        raise ValidationError("Email local part cannot start or end with a dot", "email")

    return normalized_email


def validate_email_optional(email: Optional[str]) -> Optional[str]:
    """Validate optional email format.

    Args:
        email: Optional email address to validate

    Returns:
        Normalized email address or None

    Raises:
        ValidationError: If email is provided but invalid
    """
    if email is None:
        return None

    return validate_email(email)
