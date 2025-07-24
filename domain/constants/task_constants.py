"""
Task Domain Constants

This module contains all constants related to task management domain.
Constants are defined using class-based organization for better maintainability.
"""

from typing import Final


class TaskConstants:
    """Constants for task entity and business rules"""

    # Task field limits
    TITLE_MIN_LENGTH: Final[int] = 1
    TITLE_MAX_LENGTH: Final[int] = 200
    DESCRIPTION_MIN_LENGTH: Final[int] = 1
    DESCRIPTION_MAX_LENGTH: Final[int] = 1000

    # Task business rules
    MAX_TASKS_PER_USER: Final[int] = 1000
    TASK_COMPLETION_TIMEOUT_DAYS: Final[int] = 365

    # Default values
    DEFAULT_STATUS: Final[str] = "pending"
    DEFAULT_PRIORITY: Final[str] = "medium"


class TaskValidationMessages:
    """Validation error messages for task operations"""

    # Title validation messages
    TITLE_REQUIRED: Final[str] = "Task title is required"
    TITLE_TOO_SHORT: Final[str] = (
        f"Task title must be at least {TaskConstants.TITLE_MIN_LENGTH} character long"
    )
    TITLE_TOO_LONG: Final[str] = (
        f"Task title cannot exceed {TaskConstants.TITLE_MAX_LENGTH} characters"
    )

    # Description validation messages
    DESCRIPTION_REQUIRED: Final[str] = "Task description is required"
    DESCRIPTION_TOO_SHORT: Final[str] = (
        f"Task description must be at least {TaskConstants.DESCRIPTION_MIN_LENGTH} character long"
    )
    DESCRIPTION_TOO_LONG: Final[str] = (
        f"Task description cannot exceed {TaskConstants.DESCRIPTION_MAX_LENGTH} characters"
    )

    # Business rule validation messages
    USER_INACTIVE: Final[str] = "Cannot assign task to inactive user"
    USER_NOT_FOUND: Final[str] = "User not found"
    TASK_NOT_FOUND: Final[str] = "Task not found"
    TASK_ALREADY_COMPLETED: Final[str] = "Task is already completed"
    INVALID_STATUS_TRANSITION: Final[str] = "Invalid status transition"
    MAX_TASKS_EXCEEDED: Final[str] = (
        f"User cannot have more than {TaskConstants.MAX_TASKS_PER_USER} active tasks"
    )


class TaskDatabaseConstants:
    """Database-related constants for task operations"""

    # Table and column names
    TABLE_NAME: Final[str] = "tasks"

    # Primary key
    TASK_ID_COLUMN: Final[str] = "task_id"

    # Required columns
    TITLE_COLUMN: Final[str] = "title"
    DESCRIPTION_COLUMN: Final[str] = "description"
    USER_ID_COLUMN: Final[str] = "user_id"
    STATUS_COLUMN: Final[str] = "status"
    CREATED_AT_COLUMN: Final[str] = "created_at"

    # Optional columns
    COMPLETED_AT_COLUMN: Final[str] = "completed_at"
    UPDATED_AT_COLUMN: Final[str] = "updated_at"

    # Index names
    USER_ID_INDEX: Final[str] = "idx_tasks_user_id"
    STATUS_INDEX: Final[str] = "idx_tasks_status"
    CREATED_AT_INDEX: Final[str] = "idx_tasks_created_at"


class TransactionConstants:
    """Constants for database transaction management"""

    # Transaction timeouts (in seconds)
    DEFAULT_TIMEOUT: Final[int] = 30
    SHORT_TIMEOUT: Final[int] = 10
    LONG_TIMEOUT: Final[int] = 60

    # Isolation levels
    READ_COMMITTED: Final[str] = "READ_COMMITTED"
    READ_UNCOMMITTED: Final[str] = "READ_UNCOMMITTED"
    REPEATABLE_READ: Final[str] = "REPEATABLE_READ"
    SERIALIZABLE: Final[str] = "SERIALIZABLE"

    # Retry configuration
    MAX_RETRY_ATTEMPTS: Final[int] = 3
    RETRY_DELAY_SECONDS: Final[int] = 1
    BACKOFF_MULTIPLIER: Final[float] = 2.0
