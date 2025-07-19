"""
Task Data Transfer Objects (DTOs) - Domain Layer

This module contains DTOs for task operations following Clean Architecture principles.
DTOs serve as contracts between the application layer and external interfaces,
ensuring data validation and proper serialization.

Key Features:
- Request/Response pattern implementation
- Enterprise naming conventions
- Input validation with Pydantic
- Immutable data structures
- Clear separation from domain entities
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional, List
from uuid import UUID
from pydantic import BaseModel, Field, validator

from domain.enums.task_status_enum import TaskStatusEnum, TaskPriorityEnum
from domain.constants.task_constants import TaskConstants


# =============================================================================
# REQUEST DTOs - Input validation and data contracts
# =============================================================================

class CreateTaskRequest(BaseModel):
    """
    Request DTO for creating a new task
    
    This DTO validates input data for task creation operations,
    ensuring all business rules are met before processing.
    """
    
    title: str = Field(
        ...,
        min_length=TaskConstants.TITLE_MIN_LENGTH,
        max_length=TaskConstants.TITLE_MAX_LENGTH,
        description="Task title"
    )
    
    description: str = Field(
        ...,
        min_length=TaskConstants.DESCRIPTION_MIN_LENGTH,
        max_length=TaskConstants.DESCRIPTION_MAX_LENGTH,
        description="Task description"
    )
    
    user_id: int = Field(
        ...,
        gt=0,
        description="ID of the user to assign the task to"
    )
    
    priority: Optional[TaskPriorityEnum] = Field(
        default=TaskPriorityEnum.MEDIUM,
        description="Task priority level"
    )
    
    @validator('title')
    def validate_title(cls, v):
        """Validate task title"""
        if not v or not v.strip():
            raise ValueError("Task title cannot be empty or whitespace only")
        return v.strip()
    
    @validator('description')
    def validate_description(cls, v):
        """Validate task description"""
        if not v or not v.strip():
            raise ValueError("Task description cannot be empty or whitespace only")
        return v.strip()


class UpdateTaskRequest(BaseModel):
    """
    Request DTO for updating an existing task
    
    Supports partial updates - only provided fields will be updated.
    """
    
    title: Optional[str] = Field(
        None,
        min_length=TaskConstants.TITLE_MIN_LENGTH,
        max_length=TaskConstants.TITLE_MAX_LENGTH,
        description="New task title"
    )
    
    description: Optional[str] = Field(
        None,
        min_length=TaskConstants.DESCRIPTION_MIN_LENGTH,
        max_length=TaskConstants.DESCRIPTION_MAX_LENGTH,
        description="New task description"
    )
    
    priority: Optional[TaskPriorityEnum] = Field(
        None,
        description="New task priority level"
    )
    
    @validator('title')
    def validate_title(cls, v):
        """Validate task title if provided"""
        if v is not None and (not v or not v.strip()):
            raise ValueError("Task title cannot be empty or whitespace only")
        return v.strip() if v else v
    
    @validator('description')
    def validate_description(cls, v):
        """Validate task description if provided"""
        if v is not None and (not v or not v.strip()):
            raise ValueError("Task description cannot be empty or whitespace only")
        return v.strip() if v else v


class CompleteTaskRequest(BaseModel):
    """
    Request DTO for completing a task
    
    Simple DTO that may be extended in the future with completion notes,
    time tracking, or other completion-related data.
    """
    
    completion_notes: Optional[str] = Field(
        None,
        max_length=500,
        description="Optional notes about task completion"
    )


class GetTasksByUserRequest(BaseModel):
    """
    Request DTO for retrieving tasks by user ID
    
    Supports filtering by status and pagination.
    """
    
    user_id: int = Field(
        ...,
        gt=0,
        description="ID of the user whose tasks to retrieve"
    )
    
    status_filter: Optional[TaskStatusEnum] = Field(
        None,
        description="Filter tasks by status (optional)"
    )
    
    page: int = Field(
        default=1,
        ge=1,
        description="Page number for pagination"
    )
    
    page_size: int = Field(
        default=20,
        ge=1,
        le=100,
        description="Number of tasks per page"
    )


# =============================================================================
# RESPONSE DTOs - Output data contracts
# =============================================================================

class TaskResponse(BaseModel):
    """
    Response DTO for task data
    
    This DTO provides a consistent format for returning task information
    to external interfaces while hiding internal implementation details.
    """
    
    task_id: str = Field(..., description="Unique task identifier")
    title: str = Field(..., description="Task title")
    description: str = Field(..., description="Task description")
    user_id: int = Field(..., description="ID of assigned user")
    status: str = Field(..., description="Current task status")
    priority: str = Field(..., description="Task priority level")
    created_at: str = Field(..., description="Task creation timestamp (ISO format)")
    completed_at: Optional[str] = Field(None, description="Task completion timestamp (ISO format)")
    updated_at: Optional[str] = Field(None, description="Last update timestamp (ISO format)")
    
    # Computed fields
    is_active: bool = Field(..., description="Whether task is active (can be worked on)")
    is_completed: bool = Field(..., description="Whether task is completed")
    age_in_days: int = Field(..., description="Task age in days since creation")


class CreateTaskResponse(BaseModel):
    """
    Response DTO for task creation operations
    
    Returns essential information about the newly created task.
    """
    
    task_id: str = Field(..., description="Unique identifier of created task")
    title: str = Field(..., description="Title of created task")
    status: str = Field(..., description="Initial status of created task")
    created_at: str = Field(..., description="Creation timestamp (ISO format)")
    message: str = Field(default="Task created successfully", description="Success message")


class TaskListResponse(BaseModel):
    """
    Response DTO for task list operations
    
    Provides paginated list of tasks with metadata.
    """
    
    tasks: List[TaskResponse] = Field(..., description="List of tasks")
    total_count: int = Field(..., description="Total number of tasks (all pages)")
    page: int = Field(..., description="Current page number")
    page_size: int = Field(..., description="Number of tasks per page")
    total_pages: int = Field(..., description="Total number of pages")
    has_next: bool = Field(..., description="Whether there are more pages")
    has_previous: bool = Field(..., description="Whether there are previous pages")


class TaskStatsResponse(BaseModel):
    """
    Response DTO for task statistics
    
    Provides aggregated information about tasks for a user or system.
    """
    
    total_tasks: int = Field(..., description="Total number of tasks")
    pending_tasks: int = Field(..., description="Number of pending tasks")
    in_progress_tasks: int = Field(..., description="Number of in-progress tasks")
    completed_tasks: int = Field(..., description="Number of completed tasks")
    cancelled_tasks: int = Field(..., description="Number of cancelled tasks")
    completion_rate: float = Field(..., description="Task completion rate (0-100)")


class OperationResultResponse(BaseModel):
    """
    Generic response DTO for operations that don't return specific data
    
    Used for delete, update, and other operations that primarily indicate success/failure.
    """
    
    success: bool = Field(..., description="Whether operation was successful")
    message: str = Field(..., description="Operation result message")
    operation: str = Field(..., description="Type of operation performed")
    timestamp: str = Field(..., description="Operation timestamp (ISO format)")


# =============================================================================
# DATACLASS DTOs - Internal use cases communication
# =============================================================================

@dataclass(frozen=True)
class CreateTaskCommand:
    """
    Immutable command object for task creation
    
    Used for internal communication between application layers.
    Does not include validation (handled by Request DTOs).
    """
    title: str
    description: str
    user_id: int
    priority: TaskPriorityEnum = TaskPriorityEnum.MEDIUM


@dataclass(frozen=True)
class UpdateTaskCommand:
    """
    Immutable command object for task updates
    
    Supports partial updates with None values for unchanged fields.
    """
    task_id: UUID
    title: Optional[str] = None
    description: Optional[str] = None
    priority: Optional[TaskPriorityEnum] = None


@dataclass(frozen=True)
class TaskQuery:
    """
    Immutable query object for task retrieval
    
    Encapsulates filtering and pagination parameters.
    """
    user_id: Optional[int] = None
    status_filter: Optional[TaskStatusEnum] = None
    page: int = 1
    page_size: int = 20
    include_completed: bool = True


# =============================================================================
# DTO MAPPERS - Conversion utilities
# =============================================================================

class TaskDtoMapper:
    """
    Utility class for converting between entities and DTOs
    
    Provides static methods for mapping domain entities to response DTOs
    and request DTOs to command objects.
    """
    
    @staticmethod
    def entity_to_response(entity) -> TaskResponse:
        """
        Convert TaskEntity to TaskResponse DTO
        
        Args:
            entity: TaskEntity instance
            
        Returns:
            TaskResponse: Response DTO
        """
        return TaskResponse(
            task_id=str(entity.task_id),
            title=entity.title,
            description=entity.description,
            user_id=entity.user_id,
            status=entity.status.value,
            priority=entity.priority.value,
            created_at=entity.created_at.isoformat(),
            completed_at=entity.completed_at.isoformat() if entity.completed_at else None,
            updated_at=entity.updated_at.isoformat() if entity.updated_at else None,
            is_active=entity.is_active(),
            is_completed=entity.is_completed(),
            age_in_days=entity.get_age_in_days()
        )
    
    @staticmethod
    def create_request_to_command(request: CreateTaskRequest) -> CreateTaskCommand:
        """
        Convert CreateTaskRequest to CreateTaskCommand
        
        Args:
            request: CreateTaskRequest DTO
            
        Returns:
            CreateTaskCommand: Internal command object
        """
        return CreateTaskCommand(
            title=request.title,
            description=request.description,
            user_id=request.user_id,
            priority=request.priority or TaskPriorityEnum.MEDIUM
        )
    
    @staticmethod
    def update_request_to_command(request: UpdateTaskRequest, task_id: UUID) -> UpdateTaskCommand:
        """
        Convert UpdateTaskRequest to UpdateTaskCommand
        
        Args:
            request: UpdateTaskRequest DTO
            task_id: UUID of the task to update
            
        Returns:
            UpdateTaskCommand: Internal command object
        """
        return UpdateTaskCommand(
            task_id=task_id,
            title=request.title,
            description=request.description,
            priority=request.priority
        )
    
    @staticmethod
    def entities_to_list_response(
        entities: List,
        total_count: int,
        page: int,
        page_size: int
    ) -> TaskListResponse:
        """
        Convert list of TaskEntity to TaskListResponse
        
        Args:
            entities: List of TaskEntity instances
            total_count: Total number of tasks (for pagination)
            page: Current page number
            page_size: Number of items per page
            
        Returns:
            TaskListResponse: Paginated response DTO
        """
        tasks = [TaskDtoMapper.entity_to_response(entity) for entity in entities]
        total_pages = (total_count + page_size - 1) // page_size
        
        return TaskListResponse(
            tasks=tasks,
            total_count=total_count,
            page=page,
            page_size=page_size,
            total_pages=total_pages,
            has_next=page < total_pages,
            has_previous=page > 1
        ) 