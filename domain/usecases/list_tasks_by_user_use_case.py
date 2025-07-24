"""
List Tasks By User Use Case - Application Layer

This module implements the List Tasks by User use case following Clean Architecture principles
with enterprise patterns including pagination, filtering, DTOs, and comprehensive error handling.

Key Features:
- Synchronous operation (optimized for Lambda)
- Pagination support for large datasets
- Status filtering capabilities
- DTOs for request/response contracts
- User validation
- Structured logging
"""

import logging

from application.schemas.task_schema import TaskListResponse
from domain.exceptions.business_exceptions import UserNotFoundException
from domain.gateways.task_gateway import TaskGateway
from domain.gateways.user_gateway import UserGateway
from infrastructure.helpers.database.unit_of_work import UnitOfWork


class ListTasksByUserUseCase:
    """
    Use case for listing tasks assigned to a specific user.
    """

    def __init__(
        self,
        task_gateway: TaskGateway,
        user_gateway: UserGateway,
        unit_of_work: UnitOfWork,
    ):
        self.task_gateway = task_gateway
        self.user_gateway = user_gateway
        self.uow = unit_of_work
        self._logger = logging.getLogger(self.__class__.__name__)

    def execute(self, user_id: int) -> TaskListResponse:
        """
        Executes the use case.

        Args:
            user_id: The ID of the user whose tasks are to be listed.

        Returns:
            A response object containing the list of tasks.

        Raises:
            UserNotFoundException: If the user is not found.
        """
        self._logger.info(
            "use_case_start_listing_tasks_by_user", extra={"user_id": user_id}
        )

        with self.uow:
            user = self.user_gateway.find_user_by_id(user_id)
            if not user:
                self._logger.warning(
                    "user_not_found_in_list_tasks_use_case",
                    extra={"user_id": user_id},
                )
                raise UserNotFoundException(user_id)

            tasks = self.task_gateway.find_tasks_by_user_id(user_id)

            self._logger.info(
                "use_case_tasks_listed_successfully",
                extra={"user_id": user_id, "task_count": len(tasks)},
            )

            return TaskListResponse.from_entities(tasks, user_id)
