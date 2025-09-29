"""Database configuration and session management."""

from flask import Flask
from flask_sqlalchemy import SQLAlchemy

from src.core.settings import settings

# Initialize SQLAlchemy
db = SQLAlchemy()


def init_database(app: Flask) -> None:
    """Initialize database with Flask app."""
    app.config["SQLALCHEMY_DATABASE_URI"] = settings.database_url
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
        "pool_pre_ping": True,
        "pool_recycle": 300,
    }

    db.init_app(app)


def get_db_session():
    """Get database session for manual operations."""
    return db.session


def close_db_session():
    """Close database session."""
    db.session.close()
