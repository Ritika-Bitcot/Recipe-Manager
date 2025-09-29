#!/usr/bin/env python3
"""Comprehensive test of the structured logging system."""

import os
import sys

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

# Import after path setup
from src.core.structured_logging import (  # noqa: E402
    RequestLoggingContext,
    generate_correlation_id,
    get_logger,
    log_business_operation,
    log_cache_operation,
    log_database_operation,
    setup_structured_logging,
)


def test_development_logging():
    """Test development logging with colors and key-value pairs."""
    print("=== Testing Development Logging (DEBUG Level) ===")

    os.environ["LOG_LEVEL"] = "DEBUG"
    os.environ["ENVIRONMENT"] = "development"

    setup_structured_logging(log_level="DEBUG", environment="development", log_file="test_dev.log")

    logger = get_logger("test_dev")

    # Test various log levels with context
    logger.debug(
        "Searching for user by email",
        email="test@example.com",
        correlation_id="req-12345-67890",
        operation="user_lookup",
    )

    logger.info(
        "User found successfully",
        user_id="user-123",
        email="test@example.com",
        response_time_ms=45.2,
        operation="user_lookup",
    )

    logger.warning(
        "Cache miss occurred",
        cache_key="user:123:profile",
        operation="cache_get",
        ttl_seconds=300,
    )

    logger.error(
        "Database connection failed",
        error_code="DB_CONN_001",
        retry_count=3,
        operation="database_connect",
    )

    # Test business operations
    log_business_operation(
        logger=logger,
        operation="create_recipe",
        success=True,
        duration_ms=286.21,
        user_id="user-123",
        recipe_id=2842,
    )

    # Test database operations
    log_database_operation(
        logger=logger,
        operation="create",
        table="recipes",
        success=True,
        duration_ms=45.2,
    )

    # Test cache operations
    log_cache_operation(logger=logger, operation="get", key="recipe:2842", hit=False, duration_ms=50.0)


def test_production_logging():
    """Test production logging with JSON output."""
    print("\n=== Testing Production Logging (INFO Level) ===")

    os.environ["LOG_LEVEL"] = "INFO"
    os.environ["ENVIRONMENT"] = "production"

    setup_structured_logging(log_level="INFO", environment="production", log_file="test_prod.log")

    logger = get_logger("test_prod")

    # Test structured logging in production
    logger.info(
        "API request processed",
        method="POST",
        path="/api/recipes",
        status_code=201,
        process_time_ms=286.21,
        user_id="user-123",
        correlation_id="req-abc-123",
    )

    logger.warning(
        "Rate limit approaching",
        current_requests=95,
        limit=100,
        window_seconds=60,
        operation="rate_limit_check",
    )

    logger.error(
        "Authentication failed",
        user_id="user-456",
        error="Invalid credentials",
        operation="auth",
    )


def test_context_management():
    """Test context management and correlation tracking."""
    print("\n=== Testing Context Management ===")

    os.environ["LOG_LEVEL"] = "DEBUG"
    os.environ["ENVIRONMENT"] = "development"

    setup_structured_logging(log_level="DEBUG", environment="development")

    logger = get_logger("test_context")

    # Test with context manager
    with RequestLoggingContext(
        correlation_id=generate_correlation_id(),
        user_id="user-789",
        request_path="/api/recipes",
        request_method="POST",
    ):
        logger.info("Processing request with context")
        logger.debug("Validating input data")
        logger.info("Request completed successfully")

    # Test without context (should show N/A values)
    logger.info("Logging without context")


def test_log_level_filtering():
    """Test log level filtering."""
    print("\n=== Testing Log Level Filtering ===")

    # Test INFO level (should hide DEBUG)
    print("--- INFO Level (DEBUG messages hidden) ---")
    os.environ["LOG_LEVEL"] = "INFO"
    setup_structured_logging(log_level="INFO", environment="development")
    logger = get_logger("test_levels")

    logger.debug("This debug message should not appear")
    logger.info("This info message should appear")
    logger.warning("This warning message should appear")
    logger.error("This error message should appear")

    # Test WARNING level (should hide DEBUG and INFO)
    print("\n--- WARNING Level (DEBUG and INFO messages hidden) ---")
    os.environ["LOG_LEVEL"] = "WARNING"
    setup_structured_logging(log_level="WARNING", environment="development")
    logger = get_logger("test_levels")

    logger.debug("This debug message should not appear")
    logger.info("This info message should not appear")
    logger.warning("This warning message should appear")
    logger.error("This error message should appear")


def test_flask_integration():
    """Test Flask integration with middleware."""
    print("\n=== Testing Flask Integration ===")

    os.environ["LOG_LEVEL"] = "DEBUG"
    os.environ["ENVIRONMENT"] = "development"

    from src.api.app import create_app

    app = create_app()

    with app.test_client() as client:
        print("Testing health endpoint...")
        response = client.get("/health")
        print(f"Status: {response.status_code}")

        print("\nTesting recipes endpoint (should require auth)...")
        response = client.get("/api/recipes")
        print(f"Status: {response.status_code}")


if __name__ == "__main__":
    print("🧪 Testing Structured Logging System")
    print("=" * 50)

    try:
        test_development_logging()
        test_production_logging()
        test_context_management()
        test_log_level_filtering()
        test_flask_integration()

        print("\n✅ All tests completed successfully!")
        print("\n📁 Check the following log files:")
        print("   - test_dev.log (development logs)")
        print("   - test_prod.log (production JSON logs)")
        print("   - app.log (application logs)")

    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback

        traceback.print_exc()
