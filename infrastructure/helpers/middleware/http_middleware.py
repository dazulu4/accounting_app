"""
HTTP Middleware - Enterprise Edition

This module provides enterprise-grade middleware components for Flask applications
including error handling, performance monitoring, and request logging.

Key Features:
- Structured error handling with context
- Performance monitoring and metrics
- Request logging with correlation IDs
- Security logging for suspicious activities
- Health check monitoring
"""

import time
import uuid
from typing import Dict, Any, Optional
from flask import Flask, request, g, current_app
from werkzeug.exceptions import HTTPException

from infrastructure.helpers.logger.logger_config import (
    get_logger,
    get_request_logger,
    get_performance_logger,
    get_security_logger,
    generate_request_id,
    logging_context,
)
from infrastructure.helpers.errors.error_handlers import HTTPErrorHandler
from infrastructure.helpers.middleware.rate_limit_middleware import RateLimitMiddleware


class LoggingMiddleware:
    """
    Middleware for structured request logging with context

    Provides automatic request ID generation, context binding,
    and structured logging for all HTTP requests.
    """

    def __init__(self, app: Flask):
        self.app = app
        self.logger = get_request_logger()

    def __call__(self, environ, start_response):
        # Generate request ID
        request_id = generate_request_id()
        environ["request_id"] = request_id

        # Get request details
        path = environ.get("PATH_INFO", "")
        method = environ.get("REQUEST_METHOD", "")
        user_agent = environ.get("HTTP_USER_AGENT", "")
        remote_addr = environ.get("REMOTE_ADDR", "")

        # Log request start with context
        with logging_context(request_id=request_id):
            self.logger.info(
                "request_started",
                path=path,
                method=method,
                user_agent=user_agent,
                remote_addr=remote_addr,
            )

        # Add request context to Flask g
        def custom_start_response(status, headers, exc_info=None):
            # Log response with context
            with logging_context(request_id=request_id):
                self.logger.info(
                    "request_completed",
                    path=path,
                    method=method,
                    status=status.split()[0],
                    response_time=time.time() - start_time,
                )
            return start_response(status, headers, exc_info)

        # Record start time for performance monitoring
        start_time = time.time()

        # Process request
        return self.app(environ, custom_start_response)


class ErrorHandlingMiddleware:
    """
    Middleware for centralized error handling

    Catches all exceptions and provides structured error responses
    with appropriate logging and context.
    """

    def __init__(self, app: Flask):
        self.app = app
        self.logger = get_logger(__name__)

    def __call__(self, environ, start_response):
        try:
            return self.app(environ, start_response)
        except Exception as e:
            # Get request context
            request_id = environ.get("request_id", "unknown")
            path = environ.get("PATH_INFO", "")
            method = environ.get("REQUEST_METHOD", "")

            # Log error with context
            with logging_context(request_id=request_id):
                self.logger.error(
                    "request_error",
                    path=path,
                    method=method,
                    error_type=type(e).__name__,
                    error_message=str(e),
                )

            # Handle error using centralized error handler
            response_data, status_code = HTTPErrorHandler.handle_exception(e)

            # Create response
            response_body = str(response_data)
            response_headers = [
                ("Content-Type", "application/json"),
                ("Content-Length", str(len(response_body))),
            ]

            start_response(f"{status_code} ERROR", response_headers)
            return [response_body.encode()]


class PerformanceMonitoringMiddleware:
    """
    Middleware for performance monitoring and metrics

    Tracks request duration, response sizes, and performance metrics
    for monitoring and alerting.
    """

    def __init__(self, app: Flask):
        self.app = app
        self.logger = get_performance_logger()

    def __call__(self, environ, start_response):
        start_time = time.time()
        request_id = environ.get("request_id", "unknown")

        # Track request start
        with logging_context(request_id=request_id):
            self.logger.debug("performance_monitoring_started")

        # Process request
        response = self.app(environ, start_response)

        # Calculate metrics
        duration = time.time() - start_time
        path = environ.get("PATH_INFO", "")
        method = environ.get("REQUEST_METHOD", "")

        # Log performance metrics
        with logging_context(request_id=request_id):
            self.logger.info(
                "request_performance",
                path=path,
                method=method,
                duration_ms=duration * 1000,
                duration_seconds=duration,
            )

        return response


class SecurityLoggingMiddleware:
    """
    Middleware for security event logging

    Logs security-relevant events like authentication failures,
    suspicious requests, and access patterns.
    """

    def __init__(self, app: Flask):
        self.app = app
        self.logger = get_security_logger()

    def __call__(self, environ, start_response):
        request_id = environ.get("request_id", "unknown")
        path = environ.get("PATH_INFO", "")
        method = environ.get("REQUEST_METHOD", "")
        remote_addr = environ.get("REMOTE_ADDR", "")
        user_agent = environ.get("HTTP_USER_AGENT", "")

        # Check for suspicious patterns
        suspicious_patterns = [
            "/admin",
            "/config",
            "/.env",
            "/wp-admin",
            "sqlmap",
            "nikto",
            "nmap",
            "dirb",
        ]

        is_suspicious = any(
            pattern in path.lower() or pattern in user_agent.lower()
            for pattern in suspicious_patterns
        )

        if is_suspicious:
            with logging_context(request_id=request_id):
                self.logger.warning(
                    "suspicious_request",
                    path=path,
                    method=method,
                    remote_addr=remote_addr,
                    user_agent=user_agent,
                )

        return self.app(environ, start_response)


def configure_middleware_stack(app: Flask) -> None:
    """
    Configure the complete middleware stack for the application

    Args:
        app: Flask application instance
    """
    logger = get_logger(__name__)

    logger.info("configuring_middleware_stack")

    # Import settings here to avoid circular imports
    from application.config.environment import settings

    # Apply middleware in order (last applied = first executed)
    app.wsgi_app = SecurityLoggingMiddleware(app.wsgi_app)
    app.wsgi_app = PerformanceMonitoringMiddleware(app.wsgi_app)
    app.wsgi_app = ErrorHandlingMiddleware(app.wsgi_app)
    app.wsgi_app = LoggingMiddleware(app.wsgi_app)

    # Rate limiting middleware (first in stack for early blocking)
    if settings.rate_limit.enabled:
        # Create a custom RateLimitMiddleware class with the configured parameters
        class ConfiguredRateLimitMiddleware(RateLimitMiddleware):
            def __init__(self, app):
                super().__init__(app)
                self.requests_per_second = settings.rate_limit.requests_per_second
                self.window_size = settings.rate_limit.window_size_seconds

        app.wsgi_app = ConfiguredRateLimitMiddleware(app.wsgi_app)
        logger.debug(
            "rate_limit_middleware_configured",
            requests_per_second=settings.rate_limit.requests_per_second,
            window_size=settings.rate_limit.window_size_seconds,
        )

    logger.info("middleware_stack_configured")
