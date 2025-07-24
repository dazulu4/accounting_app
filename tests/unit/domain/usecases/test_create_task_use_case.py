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
from domain.entities.user_entity import UserEntity
from domain.enums.task_status_enum import TaskStatusEnum, TaskPriorityEnum
from domain.enums.user_status_enum import UserStatusEnum
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
        sample_task_id: UUID,
    ):
        """Test successful task creation for an active user."""
        # Arrange
        active_user = UserEntity(
            user_id=1,
            name="Test User",
            email="test@example.com",
            status=UserStatusEnum.ACTIVE,
        )
        mock_user_gateway.find_user_by_id.return_value = active_user

        # Mock task count for user
        mock_task_gateway.count_tasks_by_user.return_value = 5

        use_case = CreateTaskUseCase(mock_task_gateway, mock_user_gateway)

        # Act
        response = use_case.execute(create_task_request)

        # Assert
        assert isinstance(response, CreateTaskResponse)
        assert response.title == create_task_request.title
        assert response.description == create_task_request.description
        assert response.user_id == create_task_request.user_id
        assert response.status == "pending"
        # Compare priority values directly
        expected_priority = (
            create_task_request.priority.value
            if hasattr(create_task_request.priority, "value")
            else create_task_request.priority
        )
        assert response.priority == expected_priority

        mock_user_gateway.find_user_by_id.assert_called_once_with(
            create_task_request.user_id
        )
        mock_task_gateway.count_tasks_by_user.assert_called_once_with(
            create_task_request.user_id
        )
        mock_task_gateway.save_task.assert_called_once()

    def test_execute_should_raise_exception_when_user_not_found(
        self,
        mock_task_gateway: MagicMock,
        mock_user_gateway: MagicMock,
        create_task_request: CreateTaskRequest,
    ):
        """Test task creation fails when user does not exist."""
        # Arrange
        mock_user_gateway.find_user_by_id.return_value = None
        use_case = CreateTaskUseCase(mock_task_gateway, mock_user_gateway)

        # Act & Assert
        with pytest.raises(UserNotFoundException):
            use_case.execute(create_task_request)
        mock_task_gateway.save_task.assert_not_called()

    def test_execute_should_raise_exception_when_user_is_inactive(
        self,
        mock_task_gateway: MagicMock,
        mock_user_gateway: MagicMock,
        create_task_request: CreateTaskRequest,
    ):
        """Test task creation fails for an inactive user."""
        # Arrange
        inactive_user = UserEntity(
            user_id=1,
            name="Test User",
            email="test@example.com",
            status=UserStatusEnum.SUSPENDED,
        )
        mock_user_gateway.find_user_by_id.return_value = inactive_user
        use_case = CreateTaskUseCase(mock_task_gateway, mock_user_gateway)

        # Act & Assert
        with pytest.raises(UserNotActiveException):
            use_case.execute(create_task_request)
        mock_task_gateway.save_task.assert_not_called()

    def test_execute_should_raise_exception_when_max_tasks_exceeded(
        self,
        mock_task_gateway: MagicMock,
        mock_user_gateway: MagicMock,
        create_task_request: CreateTaskRequest,
    ):
        """Test task creation fails when user has reached task limit."""
        # Arrange
        active_user = UserEntity(
            user_id=1,
            name="Test User",
            email="test@example.com",
            status=UserStatusEnum.ACTIVE,
        )
        mock_user_gateway.find_user_by_id.return_value = active_user

        # Mock 10 existing tasks (max limit)
        mock_task_gateway.count_tasks_by_user.return_value = 10

        use_case = CreateTaskUseCase(mock_task_gateway, mock_user_gateway)

        # Act & Assert
        with pytest.raises(MaxTasksExceededException):
            use_case.execute(create_task_request)
        mock_task_gateway.save_task.assert_not_called()

    def test_task_creation_is_atomic(
        self,
        mock_task_gateway: MagicMock,
        mock_user_gateway: MagicMock,
        create_task_request: CreateTaskRequest,
    ):
        """Test that task creation is atomic and fails completely on error."""
        # Arrange
        active_user = UserEntity(
            user_id=1,
            name="Test User",
            email="test@example.com",
            status=UserStatusEnum.ACTIVE,
        )
        mock_user_gateway.find_user_by_id.return_value = active_user
        mock_task_gateway.count_tasks_by_user.return_value = 5

        # Mock save to raise exception
        mock_task_gateway.save_task.side_effect = Exception("Database error")

        use_case = CreateTaskUseCase(mock_task_gateway, mock_user_gateway)

        # Act & Assert
        with pytest.raises(DatabaseException, match="Failed to save task"):
            use_case.execute(create_task_request)


# Fixtures
@pytest.fixture
def mock_task_gateway():
    """Mock task gateway."""
    mock = MagicMock(spec=TaskGateway)
    # Configure default return values
    mock.count_tasks_by_user.return_value = 0
    return mock


@pytest.fixture
def mock_user_gateway():
    """Mock user gateway."""
    return MagicMock(spec=UserGateway)


@pytest.fixture
def create_task_request():
    """Create task request fixture."""
    return CreateTaskRequest(
        title="Test Task",
        description="Test Description",
        user_id=1,
        priority=TaskPriorityEnum.MEDIUM,
    )


@pytest.fixture
def sample_task_id():
    """Sample task ID fixture."""
    return UUID("12345678-1234-5678-1234-567812345678")
