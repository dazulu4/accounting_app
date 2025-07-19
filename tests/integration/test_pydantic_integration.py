"""
Integration Tests for Pydantic Schemas - Enterprise Edition

Integration tests verifying Pydantic schema validation and serialization
with enterprise patterns and comprehensive error testing.
"""

import pytest
from datetime import datetime, timezone
from uuid import uuid4
from pydantic import ValidationError

from application.schemas.task_schema import (
    CreateTaskRequest,
    CreateTaskResponse,
    TaskListResponse,
    CompleteTaskRequest,
    CompleteTaskResponse
)
from application.schemas.user_schema import UserResponse, UserListResponse
from domain.entities.user_entity import UserEntity
from domain.entities.task_entity import TaskEntity
from domain.enums.user_status_enum import UserStatusEnum
from domain.enums.task_status_enum import TaskStatusEnum, TaskPriorityEnum


class TestPydanticSchemaIntegration:
    """Integration tests for Pydantic schema validation"""
    
    def test_create_task_request_validation_success(self):
        """Test successful task creation request validation"""
        # Arrange
        valid_data = {
            "title": "Integration Test Task",
            "description": "Task for Pydantic integration testing",
            "user_id": 1
        }
        
        # Act
        request = CreateTaskRequest(**valid_data)
        
        # Assert
        assert request.title == "Integration Test Task"
        assert request.description == "Task for Pydantic integration testing"
        assert request.user_id == 1
    
    def test_create_task_request_validation_failure(self):
        """Test task creation request validation with invalid data"""
        # Arrange
        invalid_data = {
            "title": "",  # Empty title should fail
            "description": "Valid description",
            "user_id": 1
        }
        
        # Act & Assert
        with pytest.raises(ValidationError) as exc_info:
            CreateTaskRequest(**invalid_data)
        
        # Verify validation error details
        errors = exc_info.value.errors()
        assert len(errors) > 0
        assert any(error["loc"] == ("title",) for error in errors)
    
    def test_create_task_response_serialization(self):
        """Test task response schema serialization"""
        # Arrange
        task_entity = TaskEntity(
            task_id=uuid4(),
            title="Response Test Task",
            description="Testing response serialization",
            user_id=1,
            status=TaskStatusEnum.PENDING,
            priority=TaskPriorityEnum.MEDIUM,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        )
        
        # Act
        response = CreateTaskResponse.from_entity(task_entity)
        
        # Assert
        assert str(response.task_id) == str(task_entity.task_id)
        assert response.title == task_entity.title
        assert response.description == task_entity.description
        assert response.user_id == task_entity.user_id
        assert response.status == task_entity.status.value
        assert response.priority == task_entity.priority.value
    
    def test_user_response_serialization(self):
        """Test user response schema serialization"""
        # Arrange
        user_entity = UserEntity(
            user_id=1,
            name="Integration Test User",
            email="test@example.com",
            status=UserStatusEnum.ACTIVE
        )
        
        # Act
        response = UserResponse.from_entity(user_entity)
        
        # Assert
        assert response.user_id == user_entity.user_id
        assert response.name == user_entity.name
        assert response.email == user_entity.email
        assert response.status == user_entity.status.value
    
    def test_complete_task_response_with_completion_timestamp(self):
        """Test complete task response includes completion timestamp"""
        # Arrange
        completion_time = datetime.now(timezone.utc)
        task_entity = TaskEntity(
            task_id=uuid4(),
            title="Completed Task",
            description="Task that has been completed",
            user_id=1,
            status=TaskStatusEnum.COMPLETED,
            priority=TaskPriorityEnum.HIGH,
            created_at=datetime.now(timezone.utc),
            updated_at=completion_time,
            completed_at=completion_time
        )
        
        # Act
        response = CompleteTaskResponse.from_entity(task_entity)
        
        # Assert
        assert response.status == TaskStatusEnum.COMPLETED.value
        assert response.completed_at is not None
        assert response.completed_at == completion_time
    
    def test_task_list_response_with_multiple_tasks(self):
        """Test task list response with multiple tasks"""
        # Arrange
        tasks = [
            TaskEntity(
                task_id=uuid4(),
                title=f"Task {i}",
                description=f"Description {i}",
                user_id=1,
                status=TaskStatusEnum.PENDING,
                priority=TaskPriorityEnum.MEDIUM,
                created_at=datetime.now(timezone.utc),
                updated_at=datetime.now(timezone.utc)
            ) for i in range(3)
        ]
        
        # Act
        response = TaskListResponse.from_entities(tasks, user_id=1)
        
        # Assert
        assert len(response.tasks) == 3
        assert response.total_count == 3
        assert response.user_id == 1
        assert all(task.user_id == 1 for task in response.tasks)
    
    def test_schema_json_serialization_compatibility(self):
        """Test schema JSON serialization for API compatibility"""
        # Arrange
        task_entity = TaskEntity(
            task_id=uuid4(),
            title="JSON Test Task",
            description="Testing JSON serialization",
            user_id=1,
            status=TaskStatusEnum.IN_PROGRESS,
            priority=TaskPriorityEnum.URGENT,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        )
        
        # Act
        response = CreateTaskResponse.from_entity(task_entity)
        json_data = response.model_dump(mode="json")
        
        # Assert
        assert isinstance(json_data, dict)
        assert "task_id" in json_data
        assert "title" in json_data
        assert "status" in json_data
        assert "priority" in json_data
        assert json_data["status"] == TaskStatusEnum.IN_PROGRESS.value
        assert json_data["priority"] == TaskPriorityEnum.URGENT.value 