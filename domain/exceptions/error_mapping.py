"""
Error Mapping Registry - Domain Layer

This module provides centralized error mapping for the entire application.
It serves as a single source of truth for mapping exceptions to HTTP status codes
and error types, following enterprise patterns and Clean Architecture principles.

Key Features:
- Centralized mapping for all exception types
- Hierarchical mapping (Business → Standard → Infrastructure → Default)
- Consistent error type definitions
- Easy maintenance and extension
"""

from typing import Tuple

from domain.exceptions.business_exceptions import (
    BusinessException,
    BusinessRuleViolationException,
    InvalidTaskTransitionException,
    MaxTasksExceededException,
    ResourceNotFoundException,
    TaskAlreadyCancelledException,
    TaskAlreadyCompletedException,
    TaskNotFoundException,
    TaskStateException,
    UserNotActiveException,
    UserNotFoundException,
    ValidationException,
)
from pydantic import ValidationError


class ErrorMappingRegistry:
    """
    Centralized error mapping registry
    
    Provides a single source of truth for mapping exceptions
    to HTTP status codes and error types.
    
    The mapping follows a hierarchical approach:
    1. Business exceptions (domain-specific)
    2. Standard Python exceptions
    3. Infrastructure exceptions
    4. Default fallback
    """

    # Business exceptions (from domain layer)
    BUSINESS_EXCEPTIONS = {
        ResourceNotFoundException: (404, "RESOURCE_NOT_FOUND"),
        TaskNotFoundException: (404, "TASK_NOT_FOUND"),
        UserNotFoundException: (404, "USER_NOT_FOUND"),
        ValidationException: (422, "VALIDATION_ERROR"),
        BusinessRuleViolationException: (422, "BUSINESS_RULE_VIOLATION"),
        UserNotActiveException: (422, "USER_NOT_ACTIVE"),
        MaxTasksExceededException: (422, "MAX_TASKS_EXCEEDED"),
        TaskStateException: (422, "RESOURCE_CONFLICT"),
        TaskAlreadyCompletedException: (422, "TASK_ALREADY_COMPLETED"),
        TaskAlreadyCancelledException: (422, "TASK_ALREADY_CANCELLED"),
        InvalidTaskTransitionException: (422, "INVALID_STATE_TRANSITION"),
    }
    
    # Standard Python exceptions
    STANDARD_EXCEPTIONS = {
        ValidationError: (400, "VALIDATION_ERROR"),
        ValueError: (400, "INVALID_REQUEST"),
        TypeError: (400, "INVALID_REQUEST"),
        KeyError: (400, "MISSING_REQUIRED_FIELD"),
        AttributeError: (400, "INVALID_ATTRIBUTE"),
        PermissionError: (403, "FORBIDDEN"),
        TimeoutError: (408, "REQUEST_TIMEOUT"),
        ConnectionError: (503, "SERVICE_UNAVAILABLE"),
    }
    
    # Infrastructure exceptions (to be defined in infrastructure layer)
    INFRASTRUCTURE_EXCEPTIONS = {
        # These will be imported from infrastructure layer
        # InfrastructureException: (500, "SERVICE_UNAVAILABLE"),
        # DatabaseException: (500, "DATABASE_ERROR"),
    }
    
    @classmethod
    def get_mapping(cls, exception: Exception) -> Tuple[int, str]:
        """
        Get HTTP status code and error type for an exception
        
        Args:
            exception: Exception to map
            
        Returns:
            Tuple of (status_code, error_type)
        """
        # Check business exceptions first
        if isinstance(exception, BusinessException):
            # Use exception's own status code and error code if available
            if hasattr(exception, 'http_status_code') and hasattr(exception, 'error_code'):
                return (exception.http_status_code, exception.error_code.value)
            
            # Fallback to registry mapping
            return cls.BUSINESS_EXCEPTIONS.get(
                type(exception), 
                (422, "BUSINESS_ERROR")
            )
        
        # Check standard exceptions
        exception_type = type(exception)
        if exception_type in cls.STANDARD_EXCEPTIONS:
            return cls.STANDARD_EXCEPTIONS[exception_type]
        
        # Check infrastructure exceptions
        if exception_type in cls.INFRASTRUCTURE_EXCEPTIONS:
            return cls.INFRASTRUCTURE_EXCEPTIONS[exception_type]
        
        # Default for unknown exceptions
        return (500, "INTERNAL_ERROR")
    
    @classmethod
    def register_infrastructure_exception(
        cls, 
        exception_type: type, 
        status_code: int, 
        error_type: str
    ) -> None:
        """
        Register an infrastructure exception type
        
        Args:
            exception_type: The exception class to register
            status_code: HTTP status code
            error_type: Error type identifier
        """
        cls.INFRASTRUCTURE_EXCEPTIONS[exception_type] = (status_code, error_type)
    
    @classmethod
    def get_all_mappings(cls) -> dict:
        """
        Get all registered mappings for debugging/testing
        
        Returns:
            Dict containing all mappings
        """
        return {
            "business": cls.BUSINESS_EXCEPTIONS,
            "standard": cls.STANDARD_EXCEPTIONS,
            "infrastructure": cls.INFRASTRUCTURE_EXCEPTIONS,
        } 