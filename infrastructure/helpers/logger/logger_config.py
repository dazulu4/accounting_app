"""
Structured Logging Configuration - Enterprise Edition

This module provides enterprise-grade logging configuration using structlog
with environment-aware settings, context management, and strategic logging.

Key Features:
- Structured logging with JSON output for production
- Console logging with colors for development
- Context variables for request tracing
- Log level configuration from environment
- Performance-optimized logging
"""

import logging
import logging.config
import structlog
from contextlib import contextmanager
from typing import Any, Dict, Optional
from dataclasses import dataclass

from application.config.environment import settings


@dataclass
class LoggingContext:
    """
    Context manager for logging variables
    
    Allows adding context variables to all logs within a scope.
    """
    request_id: Optional[str] = None
    user_id: Optional[str] = None
    operation: Optional[str] = None
    
    def __enter__(self):
        """Enter context and bind variables"""
        if self.request_id:
            structlog.contextvars.bind_contextvars(request_id=self.request_id)
        if self.user_id:
            structlog.contextvars.bind_contextvars(user_id=self.user_id)
        if self.operation:
            structlog.contextvars.bind_contextvars(operation=self.operation)
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Exit context and clear variables"""
        structlog.contextvars.clear_contextvars()


class LoggerConfig:
    """
    Enterprise logging configuration manager
    
    Configures structured logging based on environment settings
    with appropriate processors and formatters.
    """
    
    @staticmethod
    def configure_logging() -> None:
        """
        Configure structured logging for the application
        
        Uses environment variables to determine log level and format:
        - Development: Console output with colors
        - Production: JSON output for log aggregation
        """
        # Determine log level
        log_level = getattr(logging, settings.application.log_level.upper(), logging.INFO)
        
        # Configure processors based on environment
        processors = [
            structlog.contextvars.merge_contextvars,
            structlog.stdlib.filter_by_level,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
        ]
        
        # Add appropriate renderer based on environment
        if settings.application.environment == "development":
            # Development: colored console output
            processors.append(structlog.dev.ConsoleRenderer(colors=True))
        else:
            # Production: JSON output
            processors.append(structlog.processors.JSONRenderer())
        
        # Configure structlog
        structlog.configure(
            processors=processors,
            wrapper_class=structlog.stdlib.BoundLogger,
            logger_factory=structlog.stdlib.LoggerFactory(),
            context_class=dict,
            cache_logger_on_first_use=True,
        )
        
        # Configure standard library logging
        logging.basicConfig(
            format="%(message)s",
            level=log_level,
            handlers=[logging.StreamHandler()],
        )
    
    @staticmethod
    def get_logger_config() -> Dict[str, Any]:
        """
        Get logging configuration dictionary
        
        Returns:
            Dictionary with logging configuration
        """
        return {
            "log_level": settings.application.log_level,
            "environment": settings.application.environment,
            "format": "json" if settings.application.environment != "development" else "console"
        }


def get_logger(name: str) -> structlog.stdlib.BoundLogger:
    """
    Get a configured logger instance
    
    Args:
        name: Logger name (typically __name__)
        
    Returns:
        Configured structlog logger
    """
    # Ensure logging is configured
    if not structlog.is_configured():
        LoggerConfig.configure_logging()
    
    return structlog.get_logger(name)


@contextmanager
def logging_context(**kwargs):
    """
    Context manager for temporary logging context
    
    Usage:
        with logging_context(request_id="123", user_id="456"):
            logger.info("This will include context variables")
    
    Args:
        **kwargs: Context variables to bind
    """
    # Bind context variables
    structlog.contextvars.bind_contextvars(**kwargs)
    
    try:
        yield
    finally:
        # Clear context variables
        structlog.contextvars.clear_contextvars()


def configure_performance_logging():
    """
    Configure additional performance logging
    
    Sets up specific loggers for performance monitoring
    and database query logging.
    """
    # Configure SQLAlchemy logging for development
    if settings.application.environment == "development":
        sqlalchemy_logger = logging.getLogger('sqlalchemy.engine')
        sqlalchemy_logger.setLevel(logging.INFO)
    
    # Configure performance logger
    perf_logger = logging.getLogger('performance')
    perf_logger.setLevel(logging.INFO)


def log_function_call(func_name: str, **kwargs):
    """
    Decorator to log function calls with parameters
    
    Args:
        func_name: Name of the function being called
        **kwargs: Additional context to log
    """
    def decorator(func):
        def wrapper(*args, **func_kwargs):
            logger = get_logger(func.__module__)
            
            # Log function entry
            logger.debug(
                "function_called",
                function=func_name,
                args_count=len(args),
                kwargs_count=len(func_kwargs),
                **kwargs
            )
            
            try:
                result = func(*args, **func_kwargs)
                
                # Log successful completion
                logger.debug(
                    "function_completed",
                    function=func_name,
                    **kwargs
                )
                
                return result
                
            except Exception as e:
                # Log function error
                logger.error(
                    "function_failed",
                    function=func_name,
                    error_type=type(e).__name__,
                    error_message=str(e),
                    **kwargs
                )
                raise
        
        return wrapper
    return decorator


# Initialize logging on module import
LoggerConfig.configure_logging() 