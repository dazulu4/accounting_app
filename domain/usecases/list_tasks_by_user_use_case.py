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
from typing import List

from infrastructure.database.unit_of_work import UnitOfWork
from domain.entities.task_entity import TaskEntity
from domain.dtos.task_dtos import GetTasksByUserRequest, TaskListResponse, TaskDtoMapper
from domain.exceptions.business_exceptions import (
    UserNotFoundException,
    ValidationException
)
from domain.enums.task_status_enum import TaskStatusEnum

# Configure logger
logger = logging.getLogger(__name__)


class ListTasksByUserUseCase:
    """
    Use case for retrieving tasks assigned to a specific user
    
    This use case handles the complete workflow of task retrieval including:
    - User validation
    - Filtering by status (optional)
    - Pagination support
    - Response formatting with metadata
    
    Features:
    - Supports pagination for large datasets
    - Optional status filtering
    - Returns comprehensive metadata (total count, pages, etc.)
    - Validates user existence
    """
    
    def __init__(self):
        """
        Initialize use case
        
        Note: This use case uses Unit of Work pattern directly
        without external dependencies
        """
        pass
    
    def execute(self, request: GetTasksByUserRequest) -> TaskListResponse:
        """
        Execute list tasks by user use case
        
        Args:
            request: GetTasksByUserRequest containing user ID and filters
            
        Returns:
            TaskListResponse: Paginated list of tasks with metadata
            
        Raises:
            ValidationException: If request parameters are invalid
        """
        logger.info(
            "list_tasks_by_user_started",
            extra={
                "user_id": request.user_id,
                "status_filter": request.status_filter.value if request.status_filter else None,
                "page": request.page,
                "page_size": request.page_size
            }
        )
        
        try:
            # Step 1: Validate request parameters
            self._validate_request(request)
            
            # Step 2: Retrieve tasks with pagination
            tasks, total_count = self._retrieve_tasks_with_pagination(request)
            
            # Step 3: Create response with metadata
            response = self._create_response(tasks, total_count, request)
            
            logger.info(
                "list_tasks_by_user_completed",
                extra={
                    "user_id": request.user_id,
                    "tasks_returned": len(tasks),
                    "total_count": total_count,
                    "page": request.page,
                    "total_pages": response.total_pages
                }
            )
            
            return response
            
        except Exception as e:
            logger.error(
                "list_tasks_by_user_failed",
                extra={
                    "user_id": request.user_id,
                    "error_type": type(e).__name__,
                    "error_message": str(e)
                }
            )
            raise
    
    def _validate_request(self, request: GetTasksByUserRequest) -> None:
        """
        Validate request parameters
        
        Args:
            request: Request to validate
            
        Raises:
            ValidationException: If validation fails
        """
        # Validate user_id
        if request.user_id <= 0:
            raise ValidationException(
                message="User ID must be a positive integer",
                field_name="user_id",
                field_value=request.user_id
            )
        
        # Validate pagination parameters
        if request.page <= 0:
            raise ValidationException(
                message="Page number must be greater than 0",
                field_name="page",
                field_value=request.page
            )
        
        if request.page_size <= 0 or request.page_size > 100:
            raise ValidationException(
                message="Page size must be between 1 and 100",
                field_name="page_size",
                field_value=request.page_size
            )
    
    def _retrieve_tasks_with_pagination(self, request: GetTasksByUserRequest) -> tuple[List[TaskEntity], int]:
        """
        Retrieve tasks with pagination and filtering
        
        Args:
            request: Request containing filter and pagination parameters
            
        Returns:
            Tuple of (tasks list, total count)
        """
        with UnitOfWork() as uow:
            # Get all tasks for the user (for counting)
            if request.status_filter:
                # Filter by status
                all_user_tasks = uow.task_repository.find_tasks_by_status(request.status_filter)
                # Further filter by user_id (this could be optimized with a composite query)
                all_user_tasks = [task for task in all_user_tasks if task.user_id == request.user_id]
            else:
                # Get all tasks for user
                all_user_tasks = uow.task_repository.find_tasks_by_user_id(request.user_id)
            
            total_count = len(all_user_tasks)
            
            # Apply pagination
            start_index = (request.page - 1) * request.page_size
            end_index = start_index + request.page_size
            paginated_tasks = all_user_tasks[start_index:end_index]
            
            logger.debug(
                "tasks_retrieved_with_pagination",
                extra={
                    "user_id": request.user_id,
                    "total_available": total_count,
                    "page_start": start_index,
                    "page_end": end_index,
                    "returned_count": len(paginated_tasks)
                }
            )
            
            return paginated_tasks, total_count
    
    def _create_response(
        self, 
        tasks: List[TaskEntity], 
        total_count: int, 
        request: GetTasksByUserRequest
    ) -> TaskListResponse:
        """
        Create response DTO with tasks and pagination metadata
        
        Args:
            tasks: List of task entities
            total_count: Total number of tasks (all pages)
            request: Original request for pagination info
            
        Returns:
            TaskListResponse: Response with tasks and metadata
        """
        return TaskDtoMapper.entities_to_list_response(
            entities=tasks,
            total_count=total_count,
            page=request.page,
            page_size=request.page_size
        )


class GetTaskStatsUseCase:
    """
    Use case for getting task statistics for a user
    
    Provides aggregated information about user's tasks including
    counts by status and completion rates.
    """
    
    def __init__(self):
        """Initialize use case"""
        pass
    
    def execute(self, user_id: int) -> dict:
        """
        Execute get task statistics use case
        
        Args:
            user_id: ID of the user
            
        Returns:
            Dictionary with task statistics
        """
        logger.info(
            "get_task_stats_started",
            extra={"user_id": user_id}
        )
        
        try:
            with UnitOfWork() as uow:
                # Get all tasks for user
                all_tasks = uow.task_repository.find_tasks_by_user_id(user_id)
                
                # Calculate statistics
                stats = self._calculate_statistics(all_tasks)
                stats["user_id"] = user_id
                
                logger.info(
                    "get_task_stats_completed",
                    extra={
                        "user_id": user_id,
                        "total_tasks": stats["total_tasks"]
                    }
                )
                
                return stats
                
        except Exception as e:
            logger.error(
                "get_task_stats_failed",
                extra={
                    "user_id": user_id,
                    "error_type": type(e).__name__,
                    "error_message": str(e)
                }
            )
            raise
    
    def _calculate_statistics(self, tasks: List[TaskEntity]) -> dict:
        """
        Calculate task statistics from task list
        
        Args:
            tasks: List of task entities
            
        Returns:
            Dictionary with calculated statistics
        """
        total_tasks = len(tasks)
        
        if total_tasks == 0:
            return {
                "total_tasks": 0,
                "pending_tasks": 0,
                "in_progress_tasks": 0,
                "completed_tasks": 0,
                "cancelled_tasks": 0,
                "completion_rate": 0.0
            }
        
        # Count by status
        pending_count = sum(1 for task in tasks if task.status == TaskStatusEnum.PENDING)
        in_progress_count = sum(1 for task in tasks if task.status == TaskStatusEnum.IN_PROGRESS)
        completed_count = sum(1 for task in tasks if task.status == TaskStatusEnum.COMPLETED)
        cancelled_count = sum(1 for task in tasks if task.status == TaskStatusEnum.CANCELLED)
        
        # Calculate completion rate
        completion_rate = (completed_count / total_tasks) * 100 if total_tasks > 0 else 0.0
        
        return {
            "total_tasks": total_tasks,
            "pending_tasks": pending_count,
            "in_progress_tasks": in_progress_count,
            "completed_tasks": completed_count,
            "cancelled_tasks": cancelled_count,
            "completion_rate": round(completion_rate, 2)
        } 