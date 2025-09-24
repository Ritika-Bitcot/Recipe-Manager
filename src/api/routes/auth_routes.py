"""Authentication routes for user registration and login."""

from flask import Blueprint, jsonify, request
from flask_jwt_extended import create_access_token, get_jwt_identity, jwt_required
from pydantic import ValidationError as PydanticValidationError

from src.core.exceptions import AuthenticationError, ConflictError, ValidationError
from src.schemas.auth_schema import ErrorResponse, LoginResponse, RegisterResponse
from src.schemas.user_schema import UserCreate, UserLogin
from src.services.authentication.auth_service import AuthService

# Create blueprint
auth_bp = Blueprint("auth", __name__, url_prefix="/api/auth")

# Initialize service
auth_service = AuthService()


@auth_bp.route("/register", methods=["POST"])
def register():
    """Register a new user."""
    try:
        # Validate request data
        try:
            user_data = UserCreate(**request.get_json())
        except PydanticValidationError as e:
            return (
                jsonify(
                    ErrorResponse(
                        error="Validation Error",
                        message="Invalid input data",
                        status_code=400,
                        details=e.errors(),
                    ).dict()
                ),
                400,
            )

        # Register user
        result = auth_service.register_user(user_data)

        # Generate JWT token
        token = create_access_token(identity=str(result["user"]["id"]))

        response = RegisterResponse(
            message=result["message"],
            user=result["user"],
            token={"access_token": token, "token_type": "bearer", "expires_in": 3600},
        )

        return jsonify(response.dict()), 201

    except ConflictError as e:
        return (
            jsonify(
                ErrorResponse(error="Conflict", message=str(e), status_code=409).dict()
            ),
            409,
        )

    except ValidationError as e:
        return (
            jsonify(
                ErrorResponse(
                    error="Validation Error", message=str(e), status_code=400
                ).dict()
            ),
            400,
        )

    except Exception:
        return (
            jsonify(
                ErrorResponse(
                    error="Internal Server Error",
                    message="An unexpected error occurred",
                    status_code=500,
                ).dict()
            ),
            500,
        )


@auth_bp.route("/login", methods=["POST"])
def login():
    """Login user and return JWT token."""
    try:
        # Validate request data
        try:
            login_data = UserLogin(**request.get_json())
        except PydanticValidationError as e:
            return (
                jsonify(
                    ErrorResponse(
                        error="Validation Error",
                        message="Invalid input data",
                        status_code=400,
                        details=e.errors(),
                    ).dict()
                ),
                400,
            )

        # Authenticate user
        result = auth_service.login_user(login_data)

        # Generate JWT token
        token = create_access_token(identity=str(result["user"]["id"]))

        response = LoginResponse(
            message=result["message"],
            user=result["user"],
            token={"access_token": token, "token_type": "bearer", "expires_in": 3600},
        )

        return jsonify(response.dict()), 200

    except AuthenticationError as e:
        return (
            jsonify(
                ErrorResponse(
                    error="Authentication Error", message=str(e), status_code=401
                ).dict()
            ),
            401,
        )

    except ValidationError as e:
        return (
            jsonify(
                ErrorResponse(
                    error="Validation Error", message=str(e), status_code=400
                ).dict()
            ),
            400,
        )

    except Exception:
        return (
            jsonify(
                ErrorResponse(
                    error="Internal Server Error",
                    message="An unexpected error occurred",
                    status_code=500,
                ).dict()
            ),
            500,
        )


@auth_bp.route("/me", methods=["GET"])
@jwt_required()
def get_current_user():
    """Get current user information."""
    try:
        user_id = int(get_jwt_identity())

        # Get user data from database
        from src.core.database import get_db_session
        from src.repositories.user_repository import UserRepository

        session = get_db_session()
        user_repo = UserRepository()
        user = user_repo.get_by_id(session, user_id)

        if not user:
            return (
                jsonify(
                    ErrorResponse(
                        error="Not Found", message="User not found", status_code=404
                    ).dict()
                ),
                404,
            )

        return (
            jsonify(
                {
                    "user": user.to_dict(),
                    "message": "User information retrieved successfully",
                }
            ),
            200,
        )

    except ValueError:
        return (
            jsonify(
                ErrorResponse(
                    error="Invalid Token",
                    message="Invalid user ID in token",
                    status_code=401,
                ).dict()
            ),
            401,
        )

    except Exception:
        return (
            jsonify(
                ErrorResponse(
                    error="Internal Server Error",
                    message="An unexpected error occurred",
                    status_code=500,
                ).dict()
            ),
            500,
        )
