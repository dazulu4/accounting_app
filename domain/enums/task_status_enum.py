"""
Task Status Enumeration with State Transitions

This module provides the task status enumeration with clearly defined state transitions
following finite state machine principles for robust state management.
"""

from enum import Enum
from typing import List, Dict, Set
from domain.constants.task_constants import TaskConstants


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
    def get_valid_transitions(cls, current_status) -> List[str]:
        """
        Get valid status transitions from the current status
        
        Args:
            current_status: Current task status
            
        Returns:
            List of valid target statuses
            
        Raises:
            ValueError: If current_status is not a valid status
        """
        # Handle both enum objects and string values
        if isinstance(current_status, cls):
            current_status = current_status.value
        
        if current_status not in [member.value for member in cls]:
            raise ValueError(f"Invalid status: {current_status}")
        
        transitions = {
            cls.PENDING.value: [cls.IN_PROGRESS.value, cls.COMPLETED.value, cls.CANCELLED.value],
            cls.IN_PROGRESS.value: [cls.COMPLETED.value, cls.CANCELLED.value],
            cls.COMPLETED.value: [],  # Terminal state
            cls.CANCELLED.value: []   # Terminal state
        }
        
        return transitions.get(current_status, [])
    
    @classmethod
    def can_transition_to(cls, current_status: str, target_status: str) -> bool:
        """
        Check if transition from current status to target status is valid
        
        Args:
            current_status: Current task status
            target_status: Target task status
            
        Returns:
            True if transition is valid, False otherwise
        """
        try:
            valid_transitions = cls.get_valid_transitions(current_status)
            return target_status in valid_transitions
        except ValueError:
            return False
    
    @classmethod
    def get_initial_status(cls) -> str:
        """Get the initial status for new tasks"""
        return cls.PENDING
    
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
    
    @classmethod
    def get_default_priority(cls) -> str:
        """Get the default priority for new tasks"""
        return cls.MEDIUM
    
    def get_sort_order(self) -> int:
        """Get numeric value for sorting by priority"""
        priority_order = {
            self.LOW: 1,
            self.MEDIUM: 2,
            self.HIGH: 3,
            self.URGENT: 4
        }
        return priority_order.get(self, 2)


class UserStatusEnum(str, Enum):
    """
    User status enumeration for task assignment validation
    
    States:
    - ACTIVE: User can be assigned tasks
    - INACTIVE: User cannot be assigned new tasks
    - SUSPENDED: User is temporarily suspended
    """
    
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"
    
    @classmethod
    def get_assignable_statuses(cls) -> Set[str]:
        """Get statuses that allow task assignment"""
        return {cls.ACTIVE}
    
    def can_be_assigned_tasks(self) -> bool:
        """Check if user with this status can be assigned tasks"""
        return self in self.get_assignable_statuses() 