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
- Request ID and context tracking
"""

import uuid
from datetime import datetime, timezone
from typing import Any, Dict, Optional, Tuple

from flask import current_app, request
from pydantic import ValidationError

from domain.exceptions.business_exceptions import (
    BusinessException,
    DatabaseException,
    InfrastructureException,
)
from domain.exceptions.error_mapping import ErrorMappingRegistry
from infrastructure.helpers.logger.logger_config import get_logger

logger = get_logger(__name__)

# Register infrastructure exceptions with the centralized registry
ErrorMappingRegistry.register_infrastructure_exception(
    DatabaseException, 500, "DATABASE_ERROR"
)
ErrorMappingRegistry.register_infrastructure_exception(
    InfrastructureException, 503, "SERVICE_UNAVAILABLE"
)


class HTTPErrorHandler:
    """
    Enterprise HTTP error handler

    Maps business exceptions to appropriate HTTP responses with
    consistent error format and proper status codes.
    """

    """
    Enterprise HTTP error handler
    
    Uses centralized error mapping from domain layer.
    Maps business exceptions to appropriate HTTP responses with
    consistent error format and proper status codes.
    """

    @classmethod
    def handle_exception(cls, exception: Exception) -> Tuple[Dict[str, Any], int]:
        """
        Handle exception using centralized mapping from domain layer

        Args:
            exception: Exception to handle

        Returns:
            Tuple of (response_dict, status_code)
        """
        # Log the exception with context
        cls._log_exception(exception)

        # Logging adicional para depuración
        logger.info(
            "handling_exception",
            exception_type=type(exception).__name__,
            exception_class=exception.__class__.__name__,
            module=getattr(exception, "__module__", "unknown"),
        )

        # Handle Pydantic validation errors specially (detailed field errors)
        if (
            isinstance(exception, ValidationError)
            or exception.__class__.__name__ == "ValidationError"
        ):
            return cls._handle_validation_error(exception)

        # Get mapping from centralized registry
        status_code, error_type = ErrorMappingRegistry.get_mapping(exception)

        # Get exception details for development environment
        details = cls._get_exception_details(exception)

        # Use centralized error response creation
        response_data, status_code = create_error_response(
            error_type=error_type,
            error_code=error_type,
            message=cls._get_safe_error_message(exception, status_code),
            status_code=status_code,
            details=details,
        )

        # For backward compatibility with tests, add exception details directly to error
        if details and cls._should_include_details():
            response_data["error"].update(details)

        return response_data, status_code

    @classmethod
    def _handle_validation_error(
        cls, exception: Exception
    ) -> Tuple[Dict[str, Any], int]:
        """Handle Pydantic validation errors with detailed field information"""
        # Get request context
        request_id = get_request_id()
        path = request.path if request else None
        method = request.method if request else None

        # Extract field errors from Pydantic validation error
        field_errors = {}
        if hasattr(exception, "errors") and callable(
            getattr(exception, "errors", None)
        ):
            try:
                for error in exception.errors():
                    field_name = " -> ".join(str(loc) for loc in error["loc"])
                    field_errors[field_name] = error["msg"]
            except Exception as e:
                logger.error(f"Error extracting validation errors: {e}")
                field_errors["general"] = str(exception)
        else:
            field_errors["general"] = str(exception)

        # Create main error message
        if field_errors:
            main_message = "Validation failed for the following fields: " + ", ".join(
                field_errors.keys()
            )
        else:
            main_message = "The request data is invalid"

        # Use centralized error response creation
        return create_error_response(
            error_type="VALIDATION_ERROR",
            error_code="VALIDATION_ERROR",
            message=main_message,
            status_code=400,
            details={"field_errors": field_errors},
        )

    @classmethod
    def _get_exception_details(cls, exception: Exception) -> Optional[Dict[str, Any]]:
        """
        Get exception details for development environment

        Args:
            exception: Exception to get details for

        Returns:
            Optional dict with exception details
        """
        if not cls._should_include_details():
            return None

        details = {}
        if isinstance(exception, BusinessException):
            details = exception.details or {}
            if hasattr(exception, "inner_exception") and exception.inner_exception:
                details["inner_error"] = str(exception.inner_exception)
        else:
            details = {
                "exception_type": type(exception).__name__,
                "exception_message": str(exception),
            }

        return details if details else None

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
        request_id = get_request_id()

        error_context = {
            "exception_type": type(exception).__name__,
            "exception_message": str(exception),
            "request_path": request.path if request else None,
            "request_method": request.method if request else None,
            "request_id": request_id,
        }

        # Add user context if available
        if request and hasattr(request, "user_id"):
            error_context["user_id"] = request.user_id

        if isinstance(exception, BusinessException):
            # Business exceptions are expected and logged as warnings
            logger.warning(
                "business_exception_occurred",
                **error_context,
                error_code=(
                    exception.error_code.value
                    if hasattr(exception, "error_code")
                    else "UNKNOWN"
                ),
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

    def with_type(self, error_type: str) -> "ErrorResponseBuilder":
        """Set error type"""
        self._error_type = error_type
        return self

    def with_code(self, error_code: str) -> "ErrorResponseBuilder":
        """Set error code"""
        self._error_code = error_code
        return self

    def with_message(self, message: str) -> "ErrorResponseBuilder":
        """Set error message"""
        self._message = message
        return self

    def with_details(self, details: Dict[str, Any]) -> "ErrorResponseBuilder":
        """Set error details"""
        self._details = details
        return self

    def with_status_code(self, status_code: int) -> "ErrorResponseBuilder":
        """Set HTTP status code"""
        self._status_code = status_code
        return self

    def build(self) -> Tuple[Dict[str, Any], int]:
        """Build the error response"""
        if not self._error_type or not self._message:
            raise ValueError("Error type and message are required")

        # Get request context
        request_id = get_request_id()
        path = request.path if request else None
        method = request.method if request else None

        response = {
            "error": {
                "type": self._error_type,
                "code": self._error_code or self._error_type,
                "message": self._message,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "request_id": request_id,
                "path": path,
                "method": method,
            }
        }

        if self._details:
            response["error"]["details"] = self._details

        return response, self._status_code


def create_validation_error_response(
    message: str, field_errors: Optional[Dict[str, str]] = None
) -> Tuple[Dict[str, Any], int]:
    """
    Create a standardized validation error response

    Args:
        message: Main error message
        field_errors: Dictionary of field-specific errors

    Returns:
        Tuple of (response_dict, status_code)
    """
    builder = (
        ErrorResponseBuilder()
        .with_type("VALIDATION_ERROR")
        .with_message(message)
        .with_status_code(422)  # Mantener 422 para compatibilidad con tests
    )

    if field_errors:
        builder.with_details({"field_errors": field_errors})

    return builder.build()


def create_not_found_error_response(
    resource_type: str, resource_id: Any
) -> Tuple[Dict[str, Any], int]:
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
        .with_details({"resource_type": resource_type, "resource_id": str(resource_id)})
        .build()
    )


def create_error_response(
    error_type: str,
    error_code: str,
    message: str,
    status_code: int,
    details: Optional[Dict[str, Any]] = None,
    include_request_context: bool = True,
) -> Tuple[Dict[str, Any], int]:
    """
    Create a standardized error response with consistent JSON structure.

    Args:
        error_type: Type of error (e.g., "VALIDATION_ERROR", "NOT_FOUND")
        error_code: Error code for client consumption
        message: Human-readable error message
        status_code: HTTP status code
        details: Optional additional error details
        include_request_context: Whether to include request context (path, method, request_id)

    Returns:
        Tuple of (response_dict, status_code)
    """
    # Get request context if needed
    request_id = None
    path = None
    method = None

    if include_request_context and request:
        request_id = get_request_id()
        path = request.path
        method = request.method

    # Build response structure
    response = {
        "error": {
            "type": error_type,
            "code": error_code,
            "message": message,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
    }

    # Add request context if available (always include, even if None for tests)
    response["error"]["request_id"] = request_id
    response["error"]["path"] = path
    response["error"]["method"] = method

    # Add details if provided
    if details:
        response["error"]["details"] = details

    return response, status_code


def get_request_id() -> Optional[str]:
    """
    Get or generate request ID for tracking purposes.

    Returns:
        Request ID string if available, None otherwise
    """
    if not request:
        return None

    # Try to get existing request ID
    if hasattr(request, "request_id"):
        return request.request_id

    # Generate new request ID if not exists
    request_id = str(uuid.uuid4())
    request.request_id = request_id
    return request_id
