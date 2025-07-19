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

from datetime import datetime, timezone
from uuid import UUID

from domain.entities.task_entity import TaskEntity
from domain.enums.task_status_enum import TaskStatusEnum
from domain.value_objects.task_value_objects import CompleteTaskRequest, CompleteTaskResponse
from domain.exceptions.business_exceptions import (
    TaskNotFoundException,
    InvalidTaskTransitionException,
    ValidationException
)
from infrastructure.helpers.database.unit_of_work import UnitOfWork
from infrastructure.helpers.logger.logger_config import get_logger, LoggingContext

# Configure logger
logger = get_logger(__name__)


class CompleteTaskUseCase:
    """
    Use case for completing tasks
    
    This use case handles the complete workflow of task completion including:
    - Task existence validation
    - State transition validation
    - Business rule enforcement
    - Transactional state update
    - Response formatting
    
    Business Rules:
    - Task must exist
    - Task must be in a state that allows completion
    - State transitions must follow defined rules
    - Completion timestamp is automatically set
    """
    
    def __init__(self):
        """
        Initialize use case
        
        Note: This use case doesn't require external dependencies
        as it works directly with the Unit of Work pattern
        """
        pass
    
    def execute(self, task_id: UUID, request: CompleteTaskRequest) -> CompleteTaskResponse:
        """
        Execute task completion use case
        
        Args:
            task_id: UUID of the task to complete
            request: Optional completion request with additional data
            
        Returns:
            OperationResultResponse: Response with operation result
            
        Raises:
            TaskNotFoundException: If task does not exist
            TaskAlreadyCompletedException: If task is already completed
            InvalidTaskTransitionException: If transition is not allowed
        """
        # Create logging context for this operation
        with LoggingContext(
            operation="complete_task",
            task_id=str(task_id),
            has_completion_notes=bool(request and request.completion_notes)
        ):
            logger.info(
                "task_completion_started",
                task_id=str(task_id),
                has_completion_notes=bool(request and request.completion_notes),
                completion_notes_length=len(request.completion_notes) if request and request.completion_notes else 0
            )
            
            try:
                # Step 1: Load and validate task
                task_entity = self._load_and_validate_task(task_id)
                
                # Step 2: Validate state transition
                self._validate_completion_transition(task_entity)
                
                # Step 3: Complete task with business logic
                self._complete_task_entity(task_entity, request)
                
                # Step 4: Persist changes with Unit of Work
                self._persist_task_completion(task_entity)
                
                # Step 5: Create response
                response = self._create_response(task_entity)
                
                logger.info(
                    "task_completion_successful",
                    task_id=str(task_id),
                    completed_at=task_entity.completed_at.isoformat() if task_entity.completed_at else None,
                    final_status=task_entity.status.value,
                    user_id=task_entity.user_id
                )
                
                return response
                
            except (TaskNotFoundException, InvalidTaskTransitionException) as e:
                # Log business validation failures
                logger.warning(
                    "task_completion_failed_business_validation",
                    task_id=str(task_id),
                    error_type=type(e).__name__,
                    error_message=str(e),
                    error_code=getattr(e, 'error_code', 'UNKNOWN').value if hasattr(getattr(e, 'error_code', None), 'value') else str(getattr(e, 'error_code', 'UNKNOWN'))
                )
                raise
                
            except ValidationException as e:
                # Log validation errors
                logger.error(
                    "task_completion_failed_validation",
                    task_id=str(task_id),
                    error_message=str(e),
                    error_details=getattr(e, 'details', {})
                )
                raise
                
            except Exception as e:
                # Log unexpected errors
                logger.error(
                    "task_completion_failed_unexpected_error",
                    task_id=str(task_id),
                    error_type=type(e).__name__,
                    error_message=str(e),
                    request_data={
                        "has_completion_notes": bool(request and request.completion_notes),
                        "completion_notes_length": len(request.completion_notes) if request and request.completion_notes else 0
                    }
                )
                raise
    
    def _load_and_validate_task(self, task_id: UUID) -> TaskEntity:
        """
        Load task and validate it exists
        
        Args:
            task_id: UUID of the task to load
            
        Returns:
            TaskEntity: Loaded task entity
            
        Raises:
            TaskNotFoundException: If task does not exist
        """
        logger.debug("loading_task", task_id=str(task_id))
        
        with UnitOfWork() as uow:
            task_entity = uow.task_repository.find_task_by_id(task_id)
            
            if task_entity is None:
                logger.warning(
                    "task_load_failed_not_found",
                    task_id=str(task_id)
                )
                raise TaskNotFoundException(task_id)
            
            logger.debug(
                "task_loaded_successfully",
                task_id=str(task_id),
                current_status=task_entity.status.value,
                user_id=task_entity.user_id,
                created_at=task_entity.created_at.isoformat()
            )
            
            return task_entity
    
    def _validate_completion_transition(self, task_entity: TaskEntity) -> None:
        """
        Validate that the task can be completed
        
        Args:
            task_entity: Task entity to validate
            
        Raises:
            TaskAlreadyCompletedException: If task is already completed
            InvalidTaskTransitionException: If transition is not allowed
        """
        logger.debug(
            "validating_task_transition",
            task_id=str(task_entity.task_id),
            current_status=task_entity.status.value,
            target_status=TaskStatusEnum.COMPLETED.value
        )
        
        # Check if task is already completed
        if task_entity.status == TaskStatusEnum.COMPLETED:
            logger.warning(
                "task_already_completed",
                task_id=str(task_entity.task_id),
                current_status=task_entity.status.value,
                completed_at=task_entity.completed_at.isoformat() if task_entity.completed_at else None
            )
            raise InvalidTaskTransitionException(
                task_id=task_entity.task_id,
                current_status=task_entity.status.value,
                target_status=TaskStatusEnum.COMPLETED.value,
                valid_transitions=[t.value for t in TaskStatusEnum.get_valid_transitions(task_entity.status)]
            )
        
        # Check if transition to completed is valid
        if not TaskStatusEnum.can_transition_to(task_entity.status, TaskStatusEnum.COMPLETED):
            valid_transitions = TaskStatusEnum.get_valid_transitions(task_entity.status)
            logger.warning(
                "invalid_task_transition",
                task_id=str(task_entity.task_id),
                current_status=task_entity.status.value,
                target_status=TaskStatusEnum.COMPLETED.value,
                valid_transitions=[t.value for t in valid_transitions]
            )
            raise InvalidTaskTransitionException(
                task_id=task_entity.task_id,
                current_status=task_entity.status.value,
                target_status=TaskStatusEnum.COMPLETED.value,
                valid_transitions=[t.value for t in valid_transitions]
            )
        
        logger.debug("task_transition_validation_successful", task_id=str(task_entity.task_id))
    
    def _complete_task_entity(self, task_entity: TaskEntity, request: CompleteTaskRequest) -> None:
        """
        Apply completion business logic to task entity
        
        Args:
            task_entity: Task entity to complete
            request: Optional completion request with additional data
        """
        logger.debug(
            "completing_task_entity",
            task_id=str(task_entity.task_id),
            previous_status=task_entity.status.value
        )
        
        try:
            # Use the domain entity's business method for completion
            task_entity.complete_task()
            
            # Additional completion logic could be added here
            # For example: setting completion notes, calculating duration, etc.
            if request and request.completion_notes:
                logger.debug(
                    "completion_notes_provided",
                    task_id=str(task_entity.task_id),
                    notes_length=len(request.completion_notes)
                )
                # If we had a completion_notes field in the entity
                # task_entity.set_completion_notes(request.completion_notes)
                pass
            
            logger.debug(
                "task_entity_completed",
                task_id=str(task_entity.task_id),
                new_status=task_entity.status.value,
                completed_at=task_entity.completed_at.isoformat() if task_entity.completed_at else None
            )
            
        except Exception as e:
            logger.error(
                "task_entity_completion_failed",
                task_id=str(task_entity.task_id),
                previous_status=task_entity.status.value,
                error=str(e)
            )
            raise ValidationException(
                message=f"Failed to complete task entity: {str(e)}",
                details={"task_id": str(task_entity.task_id)}
            )
    
    def _persist_task_completion(self, task_entity: TaskEntity) -> None:
        """
        Persist task completion using Unit of Work pattern
        
        Args:
            task_entity: Completed task entity to persist
            
        Raises:
            DatabaseException: If persistence fails
        """
        logger.debug(
            "persisting_task_completion",
            task_id=str(task_entity.task_id),
            status=task_entity.status.value
        )
        
        try:
            with UnitOfWork() as uow:
                uow.task_repository.save_task(task_entity)
                
                # Additional operations within the same transaction
                # could be added here, for example:
                # - Update user statistics
                # - Create completion audit log
                # - Send notifications
                
            logger.debug(
                "task_completion_persistence_successful",
                task_id=str(task_entity.task_id),
                user_id=task_entity.user_id
            )
                
        except Exception as e:
            logger.error(
                "task_completion_persistence_failed",
                task_id=str(task_entity.task_id),
                error_type=type(e).__name__,
                error_message=str(e)
            )
            # Re-raise as business exception
            from domain.exceptions.business_exceptions import DatabaseException
            raise DatabaseException(
                message="Failed to save completed task to database",
                operation="complete_task",
                details={"task_id": str(task_entity.task_id)},
                inner_exception=e
            )
    
    def _create_response(self, task_entity: TaskEntity) -> CompleteTaskResponse:
        """
        Create response DTO for successful completion
        
        Args:
            task_entity: Completed task entity
            
        Returns:
            OperationResultResponse: Response DTO
        """
        logger.debug("creating_completion_response", task_id=str(task_entity.task_id))
        
        return CompleteTaskResponse(
            success=True,
            message=f"Task '{task_entity.title}' completed successfully",
            operation="complete_task",
            timestamp=task_entity.completed_at.isoformat() if task_entity.completed_at else task_entity.updated_at.isoformat()
        ) 