"""Authentication service implementation."""

from typing import Any, Dict

from src.core.database import get_db_session
from src.core.exceptions import AuthenticationError, ConflictError
from src.interfaces.repository.user_repository_interface import UserRepositoryInterface
from src.interfaces.service.auth_service_interface import AuthServiceInterface
from src.repositories.user_repository import UserRepository
from src.schemas.user_schema import UserCreate, UserLogin
from src.utils.jwt_helper import JWTHelper
from src.utils.password_helper import PasswordHelper
from src.validators.email_validator import validate_email
from src.validators.password_validator import validate_password


class AuthService(AuthServiceInterface):
    """Authentication service implementation."""

    def __init__(self, user_repository: UserRepositoryInterface = None):
        self.user_repository = user_repository or UserRepository()
        self.jwt_helper = JWTHelper()
        self.password_helper = PasswordHelper()

    def register_user(self, user_data: UserCreate) -> Dict[str, Any]:
        """Register a new user and return user data with token."""
        session = get_db_session()

        try:
            # Validate email and password using centralized validators
            validated_email = validate_email(user_data.email)
            validate_password(user_data.password)

            # Check if email already exists
            if self.user_repository.email_exists(session, validated_email):
                raise ConflictError("Email already registered", "email")

            # Hash password
            hashed_password = self.password_helper.hash_password(user_data.password)

            # Create user data
            user_dict = {
                "email": validated_email,
                "password_hash": hashed_password,
                "first_name": user_data.first_name.strip(),
                "last_name": user_data.last_name.strip(),
                "is_active": True,
            }

            # Create user
            user = self.user_repository.create(session, user_dict)

            # Generate token
            token = self.jwt_helper.generate_token(user.id, user.email)

            return {
                "user": user.to_dict(),
                "token": token,
                "message": "User registered successfully",
            }

        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()

    def login_user(self, login_data: UserLogin) -> Dict[str, Any]:
        """Authenticate user and return user data with token."""
        session = get_db_session()

        try:
            # Validate email format
            validated_email = validate_email(login_data.email)

            # Get user by email
            user = self.user_repository.get_by_email(session, validated_email)
            if not user:
                raise AuthenticationError("Invalid email or password")

            # Check if user is active
            if not user.is_active:
                raise AuthenticationError("Account is deactivated")

            # Verify password
            if not self.password_helper.verify_password(login_data.password, user.password_hash):
                raise AuthenticationError("Invalid email or password")

            # Generate token
            token = self.jwt_helper.generate_token(user.id, user.email)

            return {
                "user": user.to_dict(),
                "token": token,
                "message": "Login successful",
            }

        except Exception as e:
            raise e
        finally:
            session.close()

    def verify_token(self, token: str) -> Dict[str, Any]:
        """Verify JWT token and return user data."""
        try:
            payload = self.jwt_helper.verify_token(token)
            user_id = payload.get("user_id")
            email = payload.get("email")

            if not user_id or not email:
                raise AuthenticationError("Invalid token payload")

            # Verify user still exists and is active
            session = get_db_session()
            try:
                user = self.user_repository.get_active_user(session, user_id)
                if not user:
                    raise AuthenticationError("User not found or inactive")

                return {
                    "user_id": user.id,
                    "email": user.email,
                    "is_active": user.is_active,
                }
            finally:
                session.close()

        except Exception as e:
            raise AuthenticationError(f"Token verification failed: {str(e)}")

    def hash_password(self, password: str) -> str:
        """Hash a password using bcrypt."""
        return self.password_helper.hash_password(password)

    def verify_password(self, password: str, hashed_password: str) -> bool:
        """Verify a password against its hash."""
        return self.password_helper.verify_password(password, hashed_password)
