from unittest.mock import MagicMock
from uuid import uuid4

import pytest

from domain.entities.task_entity import TaskEntity
from domain.entities.user_entity import UserEntity
from domain.enums.task_status_enum import TaskStatusEnum
from domain.exceptions.business_exceptions import UserNotFoundException
from domain.usecases.list_tasks_by_user_use_case import ListTasksByUserUseCase


class TestListTasksByUserUseCase:
    """Test suite for ListTasksByUserUseCase."""

    def test_list_tasks_by_user_success(
        self,
        mock_task_gateway: MagicMock,
        mock_user_gateway: MagicMock,
    ):
        """Test listing tasks for a user successfully."""
        # Arrange
        user_id = 1
        user = UserEntity(
            user_id=user_id,
            name="Test User",
            email="test@test.com",
            status="active",
        )
        tasks = [
            TaskEntity(
                task_id=uuid4(),
                title="Task 1",
                description="Desc 1",
                user_id=user_id,
                status=TaskStatusEnum.PENDING,
            ),
            TaskEntity(
                task_id=uuid4(),
                title="Task 2",
                description="Desc 2",
                user_id=user_id,
                status=TaskStatusEnum.COMPLETED,
            ),
        ]

        mock_user_gateway.find_user_by_id.return_value = user
        mock_task_gateway.find_tasks_by_user_id.return_value = tasks

        mock_uow = MagicMock()
        use_case = ListTasksByUserUseCase(
            mock_task_gateway, mock_user_gateway, mock_uow
        )

        # Act
        result = use_case.execute(user_id)

        # Assert
        assert len(result.tasks) == 2
        assert result.tasks[0].title == "Task 1"
        mock_user_gateway.find_user_by_id.assert_called_once_with(user_id)
        mock_task_gateway.find_tasks_by_user_id.assert_called_once_with(user_id)

    def test_list_tasks_user_not_found(
        self,
        mock_task_gateway: MagicMock,
        mock_user_gateway: MagicMock,
    ):
        """Test listing tasks fails when the user is not found."""
        # Arrange
        user_id = 999
        mock_user_gateway.find_user_by_id.return_value = None

        mock_uow = MagicMock()
        use_case = ListTasksByUserUseCase(
            mock_task_gateway, mock_user_gateway, mock_uow
        )

        # Act & Assert
        with pytest.raises(UserNotFoundException):
            use_case.execute(user_id)

        mock_user_gateway.find_user_by_id.assert_called_once_with(user_id)
        mock_task_gateway.find_tasks_by_user_id.assert_not_called()

    def test_list_tasks_no_tasks_found(
        self,
        mock_task_gateway: MagicMock,
        mock_user_gateway: MagicMock,
    ):
        """Test listing tasks returns an empty list when no tasks are found."""
        # Arrange
        user_id = 2
        user = UserEntity(
            user_id=user_id,
            name="User with no tasks",
            email="no@tasks.com",
            status="active",
        )

        mock_user_gateway.find_user_by_id.return_value = user
        mock_task_gateway.find_tasks_by_user_id.return_value = []

        mock_uow = MagicMock()
        use_case = ListTasksByUserUseCase(
            mock_task_gateway, mock_user_gateway, mock_uow
        )

        # Act
        result = use_case.execute(user_id)

        # Assert
        assert len(result.tasks) == 0
        mock_user_gateway.find_user_by_id.assert_called_once_with(user_id)
        mock_task_gateway.find_tasks_by_user_id.assert_called_once_with(user_id)
