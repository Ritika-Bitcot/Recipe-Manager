"""Production-ready structured logging implementation for Flask applications.

This module provides comprehensive structured logging with:
- Environment-aware formatting (human-readable for dev, JSON for production)
- Correlation tracking with unique request IDs
- Context management for user and request information
- Caller information with file names and line numbers
- Performance monitoring with built-in timing
"""

import inspect
import logging
import logging.handlers
import sys
import uuid
from contextvars import ContextVar
from pathlib import Path
from typing import Optional

import structlog
from colorama import Fore, Style
from colorama import init as colorama_init

# Initialize colorama for cross-platform color support
colorama_init()

# Context variables for request tracking
correlation_id: ContextVar[Optional[str]] = ContextVar("correlation_id", default=None)
user_id: ContextVar[Optional[str]] = ContextVar("user_id", default=None)
request_path: ContextVar[Optional[str]] = ContextVar("request_path", default=None)
request_method: ContextVar[Optional[str]] = ContextVar("request_method", default=None)
service_name: ContextVar[Optional[str]] = ContextVar("service_name", default="recipe-manager")

# Global variable to cache project root
_PROJECT_ROOT = None


def get_project_root() -> Path:
    """Detect project root by looking for common indicators.

    Returns:
        Path: Project root directory
    """
    global _PROJECT_ROOT
    if _PROJECT_ROOT is not None:
        return _PROJECT_ROOT

    current_path = Path(__file__).resolve()

    # Look for common project root indicators
    indicators = [".git", "setup.py", "pyproject.toml", "requirements.txt"]
    for parent in [current_path] + list(current_path.parents):
        if any((parent / indicator).exists() for indicator in indicators):
            _PROJECT_ROOT = parent
            return _PROJECT_ROOT

    # Fallback to current file's parent directory
    _PROJECT_ROOT = current_path.parent
    return _PROJECT_ROOT


def get_relative_path(file_path: str) -> str:
    """Convert absolute file path to relative path from project root.

    Args:
        file_path: Absolute file path

    Returns:
        str: Relative path from project root
    """
    try:
        abs_path = Path(file_path).resolve()
        project_root = get_project_root()
        return str(abs_path.relative_to(project_root))
    except (ValueError, OSError):
        # Fallback to filename only if relative path calculation fails
        return Path(file_path).name


def add_caller_info_processor(logger, method_name, event_dict):
    """Add file and line number information to log entries.

    This processor inspects the call stack to find the original caller
    outside of logging framework internals.
    """
    try:
        stack = inspect.stack()

        # Find first frame that's not in logging internals
        for frame_info in stack:
            filename = frame_info.filename
            func_name = frame_info.function

            # Skip internal frames
            skip_patterns = [
                "structlog",
                "logging",
                "site-packages",
                "/venv/",
                "src/core/structured_logging.py",
            ]

            if any(pattern in filename for pattern in skip_patterns):
                continue

            if func_name == "add_caller_info_processor":
                continue

            # Found user code
            event_dict["filename"] = get_relative_path(filename)
            event_dict["lineno"] = frame_info.lineno
            break

    except Exception:
        # Don't add caller info if there's any error
        pass

    return event_dict


def add_context_processor(_, __, event_dict):
    """Add context variables to log entries.

    This processor adds correlation ID, user ID, and request information
    to every log entry automatically.
    """
    event_dict["correlation_id"] = correlation_id.get() or "N/A"
    event_dict["user_id"] = user_id.get() or "anonymous"
    event_dict["request_path"] = request_path.get() or "N/A"
    event_dict["request_method"] = request_method.get() or "N/A"
    event_dict["service_name"] = service_name.get() or "recipe-manager"

    return event_dict


def setup_structured_logging(
    log_level: str = "INFO",
    environment: str = "development",
    log_file: Optional[str] = None,
) -> None:
    """Configure structured logging based on environment.

    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        environment: Environment type (development, production, testing)
        log_file: Optional log file path
    """
    # Convert string log level to numeric constant
    numeric_level = getattr(logging, log_level.upper(), logging.INFO)

    # Determine output format based on environment
    is_production = environment.lower() in ["production", "prod", "testing", "test"]

    # Configure structlog processors
    processors = [
        structlog.contextvars.merge_contextvars,  # Merge context variables
        add_context_processor,  # Add our custom context
        add_caller_info_processor,  # Add file/line info
        structlog.processors.add_log_level,  # Add log level
        structlog.processors.StackInfoRenderer(),  # Render stack traces
        structlog.dev.set_exc_info,  # Set exception info
    ]

    # Add environment-specific renderer
    if is_production:
        # Production: JSON output for machine parsing
        processors.append(structlog.processors.JSONRenderer())
    else:
        # Development: Human-readable output with colors
        processors.append(structlog.dev.ConsoleRenderer(colors=True, pad_event=25, sort_keys=True))

    # Configure structlog
    structlog.configure(
        processors=processors,
        wrapper_class=structlog.make_filtering_bound_logger(numeric_level),
        logger_factory=structlog.WriteLoggerFactory(),
        context_class=dict,
        cache_logger_on_first_use=True,
    )

    # Configure standard Python logging
    _configure_standard_logging(numeric_level, is_production, log_file)

    # Log successful configuration
    logger = get_logger(__name__)
    logger.info(
        "Structured logging configured successfully",
        environment=environment,
        log_level=log_level,
        json_output=is_production,
        log_file=log_file,
    )


def _configure_standard_logging(numeric_level: int, is_production: bool, log_file: Optional[str]) -> None:
    """Configure standard Python logging to work with structlog."""
    # Create console handler
    console_handler = logging.StreamHandler(sys.stdout)

    # Set formatter based on environment
    if is_production:
        # JSON formatter for production
        formatter = logging.Formatter(
            '{"timestamp": "%(asctime)s", "level": "%(levelname)s", ' '"logger": "%(name)s", "message": "%(message)s"}'
        )
    else:
        # Colored formatter for development
        formatter = logging.Formatter(
            f"{Fore.BLUE}%(asctime)s{Style.RESET_ALL} | "
            f"{Fore.GREEN}%(levelname)-8s{Style.RESET_ALL} | "
            f"{Fore.CYAN}%(name)s{Style.RESET_ALL} - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )

    console_handler.setFormatter(formatter)

    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(numeric_level)
    root_logger.handlers.clear()
    root_logger.addHandler(console_handler)

    # Add file handler if specified
    if log_file:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)

        file_handler = logging.handlers.RotatingFileHandler(
            log_file, maxBytes=10 * 1024 * 1024, backupCount=5, encoding="utf-8"  # 10MB
        )

        if is_production:
            file_formatter = logging.Formatter(
                '{"timestamp": "%(asctime)s", "level": "%(levelname)s", '
                '"logger": "%(name)s", "message": "%(message)s"}'
            )
        else:
            file_formatter = logging.Formatter(
                "%(asctime)s | %(levelname)-8s | %(name)s - %(message)s",
                datefmt="%Y-%m-%d %H:%M:%S",
            )

        file_handler.setFormatter(file_formatter)
        root_logger.addHandler(file_handler)


def get_logger(name: str) -> structlog.BoundLogger:
    """Get a structured logger instance.

    Args:
        name: Logger name (typically __name__)

    Returns:
        structlog.BoundLogger: Configured structured logger
    """
    return structlog.get_logger(name)


def get_standard_logger(name: str) -> logging.Logger:
    """Get a standard Python logger (for compatibility).

    Args:
        name: Logger name (typically __name__)

    Returns:
        logging.Logger: Standard Python logger
    """
    return logging.getLogger(name)


def add_correlation_context(**kwargs) -> None:
    """Add correlation context to current execution context.

    Args:
        **kwargs: Context variables (correlation_id, user_id, etc.)
    """
    if "correlation_id" in kwargs:
        correlation_id.set(kwargs["correlation_id"])
    if "user_id" in kwargs:
        user_id.set(kwargs["user_id"])
    if "request_path" in kwargs:
        request_path.set(kwargs["request_path"])
    if "request_method" in kwargs:
        request_method.set(kwargs["request_method"])
    if "service_name" in kwargs:
        service_name.set(kwargs["service_name"])


def generate_correlation_id() -> str:
    """Generate a unique correlation ID.

    Returns:
        str: UUID-based correlation ID
    """
    return str(uuid.uuid4())


class RequestLoggingContext:
    """Context manager for request-scoped logging context.

    Usage:
        with RequestLoggingContext(correlation_id="abc-123", user_id="user1"):
            logger.info("Processing request")
    """

    def __init__(self, **context_vars):
        """Initialize context manager.

        Args:
            **context_vars: Context variables to set
        """
        self.context_vars = context_vars
        self.tokens = {}

    def __enter__(self):
        """Set context variables and store reset tokens."""
        for key, value in self.context_vars.items():
            if key == "correlation_id":
                self.tokens[key] = correlation_id.set(value)
            elif key == "user_id":
                self.tokens[key] = user_id.set(value)
            elif key == "request_path":
                self.tokens[key] = request_path.set(value)
            elif key == "request_method":
                self.tokens[key] = request_method.set(value)
            elif key == "service_name":
                self.tokens[key] = service_name.set(value)

        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Reset context variables to previous values."""
        for key, token in self.tokens.items():
            if key == "correlation_id":
                correlation_id.reset(token)
            elif key == "user_id":
                user_id.reset(token)
            elif key == "request_path":
                request_path.reset(token)
            elif key == "request_method":
                request_method.reset(token)
            elif key == "service_name":
                service_name.reset(token)


# Convenience functions for common logging patterns
def log_request_start(logger: structlog.BoundLogger, method: str, path: str, **kwargs) -> None:
    """Log the start of a request with context."""
    logger.info("Request started", method=method, path=path, **kwargs)


def log_request_complete(
    logger: structlog.BoundLogger,
    method: str,
    path: str,
    status_code: int,
    process_time_ms: float,
    **kwargs,
) -> None:
    """Log the completion of a request with timing."""
    logger.info(
        "Request completed",
        method=method,
        path=path,
        status_code=status_code,
        process_time_ms=process_time_ms,
        **kwargs,
    )


def log_request_error(
    logger: structlog.BoundLogger,
    method: str,
    path: str,
    error: str,
    process_time_ms: float,
    **kwargs,
) -> None:
    """Log a request error with context."""
    logger.error(
        "Request failed",
        method=method,
        path=path,
        error=error,
        process_time_ms=process_time_ms,
        exc_info=True,
        **kwargs,
    )


def log_business_operation(
    logger: structlog.BoundLogger,
    operation: str,
    success: bool = True,
    duration_ms: Optional[float] = None,
    **kwargs,
) -> None:
    """Log a business operation with context."""
    level = "info" if success else "error"
    message = f"Business operation {'completed' if success else 'failed'}"

    log_data = {"operation": operation, "success": success, **kwargs}

    if duration_ms is not None:
        log_data["duration_ms"] = duration_ms

    getattr(logger, level)(message, **log_data)


def log_database_operation(
    logger: structlog.BoundLogger,
    operation: str,
    table: str,
    success: bool = True,
    duration_ms: Optional[float] = None,
    **kwargs,
) -> None:
    """Log a database operation with context."""
    level = "debug" if success else "error"
    message = f"Database operation {'completed' if success else 'failed'}"

    log_data = {"operation": operation, "table": table, "success": success, **kwargs}

    if duration_ms is not None:
        log_data["duration_ms"] = duration_ms

    getattr(logger, level)(message, **log_data)


def log_cache_operation(
    logger: structlog.BoundLogger,
    operation: str,
    key: str,
    hit: bool = False,
    duration_ms: Optional[float] = None,
    **kwargs,
) -> None:
    """Log a cache operation with context."""
    message = f"Cache {'hit' if hit else 'miss'}"

    log_data = {"operation": operation, "key": key, "hit": hit, **kwargs}

    if duration_ms is not None:
        log_data["duration_ms"] = duration_ms

    logger.debug(message, **log_data)
