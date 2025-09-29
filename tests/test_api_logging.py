#!/usr/bin/env python3
"""Test API logging with structured key-value pairs."""

import os
import sys

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

# Import after path setup
from src.core.config import Settings  # noqa: E402
from src.core.logging_config import (  # noqa: E402
    get_logger,
    log_business_operation,
    log_cache_operation,
    log_database_operation,
    log_request_response,
    setup_logging,
)


def test_api_logging():
    """Test API-like logging with key-value pairs."""

    # Set DEBUG level
    os.environ["LOG_LEVEL"] = "DEBUG"
    settings = Settings()
    setup_logging(settings)
    logger = get_logger("api_test")

    print("=== API Request/Response Logging Demo ===")

    # Simulate a recipe creation request
    request_id = "req-12345-67890"
    user_id = "user-38511350-8031-7036-57a2-cceb5bb135ca"

    # Log request start
    log_request_response(
        logger=logger,
        method="POST",
        url="/api/recipes",
        status_code=201,
        response_time=286.21,
        request_id=request_id,
        user_id=user_id,
        body={"request": {"title": "Complete task 2", "ingredients": ["flour", "eggs"]}},
    )

    # Log business operations
    log_business_operation(
        logger=logger,
        operation="create_recipe",
        user_id=user_id,
        success=True,
        recipe_id=2842,
        duration_ms=286.21,
    )

    # Log cache operations
    log_cache_operation(logger=logger, operation="get", key="recipe:2842", hit=False, duration=0.05)

    log_cache_operation(
        logger=logger,
        operation="set",
        key="recipe:2842",
        hit=False,
        duration=0.02,
        ttl=300,
    )

    # Log database operations
    log_database_operation(logger=logger, operation="create", table="recipes", duration=45.2, success=True)

    print("\n=== Different Log Levels Demo ===")

    # Test different log levels
    logger.debug(
        "Searching for user by email",
        extra={
            "email": "somisettyreddaiah@bitcot.com",
            "correlation_id": request_id,
            "operation": "user_lookup",
        },
    )

    logger.info(
        "User found by email",
        extra={
            "user_id": user_id,
            "email": "somisettyreddaiah@bitcot.com",
            "response_time_ms": 12.5,
            "operation": "user_lookup",
        },
    )

    logger.info(
        "Creating task for owner with title",
        extra={
            "owner_id": 278,
            "title": "Complete task 2",
            "operation": "task_creation",
        },
    )

    logger.info(
        "Task created successfully",
        extra={
            "task_id": 2842,
            "owner_id": 278,
            "title": "Complete task 2",
            "operation": "task_creation",
        },
    )

    logger.debug(
        "Getting next user task ID",
        extra={"user_id": user_id, "operation": "id_generation"},
    )

    logger.debug(
        "Next user task ID",
        extra={"next_id": 2273, "user_id": user_id, "operation": "id_generation"},
    )

    logger.debug(
        "Cache invalidation pattern",
        extra={"pattern": "task:278:task_id:", "operation": "cache_invalidation"},
    )

    logger.debug(
        "Cache invalidation pattern",
        extra={"pattern": "tasks:278:", "operation": "cache_invalidation"},
    )

    logger.debug("Database session closed", extra={"operation": "database_cleanup"})

    logger.info(
        "Request completed",
        extra={
            "request_id": request_id,
            "process_time_ms": 286.21,
            "status_code": 201,
            "operation": "request_completion",
        },
    )


if __name__ == "__main__":
    test_api_logging()
