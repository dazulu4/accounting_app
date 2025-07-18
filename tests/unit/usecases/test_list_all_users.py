import pytest
from unittest.mock import Mock
from domain.usecases.list_all_users import ListAllUsersUseCase
from domain.models.user import User, UserStatus


class TestListAllUsersUseCase:
    """Pruebas unitarias para ListAllUsersUseCase"""

    @pytest.fixture
    def mock_user_gateway(self):
        """Mock del gateway de usuarios"""
        gateway = Mock()
        return gateway

    @pytest.fixture
    def use_case(self, mock_user_gateway):
        """Instancia del caso de uso con mocks"""
        return ListAllUsersUseCase(mock_user_gateway)

    @pytest.fixture
    def sample_users(self):
        """Usuarios de ejemplo para pruebas"""
        return [
            User(
                user_id=1,
                name="user1",
                status=UserStatus.ACTIVE
            ),
            User(
                user_id=2,
                name="user2",
                status=UserStatus.ACTIVE
            ),
            User(
                user_id=3,
                name="user3",
                status=UserStatus.INACTIVE
            )
        ]

    def test_list_users_success(self, use_case, mock_user_gateway, sample_users):
        """Test: Listar usuarios exitosamente"""
        # Arrange
        mock_user_gateway.get_all.return_value = sample_users

        # Act
        result = use_case.execute()

        # Assert
        assert isinstance(result, list)
        assert len(result) == 3
        assert all(isinstance(user, User) for user in result)
        
        mock_user_gateway.get_all.assert_called_once()

    def test_list_users_empty(self, use_case, mock_user_gateway):
        """Test: Lista vacía cuando no hay usuarios"""
        # Arrange
        mock_user_gateway.get_all.return_value = []

        # Act
        result = use_case.execute()

        # Assert
        assert isinstance(result, list)
        assert len(result) == 0
        
        mock_user_gateway.get_all.assert_called_once()

    def test_list_users_repository_error(self, use_case, mock_user_gateway):
        """Test: Error del repositorio"""
        # Arrange
        mock_user_gateway.get_all.side_effect = Exception("Error de base de datos")

        # Act & Assert
        with pytest.raises(Exception, match="Error de base de datos"):
            use_case.execute()

        mock_user_gateway.get_all.assert_called_once()

    def test_list_users_mixed_status(self, use_case, mock_user_gateway, sample_users):
        """Test: Listar usuarios con diferentes estados"""
        # Arrange
        mock_user_gateway.get_all.return_value = sample_users

        # Act
        result = use_case.execute()

        # Assert
        assert len(result) == 3
        assert any(user.status == UserStatus.ACTIVE for user in result)
        assert any(user.status == UserStatus.INACTIVE for user in result)

    def test_list_users_only_active(self, use_case, mock_user_gateway):
        """Test: Listar solo usuarios activos"""
        # Arrange
        active_users = [
            User(
                user_id=1,
                name="active1",
                status=UserStatus.ACTIVE
            ),
            User(
                user_id=2,
                name="active2",
                status=UserStatus.ACTIVE
            )
        ]
        mock_user_gateway.get_all.return_value = active_users

        # Act
        result = use_case.execute()

        # Assert
        assert len(result) == 2
        assert all(user.status == UserStatus.ACTIVE for user in result)

    def test_list_users_only_inactive(self, use_case, mock_user_gateway):
        """Test: Listar solo usuarios inactivos"""
        # Arrange
        inactive_users = [
            User(
                user_id=1,
                name="inactive1",
                status=UserStatus.INACTIVE
            ),
            User(
                user_id=2,
                name="inactive2",
                status=UserStatus.INACTIVE
            )
        ]
        mock_user_gateway.get_all.return_value = inactive_users

        # Act
        result = use_case.execute()

        # Assert
        assert len(result) == 2
        assert all(user.status == UserStatus.INACTIVE for user in result)

    def test_list_users_connection_timeout(self, use_case, mock_user_gateway):
        """Test: Timeout de conexión"""
        # Arrange
        mock_user_gateway.get_all.side_effect = TimeoutError("Timeout de conexión")

        # Act & Assert
        with pytest.raises(TimeoutError, match="Timeout de conexión"):
            use_case.execute()

        mock_user_gateway.get_all.assert_called_once()

    def test_list_users_database_unavailable(self, use_case, mock_user_gateway):
        """Test: Base de datos no disponible"""
        # Arrange
        mock_user_gateway.get_all.side_effect = ConnectionError("Base de datos no disponible")

        # Act & Assert
        with pytest.raises(ConnectionError, match="Base de datos no disponible"):
            use_case.execute()

        mock_user_gateway.get_all.assert_called_once()

    def test_list_users_large_dataset(self, use_case, mock_user_gateway):
        """Test: Listar gran cantidad de usuarios"""
        # Arrange
        large_user_list = [
            User(
                user_id=i,
                name=f"user{i}",
                status=UserStatus.ACTIVE if i % 2 == 0 else UserStatus.INACTIVE
            )
            for i in range(1, 101)  # 100 usuarios
        ]
        mock_user_gateway.get_all.return_value = large_user_list

        # Act
        result = use_case.execute()

        # Assert
        assert len(result) == 100
        assert all(isinstance(user, User) for user in result)
        assert all(1 <= user.user_id <= 100 for user in result)

    def test_list_users_with_duplicate_names(self, use_case, mock_user_gateway):
        """Test: Listar usuarios con nombres duplicados (caso edge)"""
        # Arrange
        users_with_duplicates = [
            User(
                user_id=1,
                name="duplicate_name",
                status=UserStatus.ACTIVE
            ),
            User(
                user_id=2,
                name="duplicate_name",
                status=UserStatus.INACTIVE
            )
        ]
        mock_user_gateway.get_all.return_value = users_with_duplicates

        # Act
        result = use_case.execute()

        # Assert
        assert len(result) == 2
        assert all(user.name == "duplicate_name" for user in result) 