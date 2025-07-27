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
