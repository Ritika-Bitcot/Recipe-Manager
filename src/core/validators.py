"""Input validators for the Recipe Manager API."""

import re
from typing import Any, Dict, List, Optional
from src.core.exceptions import ValidationError


def validate_email(email: str) -> str:
    """Validate email format."""
    if not email:
        raise ValidationError("Email is required", "email")
    
    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(email_pattern, email):
        raise ValidationError("Invalid email format", "email")
    
    return email.lower().strip()


def validate_password(password: str) -> str:
    """Validate password strength."""
    if not password:
        raise ValidationError("Password is required", "password")
    
    if len(password) < 8:
        raise ValidationError("Password must be at least 8 characters long", "password")
    
    if len(password) > 128:
        raise ValidationError("Password must be less than 128 characters", "password")
    
    return password


def validate_string_length(value: str, field_name: str, min_length: int = 1, max_length: int = 255) -> str:
    """Validate string length."""
    if not value:
        raise ValidationError(f"{field_name} is required", field_name)
    
    if len(value) < min_length:
        raise ValidationError(f"{field_name} must be at least {min_length} characters long", field_name)
    
    if len(value) > max_length:
        raise ValidationError(f"{field_name} must be less than {max_length} characters", field_name)
    
    return value.strip()


def validate_positive_integer(value: Any, field_name: str) -> int:
    """Validate positive integer."""
    try:
        int_value = int(value)
        if int_value <= 0:
            raise ValidationError(f"{field_name} must be a positive integer", field_name)
        return int_value
    except (ValueError, TypeError):
        raise ValidationError(f"{field_name} must be a valid integer", field_name)


def validate_optional_string(value: Optional[str], field_name: str, max_length: int = 1000) -> Optional[str]:
    """Validate optional string."""
    if value is None:
        return None
    
    if len(value) > max_length:
        raise ValidationError(f"{field_name} must be less than {max_length} characters", field_name)
    
    return value.strip() if value else None
