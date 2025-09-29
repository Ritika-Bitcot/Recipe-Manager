#!/usr/bin/env python3
"""Test Flask integration with structured logging."""

import os
import sys

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))


def test_flask_logging():
    """Test Flask integration with structured logging."""
    print("=== Testing Flask Integration with Structured Logging ===")

    os.environ["LOG_LEVEL"] = "DEBUG"
    os.environ["ENVIRONMENT"] = "development"
    os.environ["DATABASE_URL"] = "sqlite:///test.db"
    os.environ["SECRET_KEY"] = "test-secret-key"
    os.environ["ALLOWED_ORIGINS"] = '["*"]'

    from src.api.app import create_app

    app = create_app()

    with app.test_client() as client:
        print("Testing health endpoint...")
        response = client.get("/health")
        print(f"Status: {response.status_code}")
        print(f"Response: {response.get_json()}")

        print("\nTesting recipes endpoint (should require auth)...")
        response = client.get("/api/recipes")
        print(f"Status: {response.status_code}")
        print(f"Response: {response.get_json()}")

        print("\nTesting root endpoint...")
        response = client.get("/")
        print(f"Status: {response.status_code}")
        print(f"Response: {response.get_json()}")


if __name__ == "__main__":
    test_flask_logging()
