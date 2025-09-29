"""Flask middleware for structured logging and request correlation.

This module provides middleware components for:
- Request correlation tracking
- User context extraction
- Request/response logging
- Performance monitoring
"""

import time
from typing import List, Optional

from flask import Flask, g, request
from flask_jwt_extended import decode_token, get_jwt_identity

from .structured_logging import (
    add_correlation_context,
    generate_correlation_id,
    get_logger,
    log_request_complete,
    log_request_error,
    log_request_start,
)


class CorrelationMiddleware:
    """Middleware to add correlation IDs and request context.

    This middleware:
    1. Generates unique correlation ID per request
    2. Extracts user information from JWT tokens
    3. Sets up logging context for request lifecycle
    4. Logs request start/completion with timing
    """

    def __init__(self, app: Optional[Flask] = None, exclude_paths: Optional[List[str]] = None):
        """Initialize middleware.

        Args:
            app: Flask application instance
            exclude_paths: Paths to exclude from user extraction
        """
        self.logger = get_logger(__name__)
        self.exclude_paths = exclude_paths or ["/health", "/health/ready"]

        if app is not None:
            self.init_app(app)

    def init_app(self, app: Flask) -> None:
        """Initialize middleware with Flask app.

        Args:
            app: Flask application instance
        """
        app.before_request(self.before_request)
        app.after_request(self.after_request)
        app.teardown_request(self.teardown_request)

        self.logger.info(
            "Correlation middleware configured",
            exclude_paths=self.exclude_paths,
            correlation_enabled=True,
        )

    def before_request(self) -> None:
        """Process request before handling."""
        # Generate correlation ID
        correlation_id = generate_correlation_id()
        request_path = request.path
        request_method = request.method

        # Extract user information
        user_id = self._extract_user_id()

        # Set up logging context
        add_correlation_context(
            correlation_id=correlation_id,
            user_id=user_id,
            request_path=request_path,
            request_method=request_method,
        )

        # Store in Flask g for access in views
        g.correlation_id = correlation_id
        g.user_id = user_id
        g.request_start_time = time.time()

        # Log request start
        log_request_start(
            logger=self.logger,
            method=request_method,
            path=request_path,
            query_params=dict(request.args),
            client_ip=self._get_client_ip(),
            user_agent=request.headers.get("user-agent", "unknown"),
            content_type=request.content_type,
            content_length=request.content_length,
        )

    def after_request(self, response) -> None:
        """Process response after handling."""
        if hasattr(g, "request_start_time"):
            process_time = time.time() - g.request_start_time
            process_time_ms = round(process_time * 1000, 2)

            # Log successful completion
            log_request_complete(
                logger=self.logger,
                method=request.method,
                path=request.path,
                status_code=response.status_code,
                process_time_ms=process_time_ms,
                response_size=response.content_length,
            )

            # Add correlation ID to response headers
            response.headers["X-Correlation-ID"] = g.correlation_id
            response.headers["X-Process-Time"] = str(process_time_ms)

        return response

    def teardown_request(self, exception) -> None:
        """Handle request teardown and error logging."""
        if exception is not None and hasattr(g, "request_start_time"):
            process_time = time.time() - g.request_start_time
            process_time_ms = round(process_time * 1000, 2)

            # Log error
            log_request_error(
                logger=self.logger,
                method=request.method,
                path=request.path,
                error=str(exception),
                process_time_ms=process_time_ms,
                error_type=exception.__class__.__name__,
            )

    def _extract_user_id(self) -> str:
        """Extract user ID from JWT token or headers.

        Returns:
            str: User ID or "anonymous"
        """
        # Skip user extraction for excluded paths
        if request.path in self.exclude_paths:
            return "anonymous"

        try:
            # Try to get user ID from JWT token
            user_id = get_jwt_identity()
            if user_id:
                return str(user_id)
        except Exception:
            # JWT extraction failed, try alternative methods
            pass

        # Try to extract from Authorization header
        auth_header = request.headers.get("Authorization", "")
        if auth_header.startswith("Bearer "):
            try:
                token = auth_header.split(" ")[1]
                decoded_token = decode_token(token)
                user_id = decoded_token.get("sub") or decoded_token.get("user_id")
                if user_id:
                    return str(user_id)
            except Exception:
                # Token decoding failed
                pass

        # Try to extract from custom headers
        user_id = request.headers.get("X-User-ID")
        if user_id:
            return str(user_id)

        return "anonymous"

    def _get_client_ip(self) -> str:
        """Extract client IP address from request headers.

        Returns:
            str: Client IP address
        """
        # Check forwarded headers first
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()

        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip

        # Fall back to remote address
        if request.environ.get("HTTP_X_FORWARDED_FOR"):
            return request.environ["HTTP_X_FORWARDED_FOR"].split(",")[0].strip()

        return request.environ.get("REMOTE_ADDR", "unknown")


def setup_logging_middleware(app: Flask, exclude_paths: Optional[List[str]] = None) -> None:
    """Set up logging middleware on Flask application.

    Args:
        app: Flask application instance
        exclude_paths: Paths to exclude from user extraction
    """
    middleware = CorrelationMiddleware(app, exclude_paths)
    return middleware


class RequestContextMiddleware:
    """Additional middleware for request context management."""

    def __init__(self, app: Optional[Flask] = None):
        """Initialize middleware.

        Args:
            app: Flask application instance
        """
        self.logger = get_logger(__name__)

        if app is not None:
            self.init_app(app)

    def init_app(self, app: Flask) -> None:
        """Initialize middleware with Flask app.

        Args:
            app: Flask application instance
        """
        app.before_request(self.before_request)
        app.teardown_request(self.teardown_request)

    def before_request(self) -> None:
        """Set up request context."""
        # Add request ID to Flask g
        g.request_id = g.get("correlation_id", "unknown")

        # Add request metadata
        g.request_metadata = {
            "method": request.method,
            "path": request.path,
            "user_agent": request.headers.get("user-agent", "unknown"),
            "client_ip": request.environ.get("REMOTE_ADDR", "unknown"),
            "timestamp": time.time(),
        }

    def teardown_request(self, exception) -> None:
        """Clean up request context."""
        # Log request completion with metadata
        if hasattr(g, "request_metadata"):
            self.logger.debug(
                "Request context cleaned up",
                request_id=g.get("request_id", "unknown"),
                duration_ms=round((time.time() - g.request_metadata["timestamp"]) * 1000, 2),
            )
