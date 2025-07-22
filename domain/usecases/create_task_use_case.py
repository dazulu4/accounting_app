"""
Create Task Use Case - Domain Layer

This use case handles the creation of new tasks with enterprise validation,
business rule enforcement, and strategic logging.

Key Features:
- User validation and active status checking
- Business rule enforcement (max tasks per user)
- Strategic logging at critical points
- Transactional management with UoW pattern
- Enterprise exception handling
"""

from typing import Optional
from uuid import uuid4
from datetime import datetime, timezone

from domain.entities.task_entity import TaskEntity
from domain.enums.task_status_enum import TaskStatusEnum, TaskPriorityEnum
from domain.constants.task_constants import TaskConstants
from application.schemas.task_schema import CreateTaskRequest, CreateTaskResponse
from domain.gateways.user_gateway import UserGateway
from domain.gateways.task_gateway import TaskGateway
from domain.exceptions.business_exceptions import (
    UserNotFoundException,
    UserNotActiveException,
    MaxTasksExceededException,
    ValidationException
)
from infrastructure.helpers.database.unit_of_work import UnitOfWork
from infrastructure.helpers.logger.logger_config import get_logger, LoggingContext

# Configure logger
logger = get_logger(__name__)


class CreateTaskUseCase:
    """
    Use case for creating new tasks
    
    This use case handles the complete workflow of task creation including:
    - User validation and authorization
    - Business rule enforcement
    - Task entity creation
    - Transactional persistence
    - Response formatting
    
    Business Rules:
    - User must exist and be active
    - User cannot exceed maximum task limit
    - Task title and description must be valid
    - Task is created with PENDING status by default
    """
    
    def __init__(self, unit_of_work: UnitOfWork, user_service: UserGateway):
        """
        Initialize use case with required dependencies
        
        Args:
            user_gateway: Gateway for user operations
        """
        self._unit_of_work = unit_of_work
        self._user_service = user_service
        self._logger = get_logger(__name__)
    
    def execute(self, command: CreateTaskRequest) -> CreateTaskResponse:
        """
        Execute task creation use case
        
        Args:
            command: CreateTaskCommand containing task data
            
        Returns:
            CreateTaskResponse: Response with created task information
            
        Raises:
            UserNotFoundException: If user does not exist
            UserNotActiveException: If user is not active
            MaxTasksExceededException: If user exceeds task limit
            ValidationException: If task data is invalid
        """
        # Create logging context for this operation
        with LoggingContext(
            operation="create_task",
            user_id=str(command.user_id)
        ):
            self._logger.info(
                "task_creation_started",
                user_id=command.user_id,
                title_length=len(command.title),
                description_length=len(command.description),
                priority=command.priority.value
            )
            
            try:
                # Step 1: Validate user exists and is active
                user = self._validate_user(command.user_id)
                
                # Step 2: Enforce business rules
                self._enforce_business_rules(command, user)
                
                # Step 3: Create task entity
                task_entity = self._create_task_entity(command)
                
                # Step 4: Persist task with Unit of Work
                self._persist_task(task_entity)
                
                # Step 5: Create response
                response = self._create_response(task_entity)
                
                self._logger.info(
                    "task_creation_completed_successfully",
                    task_id=str(task_entity.task_id),
                    user_id=command.user_id,
                    status=task_entity.status.value,
                    created_at=task_entity.created_at.isoformat()
                )
                
                return response
                
            except (UserNotFoundException, UserNotActiveException, MaxTasksExceededException) as e:
                # Log business validation failures
                self._logger.warning(
                    "task_creation_failed_business_validation",
                    user_id=command.user_id,
                    error_type=type(e).__name__,
                    error_message=str(e),
                    error_code=getattr(e, 'error_code', 'UNKNOWN').value if hasattr(getattr(e, 'error_code', None), 'value') else str(getattr(e, 'error_code', 'UNKNOWN'))
                )
                raise
                
            except ValidationException as e:
                # Log validation errors
                self._logger.error(
                    "task_creation_failed_validation",
                    user_id=command.user_id,
                    error_message=str(e),
                    error_details=getattr(e, 'details', {})
                )
                raise
                
            except Exception as e:
                # Log unexpected errors
                self._logger.error(
                    "task_creation_failed_unexpected_error",
                    user_id=command.user_id,
                    error_type=type(e).__name__,
                    error_message=str(e),
                    command_data={
                        "title_length": len(command.title),
                        "description_length": len(command.description),
                        "priority": command.priority.value
                    }
                )
                raise
    
    def _validate_user(self, user_id: int):
        """
        Validate user exists and is active
        
        Args:
            user_id: ID of the user to validate
            
        Returns:
            User entity
            
        Raises:
            UserNotFoundException: If user does not exist
            UserNotActiveException: If user is not active
        """
        self._logger.debug("validating_user", user_id=user_id)
        
        user = self._user_service.find_user_by_id(user_id)
        
        if user is None:
            self._logger.warning(
                "user_validation_failed_not_found",
                user_id=user_id
            )
            raise UserNotFoundException(user_id)
        
        if not user.is_active():
            self._logger.warning(
                "user_validation_failed_inactive",
                user_id=user_id,
                user_status=user.status.value if hasattr(user, 'status') else 'unknown'
            )
            raise UserNotActiveException(user_id, user.status.value if hasattr(user, 'status') else 'inactive')
        
        self._logger.debug("user_validation_successful", user_id=user_id)
        return user
    
    def _enforce_business_rules(self, command: CreateTaskRequest, user) -> None:
        """
        Enforce business rules for task creation
        
        Args:
            command: Task creation command
            user: User entity
            
        Raises:
            MaxTasksExceededException: If user exceeds task limit
            ValidationException: If data validation fails
        """
        self._logger.debug("enforcing_business_rules", user_id=command.user_id)
        
        # Check maximum tasks per user using Unit of Work
        with self._unit_of_work as uow:
            active_task_count = uow.task_repository.count_tasks_by_user(command.user_id)
            
            self._logger.debug(
                "checking_task_limit",
                user_id=command.user_id,
                current_task_count=active_task_count,
                max_allowed=TaskConstants.MAX_TASKS_PER_USER
            )
            
            if active_task_count >= TaskConstants.MAX_TASKS_PER_USER:
                self._logger.warning(
                    "business_rule_violation_max_tasks_exceeded",
                    user_id=command.user_id,
                    current_task_count=active_task_count,
                    max_allowed=TaskConstants.MAX_TASKS_PER_USER
                )
                raise MaxTasksExceededException(
                    user_id=command.user_id,
                    current_count=active_task_count,
                    max_allowed=TaskConstants.MAX_TASKS_PER_USER
                )
        
        self._logger.debug("business_rules_validation_successful", user_id=command.user_id)
        # Additional business rule validations can be added here
        # For example: user role permissions, task category restrictions, etc.
    
    def _create_task_entity(self, command: CreateTaskRequest) -> TaskEntity:
        """
        Create task entity from command
        
        Args:
            command: Task creation command
            
        Returns:
            TaskEntity: Created task entity
            
        Raises:
            ValidationException: If entity creation fails
        """
        self._logger.debug("creating_task_entity", user_id=command.user_id)
        
        try:
            task_entity = TaskEntity.create_new_task(
                title=command.title,
                description=command.description,
                user_id=command.user_id,
                priority=command.priority
            )
            
            self._logger.debug(
                "task_entity_created",
                task_id=str(task_entity.task_id),
                user_id=command.user_id,
                status=task_entity.status.value
            )
            
            return task_entity
            
        except Exception as e:
            self._logger.error(
                "task_entity_creation_failed",
                user_id=command.user_id,
                error=str(e),
                command_data={
                    "title": command.title,
                    "description": command.description,
                    "priority": command.priority.value
                }
            )
            raise ValidationException(
                message=f"Failed to create task entity: {str(e)}",
                details={"command": command.__dict__}
            )
    
    def _persist_task(self, task_entity: TaskEntity) -> None:
        """
        Persist task entity using Unit of Work pattern
        
        Args:
            task_entity: Task entity to persist
            
        Raises:
            DatabaseException: If persistence fails
        """
        self._logger.debug(
            "persisting_task",
            task_id=str(task_entity.task_id),
            user_id=task_entity.user_id
        )
        
        try:
            with self._unit_of_work as uow:
                uow.task_repository.save_task(task_entity)
                # Additional related operations can be added here
                # within the same transaction boundary
                
            self._logger.debug(
                "task_persistence_successful",
                task_id=str(task_entity.task_id),
                user_id=task_entity.user_id
            )
                
        except Exception as e:
            self._logger.error(
                "task_persistence_failed",
                task_id=str(task_entity.task_id),
                user_id=task_entity.user_id,
                error_type=type(e).__name__,
                error_message=str(e)
            )
            # Re-raise as business exception
            from domain.exceptions.business_exceptions import DatabaseException
            raise DatabaseException(
                message="Failed to save task to database",
                operation="save_task",
                details={"task_id": str(task_entity.task_id)},
                inner_exception=e
            )
    
    def _create_response(self, task_entity: TaskEntity) -> CreateTaskResponse:
        """
        Create response DTO from task entity
        
        Args:
            task_entity: Created task entity
            
        Returns:
            CreateTaskResponse: Response DTO
        """
        self._logger.debug("creating_response", task_id=str(task_entity.task_id))
        
        return CreateTaskResponse(
            task_id=task_entity.task_id,
            title=task_entity.title,
            description=task_entity.description,
            user_id=task_entity.user_id,
            status=task_entity.status.value,
            priority=task_entity.priority.value,
            created_at=task_entity.created_at,
            updated_at=task_entity.updated_at,
            completed_at=task_entity.completed_at
        ) 