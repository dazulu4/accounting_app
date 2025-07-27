"""
List Tasks By User Use Case - Domain Layer

This module implements the List Tasks by User use case following Clean Architecture principles
with simplified patterns and consistent structure.

Key Features:
- User existence validation
- Simple task retrieval by user ID
- Clean Architecture compliance (no application/infrastructure imports)
- Consistent logging pattern
"""

# No imports from application/infrastructure layer - Clean Architecture compliance
import logging
from typing import List

from domain.entities.task_entity import TaskEntity
from domain.exceptions.business_exceptions import UserNotFoundException
from domain.gateways.task_gateway import TaskGateway
from domain.gateways.user_gateway import UserGateway

# Initialize logger
logger = logging.getLogger(__name__)


class ListTasksByUserUseCase:
    """
    Use case for listing tasks assigned to a specific user.

    This use case handles user validation and task retrieval
    following Clean Architecture principles.
    """

    def __init__(
        self,
        task_gateway: TaskGateway,
        user_gateway: UserGateway,
    ):
        """
        Initialize the use case with required gateways.

        Args:
            task_gateway: Gateway for task operations
            user_gateway: Gateway for user operations
        """
        self.task_gateway = task_gateway
        self.user_gateway = user_gateway

    def execute(self, user_id: int) -> List[TaskEntity]:
        """
        Execute the list tasks by user use case.

        Args:
            user_id: The ID of the user whose tasks are to be listed.

        Returns:
            List[TaskEntity]: List of tasks assigned to the user

        Raises:
            UserNotFoundException: If the user is not found.
        """
        logger.info(f"list_tasks_by_user_use_case_started user_id={user_id}")

        try:
            # Validate user exists
            user = self.user_gateway.find_user_by_id(user_id)
            if not user:
                raise UserNotFoundException(user_id=user_id)

            # Get tasks for user
            tasks = self.task_gateway.find_tasks_by_user_id(user_id)

            logger.info(
                f"list_tasks_by_user_use_case_completed user_id={user_id} task_count={len(tasks)}"
            )
            return tasks

        except UserNotFoundException as e:
            logger.warning(
                f"list_tasks_by_user_use_case_failed user_id={user_id} error={str(e)}"
            )
            raise
        except Exception as e:
            logger.error(
                f"list_tasks_by_user_use_case_unexpected_error user_id={user_id} error={str(e)}"
            )
            raise
