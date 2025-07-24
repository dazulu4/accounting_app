"""
Complete Task Use Case - Domain Layer

This use case handles task completion with enterprise validation,
state transition management, and strategic logging.

Key Features:
- Task existence validation
- State transition validation (only PENDING/IN_PROGRESS can be completed)
- Strategic logging at critical points
- Transactional management with UoW pattern
- Enterprise exception handling
"""

from uuid import UUID
from datetime import datetime
import logging
from typing import Optional

from application.schemas.task_schema import CompleteTaskRequest, CompleteTaskResponse
from domain.gateways.task_gateway import TaskGateway
from domain.entities.task_entity import (
    TaskEntity,
    TaskStateTransitionException,
    TaskAlreadyCompletedException,
)
from domain.exceptions.business_exceptions import TaskNotFoundException
from infrastructure.helpers.database.unit_of_work import UnitOfWork


class CompleteTaskUseCase:
    """
    Use case for completing a task.
    """

    def __init__(self, task_gateway: TaskGateway, unit_of_work: UnitOfWork):
        self.task_gateway = task_gateway
        self.uow = unit_of_work
        self._logger = logging.getLogger(self.__class__.__name__)

    def execute(self, command: CompleteTaskRequest) -> CompleteTaskResponse:
        """
        Execute the use case.
        """
        self._logger.info(
            "Starting task completion use case", extra={"task_id": str(command.task_id)}
        )

        try:
            with self.uow:
                task = self.task_gateway.find_task_by_id(command.task_id)

                if not task:
                    self._logger.warning(
                        "Task not found", extra={"task_id": str(command.task_id)}
                    )
                    raise TaskNotFoundException(command.task_id)

                task.complete_task()

                self.task_gateway.save_task(task)

                self.uow.commit()

                self._logger.info(
                    "Task completed successfully", extra={"task_id": str(task.task_id)}
                )

                return CompleteTaskResponse.from_entity(task)

        except (
            TaskNotFoundException,
            TaskAlreadyCompletedException,
            TaskStateTransitionException,
        ) as e:
            self._logger.error(
                "Error completing task",
                extra={"task_id": str(command.task_id), "error": str(e)},
            )
            raise

        except Exception as e:
            self._logger.critical(
                "Unexpected error completing task",
                extra={"task_id": str(command.task_id), "error": str(e)},
            )
            raise Exception(f"An unexpected error occurred: {e}")
