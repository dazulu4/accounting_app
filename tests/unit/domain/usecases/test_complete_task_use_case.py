"""
Unit Tests for CompleteTaskUseCase - Enterprise Edition

Comprehensive unit tests following AAA pattern for task completion
with proper mocking, state validation, and business rule testing.

Test Categories:
- Happy path task completion
- Invalid state transitions
- Task not found scenarios
- Business rule violations
- Performance validation
"""

import pytest
from unittest.mock import MagicMock
from uuid import UUID
from datetime import datetime, timezone

from domain.usecases.complete_task_use_case import CompleteTaskUseCase
from domain.entities.task_entity import (
    TaskEntity,
    TaskAlreadyCompletedException,
    TaskStateTransitionException,
)
from domain.enums.task_status_enum import TaskStatusEnum
from domain.exceptions.business_exceptions import TaskNotFoundException
from domain.gateways.task_gateway import TaskGateway
from application.schemas.task_schema import CompleteTaskRequest, CompleteTaskResponse


class TestCompleteTaskUseCase:
    """Test suite for CompleteTaskUseCase."""

    def test_execute_should_complete_task(
        self,
        mock_task_gateway: MagicMock,
        sample_task_id: UUID,
    ):
        """Test successful completion of a task."""
        # Arrange
        task = TaskEntity(
            task_id=sample_task_id,
            title="Test Task",
            description="Test Description",
            user_id=1,
            status=TaskStatusEnum.IN_PROGRESS,
            created_at=datetime.now(timezone.utc)
        )
        mock_task_gateway.find_task_by_id.return_value = task
        
        request = CompleteTaskRequest(task_id=sample_task_id)
        mock_uow = MagicMock()
        use_case = CompleteTaskUseCase(mock_task_gateway, mock_uow)

        # Act
        response = use_case.execute(request)

        # Assert
        assert isinstance(response, CompleteTaskResponse)
        assert response.status == TaskStatusEnum.COMPLETED.value
        mock_task_gateway.find_task_by_id.assert_called_once_with(sample_task_id)
        mock_task_gateway.save_task.assert_called_once()
        updated_task = mock_task_gateway.save_task.call_args[0][0]
        assert updated_task.status == TaskStatusEnum.COMPLETED

    def test_execute_should_raise_exception_when_task_not_found(
        self,
        mock_task_gateway: MagicMock,
        sample_task_id: UUID,
    ):
        """Test completion fails when the task does not exist."""
        # Arrange
        mock_task_gateway.find_task_by_id.return_value = None
        request = CompleteTaskRequest(task_id=sample_task_id)
        mock_uow = MagicMock()
        use_case = CompleteTaskUseCase(mock_task_gateway, mock_uow)

        # Act & Assert
        with pytest.raises(TaskNotFoundException):
            use_case.execute(request)
        mock_task_gateway.save_task.assert_not_called()

    def test_execute_should_raise_exception_when_task_already_completed(
        self,
        mock_task_gateway: MagicMock,
        completed_task_entity: TaskEntity
    ):
        """Test completion fails if the task is already completed."""
        # Arrange
        mock_task_gateway.find_task_by_id.return_value = completed_task_entity
        request = CompleteTaskRequest(task_id=completed_task_entity.task_id)
        mock_uow = MagicMock()
        use_case = CompleteTaskUseCase(mock_task_gateway, mock_uow)

        # Act & Assert
        with pytest.raises(TaskAlreadyCompletedException):
            use_case.execute(request)
        mock_task_gateway.save_task.assert_not_called()

    def test_execute_should_raise_exception_for_invalid_transition(
        self,
        mock_task_gateway: MagicMock,
        sample_task_id: UUID,
    ):
        """Test completion fails for a task with a status that cannot be completed."""
        # Arrange
        task = TaskEntity(
            task_id=sample_task_id,
            title="Cancelled Task",
            description=".",
            user_id=1,
            status=TaskStatusEnum.CANCELLED,
            created_at=datetime.now(timezone.utc)
        )
        mock_task_gateway.find_task_by_id.return_value = task
        request = CompleteTaskRequest(task_id=sample_task_id)
        mock_uow = MagicMock()
        use_case = CompleteTaskUseCase(mock_task_gateway, mock_uow)

        # Act & Assert
        with pytest.raises(TaskStateTransitionException):
            use_case.execute(request)
        mock_task_gateway.save_task.assert_not_called() 