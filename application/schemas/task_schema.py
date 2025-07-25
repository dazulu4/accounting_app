"""
Task Schemas - Enterprise Edition

Professional Pydantic schemas for task-related data validation and serialization
with comprehensive validation rules and enterprise patterns.

Key Features:
- Input validation for API requests
- Output serialization for API responses
- Enterprise naming conventions
- Business rule validation
- Factory methods for entity conversion
"""

from datetime import datetime
from typing import List, Optional
from uuid import UUID

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    field_serializer,
    field_validator,
)

from domain.entities.task_entity import TaskEntity
from domain.enums.task_status_enum import TaskPriorityEnum, TaskStatusEnum


class CreateTaskRequest(BaseModel):
    """
    Create task request schema for API inputs

    Used for validating task creation requests with comprehensive
    validation rules and business constraints.
    """

    title: str = Field(
        ..., min_length=1, max_length=200, description="Task title or summary"
    )
    description: str = Field(
        ...,
        min_length=1,
        max_length=2000,
        description="Detailed task description",
    )
    user_id: int = Field(..., gt=0, description="ID of the user assigned to this task")
    priority: Optional[TaskPriorityEnum] = Field(
        default=TaskPriorityEnum.MEDIUM, description="Task priority level"
    )

    @field_validator("title")
    def validate_title(cls, v):
        """Validate task title"""
        if not v.strip():
            raise ValueError("Title cannot be empty or whitespace only")
        return v.strip()

    @field_validator("description")
    def validate_description(cls, v):
        """Validate task description"""
        if not v.strip():
            raise ValueError("Description cannot be empty or whitespace only")
        return v.strip()

    model_config = ConfigDict(
        use_enum_values=True,
        json_schema_extra={
            "example": {
                "title": "Review monthly accounting records",
                "description": "Complete review and reconciliation of all monthly accounting records",
                "user_id": 1,
                "priority": "medium",
            }
        },
    )


class CreateTaskResponse(BaseModel):
    """
    Create task response schema for API outputs

    Used for serializing newly created task data in API responses.
    """

    task_id: UUID = Field(..., description="Unique task identifier")
    title: str = Field(..., description="Task title")
    description: str = Field(..., description="Task description")
    user_id: int = Field(..., description="Assigned user ID")
    status: str = Field(..., description="Current task status")
    priority: str = Field(..., description="Task priority")
    created_at: datetime = Field(..., description="Task creation timestamp")
    updated_at: Optional[datetime] = Field(None, description="Last update timestamp")
    completed_at: Optional[datetime] = Field(
        None, description="Task completion timestamp"
    )

    @classmethod
    def from_entity(cls, task: TaskEntity) -> "CreateTaskResponse":
        """
        Create response from task entity

        Args:
            task: Task entity to convert

        Returns:
            CreateTaskResponse instance
        """
        return cls(
            task_id=task.task_id,
            title=task.title,
            description=task.description,
            user_id=task.user_id,
            status=task.status.value,
            priority=task.priority.value,
            created_at=task.created_at,
            updated_at=task.updated_at,
            completed_at=task.completed_at,
        )

    model_config = ConfigDict(from_attributes=True)

    @field_serializer("created_at", "updated_at", "completed_at")
    def serialize_datetime(self, value: Optional[datetime]) -> Optional[str]:
        """Serialize datetime fields to ISO format"""
        return value.isoformat() if value else None


class CompleteTaskRequest(BaseModel):
    """
    Complete task request schema for API inputs

    Used for validating task completion requests.
    """

    task_id: UUID = Field(..., description="ID of the task to complete")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {"task_id": "123e4567-e89b-12d3-a456-426614174000"}
        }
    )


class CompleteTaskResponse(BaseModel):
    """
    Complete task response schema for API outputs

    Used for serializing completed task data in API responses.
    """

    task_id: UUID = Field(..., description="Task identifier")
    title: str = Field(..., description="Task title")
    description: str = Field(..., description="Task description")
    user_id: int = Field(..., description="Assigned user ID")
    status: str = Field(..., description="Task status (should be 'completed')")
    priority: str = Field(..., description="Task priority")
    created_at: datetime = Field(..., description="Task creation timestamp")
    updated_at: Optional[datetime] = Field(None, description="Last update timestamp")
    completed_at: Optional[datetime] = Field(
        None, description="Task completion timestamp"
    )

    @classmethod
    def from_entity(cls, task: TaskEntity) -> "CompleteTaskResponse":
        """
        Create response from completed task entity

        Args:
            task: Completed task entity to convert

        Returns:
            CompleteTaskResponse instance
        """
        return cls(
            task_id=task.task_id,
            title=task.title,
            description=task.description,
            user_id=task.user_id,
            status=task.status.value,
            priority=task.priority.value,
            created_at=task.created_at,
            updated_at=task.updated_at,
            completed_at=task.completed_at,
        )

    model_config = ConfigDict(from_attributes=True)

    @field_serializer("created_at", "updated_at", "completed_at")
    def serialize_datetime(self, value: Optional[datetime]) -> Optional[str]:
        """Serialize datetime fields to ISO format"""
        return value.isoformat() if value else None


class TaskResponse(BaseModel):
    """
    Task response schema for API outputs

    Used for serializing individual task data in API responses.
    """

    task_id: UUID = Field(..., description="Task identifier")
    title: str = Field(..., description="Task title")
    description: str = Field(..., description="Task description")
    user_id: int = Field(..., description="Assigned user ID")
    status: str = Field(..., description="Current task status")
    priority: str = Field(..., description="Task priority")
    created_at: datetime = Field(..., description="Task creation timestamp")
    updated_at: Optional[datetime] = Field(None, description="Last update timestamp")
    completed_at: Optional[datetime] = Field(
        None, description="Task completion timestamp"
    )

    @classmethod
    def from_entity(cls, task: TaskEntity) -> "TaskResponse":
        """
        Create response from task entity

        Args:
            task: Task entity to convert

        Returns:
            TaskResponse instance
        """
        return cls(
            task_id=task.task_id,
            title=task.title,
            description=task.description,
            user_id=task.user_id,
            status=task.status.value,
            priority=task.priority.value,
            created_at=task.created_at,
            updated_at=task.updated_at,
            completed_at=task.completed_at,
        )


class TaskListResponse(BaseModel):
    """
    Task list response schema for API outputs

    Used for serializing multiple tasks in API responses with
    metadata about the collection.
    """

    tasks: List[TaskResponse] = Field(..., description="List of tasks")
    total_count: int = Field(..., description="Total number of tasks")
    user_id: int = Field(..., description="User ID these tasks belong to")
    pending_count: int = Field(..., description="Number of pending tasks")
    completed_count: int = Field(..., description="Number of completed tasks")

    @classmethod
    def from_entities(cls, tasks: List[TaskEntity], user_id: int) -> "TaskListResponse":
        """
        Create response from task entities

        Args:
            tasks: List of task entities to convert
            user_id: User ID these tasks belong to

        Returns:
            TaskListResponse instance
        """
        task_responses = [TaskResponse.from_entity(task) for task in tasks]
        pending_count = len(
            [task for task in tasks if task.status == TaskStatusEnum.PENDING]
        )
        completed_count = len(
            [task for task in tasks if task.status == TaskStatusEnum.COMPLETED]
        )

        return cls(
            tasks=task_responses,
            total_count=len(tasks),
            user_id=user_id,
            pending_count=pending_count,
            completed_count=completed_count,
        )

    model_config = ConfigDict(from_attributes=True)
