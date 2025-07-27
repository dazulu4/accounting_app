"""
Complete Task Use Case - Domain Layer

This use case handles task completion following Clean Architecture principles
with simplified validation and consistent patterns.

Key Features:
- Task existence validation
- State transition validation using centralized exceptions
- Simple logging
- Clean Architecture compliance (no application/infrastructure imports)
"""

# No imports from application/infrastructure layer - Clean Architecture compliance
import logging
from uuid import UUID

from domain.entities.task_entity import TaskEntity
from domain.exceptions.business_exceptions import (
    InvalidTaskTransitionException,
    TaskAlreadyCompletedException,
    TaskNotFoundException,
)
from domain.gateways.task_gateway import TaskGateway

# Initialize logger
logger = logging.getLogger(__name__)


class CompleteTaskUseCase:
    """
    Use case for completing a task.

    This use case handles task completion with proper validation
    and state transition management.
    """

    def __init__(self, task_gateway: TaskGateway):
        """
        Initialize the use case with required gateway.

        Args:
            task_gateway: Gateway for task persistence operations
        """
        self.task_gateway = task_gateway

    def execute(self, task_id: UUID) -> TaskEntity:
        """
        Execute the task completion use case.

        Args:
            task_id: UUID of the task to complete

        Returns:
            TaskEntity: The completed task

        Raises:
            TaskNotFoundException: If the task doesn't exist
            TaskAlreadyCompletedException: If task is already completed
            InvalidTaskTransitionException: If task cannot be completed
        """
        logger.info(f"complete_task_use_case_started task_id={task_id}")

        try:
            # Find task
            task = self.task_gateway.find_task_by_id(task_id)
            if not task:
                raise TaskNotFoundException(task_id=task_id)

            # Complete task (this will handle state validation)
            task.complete()

            # Save task
            self.task_gateway.save_task(task)

            logger.info(f"complete_task_use_case_completed task_id={task_id}")
            return task

        except (
            TaskNotFoundException,
            TaskAlreadyCompletedException,
            InvalidTaskTransitionException,
        ) as e:
            logger.warning(
                f"complete_task_use_case_failed task_id={task_id} error={str(e)}"
            )
            raise
        except Exception as e:
            logger.error(
                f"complete_task_use_case_unexpected_error task_id={task_id} error={str(e)}"
            )
            raise
