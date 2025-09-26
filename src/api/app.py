"""Flask application factory for the Recipe Manager API."""

from flask import Flask, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager

from src.api.routes.auth_routes import auth_bp
from src.api.routes.health_routes import health_bp
from src.api.routes.recipe_routes import recipe_bp
from src.core.database import db, init_database
from src.core.exceptions import (
    AuthenticationError,
    AuthorizationError,
    ConflictError,
    NotFoundError,
    RecipeManagerException,
    ValidationError,
)
from src.core.settings import settings


def create_app() -> Flask:
    """Create and configure Flask application."""
    app = Flask(__name__)

    # Configure Flask
    app.config["SECRET_KEY"] = settings.SECRET_KEY
    app.config["JWT_SECRET_KEY"] = settings.SECRET_KEY
    app.config["JWT_ACCESS_TOKEN_EXPIRES"] = settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60

    # Initialize extensions
    CORS(app)
    JWTManager(app)
    init_database(app)

    # Register blueprints
    app.register_blueprint(health_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(recipe_bp)

    # Error handlers
    @app.errorhandler(ValidationError)
    def handle_validation_error(e):
        return (
            jsonify(
                {
                    "error": "Validation Error",
                    "message": e.message,
                    "status_code": e.status_code,
                    "field": getattr(e, "field", None),
                }
            ),
            e.status_code,
        )

    @app.errorhandler(AuthenticationError)
    def handle_authentication_error(e):
        return (
            jsonify(
                {
                    "error": "Authentication Error",
                    "message": e.message,
                    "status_code": e.status_code,
                }
            ),
            e.status_code,
        )

    @app.errorhandler(AuthorizationError)
    def handle_authorization_error(e):
        return (
            jsonify(
                {
                    "error": "Authorization Error",
                    "message": e.message,
                    "status_code": e.status_code,
                }
            ),
            e.status_code,
        )

    @app.errorhandler(NotFoundError)
    def handle_not_found_error(e):
        return (
            jsonify(
                {
                    "error": "Not Found",
                    "message": e.message,
                    "status_code": e.status_code,
                }
            ),
            e.status_code,
        )

    @app.errorhandler(ConflictError)
    def handle_conflict_error(e):
        return (
            jsonify(
                {
                    "error": "Conflict",
                    "message": e.message,
                    "status_code": e.status_code,
                }
            ),
            e.status_code,
        )

    @app.errorhandler(RecipeManagerException)
    def handle_recipe_manager_error(e):
        return (
            jsonify(
                {
                    "error": "Recipe Manager Error",
                    "message": e.message,
                    "status_code": e.status_code,
                }
            ),
            e.status_code,
        )

    @app.errorhandler(404)
    def handle_not_found(e):
        return (
            jsonify(
                {
                    "error": "Not Found",
                    "message": "The requested resource was not found",
                    "status_code": 404,
                }
            ),
            404,
        )

    @app.errorhandler(500)
    def handle_internal_error(e):
        return (
            jsonify(
                {
                    "error": "Internal Server Error",
                    "message": "An unexpected error occurred",
                    "status_code": 500,
                }
            ),
            500,
        )

    # Root endpoint
    @app.route("/")
    def root():
        return jsonify({"message": "Recipe Manager API", "version": "1.0.0", "status": "running"})

    # Create database tables
    with app.app_context():
        db.create_all()

    return app


# Create app instance
app = create_app()


if __name__ == "__main__":
    app.run(debug=settings.ENVIRONMENT == "development", host="0.0.0.0", port=5000)
