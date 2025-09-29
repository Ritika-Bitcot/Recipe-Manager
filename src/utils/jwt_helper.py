"""JWT utility functions for token generation and validation."""

from datetime import datetime, timedelta
from typing import Any, Dict, Optional

import jwt

from src.core.exceptions import AuthenticationError
from src.core.settings import settings


class JWTHelper:
    """JWT helper class for token operations."""

    @staticmethod
    def generate_token(user_id: int, email: str) -> str:
        """Generate JWT access token."""
        payload = {
            "user_id": user_id,
            "email": email,
            "exp": datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
            "iat": datetime.utcnow(),
        }

        return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

    @staticmethod
    def verify_token(token: str) -> Optional[Dict[str, Any]]:
        """Verify JWT token and return payload."""
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
            return payload
        except jwt.ExpiredSignatureError:
            raise AuthenticationError("Token has expired")
        except jwt.InvalidTokenError:
            raise AuthenticationError("Invalid token")
        except Exception as e:
            raise AuthenticationError(f"Token verification failed: {str(e)}")

    @staticmethod
    def extract_user_id(token: str) -> int:
        """Extract user ID from token."""
        payload = JWTHelper.verify_token(token)
        return payload.get("user_id")

    @staticmethod
    def extract_email(token: str) -> str:
        """Extract email from token."""
        payload = JWTHelper.verify_token(token)
        return payload.get("email")

    @staticmethod
    def is_token_expired(token: str) -> bool:
        """Check if token is expired."""
        try:
            payload = jwt.decode(
                token,
                settings.SECRET_KEY,
                algorithms=[settings.ALGORITHM],
                options={"verify_exp": False},
            )
            exp = payload.get("exp")
            if exp:
                return datetime.utcnow() > datetime.fromtimestamp(exp)
            return True
        except jwt.PyJWTError:
            return True
