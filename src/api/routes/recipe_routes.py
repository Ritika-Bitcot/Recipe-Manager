"""Recipe routes for CRUD operations."""

from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required
from pydantic import ValidationError as PydanticValidationError

from src.core.exceptions import NotFoundError, ValidationError
from src.schemas.auth_schema import ErrorResponse
from src.schemas.recipe_schema import RecipeCreate, RecipeUpdate
from src.services.recipe_management.recipe_service import RecipeService

# Create blueprint
recipe_bp = Blueprint("recipes", __name__, url_prefix="/api/recipes")

# Initialize service
recipe_service = RecipeService()


@recipe_bp.route("", methods=["POST"])
@jwt_required()
def create_recipe():
    """Create a new recipe."""
    try:
        user_id = int(get_jwt_identity())

        # Validate request data
        try:
            recipe_data = RecipeCreate(**request.get_json())
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

        # Create recipe
        result = recipe_service.create_recipe(recipe_data, user_id)

        return jsonify(result), 201

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


@recipe_bp.route("", methods=["GET"])
@jwt_required()
def get_recipes():
    """Get all recipes for the current user."""
    try:
        user_id = int(get_jwt_identity())

        # Get query parameters
        page = int(request.args.get("page", 1))
        per_page = int(request.args.get("per_page", 10))
        search = request.args.get("search")
        category = request.args.get("category")

        # Validate pagination parameters
        if page < 1:
            page = 1
        if per_page < 1 or per_page > 100:
            per_page = 10

        # Get recipes
        result = recipe_service.get_user_recipes(
            user_id=user_id,
            page=page,
            per_page=per_page,
            search=search,
            category=category,
        )

        return jsonify(result.dict()), 200

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


@recipe_bp.route("/<int:recipe_id>", methods=["GET"])
@jwt_required()
def get_recipe(recipe_id):
    """Get a specific recipe by ID."""
    try:
        user_id = int(get_jwt_identity())

        # Get recipe
        result = recipe_service.get_recipe(recipe_id, user_id)

        return jsonify(result), 200

    except NotFoundError as e:
        return (
            jsonify(
                ErrorResponse(error="Not Found", message=str(e), status_code=404).dict()
            ),
            404,
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


@recipe_bp.route("/<int:recipe_id>", methods=["PUT"])
@jwt_required()
def update_recipe(recipe_id):
    """Update a specific recipe."""
    try:
        user_id = int(get_jwt_identity())

        # Validate request data
        try:
            recipe_data = RecipeUpdate(**request.get_json())
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

        # Update recipe
        result = recipe_service.update_recipe(recipe_id, recipe_data, user_id)

        return jsonify(result), 200

    except NotFoundError as e:
        return (
            jsonify(
                ErrorResponse(error="Not Found", message=str(e), status_code=404).dict()
            ),
            404,
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


@recipe_bp.route("/<int:recipe_id>", methods=["DELETE"])
@jwt_required()
def delete_recipe(recipe_id):
    """Delete a specific recipe."""
    try:
        user_id = int(get_jwt_identity())

        # Delete recipe
        success = recipe_service.delete_recipe(recipe_id, user_id)

        if success:
            return jsonify({"message": "Recipe deleted successfully"}), 200
        else:
            return (
                jsonify(
                    ErrorResponse(
                        error="Not Found", message="Recipe not found", status_code=404
                    ).dict()
                ),
                404,
            )

    except NotFoundError as e:
        return (
            jsonify(
                ErrorResponse(error="Not Found", message=str(e), status_code=404).dict()
            ),
            404,
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
