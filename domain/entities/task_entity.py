"""
Task Entity - Domain Model

Simplified task entity using Pydantic for consistency with UserEntity
and following Domain-Driven Design principles.

Key Features:
- Pydantic BaseModel for automatic validation and serialization
- State transition validation using TaskStatusEnum
- Business rule validation with centralized exceptions
- Consistent with UserEntity design
"""

from datetime import datetime, timezone
from typing import Optional
from uuid import UUID, uuid4

from pydantic import BaseModel, Field, field_validator

from domain.constants.task_constants import TaskConstants
from domain.enums.task_status_enum import TaskPriorityEnum, TaskStatusEnum
from domain.exceptions.business_exceptions import (
    InvalidTaskTransitionException,
    TaskAlreadyCancelledException,
    TaskAlreadyCompletedException,
)


class TaskEntity(BaseModel):
    """
    Task entity representing a work item in the accounting system

    This entity encapsulates all business logic related to task management
    including state transitions, validation, and business rules.
    """

    task_id: UUID = Field(
        default_factory=uuid4, description="Unique identifier for the task"
    )
    title: str = Field(..., min_length=1, max_length=200, description="Task title")
    description: str = Field(
        ..., min_length=1, max_length=1000, description="Task description"
    )
    user_id: int = Field(..., gt=0, description="ID of the user assigned to this task")
    status: TaskStatusEnum = Field(
        default=TaskStatusEnum.PENDING, description="Current task status"
    )
    priority: TaskPriorityEnum = Field(
        default=TaskPriorityEnum.MEDIUM, description="Task priority"
    )
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="Creation timestamp",
    )
    completed_at: Optional[datetime] = Field(
        default=None, description="Completion timestamp"
    )
    updated_at: Optional[datetime] = Field(
        default=None, description="Last update timestamp"
    )

    @field_validator("title")
    @classmethod
    def validate_title(cls, v: str) -> str:
        """Validate and clean task title"""
        if not v.strip():
            raise ValueError("Task title cannot be empty or whitespace")
        return v.strip()

    @field_validator("description")
    @classmethod
    def validate_description(cls, v: str) -> str:
        """Validate and clean task description"""
        if not v.strip():
            raise ValueError("Task description cannot be empty or whitespace")
        return v.strip()

    def model_post_init(self, __context) -> None:
        """Set initial updated_at if not provided"""
        if self.updated_at is None:
            self.updated_at = self.created_at

    @classmethod
    def create_new_task(
        cls,
        title: str,
        description: str,
        user_id: int,
        priority: TaskPriorityEnum = TaskPriorityEnum.MEDIUM,
    ) -> "TaskEntity":
        """
        Factory method to create a new task with proper validation

        Args:
            title: Task title
            description: Task description
            user_id: User ID to assign the task to
            priority: Task priority (default: MEDIUM)

        Returns:
            TaskEntity: New task instance
        """
        return cls(
            title=title,
            description=description,
            user_id=user_id,
            priority=priority,
        )

    def complete(self) -> None:
        """
        Mark task as completed

        Raises:
            TaskStateException: If task cannot be completed
        """
        if self.status.is_terminal():
            raise TaskAlreadyCompletedException(
                task_id=self.task_id, attempted_operation="complete"
            )

        self.status = TaskStatusEnum.COMPLETED
        self.completed_at = datetime.now(timezone.utc)
        self._update_timestamp()

    def start_task(self) -> None:
        """
        Start working on the task (transition to IN_PROGRESS)

        Raises:
            TaskAlreadyCompletedException: If task is already completed
            InvalidTaskTransitionException: If transition is not allowed
        """
        if self.status == TaskStatusEnum.COMPLETED:
            raise TaskAlreadyCompletedException(
                task_id=self.task_id, attempted_operation="start"
            )
        elif self.status == TaskStatusEnum.CANCELLED:
            raise TaskAlreadyCancelledException(
                task_id=self.task_id, attempted_operation="start"
            )
        elif self.status != TaskStatusEnum.PENDING:
            raise InvalidTaskTransitionException(
                task_id=self.task_id,
                current_status=self.status.value,
                target_status=TaskStatusEnum.IN_PROGRESS.value,
            )

        self.status = TaskStatusEnum.IN_PROGRESS
        self._update_timestamp()

    def cancel_task(self) -> None:
        """
        Cancel the task

        Raises:
            TaskStateException: If task cannot be cancelled
        """
        if self.status.is_terminal():
            raise InvalidTaskTransitionException(
                task_id=self.task_id,
                current_status=self.status.value,
                target_status=TaskStatusEnum.CANCELLED.value,
            )

        self.status = TaskStatusEnum.CANCELLED
        self._update_timestamp()

    def update_task(
        self, title: Optional[str] = None, description: Optional[str] = None
    ) -> None:
        """
        Update task title and/or description

        Args:
            title: New title (optional)
            description: New description (optional)

        Raises:
            TaskStateException: If task cannot be updated
        """
        if self.status.is_terminal():
            raise TaskAlreadyCompletedException(
                task_id=self.task_id, attempted_operation="update"
            )

        if title is not None:
            self.title = title
        if description is not None:
            self.description = description

        self._update_timestamp()

    def is_active(self) -> bool:
        """Check if task is in an active state"""
        return not self.status.is_terminal()

    def is_completed(self) -> bool:
        """Check if task is completed"""
        return self.status.is_completed()

    def is_overdue(
        self, days_threshold: int = TaskConstants.TASK_COMPLETION_TIMEOUT_DAYS
    ) -> bool:
        """
        Check if task is overdue based on creation date

        Args:
            days_threshold: Number of days after which task is considered overdue

        Returns:
            bool: True if task is overdue and still active
        """
        if self.status.is_terminal():
            return False

        days_since_creation = (datetime.now(timezone.utc) - self.created_at).days
        return days_since_creation > days_threshold

    def get_age_in_days(self) -> int:
        """Get task age in days since creation"""
        return (datetime.now(timezone.utc) - self.created_at).days

    def _update_timestamp(self) -> None:
        """Update the updated_at timestamp"""
        self.updated_at = datetime.now(timezone.utc)

    def __str__(self) -> str:
        """String representation of the task"""
        return f"Task({self.task_id}): {self.title} [{self.status.value}]"
