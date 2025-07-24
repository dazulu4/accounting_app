import pytest
from unittest.mock import MagicMock
from uuid import uuid4
from datetime import datetime, timezone

from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from infrastructure.driven_adapters.repositories.task_repository import (
    TaskRepository,
    TaskModelMapper,
    TaskModel,
)
from domain.entities.task_entity import TaskEntity, TaskDomainException
from domain.enums.task_status_enum import TaskStatusEnum, TaskPriorityEnum


@pytest.fixture
def mock_session():
    """Fixture for a mocked SQLAlchemy session."""
    return MagicMock()


@pytest.fixture
def task_entity():
    """Fixture for a sample TaskEntity."""
    return TaskEntity(
        task_id=uuid4(),
        title="Test Task",
        description="A task for testing.",
        user_id=1,
        status=TaskStatusEnum.PENDING,
        priority=TaskPriorityEnum.MEDIUM,
        created_at=datetime.now(timezone.utc),
    )


class TestTaskRepository:
    """Test suite for the TaskRepository."""

    def test_save_task_success(self, mock_session, task_entity):
        """Test successful saving of a task."""
        repo = TaskRepository(mock_session)
        repo.save_task(task_entity)

        mock_session.merge.assert_called_once()
        mock_session.commit.assert_called_once()
        mock_session.rollback.assert_not_called()

    def test_save_task_integrity_error(self, mock_session, task_entity):
        """Test handling of IntegrityError during save."""
        mock_session.commit.side_effect = IntegrityError(
            "mocked integrity error", [], None
        )
        repo = TaskRepository(mock_session)

        with pytest.raises(TaskDomainException):
            repo.save_task(task_entity)

        mock_session.rollback.assert_called_once()

    def test_find_task_by_id_found(self, mock_session, task_entity):
        """Test finding a task by ID when it exists."""
        # Create a real TaskModel instead of a mock
        from infrastructure.driven_adapters.repositories.task_repository import (
            TaskModel,
        )

        mock_model = TaskModel(
            task_id=task_entity.task_id,
            title=task_entity.title,
            description=task_entity.description,
            user_id=task_entity.user_id,
            status=task_entity.status.value,
            priority=task_entity.priority.value,
            created_at=task_entity.created_at,
            completed_at=task_entity.completed_at,
            updated_at=task_entity.updated_at,
        )

        # Configure the mock to return our real model
        mock_session.get.return_value = mock_model

        repo = TaskRepository(mock_session)
        result = repo.find_task_by_id(task_entity.task_id)

        assert result is not None
        assert result.task_id == task_entity.task_id
        mock_session.get.assert_called_once_with(TaskModel, task_entity.task_id)

    def test_find_task_by_id_not_found(self, mock_session):
        """Test finding a task by ID when it does not exist."""
        # Configure mock to return None for not found
        mock_session.get.return_value = None

        repo = TaskRepository(mock_session)
        result = repo.find_task_by_id(uuid4())

        assert result is None
        mock_session.get.assert_called_once()


class TestTaskModelMapper:
    """Test suite for the TaskModelMapper."""

    def test_entity_to_model(self, task_entity):
        """Test mapping from TaskEntity to TaskModel."""
        model = TaskModelMapper.entity_to_model(task_entity)
        assert isinstance(model, TaskModel)
        assert model.task_id == task_entity.task_id
        assert model.status == task_entity.status.value

    def test_model_to_entity(self):
        """Test mapping from TaskModel to TaskEntity."""
        model = TaskModel(
            task_id=uuid4(),
            title="Model Task",
            description="A model for testing.",
            user_id=2,
            status="in_progress",
            priority="high",
            created_at=datetime.now(timezone.utc),
        )
        entity = TaskModelMapper.model_to_entity(model)
        assert isinstance(entity, TaskEntity)
        assert entity.task_id == model.task_id
        assert entity.status == TaskStatusEnum.IN_PROGRESS

    def test_model_to_entity_invalid_status(self):
        """Test mapping with an invalid status raises an exception."""
        model = TaskModel(
            task_id=uuid4(),
            title="Invalid",
            description=".",
            user_id=1,
            status="INVALID_STATUS",
            priority="LOW",
            created_at=datetime.now(timezone.utc),
        )
        with pytest.raises(TaskDomainException):
            TaskModelMapper.model_to_entity(model)
