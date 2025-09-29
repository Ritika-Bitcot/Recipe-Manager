"""Flask error handlers with structured logging.

This module provides centralized error handling for the Flask application
with structured logging and consistent error response formatting.
"""

from flask import Flask, g, jsonify, request

from .structured_logging import get_logger


def create_error_handler(app: Flask) -> None:
    """Create global error handlers with structured logging.

    Args:
        app: Flask application instance
    """
    logger = get_logger(__name__)

    @app.errorhandler(400)
    def bad_request(error):
        """Handle 400 Bad Request errors."""
        logger.warning(
            "Bad request error",
            error=str(error),
            status_code=400,
            path=request.path,
            method=request.method,
        )
        return (
            jsonify(
                {
                    "error": "Bad Request",
                    "message": str(error),
                    "status_code": 400,
                    "correlation_id": g.get("correlation_id", "unknown"),
                }
            ),
            400,
        )

    @app.errorhandler(401)
    def unauthorized(error):
        """Handle 401 Unauthorized errors."""
        logger.warning(
            "Unauthorized access attempt",
            error=str(error),
            status_code=401,
            path=request.path,
            method=request.method,
            client_ip=request.environ.get("REMOTE_ADDR", "unknown"),
        )
        return (
            jsonify(
                {
                    "error": "Unauthorized",
                    "message": "Authentication required",
                    "status_code": 401,
                    "correlation_id": g.get("correlation_id", "unknown"),
                }
            ),
            401,
        )

    @app.errorhandler(403)
    def forbidden(error):
        """Handle 403 Forbidden errors."""
        logger.warning(
            "Forbidden access attempt",
            error=str(error),
            status_code=403,
            path=request.path,
            method=request.method,
            user_id=g.get("user_id", "anonymous"),
        )
        return (
            jsonify(
                {
                    "error": "Forbidden",
                    "message": "Access denied",
                    "status_code": 403,
                    "correlation_id": g.get("correlation_id", "unknown"),
                }
            ),
            403,
        )

    @app.errorhandler(404)
    def not_found(error):
        """Handle 404 Not Found errors."""
        logger.info(
            "Resource not found",
            error=str(error),
            status_code=404,
            path=request.path,
            method=request.method,
        )
        return (
            jsonify(
                {
                    "error": "Not Found",
                    "message": "The requested resource was not found",
                    "status_code": 404,
                    "correlation_id": g.get("correlation_id", "unknown"),
                }
            ),
            404,
        )

    @app.errorhandler(500)
    def internal_error(error):
        """Handle 500 Internal Server errors."""
        logger.error(
            "Internal server error",
            error=str(error),
            status_code=500,
            path=request.path,
            method=request.method,
            exc_info=True,
        )
        return (
            jsonify(
                {
                    "error": "Internal Server Error",
                    "message": "An unexpected error occurred",
                    "status_code": 500,
                    "correlation_id": g.get("correlation_id", "unknown"),
                }
            ),
            500,
        )
