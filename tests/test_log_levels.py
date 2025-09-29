#!/usr/bin/env python3
"""Test log level filtering with key-value pairs."""

import os
import sys

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))


def test_log_levels():
    """Test different log levels with filtering."""

    print("=== Testing DEBUG Level (should show all messages) ===")
    os.environ["LOG_LEVEL"] = "DEBUG"

    from src.core.config import Settings
    from src.core.logging_config import get_logger, setup_logging

    settings = Settings()
    setup_logging(settings)
    logger = get_logger("test_logger")

    logger.debug("Debug message", extra={"key1": "value1", "operation": "debug_test"})
    logger.info("Info message", extra={"key2": "value2", "operation": "info_test"})
    logger.warning("Warning message", extra={"key3": "value3", "operation": "warning_test"})
    logger.error("Error message", extra={"key4": "value4", "operation": "error_test"})

    print("\n=== Testing INFO Level (should hide DEBUG messages) ===")
    os.environ["LOG_LEVEL"] = "INFO"

    # Recreate settings and logger
    settings = Settings()
    setup_logging(settings)
    logger = get_logger("test_logger")

    logger.debug(
        "Debug message - should not appear",
        extra={"key1": "value1", "operation": "debug_test"},
    )
    logger.info("Info message", extra={"key2": "value2", "operation": "info_test"})
    logger.warning("Warning message", extra={"key3": "value3", "operation": "warning_test"})
    logger.error("Error message", extra={"key4": "value4", "operation": "error_test"})

    print("\n=== Testing WARNING Level (should hide DEBUG and INFO messages) ===")
    os.environ["LOG_LEVEL"] = "WARNING"

    # Recreate settings and logger
    settings = Settings()
    setup_logging(settings)
    logger = get_logger("test_logger")

    logger.debug(
        "Debug message - should not appear",
        extra={"key1": "value1", "operation": "debug_test"},
    )
    logger.info(
        "Info message - should not appear",
        extra={"key2": "value2", "operation": "info_test"},
    )
    logger.warning("Warning message", extra={"key3": "value3", "operation": "warning_test"})
    logger.error("Error message", extra={"key4": "value4", "operation": "error_test"})

    print("\n=== Testing ERROR Level (should only show ERROR messages) ===")
    os.environ["LOG_LEVEL"] = "ERROR"

    # Recreate settings and logger
    settings = Settings()
    setup_logging(settings)
    logger = get_logger("test_logger")

    logger.debug(
        "Debug message - should not appear",
        extra={"key1": "value1", "operation": "debug_test"},
    )
    logger.info(
        "Info message - should not appear",
        extra={"key2": "value2", "operation": "info_test"},
    )
    logger.warning(
        "Warning message - should not appear",
        extra={"key3": "value3", "operation": "warning_test"},
    )
    logger.error("Error message", extra={"key4": "value4", "operation": "error_test"})


if __name__ == "__main__":
    test_log_levels()
