"""
Unit Tests for CompleteTaskUseCase - Simplified Edition

Comprehensive unit tests following AAA pattern for task completion
with proper mocking, state validation, and business rule testing.

Test Categories:
- Happy path task completion
- Invalid state transitions
- Task not found scenarios
- Business rule violations
"""

from unittest.mock import MagicMock
from uuid import UUID

import pytest

from domain.entities.task_entity import TaskEntity
from domain.enums.task_status_enum import TaskPriorityEnum, TaskStatusEnum
from domain.exceptions.business_exceptions import (
    TaskAlreadyCompletedException,
    TaskNotFoundException,
)
from domain.gateways.task_gateway import TaskGateway
from domain.usecases.complete_task_use_case import CompleteTaskUseCase


class TestCompleteTaskUseCase:
    """Test suite for CompleteTaskUseCase."""

    def test_execute_should_complete_task(
        self,
        mock_task_gateway: MagicMock,
        sample_task_id: UUID,
    ):
        """Test successful completion of a task."""
        # Arrange
        task = TaskEntity.create_new_task(
            title="Test Task",
            description="Test Description",
            user_id=1,
            priority=TaskPriorityEnum.MEDIUM,
        )
        task.start_task()  # Put it in IN_PROGRESS
        mock_task_gateway.find_task_by_id.return_value = task

        use_case = CompleteTaskUseCase(mock_task_gateway)

        # Act
        result = use_case.execute(sample_task_id)

        # Assert
        assert isinstance(result, TaskEntity)
        assert result.status == TaskStatusEnum.COMPLETED
        assert result.completed_at is not None
        mock_task_gateway.find_task_by_id.assert_called_once_with(sample_task_id)
        mock_task_gateway.save_task.assert_called_once_with(task)

    def test_execute_should_raise_exception_when_task_not_found(
        self,
        mock_task_gateway: MagicMock,
        sample_task_id: UUID,
    ):
        """Test completion fails when the task does not exist."""
        # Arrange
        mock_task_gateway.find_task_by_id.return_value = None
        use_case = CompleteTaskUseCase(mock_task_gateway)

        # Act & Assert
        with pytest.raises(TaskNotFoundException):
            use_case.execute(sample_task_id)
        mock_task_gateway.save_task.assert_not_called()

    def test_execute_should_raise_exception_when_task_already_completed(
        self, mock_task_gateway: MagicMock, sample_task_id: UUID
    ):
        """Test completion fails if the task is already completed."""
        # Arrange
        task = TaskEntity.create_new_task(
            title="Completed Task", description="Already completed", user_id=1
        )
        task.complete()  # Already completed
        mock_task_gateway.find_task_by_id.return_value = task
        use_case = CompleteTaskUseCase(mock_task_gateway)

        # Act & Assert
        with pytest.raises(TaskAlreadyCompletedException):
            use_case.execute(sample_task_id)
        # save_task should not be called because exception is raised before saving
        mock_task_gateway.save_task.assert_not_called()

    def test_execute_should_raise_exception_for_invalid_transition(
        self,
        mock_task_gateway: MagicMock,
        sample_task_id: UUID,
    ):
        """Test completion fails for a task with a status that cannot be completed."""
        # Arrange
        task = TaskEntity.create_new_task(
            title="Cancelled Task", description="This task was cancelled", user_id=1
        )
        task.cancel_task()  # Task is cancelled, cannot be completed
        mock_task_gateway.find_task_by_id.return_value = task
        use_case = CompleteTaskUseCase(mock_task_gateway)

        # Act & Assert
        with pytest.raises(
            TaskAlreadyCompletedException
        ):  # TaskEntity raises this for terminal states
            use_case.execute(sample_task_id)
        mock_task_gateway.save_task.assert_not_called()


# Fixtures
@pytest.fixture
def mock_task_gateway():
    """Mock task gateway."""
    return MagicMock(spec=TaskGateway)


@pytest.fixture
def sample_task_id():
    """Sample task ID fixture."""
    return UUID("12345678-1234-5678-1234-567812345678")
