from unittest.mock import MagicMock

from domain.entities.user_entity import UserEntity
from domain.enums.user_status_enum import UserStatusEnum
from domain.usecases.list_all_users_use_case import ListAllUsersUseCase


class TestListAllUsersUseCase:
    """Test suite for ListAllUsersUseCase."""

    def test_list_all_users_no_filter(
        self,
        mock_user_gateway: MagicMock,
    ):
        """Test listing all users without any filter."""
        # Arrange
        users = [
            UserEntity(
                user_id=1,
                name="User A",
                email="a@test.com",
                status=UserStatusEnum.ACTIVE,
            ),
            UserEntity(
                user_id=2,
                name="User B",
                email="b@test.com",
                status=UserStatusEnum.INACTIVE,
            ),
        ]
        mock_user_gateway.find_all_users.return_value = users
        use_case = ListAllUsersUseCase(mock_user_gateway)

        # Act
        result = use_case.execute()

        # Assert
        assert len(result) == 2
        mock_user_gateway.find_all_users.assert_called_once()
        mock_user_gateway.find_users_by_status.assert_not_called()

    def test_list_all_users_with_active_filter(
        self,
        mock_user_gateway: MagicMock,
    ):
        """Test listing only active users."""
        # Arrange
        active_users = [
            UserEntity(
                user_id=1,
                name="User A",
                email="a@test.com",
                status=UserStatusEnum.ACTIVE,
            ),
        ]
        mock_user_gateway.find_users_by_status.return_value = active_users
        use_case = ListAllUsersUseCase(mock_user_gateway)

        # Act
        result = use_case.execute(status_filter=UserStatusEnum.ACTIVE)

        # Assert
        assert len(result) == 1
        assert result[0].status == UserStatusEnum.ACTIVE
        mock_user_gateway.find_users_by_status.assert_called_once_with(
            UserStatusEnum.ACTIVE
        )
        mock_user_gateway.find_all_users.assert_not_called()

    def test_list_all_users_empty_result(
        self,
        mock_user_gateway: MagicMock,
    ):
        """Test listing users returns an empty list when no users are found."""
        # Arrange
        mock_user_gateway.find_all_users.return_value = []
        use_case = ListAllUsersUseCase(mock_user_gateway)

        # Act
        result = use_case.execute()

        # Assert
        assert len(result) == 0
        mock_user_gateway.find_all_users.assert_called_once()
