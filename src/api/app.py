"""Flask application factory for the Recipe Manager API."""

from flask import Flask, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_jwt_extended.exceptions import JWTExtendedException

from src.api.routes.auth_routes import auth_bp
from src.api.routes.health_routes import health_bp
from src.api.routes.recipe_routes import recipe_bp
from src.core.database import init_database
from src.core.error_handler import register_exception_handlers
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
    jwt = JWTManager(app)
    init_database(app)

    # Configure JWT error handlers
    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        return (
            jsonify(
                {
                    "error": "AUTHENTICATION_ERROR",
                    "message": "Token has expired",
                    "status_code": 401,
                }
            ),
            401,
        )

    @jwt.invalid_token_loader
    def invalid_token_callback(error):
        return (
            jsonify(
                {
                    "error": "AUTHENTICATION_ERROR",
                    "message": "Invalid token",
                    "status_code": 401,
                }
            ),
            401,
        )

    @jwt.unauthorized_loader
    def missing_token_callback(error):
        return (
            jsonify(
                {
                    "error": "AUTHENTICATION_ERROR",
                    "message": "Authorization token required",
                    "status_code": 401,
                }
            ),
            401,
        )

    # Register blueprints
    app.register_blueprint(health_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(recipe_bp)

    # Register centralized error handlers
    register_exception_handlers(app)

    # Custom JWT error handlers
    @app.errorhandler(JWTExtendedException)
    def handle_jwt_exceptions(e):
        return (
            jsonify(
                {
                    "error": "AUTHENTICATION_ERROR",
                    "message": "Invalid or expired token",
                    "status_code": 401,
                }
            ),
            401,
        )

    # Root endpoint
    @app.route("/")
    def root():
        return jsonify({"message": "Recipe Manager API", "version": "1.0.0", "status": "running"})

    return app


# Create app instance
app = create_app()


if __name__ == "__main__":
    app.run(debug=settings.ENVIRONMENT == "development", host="0.0.0.0", port=5000)
