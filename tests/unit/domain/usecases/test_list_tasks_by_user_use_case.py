from unittest.mock import MagicMock

import pytest

from domain.entities.task_entity import TaskEntity
from domain.entities.user_entity import UserEntity
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
            TaskEntity.create_new_task(
                title="Task 1",
                description="Desc 1",
                user_id=user_id,
            ),
            TaskEntity.create_new_task(
                title="Task 2",
                description="Desc 2",
                user_id=user_id,
            ),
        ]
        tasks[1].complete()  # Make second task completed

        mock_user_gateway.find_user_by_id.return_value = user
        mock_task_gateway.find_tasks_by_user_id.return_value = tasks

        use_case = ListTasksByUserUseCase(mock_task_gateway, mock_user_gateway)

        # Act
        result = use_case.execute(user_id)

        # Assert
        assert isinstance(result, list)
        assert len(result) == 2
        assert all(isinstance(task, TaskEntity) for task in result)
        assert result[0].title == "Task 1"
        assert result[1].title == "Task 2"
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

        use_case = ListTasksByUserUseCase(mock_task_gateway, mock_user_gateway)

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

        use_case = ListTasksByUserUseCase(mock_task_gateway, mock_user_gateway)

        # Act
        result = use_case.execute(user_id)

        # Assert
        assert isinstance(result, list)
        assert len(result) == 0
        mock_user_gateway.find_user_by_id.assert_called_once_with(user_id)
        mock_task_gateway.find_tasks_by_user_id.assert_called_once_with(user_id)


# Fixtures
@pytest.fixture
def mock_task_gateway():
    """Mock task gateway."""
    from domain.gateways.task_gateway import TaskGateway

    return MagicMock(spec=TaskGateway)


@pytest.fixture
def mock_user_gateway():
    """Mock user gateway."""
    from domain.gateways.user_gateway import UserGateway

    return MagicMock(spec=UserGateway)
