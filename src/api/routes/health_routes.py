"""Health check routes for monitoring."""

from flask import Blueprint, jsonify
from sqlalchemy import text

from src.core.database import db

# Create blueprint
health_bp = Blueprint("health", __name__, url_prefix="/api/health")


@health_bp.route("", methods=["GET"])
def health_check():
    """Basic health check endpoint."""
    return jsonify({"status": "ok", "message": "Recipe Manager API is running"}), 200


@health_bp.route("/ready", methods=["GET"])
def readiness_check():
    """Readiness check including database connectivity."""
    try:
        # Test database connection
        db.session.execute(text("SELECT 1"))

        return (
            jsonify(
                {
                    "status": "ready",
                    "message": "Recipe Manager API is ready",
                    "database": "connected",
                }
            ),
            200,
        )

    except Exception as e:
        return (
            jsonify(
                {
                    "status": "not ready",
                    "message": "Recipe Manager API is not ready",
                    "database": "disconnected",
                    "error": str(e),
                }
            ),
            503,
        )
