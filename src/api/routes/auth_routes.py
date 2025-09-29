"""Authentication routes for user registration and login."""

import json

from flask import Blueprint, jsonify, request
from flask_jwt_extended import create_access_token, get_jwt_identity, jwt_required
from pydantic import ValidationError as PydanticValidationError
from werkzeug.exceptions import BadRequest

from src.core.exceptions import AuthenticationError, ConflictError, ResourceNotFoundError, ValidationError
from src.schemas.auth_schema import AuthResponse, ErrorResponse
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
        # Get request data
        try:
            request_data = request.get_json()
        except (json.JSONDecodeError, TypeError, Exception):
            return (
                jsonify(
                    ErrorResponse(
                        error="Validation Error",
                        message="Invalid JSON data",
                        status_code=400,
                    ).model_dump()
                ),
                400,
            )

        if request_data is None:
            return (
                jsonify(
                    ErrorResponse(
                        error="Validation Error",
                        message="Request body is required",
                        status_code=400,
                    ).model_dump()
                ),
                400,
            )

        # Validate request data
        try:
            user_data = UserCreate(**request_data)
        except PydanticValidationError as e:
            return (
                jsonify(
                    ErrorResponse(
                        error="Validation Error",
                        message="Invalid input data",
                        status_code=400,
                        details=e.errors(),
                    ).model_dump()
                ),
                400,
            )

        # Register user
        result = auth_service.register_user(user_data)

        # Generate JWT token
        token = create_access_token(identity=str(result["user"]["id"]))

        response = AuthResponse(
            message=result["message"],
            user=result["user"],
            token={"access_token": token, "token_type": "bearer", "expires_in": 3600},
        )

        return jsonify(response.model_dump()), 201

    except ConflictError as e:
        return (
            jsonify(
                ErrorResponse(
                    error=e.error_code,
                    message=str(e),
                    status_code=e.status_code,
                    details=e.details,
                ).model_dump()
            ),
            e.status_code,
        )

    except ValidationError as e:
        return (
            jsonify(ErrorResponse(error="Validation Error", message=str(e), status_code=400).model_dump()),
            400,
        )

    except BadRequest:
        return (
            jsonify(
                ErrorResponse(
                    error="Validation Error",
                    message="Invalid JSON data",
                    status_code=400,
                ).model_dump()
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
                ).model_dump()
            ),
            500,
        )


@auth_bp.route("/login", methods=["POST"])
def login():
    """Login user and return JWT token."""
    try:
        # Get request data
        try:
            request_data = request.get_json()
        except (json.JSONDecodeError, TypeError, Exception):
            return (
                jsonify(
                    ErrorResponse(
                        error="Validation Error",
                        message="Invalid JSON data",
                        status_code=400,
                    ).model_dump()
                ),
                400,
            )

        if request_data is None:
            return (
                jsonify(
                    ErrorResponse(
                        error="Validation Error",
                        message="Request body is required",
                        status_code=400,
                    ).model_dump()
                ),
                400,
            )

        # Validate request data
        try:
            login_data = UserLogin(**request_data)
        except PydanticValidationError as e:
            return (
                jsonify(
                    ErrorResponse(
                        error="Validation Error",
                        message="Invalid input data",
                        status_code=400,
                        details=e.errors(),
                    ).model_dump()
                ),
                400,
            )

        # Authenticate user
        result = auth_service.login_user(login_data)

        # Generate JWT token
        token = create_access_token(identity=str(result["user"]["id"]))

        response = AuthResponse(
            message=result["message"],
            user=result["user"],
            token={"access_token": token, "token_type": "bearer", "expires_in": 3600},
        )

        return jsonify(response.model_dump()), 200

    except AuthenticationError as e:
        return (
            jsonify(
                ErrorResponse(
                    error=e.error_code,
                    message=str(e),
                    status_code=e.status_code,
                    details=e.details,
                ).model_dump()
            ),
            e.status_code,
        )

    except ValidationError as e:
        return (
            jsonify(ErrorResponse(error="Validation Error", message=str(e), status_code=400).model_dump()),
            400,
        )

    except BadRequest:
        return (
            jsonify(
                ErrorResponse(
                    error="Validation Error",
                    message="Invalid JSON data",
                    status_code=400,
                ).model_dump()
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
                ).model_dump()
            ),
            500,
        )


@auth_bp.route("/me", methods=["GET"])
@jwt_required()
def get_current_user():
    """Get current user information."""
    try:
        user_id = int(get_jwt_identity())

        # Get user data using auth service
        result = auth_service.get_current_user(user_id)

        return jsonify(result), 200

    except ResourceNotFoundError as e:
        return (
            jsonify(ErrorResponse(error="Not Found", message=str(e), status_code=404).model_dump()),
            404,
        )

    except ValueError:
        return (
            jsonify(
                ErrorResponse(
                    error="Invalid Token",
                    message="Invalid user ID in token",
                    status_code=401,
                ).model_dump()
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
                ).model_dump()
            ),
            500,
        )
