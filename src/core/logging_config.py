"""Structured logging configuration for the Recipe Manager application."""

import json
import logging
import logging.config
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional

from src.core.config import Settings


class StructuredFormatter(logging.Formatter):
    """Custom formatter for structured JSON logging."""

    def format(self, record: logging.LogRecord) -> str:
        """Format log record as structured JSON."""
        # Base log structure
        log_entry = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": record.levelname,
            "logger": record.name,
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
            "message": record.getMessage(),
        }

        # Add thread information
        if hasattr(record, "thread"):
            log_entry["thread"] = record.thread
        if hasattr(record, "threadName"):
            log_entry["thread_name"] = record.threadName

        # Add process information
        if hasattr(record, "process"):
            log_entry["process"] = record.process
        if hasattr(record, "processName"):
            log_entry["process_name"] = record.processName

        # Add exception information if present
        if record.exc_info:
            log_entry["exception"] = {
                "type": record.exc_info[0].__name__ if record.exc_info[0] else None,
                "message": str(record.exc_info[1]) if record.exc_info[1] else None,
                "traceback": self.formatException(record.exc_info),
            }

        # Add extra fields from the log record
        for key, value in record.__dict__.items():
            if key not in {
                "name",
                "msg",
                "args",
                "levelname",
                "levelno",
                "pathname",
                "filename",
                "module",
                "lineno",
                "funcName",
                "created",
                "msecs",
                "relativeCreated",
                "thread",
                "threadName",
                "processName",
                "process",
                "getMessage",
                "exc_info",
                "exc_text",
                "stack_info",
            }:
                log_entry[key] = value

        return json.dumps(log_entry, default=str, ensure_ascii=False)


class DevelopmentFormatter(logging.Formatter):
    """Human-readable formatter for development with key-value pairs."""

    def __init__(self, fmt=None, datefmt=None):
        if fmt is None:
            fmt = "[%(levelname)s] %(message)s"
        if datefmt is None:
            datefmt = "%Y-%m-%d %H:%M:%S"
        super().__init__(fmt=fmt, datefmt=datefmt)

    def format(self, record: logging.LogRecord) -> str:
        """Format log record with key-value pairs."""
        # Get the base message
        message = record.getMessage()

        # Extract extra fields for key-value pairs
        extra_fields = []
        for key, value in record.__dict__.items():
            if key not in {
                "name",
                "msg",
                "args",
                "levelname",
                "levelno",
                "pathname",
                "filename",
                "module",
                "lineno",
                "funcName",
                "created",
                "msecs",
                "relativeCreated",
                "thread",
                "threadName",
                "processName",
                "process",
                "getMessage",
                "exc_info",
                "exc_text",
                "stack_info",
                "message",
            }:
                extra_fields.append(f"{key}={value}")

        # Add standard fields
        extra_fields.extend(
            [
                f"filename=src/{record.module}.py",
                f"lineno={record.lineno}",
                f"funcName={record.funcName}",
            ]
        )

        # Combine message with key-value pairs
        if extra_fields:
            kv_pairs = " ".join(extra_fields)
            return f"[{record.levelname}] {message} {kv_pairs}"
        else:
            return f"[{record.levelname}] {message}"


class RequestFormatter(logging.Formatter):
    """Formatter for request/response logging."""

    def __init__(self, fmt=None, datefmt=None):
        if fmt is None:
            fmt = "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
        if datefmt is None:
            datefmt = "%Y-%m-%d %H:%M:%S"
        super().__init__(fmt=fmt, datefmt=datefmt)

    def format(self, record: logging.LogRecord) -> str:
        """Format request log record."""
        if hasattr(record, "request_id"):
            record.msg = f"[{record.request_id}] {record.msg}"
        return super().format(record)


def setup_logging(settings: Settings) -> None:
    """Set up structured logging based on configuration."""
    # Create logs directory if it doesn't exist
    log_file_path = Path(settings.LOG_FILE)
    log_file_path.parent.mkdir(parents=True, exist_ok=True)

    # Determine formatter based on logger type
    if settings.LOGGER_TYPE in ["development", "dev"]:
        formatter_class = DevelopmentFormatter
        formatter_config = {
            "format": ("%(asctime)s | %(levelname)-8s | %(name)s.%(module)s:%(lineno)d | " "%(message)s"),
            "datefmt": "%Y-%m-%d %H:%M:%S",
        }
    else:
        formatter_class = StructuredFormatter
        formatter_config = {}

    # Configure logging
    logging_config = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "default": {
                "()": formatter_class,
                **formatter_config,
            },
            "request": {
                "()": RequestFormatter,
                "format": "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
                "datefmt": "%Y-%m-%d %H:%M:%S",
            },
            "structured": {
                "()": StructuredFormatter,
            },
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "level": settings.LOG_LEVEL,
                "formatter": "default",
                "stream": sys.stdout,
            },
            "file": {
                "class": "logging.handlers.RotatingFileHandler",
                "level": settings.LOG_LEVEL,
                "formatter": ("structured" if settings.LOGGER_TYPE in ["production", "prod"] else "default"),
                "filename": str(log_file_path),
                "maxBytes": 10485760,  # 10MB
                "backupCount": 5,
                "encoding": "utf-8",
            },
            "error_file": {
                "class": "logging.handlers.RotatingFileHandler",
                "level": "ERROR",
                "formatter": ("structured" if settings.LOGGER_TYPE in ["production", "prod"] else "default"),
                "filename": str(log_file_path.parent / "error.log"),
                "maxBytes": 10485760,  # 10MB
                "backupCount": 5,
                "encoding": "utf-8",
            },
        },
        "loggers": {
            "": {  # Root logger
                "level": settings.LOG_LEVEL,
                "handlers": ["console", "file"],
                "propagate": False,
            },
            "src": {  # Application logger
                "level": settings.LOG_LEVEL,
                "handlers": ["console", "file"],
                "propagate": False,
            },
            "src.api": {  # API logger
                "level": settings.LOG_LEVEL,
                "handlers": ["console", "file"],
                "propagate": False,
            },
            "src.services": {  # Services logger
                "level": settings.LOG_LEVEL,
                "handlers": ["console", "file"],
                "propagate": False,
            },
            "src.repositories": {  # Repositories logger
                "level": settings.LOG_LEVEL,
                "handlers": ["console", "file"],
                "propagate": False,
            },
            "src.core": {  # Core logger
                "level": settings.LOG_LEVEL,
                "handlers": ["console", "file"],
                "propagate": False,
            },
            "flask": {  # Flask logger
                "level": "WARNING",
                "handlers": ["console", "file"],
                "propagate": False,
            },
            "sqlalchemy": {  # SQLAlchemy logger
                "level": "WARNING",
                "handlers": ["console", "file"],
                "propagate": False,
            },
            "werkzeug": {  # Werkzeug logger
                "level": "WARNING",
                "handlers": ["console", "file"],
                "propagate": False,
            },
        },
    }

    # Apply logging configuration
    logging.config.dictConfig(logging_config)

    # Set up error handler
    error_logger = logging.getLogger("error")
    error_logger.addHandler(logging_config["handlers"]["error_file"])

    # Log configuration info
    logger = logging.getLogger(__name__)
    logger.info(
        "Logging system initialized",
        extra={
            "log_level": settings.LOG_LEVEL,
            "log_file": str(log_file_path),
            "logger_type": settings.LOGGER_TYPE,
            "log_body": settings.LOG_BODY,
        },
    )


def get_logger(name: str) -> logging.Logger:
    """Get a logger instance with the specified name."""
    return logging.getLogger(name)


class LoggerMixin:
    """Mixin class to add logging capabilities to any class."""

    @property
    def logger(self) -> logging.Logger:
        """Get logger for this class."""
        return get_logger(f"{self.__class__.__module__}.{self.__class__.__name__}")


def log_request_response(
    logger: logging.Logger,
    method: str,
    url: str,
    status_code: int,
    response_time: float,
    request_id: Optional[str] = None,
    user_id: Optional[str] = None,
    body: Optional[Dict[str, Any]] = None,
) -> None:
    """Log HTTP request and response information."""
    log_data = {
        "request_id": request_id,
        "method": method,
        "url": url,
        "status_code": status_code,
        "response_time_ms": round(response_time * 1000, 2),
        "user_id": user_id,
    }

    if body and logger.isEnabledFor(logging.DEBUG):
        log_data["request_body"] = body

    if status_code >= 400:
        logger.error("HTTP request failed", extra=log_data)
    elif status_code >= 300:
        logger.warning("HTTP request redirected", extra=log_data)
    else:
        logger.info("HTTP request completed", extra=log_data)


def log_database_operation(
    logger: logging.Logger,
    operation: str,
    table: str,
    duration: float,
    success: bool,
    error: Optional[str] = None,
    **kwargs: Any,
) -> None:
    """Log database operation information."""
    log_data = {
        "operation": operation,
        "table": table,
        "duration_ms": round(duration * 1000, 2),
        "success": success,
        **kwargs,
    }

    if error:
        log_data["error"] = error

    if success:
        logger.debug("Database operation completed", extra=log_data)
    else:
        logger.error("Database operation failed", extra=log_data)


def log_cache_operation(
    logger: logging.Logger,
    operation: str,
    key: str,
    hit: bool,
    duration: float,
    **kwargs: Any,
) -> None:
    """Log cache operation information."""
    log_data = {
        "operation": operation,
        "key": key,
        "hit": hit,
        "duration_ms": round(duration * 1000, 2),
        **kwargs,
    }

    if hit:
        logger.debug("Cache hit", extra=log_data)
    else:
        logger.debug("Cache miss", extra=log_data)


def log_business_operation(
    logger: logging.Logger,
    operation: str,
    user_id: Optional[str] = None,
    success: bool = True,
    error: Optional[str] = None,
    **kwargs: Any,
) -> None:
    """Log business operation information."""
    log_data = {
        "operation": operation,
        "user_id": user_id,
        "success": success,
        **kwargs,
    }

    if error:
        log_data["error"] = error

    if success:
        logger.info("Business operation completed", extra=log_data)
    else:
        logger.error("Business operation failed", extra=log_data)
