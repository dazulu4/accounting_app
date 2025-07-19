"""
HTTP Middleware - Infrastructure Layer

This module provides enterprise-grade middleware for Flask applications,
including error handling, request logging, and security features.

Key Features:
- Automatic error handling and response formatting
- Request/response logging with context
- Request ID generation for tracing
- Security headers injection
- Performance monitoring
"""

import time
import uuid
from functools import wraps
from typing import Any, Callable, Optional

from flask import Flask, request, g, jsonify
from werkzeug.exceptions import HTTPException

from infrastructure.helpers.errors.error_handlers import HTTPErrorHandler
from infrastructure.helpers.logger.logger_config import get_logger, LoggingContext

logger = get_logger(__name__)


class ErrorHandlingMiddleware:
    """
    Middleware for automatic error handling in Flask applications
    
    Intercepts exceptions and converts them to appropriate HTTP responses
    using the HTTPErrorHandler.
    """
    
    def __init__(self, app: Optional[Flask] = None):
        """
        Initialize middleware
        
        Args:
            app: Flask application instance (optional)
        """
        self.app = app
        if app is not None:
            self.init_app(app)
    
    def init_app(self, app: Flask) -> None:
        """
        Initialize middleware with Flask app
        
        Args:
            app: Flask application instance
        """
        # Register error handlers for different exception types
        app.register_error_handler(Exception, self._handle_exception)
        app.register_error_handler(HTTPException, self._handle_http_exception)
        
        # Register before/after request handlers
        app.before_request(self._before_request)
        app.after_request(self._after_request)
        app.teardown_request(self._teardown_request)
    
    def _handle_exception(self, error: Exception):
        """Handle general exceptions"""
        logger.error(
            "unhandled_exception_caught_by_middleware",
            exception_type=type(error).__name__,
            exception_message=str(error),
            request_path=request.path,
            request_method=request.method
        )
        
        response_data, status_code = HTTPErrorHandler.handle_exception(error)
        return jsonify(response_data), status_code
    
    def _handle_http_exception(self, error: HTTPException):
        """Handle Werkzeug HTTP exceptions"""
        logger.warning(
            "http_exception_occurred",
            status_code=error.code,
            error_name=error.name,
            error_description=error.description,
            request_path=request.path,
            request_method=request.method
        )
        
        # Convert HTTPException to our standard format
        response_data = {
            "error": {
                "type": "HTTP_ERROR",
                "code": error.name.upper().replace(" ", "_"),
                "message": error.description or error.name,
                "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
                "path": request.path
            }
        }
        
        return jsonify(response_data), error.code
    
    def _before_request(self):
        """Execute before each request"""
        # Generate unique request ID for tracing
        request_id = str(uuid.uuid4())
        g.request_id = request_id
        g.start_time = time.time()
        
        # Add request ID to logging context
        g.logging_context = LoggingContext(request_id=request_id)
        g.logging_context.__enter__()
        
        # Log request start
        logger.info(
            "request_started",
            request_id=request_id,
            method=request.method,
            path=request.path,
            remote_addr=request.remote_addr,
            user_agent=request.headers.get("User-Agent", "")[:100]  # Truncate long user agents
        )
    
    def _after_request(self, response):
        """Execute after each request"""
        # Calculate request duration
        duration = time.time() - g.get('start_time', time.time())
        
        # Log request completion
        logger.info(
            "request_completed",
            request_id=g.get('request_id'),
            status_code=response.status_code,
            duration_ms=round(duration * 1000, 2),
            content_length=response.content_length
        )
        
        # Add security headers
        response = self._add_security_headers(response)
        
        # Add request ID to response headers for client tracing
        if hasattr(g, 'request_id'):
            response.headers['X-Request-ID'] = g.request_id
        
        return response
    
    def _teardown_request(self, exception=None):
        """Execute on request teardown"""
        # Clean up logging context
        if hasattr(g, 'logging_context'):
            try:
                g.logging_context.__exit__(None, None, None)
            except Exception as e:
                logger.warning("failed_to_cleanup_logging_context", error=str(e))
        
        # Log any teardown exceptions
        if exception:
            logger.error(
                "request_teardown_exception",
                request_id=g.get('request_id'),
                exception_type=type(exception).__name__,
                exception_message=str(exception)
            )
    
    def _add_security_headers(self, response):
        """Add security headers to response"""
        # Prevent clickjacking
        response.headers['X-Frame-Options'] = 'DENY'
        
        # Prevent MIME type sniffing
        response.headers['X-Content-Type-Options'] = 'nosniff'
        
        # Enable XSS protection
        response.headers['X-XSS-Protection'] = '1; mode=block'
        
        # Add Content Security Policy (basic)
        response.headers['Content-Security-Policy'] = "default-src 'self'"
        
        # Hide server information
        response.headers.pop('Server', None)
        
        return response


def log_endpoint_access(operation_name: str):
    """
    Decorator to log endpoint access with operation context
    
    Args:
        operation_name: Name of the business operation being performed
        
    Usage:
        @app.route('/api/tasks', methods=['POST'])
        @log_endpoint_access('create_task')
        def create_task():
            pass
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Log endpoint access
            logger.info(
                "endpoint_accessed",
                operation=operation_name,
                request_id=g.get('request_id'),
                method=request.method,
                path=request.path,
                endpoint=request.endpoint
            )
            
            try:
                # Execute endpoint function
                result = func(*args, **kwargs)
                
                # Log successful completion
                logger.info(
                    "endpoint_completed_successfully",
                    operation=operation_name,
                    request_id=g.get('request_id'),
                    status_code=getattr(result, 'status_code', 200) if hasattr(result, 'status_code') else 200
                )
                
                return result
                
            except Exception as e:
                # Log endpoint failure (will be handled by error middleware)
                logger.error(
                    "endpoint_failed",
                    operation=operation_name,
                    request_id=g.get('request_id'),
                    error_type=type(e).__name__,
                    error_message=str(e)
                )
                raise
        
        return wrapper
    return decorator


def require_json():
    """
    Decorator to require JSON content type for endpoints
    
    Usage:
        @app.route('/api/tasks', methods=['POST'])
        @require_json()
        def create_task():
            pass
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            if request.method in ['POST', 'PUT', 'PATCH']:
                if not request.is_json:
                    logger.warning(
                        "invalid_content_type_rejected",
                        request_id=g.get('request_id'),
                        content_type=request.content_type,
                        expected="application/json"
                    )
                    
                    from infrastructure.helpers.errors.error_handlers import create_validation_error_response
                    response_data, status_code = create_validation_error_response(
                        "Content-Type must be application/json"
                    )
                    return jsonify(response_data), status_code
            
            return func(*args, **kwargs)
        return wrapper
    return decorator


class PerformanceMonitoringMiddleware:
    """
    Middleware for monitoring application performance
    
    Tracks request duration, database query counts, and other metrics.
    """
    
    def __init__(self, app: Optional[Flask] = None):
        """Initialize performance monitoring"""
        self.app = app
        if app is not None:
            self.init_app(app)
    
    def init_app(self, app: Flask) -> None:
        """Initialize middleware with Flask app"""
        app.before_request(self._start_monitoring)
        app.after_request(self._end_monitoring)
    
    def _start_monitoring(self):
        """Start performance monitoring for request"""
        g.perf_start_time = time.time()
        g.perf_cpu_start = time.process_time()
    
    def _end_monitoring(self, response):
        """End performance monitoring and log metrics"""
        if not hasattr(g, 'perf_start_time'):
            return response
        
        # Calculate metrics
        total_time = time.time() - g.perf_start_time
        cpu_time = time.process_time() - g.get('perf_cpu_start', 0)
        
        # Log performance metrics
        logger.info(
            "request_performance_metrics",
            request_id=g.get('request_id'),
            total_time_ms=round(total_time * 1000, 2),
            cpu_time_ms=round(cpu_time * 1000, 2),
            status_code=response.status_code,
            endpoint=request.endpoint,
            method=request.method
        )
        
        # Add performance headers for debugging
        response.headers['X-Response-Time'] = f"{round(total_time * 1000, 2)}ms"
        
        # Warn on slow requests
        if total_time > 1.0:  # More than 1 second
            logger.warning(
                "slow_request_detected",
                request_id=g.get('request_id'),
                duration_ms=round(total_time * 1000, 2),
                endpoint=request.endpoint,
                threshold_ms=1000
            )
        
        return response 