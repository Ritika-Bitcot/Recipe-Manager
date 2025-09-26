"""Password validation for the Recipe Manager API."""

import re

from src.core.exceptions import ValidationError


def validate_password(password: str) -> str:
    """Validate password strength and return validated password.

    Args:
        password: Password to validate

    Returns:
        Validated password

    Raises:
        ValidationError: If password doesn't meet requirements
    """
    if not password:
        raise ValidationError("Password is required", "password")

    # Length validation
    if len(password) < 8:
        raise ValidationError("Password must be at least 8 characters long", "password")

    if len(password) > 128:
        raise ValidationError("Password must be less than 128 characters", "password")

    # Check for common weak passwords first (before other validations)
    weak_passwords = [
        "password",
        "123456",
        "123456789",
        "qwerty",
        "abc123",
        "password123",
        "admin",
        "letmein",
        "welcome",
        "monkey",
    ]

    if password.lower() in weak_passwords:
        raise ValidationError("Password is too common, please choose a stronger password", "password")

    # Check for at least one character and one number
    if not re.search(r"[A-Za-z]", password):
        raise ValidationError("Password must contain at least one letter", "password")

    if not re.search(r"\d", password):
        raise ValidationError("Password must contain at least one number", "password")

    return password


def validate_password_strength(password: str) -> dict:
    """Validate password strength and return detailed feedback.

    Args:
        password: Password to validate

    Returns:
        Dictionary with strength score and feedback

    Raises:
        ValidationError: If password doesn't meet basic requirements
    """
    if not password:
        raise ValidationError("Password is required", "password")

    errors = []
    warnings = []
    score = 0

    # Length checks
    if len(password) < 8:
        errors.append("Password must be at least 8 characters long")
    elif len(password) >= 12:
        score += 1
    else:
        warnings.append("Consider using a longer password (12+ characters)")

    if len(password) > 128:
        errors.append("Password must be less than 128 characters")

    # Character type checks
    has_lower = bool(re.search(r"[a-z]", password))
    has_upper = bool(re.search(r"[A-Z]", password))
    has_digit = bool(re.search(r"\d", password))
    has_special = bool(re.search(r"[!@#$%^&*(),.?\":{}|<>]", password))

    if not has_lower:
        errors.append("Password must contain at least one lowercase letter")
    else:
        score += 1

    if not has_upper:
        errors.append("Password must contain at least one uppercase letter")
    else:
        score += 1

    if not has_digit:
        errors.append("Password must contain at least one number")
    else:
        score += 1

    if not has_special:
        warnings.append("Consider adding special characters for better security")
    else:
        score += 1

    # Common password check
    weak_passwords = [
        "password",
        "123456",
        "123456789",
        "qwerty",
        "abc123",
        "password123",
        "admin",
        "letmein",
        "welcome",
        "monkey",
    ]

    if password.lower() in weak_passwords:
        errors.append("Password is too common, please choose a stronger password")

    # Consecutive character check
    if re.search(r"(.)\1{2,}", password):
        warnings.append("Avoid using the same character consecutively")

    # Sequential character check
    if re.search(
        r"(abc|bcd|cde|def|efg|fgh|ghi|hij|ijk|jkl|klm|lmn|mno|nop|opq|pqr|qrs|rst|stu|tuv|uvw|vwx|wxy|xyz)",
        password.lower(),
    ):
        warnings.append("Avoid using sequential characters")

    if errors:
        raise ValidationError("; ".join(errors), "password")

    return {
        "score": score,
        "max_score": 5,
        "strength": _get_strength_level(score),
        "warnings": warnings,
    }


def _get_strength_level(score: int) -> str:
    """Get password strength level based on score."""
    if score <= 1:
        return "very_weak"
    elif score == 2:
        return "weak"
    elif score == 3:
        return "fair"
    elif score == 4:
        return "good"
    else:
        return "strong"
