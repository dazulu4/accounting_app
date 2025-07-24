"""
Task Entity - Domain Model

This module contains the core Task entity following Domain-Driven Design principles
with enterprise naming conventions, state transitions, and business rule validation.

Key Features:
- English naming conventions throughout
- State transition validation using TaskStatusEnum
- Business rule validation with custom exceptions
- Immutable entity design where appropriate
- Rich domain methods for business operations
"""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional
from uuid import UUID, uuid4

from domain.enums.task_status_enum import TaskStatusEnum, TaskPriorityEnum
from domain.constants.task_constants import TaskConstants, TaskValidationMessages


class TaskDomainException(Exception):
    """Base exception for task domain errors"""

    pass


class TaskValidationException(TaskDomainException):
    """Raised when task validation fails"""

    pass


class TaskStateTransitionException(TaskDomainException):
    """Raised when invalid state transition is attempted"""

    pass


class TaskAlreadyCompletedException(TaskDomainException):
    """Raised when trying to modify a completed task"""

    pass


class TaskBusinessRuleException(TaskDomainException):
    """Raised when business rule validation fails"""

    pass


@dataclass
class TaskEntity:
    """
    Task entity representing a work item in the accounting system

    This entity encapsulates all business logic related to task management
    including state transitions, validation, and business rules.

    Attributes:
        task_id: Unique identifier for the task
        title: Task title (1-200 characters)
        description: Task description (1-1000 characters)
        user_id: ID of the user assigned to this task
        status: Current task status (from TaskStatusEnum)
        priority: Task priority (from TaskPriorityEnum)
        created_at: Timestamp when task was created
        completed_at: Timestamp when task was completed (None if not completed)
        updated_at: Timestamp when task was last updated
    """

    task_id: UUID
    title: str
    description: str
    user_id: int
    status: TaskStatusEnum = field(default=TaskStatusEnum.PENDING)
    priority: TaskPriorityEnum = field(default=TaskPriorityEnum.MEDIUM)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    completed_at: Optional[datetime] = field(default=None)
    updated_at: Optional[datetime] = field(default=None)

    def __post_init__(self):
        """Validate entity after initialization"""
        self._validate_title()
        self._validate_description()
        self._validate_user_id()

        # Set initial updated_at if not provided
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

        Raises:
            TaskValidationException: If validation fails
        """
        task_id = uuid4()

        task = cls(
            task_id=task_id,
            title=title,
            description=description,
            user_id=user_id,
            priority=priority,
        )

        return task

    def _validate_title(self) -> None:
        """Validate task title"""
        if not self.title or not self.title.strip():
            raise TaskValidationException(TaskValidationMessages.TITLE_REQUIRED)

        if len(self.title.strip()) < TaskConstants.TITLE_MIN_LENGTH:
            raise TaskValidationException(TaskValidationMessages.TITLE_TOO_SHORT)

        if len(self.title) > TaskConstants.TITLE_MAX_LENGTH:
            raise TaskValidationException(TaskValidationMessages.TITLE_TOO_LONG)

    def _validate_description(self) -> None:
        """Validate task description"""
        if not self.description or not self.description.strip():
            raise TaskValidationException(TaskValidationMessages.DESCRIPTION_REQUIRED)

        if len(self.description.strip()) < TaskConstants.DESCRIPTION_MIN_LENGTH:
            raise TaskValidationException(TaskValidationMessages.DESCRIPTION_TOO_SHORT)

        if len(self.description) > TaskConstants.DESCRIPTION_MAX_LENGTH:
            raise TaskValidationException(TaskValidationMessages.DESCRIPTION_TOO_LONG)

    def _validate_user_id(self) -> None:
        """Validate user ID"""
        if not isinstance(self.user_id, int) or self.user_id <= 0:
            raise TaskValidationException("User ID must be a positive integer")

    def _update_timestamp(self) -> None:
        """Update the updated_at timestamp"""
        self.updated_at = datetime.now(timezone.utc)

    def start_task(self) -> None:
        """
        Start working on the task (transition to IN_PROGRESS)

        Raises:
            TaskStateTransitionException: If transition is not allowed
            TaskAlreadyCompletedException: If task is already completed
        """
        if self.status.is_terminal():
            raise TaskAlreadyCompletedException(
                TaskValidationMessages.TASK_ALREADY_COMPLETED
            )

        if not TaskStatusEnum.can_transition_to(
            self.status.value, TaskStatusEnum.IN_PROGRESS.value
        ):
            raise TaskStateTransitionException(
                f"Cannot transition from {self.status} to {TaskStatusEnum.IN_PROGRESS}"
            )

        self.status = TaskStatusEnum.IN_PROGRESS
        self._update_timestamp()

    def complete_task(self) -> None:
        """
        Mark task as completed

        Raises:
            TaskStateTransitionException: If transition is not allowed
            TaskAlreadyCompletedException: If task is already completed
        """
        if self.status == TaskStatusEnum.COMPLETED:
            raise TaskAlreadyCompletedException(
                TaskValidationMessages.TASK_ALREADY_COMPLETED
            )

        if not TaskStatusEnum.can_transition_to(
            self.status.value, TaskStatusEnum.COMPLETED.value
        ):
            raise TaskStateTransitionException(
                f"Cannot transition from {self.status} to {TaskStatusEnum.COMPLETED}"
            )

        self.status = TaskStatusEnum.COMPLETED
        self.completed_at = datetime.now(timezone.utc)
        self._update_timestamp()

    def cancel_task(self) -> None:
        """
        Cancel the task

        Raises:
            TaskStateTransitionException: If transition is not allowed
            TaskAlreadyCompletedException: If task is already completed
        """
        if self.status.is_terminal():
            raise TaskAlreadyCompletedException("Cannot cancel a terminal task")

        if not TaskStatusEnum.can_transition_to(
            self.status.value, TaskStatusEnum.CANCELLED.value
        ):
            raise TaskStateTransitionException(
                f"Cannot transition from {self.status} to {TaskStatusEnum.CANCELLED}"
            )

        self.status = TaskStatusEnum.CANCELLED
        self._update_timestamp()

    def update_title(self, new_title: str) -> None:
        """
        Update task title with validation

        Args:
            new_title: New title for the task

        Raises:
            TaskValidationException: If new title is invalid
            TaskAlreadyCompletedException: If task is completed
        """
        if self.status.is_terminal():
            raise TaskAlreadyCompletedException(
                "Cannot update completed or cancelled task"
            )

        old_title = self.title
        self.title = new_title

        try:
            self._validate_title()
            self._update_timestamp()
        except TaskValidationException:
            # Rollback on validation failure
            self.title = old_title
            raise

    def update_description(self, new_description: str) -> None:
        """
        Update task description with validation

        Args:
            new_description: New description for the task

        Raises:
            TaskValidationException: If new description is invalid
            TaskAlreadyCompletedException: If task is completed
        """
        if self.status.is_terminal():
            raise TaskAlreadyCompletedException(
                "Cannot update completed or cancelled task"
            )

        old_description = self.description
        self.description = new_description

        try:
            self._validate_description()
            self._update_timestamp()
        except TaskValidationException:
            # Rollback on validation failure
            self.description = old_description
            raise

    def change_priority(self, new_priority: TaskPriorityEnum) -> None:
        """
        Change task priority

        Args:
            new_priority: New priority for the task

        Raises:
            TaskAlreadyCompletedException: If task is completed
        """
        if self.status.is_terminal():
            raise TaskAlreadyCompletedException(
                "Cannot change priority of completed or cancelled task"
            )

        self.priority = new_priority
        self._update_timestamp()

    def is_active(self) -> bool:
        """Check if task is active (can be worked on)"""
        return self.status.is_active()

    def is_completed(self) -> bool:
        """Check if task is completed"""
        return self.status.is_completed()

    def is_cancelled(self) -> bool:
        """Check if task is cancelled"""
        return self.status.is_cancelled()

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

    def to_dict(self) -> dict:
        """Convert entity to dictionary for serialization"""
        return {
            "task_id": str(self.task_id),
            "title": self.title,
            "description": self.description,
            "user_id": self.user_id,
            "status": self.status.value,
            "priority": self.priority.value,
            "created_at": self.created_at.isoformat(),
            "completed_at": (
                self.completed_at.isoformat() if self.completed_at else None
            ),
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "is_active": self.is_active(),
            "is_completed": self.is_completed(),
            "age_in_days": self.get_age_in_days(),
        }

    def __str__(self) -> str:
        """String representation of the task"""
        return f"Task({self.task_id}): {self.title} [{self.status.value}]"

    def __repr__(self) -> str:
        """Detailed string representation for debugging"""
        return (
            f"TaskEntity("
            f"task_id={self.task_id}, "
            f"title='{self.title}', "
            f"status={self.status.value}, "
            f"user_id={self.user_id}"
            f")"
        )
