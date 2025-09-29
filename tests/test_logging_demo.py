#!/usr/bin/env python3
"""Demo script to test structured logging with key-value pairs."""

import os
import sys

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

# Import after path setup
from src.core.config import Settings  # noqa: E402
from src.core.logging_config import get_logger, setup_logging  # noqa: E402


def test_logging_levels():
    """Test different log levels with key-value pairs."""

    # Test with DEBUG level
    print("=== Testing DEBUG Level ===")
    os.environ["LOG_LEVEL"] = "DEBUG"
    settings = Settings()
    setup_logging(settings)
    logger = get_logger("test_logger")

    # Test various log levels with extra data
    logger.debug(
        "Searching for user by email",
        extra={
            "email": "test@example.com",
            "correlation_id": "12345-67890",
            "operation": "user_lookup",
        },
    )

    logger.info(
        "User found successfully",
        extra={
            "user_id": "user-123",
            "email": "test@example.com",
            "response_time_ms": 45.2,
            "operation": "user_lookup",
        },
    )

    logger.warning(
        "Cache miss occurred",
        extra={
            "cache_key": "user:123:profile",
            "operation": "cache_get",
            "ttl_seconds": 300,
        },
    )

    logger.error(
        "Database connection failed",
        extra={
            "error_code": "DB_CONN_001",
            "retry_count": 3,
            "operation": "database_connect",
        },
    )

    print("\n=== Testing INFO Level ===")
    os.environ["LOG_LEVEL"] = "INFO"
    settings = Settings()
    setup_logging(settings)
    logger = get_logger("test_logger")

    logger.debug("This debug message should not appear")
    logger.info(
        "User authentication successful",
        extra={
            "user_id": "user-456",
            "method": "jwt",
            "duration_ms": 12.5,
            "operation": "auth",
        },
    )

    logger.warning(
        "Rate limit approaching",
        extra={
            "current_requests": 95,
            "limit": 100,
            "window_seconds": 60,
            "operation": "rate_limit_check",
        },
    )

    print("\n=== Testing WARNING Level ===")
    os.environ["LOG_LEVEL"] = "WARNING"
    settings = Settings()
    setup_logging(settings)
    logger = get_logger("test_logger")

    logger.info("This info message should not appear")
    logger.warning(
        "Memory usage high",
        extra={
            "memory_usage_percent": 85.3,
            "threshold_percent": 80.0,
            "operation": "memory_monitor",
        },
    )

    logger.error(
        "API rate limit exceeded",
        extra={
            "endpoint": "/api/recipes",
            "limit": 100,
            "current_requests": 105,
            "operation": "rate_limit",
        },
    )


if __name__ == "__main__":
    test_logging_levels()
