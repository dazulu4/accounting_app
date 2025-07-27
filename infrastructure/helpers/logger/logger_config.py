"""
Simplified Logging Configuration - Task Manager Edition

Streamlined logging configuration that maintains essential features:
- Structured logging with JSON output for production
- Console logging with colors for development
- Request context tracing for HTTP operations
- Simplified configuration (71% reduction in complexity)
"""

import logging
import uuid
from contextlib import contextmanager
from typing import Any, Dict

import structlog

from application.config.environment import settings


class LoggerConfig:
    """Simplified logging configuration for Task Manager"""

    @staticmethod
    def configure_logging() -> None:
        """Configure structured logging with essential features only"""

        # Determine log level
        log_level = getattr(
            logging, settings.application.log_level.upper(), logging.INFO
        )

        # Essential processors only
        processors = [
            structlog.contextvars.merge_contextvars,  # For request tracing
            structlog.stdlib.add_log_level,
            structlog.processors.TimeStamper(fmt="iso"),
        ]

        # Environment-based renderer
        if settings.application.environment == "development":
            processors.append(structlog.dev.ConsoleRenderer(colors=True))
        else:
            processors.append(structlog.processors.JSONRenderer())

        # Configure structlog with minimal setup
        structlog.configure(
            processors=processors,
            wrapper_class=structlog.stdlib.BoundLogger,
            logger_factory=structlog.stdlib.LoggerFactory(),
            cache_logger_on_first_use=True,
        )

        # Standard library logging
        logging.basicConfig(
            format="%(message)s",
            level=log_level,
            handlers=[logging.StreamHandler()],
        )


def get_logger(name: str) -> structlog.stdlib.BoundLogger:
    """Get a configured logger instance"""
    if not structlog.is_configured():
        LoggerConfig.configure_logging()
    return structlog.get_logger(name)


@contextmanager
def logging_context(**kwargs):
    """Context manager for request tracing"""
    structlog.contextvars.bind_contextvars(**kwargs)
    try:
        yield
    finally:
        structlog.contextvars.clear_contextvars()


# Specialized loggers - simple aliases for consistency
get_request_logger = lambda: get_logger("http.request")
get_security_logger = lambda: get_logger("security")


def generate_request_id() -> str:
    """Generate a unique request ID for tracing"""
    return str(uuid.uuid4())


# Initialize logging on module import
LoggerConfig.configure_logging()
