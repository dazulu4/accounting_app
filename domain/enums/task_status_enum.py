"""
Task Status Enumeration with State Transitions

This module provides the task status enumeration with clearly defined state transitions
following finite state machine principles for robust state management.
"""

from enum import Enum
from typing import Set


class TaskStatusEnum(str, Enum):
    """
    Task status enumeration with state transition validation

    States:
    - PENDING: Task created but not started
    - IN_PROGRESS: Task is actively being worked on
    - COMPLETED: Task has been finished successfully
    - CANCELLED: Task has been cancelled and won't be completed

    State Transitions:
    - PENDING -> IN_PROGRESS: Start working on task
    - PENDING -> COMPLETED: Complete task directly (for simple tasks)
    - PENDING -> CANCELLED: Cancel task before starting
    - IN_PROGRESS -> COMPLETED: Finish active task
    - IN_PROGRESS -> CANCELLED: Cancel active task
    - No transitions allowed from COMPLETED or CANCELLED (terminal states)
    """

    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

    @classmethod
    def get_terminal_statuses(cls) -> Set[str]:
        """Get all terminal statuses (no further transitions allowed)"""
        return {cls.COMPLETED, cls.CANCELLED}

    @classmethod
    def get_active_statuses(cls) -> Set[str]:
        """Get all active statuses (can still be worked on)"""
        return {cls.PENDING, cls.IN_PROGRESS}

    def is_terminal(self) -> bool:
        """Check if this status is terminal (no further transitions)"""
        return self in self.get_terminal_statuses()

    def is_active(self) -> bool:
        """Check if this status represents an active task"""
        return self in self.get_active_statuses()

    def is_completed(self) -> bool:
        """Check if this status represents a completed task"""
        return self == self.COMPLETED

    def is_cancelled(self) -> bool:
        """Check if this status represents a cancelled task"""
        return self == self.CANCELLED


class TaskPriorityEnum(str, Enum):
    """
    Task priority enumeration

    Priority levels from lowest to highest impact:
    - LOW: Nice to have, can be done later
    - MEDIUM: Standard priority, should be done in normal timeframe
    - HIGH: Important, should be prioritized
    - URGENT: Critical, needs immediate attention
    """

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"
