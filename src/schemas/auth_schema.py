"""Authentication schemas for login/register responses."""

from typing import Optional, Union

from pydantic import BaseModel


class TokenResponse(BaseModel):
    """Schema for JWT token response."""

    access_token: str
    token_type: str = "bearer"
    expires_in: int


class AuthResponse(BaseModel):
    """Schema for successful authentication response (login/register)."""

    message: str
    user: dict
    token: TokenResponse


# Legacy aliases for backward compatibility
LoginResponse = AuthResponse
RegisterResponse = AuthResponse


class ErrorResponse(BaseModel):
    """Schema for error responses."""

    error: str
    message: str
    status_code: int
    details: Optional[Union[dict, list]] = None
