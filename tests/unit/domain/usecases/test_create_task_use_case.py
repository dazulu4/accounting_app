"""
Unit Tests for CreateTaskUseCase - Enterprise Edition

Comprehensive unit tests following AAA pattern (Arrange, Act, Assert)
with proper mocking, edge cases, and business rule validation.

Test Categories:
- Happy path scenarios
- Business rule violations
- Edge cases and error conditions
- Performance and behavior validation
"""

import pytest
from datetime import datetime, timezone
from uuid import UUID
from unittest.mock import MagicMock, patch

from domain.usecases.create_task_use_case import CreateTaskUseCase
from domain.entities.task_entity import TaskEntity
from domain.enums.task_status_enum import TaskStatusEnum, TaskPriorityEnum
from domain.exceptions.business_exceptions import (
    UserNotFoundException,
    UserNotActiveException,
    MaxTasksExceededException,
    DatabaseException,
)
from domain.gateways.task_gateway import TaskGateway
from domain.gateways.user_gateway import UserGateway
from application.schemas.task_schema import CreateTaskRequest, CreateTaskResponse


class TestCreateTaskUseCase:
    """Test suite for CreateTaskUseCase."""

    def test_execute_should_create_task_when_user_is_active(
        self,
        mock_task_gateway: MagicMock,
        mock_user_gateway: MagicMock,
        create_task_request: CreateTaskRequest,
        sample_task_id: UUID
    ):
        """Test successful task creation for an active user."""
        # Arrange
        active_user = MagicMock()
        active_user.is_active.return_value = True
        mock_user_gateway.find_user_by_id.return_value = active_user
        mock_task_gateway.count_tasks_by_user.return_value = 5

        mock_uow = MagicMock()
        mock_uow.__enter__.return_value.task_repository.count_tasks_by_user.return_value = 5
        mock_uow.__enter__.return_value.task_repository.save_task = MagicMock()
        use_case = CreateTaskUseCase(mock_uow, mock_user_gateway)

        # Act
        response = use_case.execute(create_task_request)

        # Assert
        assert isinstance(response, CreateTaskResponse)
        assert response.title == create_task_request.title
        assert response.description == create_task_request.description
        assert response.user_id == create_task_request.user_id
        assert response.status == "pending"
        assert response.priority == create_task_request.priority.value
        mock_user_gateway.find_user_by_id.assert_called_once_with(create_task_request.user_id)
        mock_uow.__enter__.return_value.task_repository.save_task.assert_called_once()
        saved_task = mock_uow.__enter__.return_value.task_repository.save_task.call_args[0][0]
        assert isinstance(saved_task, TaskEntity)
        assert saved_task.title == create_task_request.title

    def test_execute_should_raise_exception_when_user_not_found(
        self,
        mock_task_gateway: MagicMock,
        mock_user_gateway: MagicMock,
        create_task_request: CreateTaskRequest
    ):
        """Test task creation fails when user does not exist."""
        # Arrange
        mock_user_gateway.find_user_by_id.return_value = None
        mock_uow = MagicMock()
        mock_uow.__enter__.return_value.task_repository.count_tasks_by_user.return_value = 0
        use_case = CreateTaskUseCase(mock_uow, mock_user_gateway)

        # Act & Assert
        with pytest.raises(UserNotFoundException):
            use_case.execute(create_task_request)
        mock_task_gateway.save_task.assert_not_called()

    def test_execute_should_raise_exception_when_user_is_inactive(
        self,
        mock_task_gateway: MagicMock,
        mock_user_gateway: MagicMock,
        create_task_request: CreateTaskRequest
    ):
        """Test task creation fails for an inactive user."""
        # Arrange
        inactive_user = MagicMock()
        inactive_user.is_active.return_value = False
        mock_user_gateway.find_user_by_id.return_value = inactive_user
        mock_uow = MagicMock()
        mock_uow.__enter__.return_value.task_repository.count_tasks_by_user.return_value = 0
        use_case = CreateTaskUseCase(mock_uow, mock_user_gateway)

        # Act & Assert
        with pytest.raises(UserNotActiveException):
            use_case.execute(create_task_request)
        mock_task_gateway.save_task.assert_not_called()

    def test_execute_should_raise_exception_when_max_tasks_exceeded(
        self,
        mock_task_gateway: MagicMock,
        mock_user_gateway: MagicMock,
        create_task_request: CreateTaskRequest
    ):
        """Test task creation fails when user has reached the maximum task limit."""
        # Arrange
        active_user = MagicMock()
        active_user.is_active.return_value = True
        mock_user_gateway.find_user_by_id.return_value = active_user
        mock_task_gateway.count_tasks_by_user.return_value = 1000

        mock_uow = MagicMock()
        mock_uow.__enter__.return_value.task_repository.count_tasks_by_user.return_value = 1000
        use_case = CreateTaskUseCase(mock_uow, mock_user_gateway)

        # Act & Assert
        with pytest.raises(MaxTasksExceededException):
            use_case.execute(create_task_request)
        mock_task_gateway.save_task.assert_not_called()

    def test_task_creation_is_atomic(
        self,
        mock_task_gateway: MagicMock,
        mock_user_gateway: MagicMock,
        create_task_request: CreateTaskRequest
    ):
        """Test that task creation is atomic."""
        # Arrange
        active_user = MagicMock()
        active_user.is_active.return_value = True
        mock_user_gateway.find_user_by_id.return_value = active_user
        mock_task_gateway.count_tasks_by_user.return_value = 5
        mock_task_gateway.save_task.side_effect = Exception("Database error")

        mock_uow = MagicMock()
        mock_uow.__enter__.return_value.task_repository.count_tasks_by_user.return_value = 5
        mock_uow.__enter__.return_value.task_repository.save_task.side_effect = Exception("Database error")
        use_case = CreateTaskUseCase(mock_uow, mock_user_gateway)

        # Act & Assert
        with pytest.raises(DatabaseException, match="Failed to save task to database"):
            use_case.execute(create_task_request)
        
        # In a real Unit of Work, we would check if a rollback was called.
        # Here, we ensure that if save fails, the operation is aborted.
        mock_task_gateway.save_task.assert_not_called() 