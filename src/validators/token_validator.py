"""Token validation for the Recipe Manager API."""

import re
from typing import Optional

from src.core.exceptions import AuthenticationError, ValidationError


def validate_token(token: str) -> str:
    """Validate JWT token format.

    Args:
        token: JWT token to validate

    Returns:
        Validated token

    Raises:
        ValidationError: If token format is invalid
        AuthenticationError: If token is missing or malformed
    """
    if not token:
        raise AuthenticationError("Token is required")

    if not isinstance(token, str):
        raise ValidationError("Token must be a string", "token")

    # Basic JWT format validation (header.payload.signature)
    jwt_pattern = r"^[A-Za-z0-9-_]+\.[A-Za-z0-9-_]+\.[A-Za-z0-9-_]+$"
    if not re.match(jwt_pattern, token):
        raise AuthenticationError("Invalid token format")

    # Check token length (reasonable bounds)
    if len(token) < 20:  # Minimum reasonable JWT length
        raise AuthenticationError("Token is too short")

    if len(token) > 2000:  # Maximum reasonable JWT length
        raise AuthenticationError("Token is too long")

    return token.strip()


def validate_bearer_token(authorization_header: Optional[str]) -> str:
    """Validate Bearer token from Authorization header.

    Args:
        authorization_header: Authorization header value

    Returns:
        Extracted and validated token

    Raises:
        AuthenticationError: If authorization header is invalid
    """
    if not authorization_header:
        raise AuthenticationError("Authorization header is required")

    if not isinstance(authorization_header, str):
        raise AuthenticationError("Authorization header must be a string")

    # Check Bearer format
    if not authorization_header.startswith("Bearer "):
        raise AuthenticationError("Authorization header must start with 'Bearer '")

    # Extract token
    token = authorization_header[7:].strip()  # Remove "Bearer " prefix

    if not token:
        raise AuthenticationError("Token cannot be empty")

    return validate_token(token)


def validate_refresh_token(token: str) -> str:
    """Validate refresh token.

    Args:
        token: Refresh token to validate

    Returns:
        Validated refresh token

    Raises:
        ValidationError: If token format is invalid
        AuthenticationError: If token is missing or malformed
    """
    if not token:
        raise AuthenticationError("Refresh token is required")

    if not isinstance(token, str):
        raise ValidationError("Refresh token must be a string", "refresh_token")

    # Refresh tokens can be longer and have different format
    if len(token) < 16:  # Minimum reasonable refresh token length
        raise AuthenticationError("Refresh token is too short")

    if len(token) > 500:  # Maximum reasonable refresh token length
        raise AuthenticationError("Refresh token is too long")

    # Basic format validation (alphanumeric and some special chars)
    token_pattern = r"^[A-Za-z0-9._-]+$"
    if not re.match(token_pattern, token):
        raise AuthenticationError("Invalid refresh token format")

    return token.strip()


def validate_token_optional(token: Optional[str]) -> Optional[str]:
    """Validate optional token.

    Args:
        token: Optional token to validate

    Returns:
        Validated token or None

    Raises:
        ValidationError: If token is provided but invalid
    """
    if token is None:
        return None

    return validate_token(token)
