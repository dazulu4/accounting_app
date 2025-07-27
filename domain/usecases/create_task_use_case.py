"""
Create Task Use Case - Enterprise Edition

This module implements the business logic for creating tasks in the system.
It follows the Clean Architecture pattern and uses dependency injection
for external dependencies.

Key Features:
- Business logic validation
- Domain entity creation
- Repository interaction
- Structured logging
- Error handling with domain exceptions
"""

# No imports from application layer - Clean Architecture compliance
import logging

from domain.constants.task_constants import TaskConstants
from domain.entities.task_entity import TaskEntity
from domain.enums.task_status_enum import TaskPriorityEnum
from domain.exceptions.business_exceptions import (
    DatabaseException,
    MaxTasksExceededException,
    UserNotActiveException,
    UserNotFoundException,
)
from domain.gateways.task_gateway import TaskGateway
from domain.gateways.user_gateway import UserGateway

# Initialize logger
logger = logging.getLogger(__name__)


class CreateTaskUseCase:
    """
    Use case for creating tasks in the system.

    This use case handles the business logic for task creation,
    including validation of user existence and status, task limits,
    and proper error handling.
    """

    def __init__(self, task_gateway: TaskGateway, user_gateway: UserGateway):
        """
        Initialize the use case with required gateways.

        Args:
            task_gateway: Gateway for task persistence operations
            user_gateway: Gateway for user retrieval operations
        """
        self.task_gateway = task_gateway
        self.user_gateway = user_gateway

    def execute(
        self,
        title: str,
        description: str,
        user_id: int,
        priority: TaskPriorityEnum = TaskPriorityEnum.MEDIUM,
    ) -> TaskEntity:
        """
        Execute the task creation use case.

        Args:
            title: Task title
            description: Task description
            user_id: ID of the user to assign the task to
            priority: Task priority (optional, defaults to MEDIUM)

        Returns:
            TaskEntity: The created task

        Raises:
            UserNotFoundException: If the specified user doesn't exist
            UserNotActiveException: If the user is not active
            DatabaseException: If task creation fails
            MaxTasksExceededException: If user has reached task limit
        """
        logger.info(f"create_task_use_case_started user_id={user_id}")

        try:
            # Validate user exists and is active
            user = self.user_gateway.find_user_by_id(user_id)
            if not user:
                raise UserNotFoundException(user_id=user_id)

            if not user.is_active():
                raise UserNotActiveException(user_id=user_id)

            # Check task limits
            current_tasks = self.task_gateway.count_tasks_by_user(user_id)
            if current_tasks >= TaskConstants.MAX_TASKS_PER_USER:
                raise MaxTasksExceededException(
                    user_id=user_id,
                    current_count=current_tasks,
                    max_allowed=TaskConstants.MAX_TASKS_PER_USER,
                )

            # Create and save task
            task_entity = TaskEntity.create_new_task(
                title=title,
                description=description,
                user_id=user_id,
                priority=priority,
            )

            self.task_gateway.save_task(task_entity)

            logger.info(
                f"create_task_use_case_completed user_id={user_id} task_id={task_entity.task_id}"
            )
            return task_entity

        except (
            UserNotFoundException,
            UserNotActiveException,
            MaxTasksExceededException,
        ) as e:
            logger.warning(
                f"create_task_use_case_failed user_id={user_id} error={str(e)}"
            )
            raise
        except Exception as e:
            logger.error(
                f"create_task_use_case_unexpected_error user_id={user_id} error={str(e)}"
            )
            raise DatabaseException(
                message=f"Failed to create task: {str(e)}",
                operation="create_task",
                details={"user_id": user_id},
            )
