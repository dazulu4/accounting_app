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

from typing import Optional
from datetime import datetime

from domain.entities.task_entity import TaskEntity
from domain.entities.user_entity import UserEntity
from domain.gateways.task_gateway import TaskGateway
from domain.gateways.user_gateway import UserGateway
from domain.enums.task_status_enum import TaskPriorityEnum
from domain.exceptions.business_exceptions import (
    UserNotFoundException,
    UserNotActiveException,
    DatabaseException,
    MaxTasksExceededException,
)
from application.schemas.task_schema import CreateTaskRequest, CreateTaskResponse
from infrastructure.helpers.logger.logger_config import get_logger, logging_context

# Initialize structured logger
logger = get_logger(__name__)


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

    def execute(self, request: CreateTaskRequest) -> CreateTaskResponse:
        """
        Execute the task creation use case.

        Args:
            request: CreateTaskRequest containing task data

        Returns:
            CreateTaskResponse with created task information

        Raises:
            UserNotFoundException: If the specified user doesn't exist
            UserNotActiveException: If the user is not active
            DatabaseException: If task creation fails
            MaxTasksExceededException: If user has reached task limit
        """
        # Generate request ID for tracing
        request_id = getattr(request, "request_id", "unknown")

        with logging_context(request_id=request_id, user_id=request.user_id):
            logger.info(
                "create_task_use_case_started",
                user_id=request.user_id,
                title=(
                    request.title[:50] + "..."
                    if len(request.title) > 50
                    else request.title
                ),
            )

            try:
                # Step 1: Validate user exists and is active
                logger.debug("validating_user", user_id=request.user_id)
                user = self._validate_user(request.user_id)

                # Step 2: Check task limits
                logger.debug("checking_task_limits", user_id=request.user_id)
                self._check_task_limits(request.user_id)

                # Step 3: Create task entity
                logger.debug("creating_task_entity", user_id=request.user_id)
                task_entity = self._create_task_entity(request)

                # Step 4: Save task
                logger.debug("saving_task", user_id=request.user_id)
                saved_task = self._save_task(task_entity)

                # Step 5: Create response
                logger.debug("creating_response", user_id=request.user_id)
                response = self._create_response(saved_task)

                logger.info(
                    "create_task_use_case_completed",
                    user_id=request.user_id,
                    task_id=response.task_id,
                )

                return response

            except (
                UserNotFoundException,
                UserNotActiveException,
                DatabaseException,
                MaxTasksExceededException,
            ) as e:
                # Re-raise domain exceptions
                logger.warning(
                    "create_task_use_case_failed_domain_exception",
                    user_id=request.user_id,
                    error_type=type(e).__name__,
                    error_message=str(e),
                )
                raise
            except Exception as e:
                # Log unexpected errors
                logger.error(
                    "create_task_use_case_failed_unexpected_error",
                    user_id=request.user_id,
                    error_type=type(e).__name__,
                    error_message=str(e),
                )
                raise DatabaseException(
                    message=f"Failed to create task: {str(e)}",
                    operation="create_task",
                    details={"user_id": request.user_id},
                )

    def _validate_user(self, user_id: int) -> UserEntity:
        """
        Validate that the user exists and is active.

        Args:
            user_id: ID of the user to validate

        Returns:
            UserEntity if user exists and is active

        Raises:
            UserNotFoundException: If user doesn't exist
            UserNotActiveException: If user is not active
        """
        logger.debug("validating_user_existence", user_id=user_id)

        user = self.user_gateway.find_user_by_id(user_id)
        if not user:
            logger.warning("user_not_found", user_id=user_id)
            raise UserNotFoundException(f"User with ID {user_id} not found")

        logger.debug("user_found", user_id=user_id, user_status=user.status.value)

        if not user.is_active():
            logger.warning("user_not_active", user_id=user_id, status=user.status.value)
            raise UserNotActiveException(
                f"User with ID {user_id} is not active (status: {user.status.value})"
            )

        logger.debug("user_validation_passed", user_id=user_id)
        return user

    def _check_task_limits(self, user_id: int) -> None:
        """
        Check if the user has reached the maximum number of tasks.

        Args:
            user_id: ID of the user to check

        Raises:
            MaxTasksExceededException: If user has reached task limit
        """
        logger.debug("checking_task_limits", user_id=user_id)

        # Get current task count for user
        current_count = self.task_gateway.count_tasks_by_user(user_id)

        logger.debug("current_task_count", user_id=user_id, count=current_count)

        # Check against maximum limit (configurable, default 10)
        max_tasks = 10  # This could come from configuration
        if current_count >= max_tasks:
            logger.warning(
                "max_tasks_exceeded",
                user_id=user_id,
                current_count=current_count,
                max_tasks=max_tasks,
            )
            raise MaxTasksExceededException(
                user_id=user_id, current_count=current_count, max_allowed=max_tasks
            )

        logger.debug("task_limits_check_passed", user_id=user_id)

    def _create_task_entity(self, request: CreateTaskRequest) -> TaskEntity:
        """
        Create a task entity from the request data.

        Args:
            request: CreateTaskRequest containing task data

        Returns:
            TaskEntity with the task information
        """
        logger.debug("creating_task_entity", user_id=request.user_id)

        # Ensure priority is the correct enum type
        priority = request.priority
        if isinstance(priority, str):
            priority = TaskPriorityEnum(priority)

        task_entity = TaskEntity.create_new_task(
            title=request.title,
            description=request.description,
            user_id=request.user_id,
            priority=priority,
        )

        logger.debug("task_entity_created", user_id=request.user_id)
        return task_entity

    def _save_task(self, task_entity: TaskEntity) -> TaskEntity:
        """
        Save the task entity using the task gateway.

        Args:
            task_entity: TaskEntity to save

        Returns:
            TaskEntity with saved data (including ID)

        Raises:
            DatabaseException: If saving fails
        """
        logger.debug("saving_task", user_id=task_entity.user_id)

        try:
            self.task_gateway.save_task(task_entity)
            logger.debug("task_saved_successfully", user_id=task_entity.user_id)
            return task_entity
        except Exception as e:
            logger.error(
                "task_save_failed",
                user_id=task_entity.user_id,
                error_type=type(e).__name__,
                error_message=str(e),
            )
            raise DatabaseException(
                message=f"Failed to save task: {str(e)}",
                operation="save_task",
                details={"user_id": task_entity.user_id},
            )

    def _create_response(self, task_entity: TaskEntity) -> CreateTaskResponse:
        """
        Create a response DTO from the task entity.

        Args:
            task_entity: TaskEntity with saved data

        Returns:
            CreateTaskResponse with task information
        """
        logger.debug("creating_response", user_id=task_entity.user_id)

        response = CreateTaskResponse.from_entity(task_entity)
        logger.debug("response_created", user_id=task_entity.user_id)
        return response
