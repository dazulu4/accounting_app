from datetime import datetime, timezone
from uuid import uuid4

import pytest
from pydantic import ValidationError

from application.schemas.task_schema import (
    CompleteTaskResponse,
    CreateTaskRequest,
    CreateTaskResponse,
    TaskListResponse,
    TaskResponse,
)
from domain.entities.task_entity import TaskEntity
from domain.enums.task_status_enum import TaskPriorityEnum, TaskStatusEnum


class TestCreateTaskRequest:
    """Test suite for the CreateTaskRequest schema."""

    def test_create_task_request_success(self):
        """Test successful creation of a CreateTaskRequest."""
        data = {
            "title": "New Task",
            "description": "A valid description.",
            "user_id": 123,
            "priority": TaskPriorityEnum.HIGH,
        }
        req = CreateTaskRequest(**data)
        assert req.title == "New Task"
        assert req.priority == TaskPriorityEnum.HIGH

    @pytest.mark.parametrize(
        "invalid_data, expected_error",
        [
            (
                {"title": " ", "description": "d", "user_id": 1},
                "Title cannot be empty",
            ),
            (
                {"title": "t", "description": " ", "user_id": 1},
                "Description cannot be empty",
            ),
            (
                {"title": "t", "description": "d", "user_id": 0},
                "greater than 0",
            ),
        ],
    )
    def test_create_task_request_validation_error(self, invalid_data, expected_error):
        """Test validation errors for CreateTaskRequest."""
        with pytest.raises(ValidationError) as exc_info:
            CreateTaskRequest(**invalid_data)
        assert expected_error in str(exc_info.value)


class TestTaskResponseSchemas:
    """Test suite for response schemas that use from_entity."""

    @pytest.fixture
    def task_entity(self) -> TaskEntity:
        """Fixture for a sample TaskEntity."""
        return TaskEntity(
            task_id=uuid4(),
            title="Entity Task",
            description="Description from entity.",
            user_id=1,
            status=TaskStatusEnum.COMPLETED,
            priority=TaskPriorityEnum.URGENT,
            created_at=datetime.now(timezone.utc),
            completed_at=datetime.now(timezone.utc),
        )

    def test_create_task_response_from_entity(self, task_entity):
        """Test CreateTaskResponse.from_entity."""
        res = CreateTaskResponse.from_entity(task_entity)
        assert res.task_id == task_entity.task_id
        assert res.status == TaskStatusEnum.COMPLETED.value
        assert res.priority == TaskPriorityEnum.URGENT.value

    def test_complete_task_response_from_entity(self, task_entity):
        """Test CompleteTaskResponse.from_entity."""
        res = CompleteTaskResponse.from_entity(task_entity)
        assert res.task_id == task_entity.task_id
        assert res.completed_at is not None

    def test_task_response_from_entity(self, task_entity):
        """Test TaskResponse.from_entity."""
        res = TaskResponse.from_entity(task_entity)
        assert res.task_id == task_entity.task_id

    def test_task_list_response_from_entities(self, task_entity):
        """Test TaskListResponse.from_entities."""
        tasks = [task_entity]
        user_id = 1
        res = TaskListResponse.from_entities(tasks, user_id)
        assert len(res.tasks) == 1
        assert res.total_count == 1
        assert res.user_id == user_id
        assert res.completed_count == 1
        assert res.pending_count == 0
