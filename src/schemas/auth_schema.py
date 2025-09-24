"""Authentication schemas for login/register responses."""

from typing import Optional

from pydantic import BaseModel


class TokenResponse(BaseModel):
    """Schema for JWT token response."""

    access_token: str
    token_type: str = "bearer"
    expires_in: int


class LoginResponse(BaseModel):
    """Schema for successful login response."""

    message: str
    user: dict
    token: TokenResponse


class RegisterResponse(BaseModel):
    """Schema for successful registration response."""

    message: str
    user: dict
    token: TokenResponse


class ErrorResponse(BaseModel):
    """Schema for error responses."""

    error: str
    message: str
    status_code: int
    details: Optional[dict] = None
