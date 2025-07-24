"""
Business Exceptions - Domain Layer

This module contains all business-related exceptions following enterprise patterns
with proper error codes, structured messages, and HTTP status code mapping.

Key Features:
- Hierarchical exception structure
- Error codes for external APIs
- HTTP status code mapping
- Structured error information
- I18n-ready error messages
"""

from typing import Optional, Dict, Any
from enum import Enum


class ErrorCodeEnum(str, Enum):
    """
    Enumeration of business error codes

    These codes provide stable identifiers for different types of business errors
    that can be used by external systems and for internationalization.
    """

    # Generic errors
    VALIDATION_ERROR = "VALIDATION_ERROR"
    BUSINESS_RULE_VIOLATION = "BUSINESS_RULE_VIOLATION"
    RESOURCE_NOT_FOUND = "RESOURCE_NOT_FOUND"
    RESOURCE_CONFLICT = "RESOURCE_CONFLICT"

    # User-related errors
    USER_NOT_FOUND = "USER_NOT_FOUND"
    USER_NOT_ACTIVE = "USER_NOT_ACTIVE"
    USER_SUSPENDED = "USER_SUSPENDED"

    # Task-related errors
    TASK_NOT_FOUND = "TASK_NOT_FOUND"
    TASK_ALREADY_COMPLETED = "TASK_ALREADY_COMPLETED"
    TASK_ALREADY_CANCELLED = "TASK_ALREADY_CANCELLED"
    INVALID_TASK_TRANSITION = "INVALID_TASK_TRANSITION"
    MAX_TASKS_EXCEEDED = "MAX_TASKS_EXCEEDED"
    TASK_ASSIGNMENT_FAILED = "TASK_ASSIGNMENT_FAILED"

    # Data validation errors
    INVALID_TITLE = "INVALID_TITLE"
    INVALID_DESCRIPTION = "INVALID_DESCRIPTION"
    INVALID_USER_ID = "INVALID_USER_ID"
    INVALID_TASK_ID = "INVALID_TASK_ID"
    INVALID_STATUS = "INVALID_STATUS"
    INVALID_PRIORITY = "INVALID_PRIORITY"


class BusinessException(Exception):
    """
    Base class for all business exceptions

    Provides common functionality for error handling including error codes,
    HTTP status mapping, and structured error information.
    """

    def __init__(
        self,
        message: str,
        error_code: ErrorCodeEnum,
        http_status_code: int = 400,
        details: Optional[Dict[str, Any]] = None,
        inner_exception: Optional[Exception] = None,
    ):
        """
        Initialize business exception

        Args:
            message: Human-readable error message
            error_code: Standardized error code
            http_status_code: HTTP status code for API responses
            details: Additional error details for debugging
            inner_exception: Original exception that caused this error
        """
        super().__init__(message)
        self.message = message
        self.error_code = error_code
        self.http_status_code = http_status_code
        self.details = details or {}
        self.inner_exception = inner_exception

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert exception to dictionary for serialization

        Returns:
            Dict containing error information
        """
        result = {
            "error_code": self.error_code.value,
            "message": self.message,
            "http_status_code": self.http_status_code,
        }

        if self.details:
            result["details"] = self.details

        if self.inner_exception:
            result["inner_error"] = str(self.inner_exception)

        return result

    def __str__(self) -> str:
        """String representation including error code"""
        return f"[{self.error_code.value}] {self.message}"


# =============================================================================
# VALIDATION EXCEPTIONS
# =============================================================================


class ValidationException(BusinessException):
    """Raised when input validation fails"""

    def __init__(
        self,
        message: str,
        field_name: Optional[str] = None,
        field_value: Optional[Any] = None,
        details: Optional[Dict[str, Any]] = None,
    ):
        validation_details = details or {}
        if field_name:
            validation_details["field_name"] = field_name
        if field_value is not None:
            validation_details["field_value"] = str(field_value)

        super().__init__(
            message=message,
            error_code=ErrorCodeEnum.VALIDATION_ERROR,
            http_status_code=422,  # Unprocessable Entity
            details=validation_details,
        )


class TaskValidationException(ValidationException):
    """Raised when task data validation fails"""

    pass


class UserValidationException(ValidationException):
    """Raised when user data validation fails"""

    pass


# =============================================================================
# RESOURCE NOT FOUND EXCEPTIONS
# =============================================================================


class ResourceNotFoundException(BusinessException):
    """Base class for resource not found errors"""

    def __init__(
        self, resource_type: str, resource_id: Any, message: Optional[str] = None
    ):
        default_message = f"{resource_type} with ID '{resource_id}' not found"
        super().__init__(
            message=message or default_message,
            error_code=ErrorCodeEnum.RESOURCE_NOT_FOUND,
            http_status_code=404,
            details={"resource_type": resource_type, "resource_id": str(resource_id)},
        )


class TaskNotFoundException(ResourceNotFoundException):
    """Raised when a task cannot be found"""

    def __init__(self, task_id: Any, message: Optional[str] = None):
        super().__init__(
            resource_type="Task",
            resource_id=task_id,
            message=message or f"Task with ID '{task_id}' not found",
        )
        self.error_code = ErrorCodeEnum.TASK_NOT_FOUND


class UserNotFoundException(ResourceNotFoundException):
    """Raised when a user cannot be found"""

    def __init__(self, user_id: Any, message: Optional[str] = None):
        super().__init__(
            resource_type="User",
            resource_id=user_id,
            message=message or f"User with ID '{user_id}' not found",
        )
        self.error_code = ErrorCodeEnum.USER_NOT_FOUND


# =============================================================================
# BUSINESS RULE VIOLATIONS
# =============================================================================


class BusinessRuleViolationException(BusinessException):
    """Base class for business rule violations"""

    def __init__(
        self, message: str, rule_name: str, details: Optional[Dict[str, Any]] = None
    ):
        business_details = details or {}
        business_details["violated_rule"] = rule_name

        super().__init__(
            message=message,
            error_code=ErrorCodeEnum.BUSINESS_RULE_VIOLATION,
            http_status_code=400,
            details=business_details,
        )


class UserNotActiveException(BusinessRuleViolationException):
    """Raised when trying to assign tasks to an inactive user"""

    def __init__(self, user_id: Any, user_status: str = "inactive"):
        super().__init__(
            message=f"Cannot assign task to user {user_id}: user is {user_status}",
            rule_name="active_user_assignment_rule",
            details={"user_id": str(user_id), "user_status": user_status},
        )
        self.error_code = ErrorCodeEnum.USER_NOT_ACTIVE


class MaxTasksExceededException(BusinessRuleViolationException):
    """Raised when user exceeds maximum allowed tasks"""

    def __init__(self, user_id: Any, current_count: int, max_allowed: int):
        super().__init__(
            message=f"User {user_id} has reached maximum task limit ({current_count}/{max_allowed})",
            rule_name="max_tasks_per_user_rule",
            details={
                "user_id": str(user_id),
                "current_task_count": current_count,
                "max_allowed_tasks": max_allowed,
            },
        )
        self.error_code = ErrorCodeEnum.MAX_TASKS_EXCEEDED


# =============================================================================
# TASK STATE EXCEPTIONS
# =============================================================================


class TaskStateException(BusinessException):
    """Base class for task state-related errors"""

    def __init__(
        self,
        message: str,
        task_id: Any,
        current_status: str,
        error_code: ErrorCodeEnum,
        details: Optional[Dict[str, Any]] = None,
    ):
        state_details = details or {}
        state_details.update(
            {"task_id": str(task_id), "current_status": current_status}
        )

        super().__init__(
            message=message,
            error_code=error_code,
            http_status_code=409,  # Conflict
            details=state_details,
        )


class TaskAlreadyCompletedException(TaskStateException):
    """Raised when trying to modify a completed task"""

    def __init__(self, task_id: Any, attempted_operation: str = "modify"):
        super().__init__(
            message=f"Cannot {attempted_operation} task {task_id}: task is already completed",
            task_id=task_id,
            current_status="completed",
            error_code=ErrorCodeEnum.TASK_ALREADY_COMPLETED,
            details={"attempted_operation": attempted_operation},
        )


class TaskAlreadyCancelledException(TaskStateException):
    """Raised when trying to modify a cancelled task"""

    def __init__(self, task_id: Any, attempted_operation: str = "modify"):
        super().__init__(
            message=f"Cannot {attempted_operation} task {task_id}: task is already cancelled",
            task_id=task_id,
            current_status="cancelled",
            error_code=ErrorCodeEnum.TASK_ALREADY_CANCELLED,
            details={"attempted_operation": attempted_operation},
        )


class InvalidTaskTransitionException(TaskStateException):
    """Raised when attempting an invalid status transition"""

    def __init__(
        self,
        task_id: Any,
        current_status: str,
        target_status: str,
        valid_transitions: Optional[list] = None,
    ):
        message = f"Cannot transition task {task_id} from '{current_status}' to '{target_status}'"
        details = {
            "target_status": target_status,
            "valid_transitions": valid_transitions or [],
        }

        super().__init__(
            message=message,
            task_id=task_id,
            current_status=current_status,
            error_code=ErrorCodeEnum.INVALID_TASK_TRANSITION,
            details=details,
        )


# =============================================================================
# INFRASTRUCTURE EXCEPTIONS
# =============================================================================


class InfrastructureException(BusinessException):
    """Base class for infrastructure-related errors"""

    def __init__(
        self,
        message: str,
        component: str,
        details: Optional[Dict[str, Any]] = None,
        inner_exception: Optional[Exception] = None,
    ):
        infra_details = details or {}
        infra_details["component"] = component

        super().__init__(
            message=message,
            error_code=ErrorCodeEnum.BUSINESS_RULE_VIOLATION,  # Generic for infrastructure
            http_status_code=500,  # Internal Server Error
            details=infra_details,
            inner_exception=inner_exception,
        )


class DatabaseException(InfrastructureException):
    """Raised when database operations fail"""

    def __init__(
        self,
        message: str,
        operation: str,
        details: Optional[Dict[str, Any]] = None,
        inner_exception: Optional[Exception] = None,
    ):
        db_details = details or {}
        db_details["operation"] = operation

        super().__init__(
            message=message,
            component="database",
            details=db_details,
            inner_exception=inner_exception,
        )


class ExternalServiceException(InfrastructureException):
    """Raised when external service calls fail"""

    def __init__(
        self,
        message: str,
        service_name: str,
        endpoint: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
        inner_exception: Optional[Exception] = None,
    ):
        service_details = details or {}
        service_details["service_name"] = service_name
        if endpoint:
            service_details["endpoint"] = endpoint

        super().__init__(
            message=message,
            component="external_service",
            details=service_details,
            inner_exception=inner_exception,
        )


# =============================================================================
# EXCEPTION UTILITIES
# =============================================================================


class ExceptionMapper:
    """
    Utility class for mapping exceptions to HTTP responses

    Provides centralized mapping of business exceptions to appropriate
    HTTP status codes and error response formats.
    """

    @staticmethod
    def get_http_status_code(exception: Exception) -> int:
        """
        Get appropriate HTTP status code for an exception

        Args:
            exception: Exception instance

        Returns:
            int: HTTP status code
        """
        if isinstance(exception, BusinessException):
            return exception.http_status_code

        # Default mapping for common exceptions
        exception_mapping = {
            ValueError: 400,
            TypeError: 400,
            KeyError: 404,
            PermissionError: 403,
            TimeoutError: 408,
            ConnectionError: 503,
        }

        return exception_mapping.get(type(exception), 500)

    @staticmethod
    def exception_to_error_response(exception: Exception) -> Dict[str, Any]:
        """
        Convert exception to standardized error response

        Args:
            exception: Exception instance

        Returns:
            Dict: Standardized error response
        """
        if isinstance(exception, BusinessException):
            return {
                "error": exception.to_dict(),
                "timestamp": None,  # Will be set by the API layer
                "path": None,  # Will be set by the API layer
            }

        # Handle non-business exceptions
        return {
            "error": {
                "error_code": "INTERNAL_ERROR",
                "message": str(exception),
                "http_status_code": ExceptionMapper.get_http_status_code(exception),
            },
            "timestamp": None,
            "path": None,
        }
