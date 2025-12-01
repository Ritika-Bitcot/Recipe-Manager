"""Authentication decorators with bypass functionality for development."""

import logging
from functools import wraps

from flask import g, jsonify
from flask_jwt_extended import get_jwt_identity, verify_jwt_in_request

from src.core.database import get_db_session
from src.core.exceptions import AuthenticationError, ResourceNotFoundError
from src.core.settings import settings
from src.services.authentication.auth_service import AuthService

logger = logging.getLogger(__name__)


def get_current_user_email() -> str:
    """
    Get current authenticated user email from JWT token, or bypass for development.

    Returns:
        str: User email address

    Raises:
        AuthenticationError: If authentication fails and no bypass is configured
    """
    # Check for authentication bypass
    if settings.AUTH_BYPASS_EMAIL:
        logger.info(f"Bypassing authentication for development. " f"Using email: {settings.AUTH_BYPASS_EMAIL}")
        return settings.AUTH_BYPASS_EMAIL

    # For production mode, we need to get email from the JWT token directly
    # This function should only be called when JWT is already verified
    try:
        # Get email from JWT token (this should work if @jwt_required is active)
        email = get_jwt_identity()
        if not email:
            raise AuthenticationError("Invalid authentication credentials")

        # If the JWT identity is already an email, return it directly
        if isinstance(email, str) and "@" in email:
            return email

        # If it's a user ID, get the email from database
        auth_service = AuthService()
        session = get_db_session()
        try:
            user = auth_service.user_repository.get_by_id(session, int(email))
            if not user:
                raise AuthenticationError("User not found")
            return user.email
        finally:
            if hasattr(session, "close"):
                session.close()

    except Exception as e:
        logger.error(f"Token verification failed: {str(e)}", exc_info=True)
        raise AuthenticationError("Invalid authentication credentials")


def get_current_user_id() -> int:
    """
    Get current authenticated user ID from JWT token, or bypass for development.

    Returns:
        int: User ID

    Raises:
        AuthenticationError: If authentication fails and no bypass is configured
    """
    # Check for authentication bypass
    if settings.AUTH_BYPASS_EMAIL:
        logger.info(f"Bypassing authentication for development. " f"Using email: {settings.AUTH_BYPASS_EMAIL}")
        # For bypass, we need to get the user ID from the database
        try:
            auth_service = AuthService()
            session = get_db_session()
            try:
                # Find user by email
                user = auth_service.user_repository.get_by_email(session, settings.AUTH_BYPASS_EMAIL)
                if not user:
                    raise AuthenticationError(f"Bypass user not found: {settings.AUTH_BYPASS_EMAIL}")
                return user.id
            finally:
                if hasattr(session, "close"):
                    session.close()
        except Exception as e:
            logger.error(f"Failed to get bypass user ID: {str(e)}", exc_info=True)
            raise AuthenticationError(f"Bypass authentication failed: {str(e)}")

    # Normal JWT authentication
    try:
        identity = get_jwt_identity()
        if not identity:
            raise AuthenticationError("Invalid authentication credentials")

        # If the JWT identity is already a user ID, return it directly
        if isinstance(identity, (int, str)) and str(identity).isdigit():
            return int(identity)

        # If it's an email, get the user ID from database
        if isinstance(identity, str) and "@" in identity:
            auth_service = AuthService()
            session = get_db_session()
            try:
                user = auth_service.user_repository.get_by_email(session, identity)
                if not user:
                    raise ResourceNotFoundError("User not found")
                return user.id
            finally:
                if hasattr(session, "close"):
                    session.close()

        # If we can't determine what it is, try to convert to int
        return int(identity)

    except ResourceNotFoundError:
        # Re-raise ResourceNotFoundError as-is
        raise
    except Exception as e:
        logger.error(f"Token verification failed: {str(e)}", exc_info=True)
        raise AuthenticationError("Invalid authentication credentials")


def auth_required(f):
    """
    Decorator that requires authentication but supports bypass for development.

    This decorator:
    1. Checks if AUTH_BYPASS_EMAIL is configured
    2. If bypass is enabled, skips JWT validation and uses the bypass email
    3. If bypass is disabled, uses normal JWT authentication
    4. Stores user information in Flask's g object for easy access
    """

    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            # Get user information (email and ID)
            user_email = get_current_user_email()
            user_id = get_current_user_id()

            # Store in Flask's g object for easy access in route handlers
            g.current_user_email = user_email
            g.current_user_id = user_id

            return f(*args, **kwargs)

        except AuthenticationError as e:
            logger.warning(f"Authentication failed: {str(e)}")

            return (
                jsonify(
                    {
                        "error": "AUTHENTICATION_ERROR",
                        "message": str(e),
                        "status_code": 401,
                    }
                ),
                401,
            )
        except Exception as e:
            logger.error(f"Unexpected error during authentication: {str(e)}", exc_info=True)

            return (
                jsonify(
                    {
                        "error": "INTERNAL_SERVER_ERROR",
                        "message": "An unexpected error occurred during authentication",
                        "status_code": 500,
                    }
                ),
                500,
            )

    return decorated_function


def jwt_required_with_bypass(f):
    """
    Decorator that combines JWT requirement with bypass functionality.

    This is an alternative to the auth_required decorator that still uses
    Flask-JWT-Extended's @jwt_required() but adds bypass logic.
    """

    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            # Check for bypass first
            if settings.AUTH_BYPASS_EMAIL:
                logger.info(
                    f"Bypassing JWT authentication for development. " f"Using email: {settings.AUTH_BYPASS_EMAIL}"
                )
                # Get user ID for bypass user
                auth_service = AuthService()
                session = get_db_session()
                try:
                    user = auth_service.user_repository.get_by_email(session, settings.AUTH_BYPASS_EMAIL)
                    if not user:
                        raise AuthenticationError(f"Bypass user not found: {settings.AUTH_BYPASS_EMAIL}")
                    g.current_user_email = settings.AUTH_BYPASS_EMAIL
                    g.current_user_id = user.id
                finally:
                    if hasattr(session, "close"):
                        session.close()
            else:
                # Normal JWT flow - verify JWT token manually
                # Verify JWT token
                verify_jwt_in_request()
                identity = get_jwt_identity()
                if not identity:
                    raise AuthenticationError("Invalid authentication credentials")

                # Get user information from database
                auth_service = AuthService()
                session = get_db_session()
                try:
                    # If the JWT identity is already an email, get user by email
                    if isinstance(identity, str) and "@" in identity:
                        user = auth_service.user_repository.get_by_email(session, identity)
                        if not user:
                            raise ResourceNotFoundError("User not found")
                        g.current_user_email = user.email
                        g.current_user_id = user.id
                    else:
                        # If it's a user ID, get user by ID
                        user = auth_service.user_repository.get_by_id(session, int(identity))
                        if not user:
                            raise ResourceNotFoundError("User not found")
                        g.current_user_email = user.email
                        g.current_user_id = int(identity)
                finally:
                    if hasattr(session, "close"):
                        session.close()

            return f(*args, **kwargs)

        except AuthenticationError as e:
            logger.warning(f"Authentication failed: {str(e)}")

            return (
                jsonify(
                    {
                        "error": "AUTHENTICATION_ERROR",
                        "message": str(e),
                        "status_code": 401,
                    }
                ),
                401,
            )
        except Exception as e:
            logger.error(f"Unexpected error during authentication: {str(e)}", exc_info=True)

            return (
                jsonify(
                    {
                        "error": "INTERNAL_SERVER_ERROR",
                        "message": "An unexpected error occurred during authentication",
                        "status_code": 500,
                    }
                ),
                500,
            )

    return decorated_function


# Make these functions available at module level for testing
__all__ = [
    "get_current_user_email",
    "get_current_user_id",
    "auth_required",
    "jwt_required_with_bypass",
    "get_jwt_identity",
    "verify_jwt_in_request",
    "get_db_session",
]
