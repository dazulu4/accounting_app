"""
HTTP Error Handlers - Infrastructure Layer

This module provides enterprise-grade error handling for HTTP requests,
mapping business exceptions to appropriate HTTP status codes and structured responses.

Key Features:
- Business exception to HTTP status code mapping
- Structured error response format
- Security-conscious error information disclosure
- Logging integration for error tracking
- Support for development vs production error details
"""

from datetime import datetime, timezone
from typing import Dict, Any, Tuple, Type, Optional
from flask import request, current_app

from domain.exceptions.business_exceptions import (
    BusinessException,
    ValidationException,
    ResourceNotFoundException,
    BusinessRuleViolationException,
    TaskStateException,
    InfrastructureException,
    UserNotFoundException,
    TaskNotFoundException,
    UserNotActiveException,
    MaxTasksExceededException,
    TaskAlreadyCompletedException,
    TaskAlreadyCancelledException,
    InvalidTaskTransitionException,
    DatabaseException,
    ExternalServiceException
)
from infrastructure.helpers.logger.logger_config import get_logger

logger = get_logger(__name__)


class HTTPErrorHandler:
    """
    Enterprise HTTP error handler
    
    Maps business exceptions to appropriate HTTP responses with
    consistent error format and proper status codes.
    """
    
    # Mapping of exception types to HTTP status codes and error types
    ERROR_MAPPINGS = {
        # Validation errors
        ValidationException: (422, "VALIDATION_ERROR"),
        
        # Resource not found errors
        ResourceNotFoundException: (404, "RESOURCE_NOT_FOUND"),
        TaskNotFoundException: (404, "TASK_NOT_FOUND"),
        UserNotFoundException: (404, "USER_NOT_FOUND"),
        
        # Business rule violations
        BusinessRuleViolationException: (400, "BUSINESS_RULE_VIOLATION"),
        UserNotActiveException: (400, "USER_NOT_ACTIVE"),
        MaxTasksExceededException: (400, "MAX_TASKS_EXCEEDED"),
        
        # State conflicts
        TaskStateException: (409, "RESOURCE_CONFLICT"),
        TaskAlreadyCompletedException: (409, "TASK_ALREADY_COMPLETED"),
        TaskAlreadyCancelledException: (409, "TASK_ALREADY_CANCELLED"),
        InvalidTaskTransitionException: (409, "INVALID_STATE_TRANSITION"),
        
        # Infrastructure errors
        InfrastructureException: (503, "SERVICE_UNAVAILABLE"),
        DatabaseException: (503, "DATABASE_ERROR"),
        ExternalServiceException: (502, "EXTERNAL_SERVICE_ERROR"),
    }
    
    @classmethod
    def handle_exception(cls, exception: Exception) -> Tuple[Dict[str, Any], int]:
        """
        Handle exception and return appropriate HTTP response
        
        Args:
            exception: Exception to handle
            
        Returns:
            Tuple of (response_dict, status_code)
        """
        # Log the exception with context
        cls._log_exception(exception)
        
        # Handle business exceptions
        if isinstance(exception, BusinessException):
            return cls._handle_business_exception(exception)
        
        # Handle unknown exceptions
        return cls._handle_unknown_exception(exception)
    
    @classmethod
    def _handle_business_exception(cls, exception: BusinessException) -> Tuple[Dict[str, Any], int]:
        """Handle known business exceptions"""
        status_code, error_type = cls.ERROR_MAPPINGS.get(
            type(exception),
            (400, "BUSINESS_ERROR")
        )
        
        response = {
            "error": {
                "type": error_type,
                "code": exception.error_code.value if hasattr(exception, 'error_code') else error_type,
                "message": str(exception),
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "path": request.path if request else None
            }
        }
        
        # Add details for development environment
        if cls._should_include_details():
            response["error"]["details"] = exception.details if hasattr(exception, 'details') else {}
            
            if hasattr(exception, 'inner_exception') and exception.inner_exception:
                response["error"]["inner_error"] = str(exception.inner_exception)
        
        return response, status_code
    
    @classmethod
    def _handle_unknown_exception(cls, exception: Exception) -> Tuple[Dict[str, Any], int]:
        """Handle unknown exceptions with appropriate security measures"""
        # Default mapping for common Python exceptions
        exception_mapping = {
            ValueError: (400, "INVALID_REQUEST"),
            TypeError: (400, "INVALID_REQUEST"),
            KeyError: (400, "MISSING_REQUIRED_FIELD"),
            PermissionError: (403, "FORBIDDEN"),
            TimeoutError: (408, "REQUEST_TIMEOUT"),
            ConnectionError: (503, "SERVICE_UNAVAILABLE"),
        }
        
        status_code, error_type = exception_mapping.get(type(exception), (500, "INTERNAL_ERROR"))
        
        # Create safe error response
        response = {
            "error": {
                "type": error_type,
                "code": error_type,
                "message": cls._get_safe_error_message(exception, status_code),
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "path": request.path if request else None
            }
        }
        
        # Add technical details only in development
        if cls._should_include_details():
            response["error"]["exception_type"] = type(exception).__name__
            response["error"]["exception_message"] = str(exception)
        
        return response, status_code
    
    @classmethod
    def _get_safe_error_message(cls, exception: Exception, status_code: int) -> str:
        """Get safe error message that doesn't expose internal details"""
        if status_code >= 500:
            # Don't expose internal error details to clients
            return "An internal server error occurred. Please try again later."
        
        # For client errors, we can be more specific
        safe_messages = {
            ValueError: "The request contains invalid data.",
            TypeError: "The request format is incorrect.",
            KeyError: "A required field is missing from the request.",
            PermissionError: "You don't have permission to perform this action.",
            TimeoutError: "The request timed out. Please try again.",
            ConnectionError: "The service is temporarily unavailable.",
        }
        
        return safe_messages.get(type(exception), str(exception))
    
    @classmethod
    def _should_include_details(cls) -> bool:
        """Determine if detailed error information should be included"""
        try:
            # Include details in development or when explicitly configured
            return current_app.debug if current_app else False
        except RuntimeError:
            # Outside application context
            return False
    
    @classmethod
    def _log_exception(cls, exception: Exception) -> None:
        """Log exception with appropriate level and context"""
        error_context = {
            "exception_type": type(exception).__name__,
            "exception_message": str(exception),
            "request_path": request.path if request else None,
            "request_method": request.method if request else None,
        }
        
        # Add request ID if available
        if request and hasattr(request, 'request_id'):
            error_context["request_id"] = request.request_id
        
        # Add user context if available
        if request and hasattr(request, 'user_id'):
            error_context["user_id"] = request.user_id
        
        if isinstance(exception, BusinessException):
            # Business exceptions are expected and logged as warnings
            logger.warning(
                "business_exception_occurred",
                **error_context,
                error_code=exception.error_code.value if hasattr(exception, 'error_code') else 'UNKNOWN'
            )
        elif isinstance(exception, (ValueError, TypeError, KeyError)):
            # Client errors logged as warnings
            logger.warning("client_error_occurred", **error_context)
        else:
            # Unexpected errors logged as errors
            logger.error("unexpected_error_occurred", **error_context)


class ErrorResponseBuilder:
    """
    Builder for creating consistent error responses
    
    Provides a fluent interface for building error responses
    with validation and consistency checks.
    """
    
    def __init__(self):
        self._error_type: Optional[str] = None
        self._error_code: Optional[str] = None
        self._message: Optional[str] = None
        self._details: Dict[str, Any] = {}
        self._status_code: int = 500
    
    def with_type(self, error_type: str) -> 'ErrorResponseBuilder':
        """Set error type"""
        self._error_type = error_type
        return self
    
    def with_code(self, error_code: str) -> 'ErrorResponseBuilder':
        """Set error code"""
        self._error_code = error_code
        return self
    
    def with_message(self, message: str) -> 'ErrorResponseBuilder':
        """Set error message"""
        self._message = message
        return self
    
    def with_details(self, details: Dict[str, Any]) -> 'ErrorResponseBuilder':
        """Set error details"""
        self._details = details
        return self
    
    def with_status_code(self, status_code: int) -> 'ErrorResponseBuilder':
        """Set HTTP status code"""
        self._status_code = status_code
        return self
    
    def build(self) -> Tuple[Dict[str, Any], int]:
        """Build the error response"""
        if not self._error_type or not self._message:
            raise ValueError("Error type and message are required")
        
        response = {
            "error": {
                "type": self._error_type,
                "code": self._error_code or self._error_type,
                "message": self._message,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "path": request.path if request else None
            }
        }
        
        if self._details:
            response["error"]["details"] = self._details
        
        return response, self._status_code


def create_validation_error_response(
    message: str,
    field_errors: Optional[Dict[str, str]] = None
) -> Tuple[Dict[str, Any], int]:
    """
    Create a standardized validation error response
    
    Args:
        message: Main error message
        field_errors: Dictionary of field-specific errors
        
    Returns:
        Tuple of (response_dict, status_code)
    """
    builder = ErrorResponseBuilder().with_type("VALIDATION_ERROR").with_message(message).with_status_code(422)
    
    if field_errors:
        builder.with_details({"field_errors": field_errors})
    
    return builder.build()


def create_not_found_error_response(resource_type: str, resource_id: Any) -> Tuple[Dict[str, Any], int]:
    """
    Create a standardized not found error response
    
    Args:
        resource_type: Type of resource that was not found
        resource_id: ID of the resource
        
    Returns:
        Tuple of (response_dict, status_code)
    """
    return (
        ErrorResponseBuilder()
        .with_type("RESOURCE_NOT_FOUND")
        .with_message(f"{resource_type} with ID '{resource_id}' not found")
        .with_status_code(404)
        .with_details({
            "resource_type": resource_type,
            "resource_id": str(resource_id)
        })
        .build()
    ) 