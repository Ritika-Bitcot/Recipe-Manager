"""Recipe routes for CRUD operations."""

import json
import logging

from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required
from pydantic import ValidationError as PydanticValidationError

from src.core.exceptions import ResourceNotFoundError, UnauthorizedError, ValidationError
from src.schemas.auth_schema import ErrorResponse
from src.schemas.recipe_schema import RecipeCreate, RecipeUpdate
from src.services.recipe_management.recipe_service import RecipeService

# Create blueprint
recipe_bp = Blueprint("recipes", __name__, url_prefix="/api/recipes")

# Initialize service
recipe_service = RecipeService()

# Logger for route operations
logger = logging.getLogger(__name__)


def _handle_json_validation_error() -> tuple[dict, int]:
    """Handle JSON validation errors consistently across routes.

    Returns:
        Tuple of (error_response, status_code)
    """
    return (
        jsonify(
            ErrorResponse(
                error="VALIDATION_ERROR",
                message="Invalid JSON data",
                status_code=400,
            ).model_dump()
        ),
        400,
    )


def _handle_empty_request_error() -> tuple[dict, int]:
    """Handle empty request body errors consistently across routes.

    Returns:
        Tuple of (error_response, status_code)
    """
    return (
        jsonify(
            ErrorResponse(
                error="VALIDATION_ERROR",
                message="Request body is required",
                status_code=400,
            ).model_dump()
        ),
        400,
    )


def _handle_pydantic_validation_error(
    error: PydanticValidationError,
) -> tuple[dict, int]:
    """Handle Pydantic validation errors consistently across routes.

    Args:
        error: Pydantic validation error

    Returns:
        Tuple of (error_response, status_code)
    """
    return (
        jsonify(
            ErrorResponse(
                error="VALIDATION_ERROR",
                message="Invalid input data",
                status_code=400,
                details=error.errors(),
            ).model_dump()
        ),
        400,
    )


def _handle_generic_error(error: Exception, operation: str) -> tuple[dict, int]:
    """Handle generic errors consistently across routes.

    Args:
        error: Exception that occurred
        operation: Description of the operation that failed

    Returns:
        Tuple of (error_response, status_code)
    """
    logger.error(f"Error during {operation}: {str(error)}", exc_info=True)
    return (
        jsonify(
            ErrorResponse(
                error="INTERNAL_SERVER_ERROR",
                message="An unexpected error occurred",
                status_code=500,
            ).model_dump()
        ),
        500,
    )


@recipe_bp.route("", methods=["POST"])
@jwt_required()
def create_recipe():
    """Create a new recipe with improved error handling and logging."""
    try:
        user_id = int(get_jwt_identity())
        logger.info(f"Creating recipe for user {user_id}")

        # Get and validate request data
        try:
            request_data = request.get_json()
        except (json.JSONDecodeError, TypeError, Exception):
            logger.warning(f"Invalid JSON data received from user {user_id}")
            return _handle_json_validation_error()

        if request_data is None:
            logger.warning(f"Empty request body received from user {user_id}")
            return _handle_empty_request_error()

        try:
            recipe_data = RecipeCreate(**request_data)
        except PydanticValidationError as e:
            logger.warning(f"Pydantic validation error for user {user_id}: {e.errors()}")
            return _handle_pydantic_validation_error(e)

        # Create recipe
        from src.core.database import get_db_session

        session = get_db_session()
        result = recipe_service.create_recipe(session, recipe_data, user_id)
        logger.info(f"Successfully created recipe {result.get('id', 'unknown')} " f"for user {user_id}")

        return jsonify(result), 201

    except ValidationError as e:
        logger.warning(f"Validation error for user {user_id}: {str(e)}")
        return (
            jsonify(ErrorResponse(error="VALIDATION_ERROR", message=str(e), status_code=400).model_dump()),
            400,
        )

    except Exception as e:
        return _handle_generic_error(e, f"recipe creation for user {user_id}")


@recipe_bp.route("", methods=["GET"])
@jwt_required()
def get_recipes():
    """Get all recipes (multi-tenancy read access)."""
    try:
        # Get query parameters
        page = int(request.args.get("page", 1))
        per_page = int(request.args.get("per_page", 10))

        # Validate pagination parameters
        if page < 1:
            return (
                jsonify(
                    ErrorResponse(
                        error="Validation Error",
                        message="Page number must be greater than 0",
                        status_code=400,
                    ).model_dump()
                ),
                400,
            )
        if per_page < 1 or per_page > 100:
            return (
                jsonify(
                    ErrorResponse(
                        error="Validation Error",
                        message="Per page must be between 1 and 100",
                        status_code=400,
                    ).model_dump()
                ),
                400,
            )

        # Get all recipes
        from src.core.database import get_db_session

        session = get_db_session()
        result = recipe_service.list_recipes(session, page=page, per_page=per_page)

        return jsonify(result), 200

    except ValidationError as e:
        return (
            jsonify(ErrorResponse(error="Validation Error", message=str(e), status_code=400).model_dump()),
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


@recipe_bp.route("/<int:recipe_id>", methods=["GET"])
@jwt_required()
def get_recipe(recipe_id):
    """Get a specific recipe by ID."""
    try:
        user_id = int(get_jwt_identity())

        # Get recipe
        from src.core.database import get_db_session

        session = get_db_session()
        result = recipe_service.get_recipe(session, recipe_id, user_id)

        return jsonify(result), 200

    except ResourceNotFoundError as e:
        return (
            jsonify(ErrorResponse(error="Not Found", message=str(e), status_code=404).model_dump()),
            404,
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


@recipe_bp.route("/<int:recipe_id>", methods=["PUT"])
@jwt_required()
def update_recipe(recipe_id):
    """Update a specific recipe."""
    try:
        user_id = int(get_jwt_identity())

        # Get and validate request data
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

        try:
            recipe_data = RecipeUpdate(**request_data)
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

        # Update recipe
        from src.core.database import get_db_session

        session = get_db_session()
        result = recipe_service.update_recipe(session, recipe_id, recipe_data, user_id)

        return jsonify(result), 200

    except ResourceNotFoundError as e:
        return (
            jsonify(ErrorResponse(error="Not Found", message=str(e), status_code=404).model_dump()),
            404,
        )

    except UnauthorizedError as e:
        return (
            jsonify(ErrorResponse(error="Unauthorized", message=str(e), status_code=403).model_dump()),
            403,
        )

    except ValidationError as e:
        return (
            jsonify(ErrorResponse(error="Validation Error", message=str(e), status_code=400).model_dump()),
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


@recipe_bp.route("/<int:recipe_id>", methods=["DELETE"])
@jwt_required()
def delete_recipe(recipe_id):
    """Delete a specific recipe."""
    try:
        user_id = int(get_jwt_identity())

        # Delete recipe
        from src.core.database import get_db_session

        session = get_db_session()
        result = recipe_service.delete_recipe(session, recipe_id, user_id)

        return jsonify(result), 200

    except ResourceNotFoundError as e:
        return (
            jsonify(ErrorResponse(error="Not Found", message=str(e), status_code=404).model_dump()),
            404,
        )

    except UnauthorizedError as e:
        return (
            jsonify(ErrorResponse(error="Unauthorized", message=str(e), status_code=403).model_dump()),
            403,
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


@recipe_bp.route("/search", methods=["GET"])
@jwt_required()
def search_recipes():
    """Search recipes with filters."""
    try:
        user_id = int(get_jwt_identity())

        # Get query parameters
        query_params = request.args.to_dict()

        # Validate query parameters
        if "difficulty" in query_params:
            valid_difficulties = ["easy", "medium", "hard"]
            if query_params["difficulty"] not in valid_difficulties:
                return (
                    jsonify(
                        ErrorResponse(
                            error="Validation Error",
                            message="Difficulty must be one of: easy, medium, hard",
                            status_code=400,
                        ).model_dump()
                    ),
                    400,
                )

        if "prep_time_max" in query_params:
            try:
                prep_time = int(query_params["prep_time_max"])
                if prep_time < 0:
                    return (
                        jsonify(
                            ErrorResponse(
                                error="Validation Error",
                                message="Prep time must be non-negative",
                                status_code=400,
                            ).model_dump()
                        ),
                        400,
                    )
            except ValueError:
                return (
                    jsonify(
                        ErrorResponse(
                            error="Validation Error",
                            message="Prep time must be a valid number",
                            status_code=400,
                        ).model_dump()
                    ),
                    400,
                )

        # Get database session
        from src.core.database import get_db_session

        session = get_db_session()

        # Search recipes
        result = recipe_service.search_recipes(session, user_id, query_params)

        return jsonify(result), 200

    except ValidationError as e:
        return (
            jsonify(
                ErrorResponse(
                    error="Validation Error",
                    message=e.message,
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
