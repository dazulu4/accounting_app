import pytest
from unittest.mock import Mock, AsyncMock
from uuid import uuid4
from domain.usecases.create_task import CreateTaskUseCase
from domain.models.task import Task
from domain.models.user import User, UserStatus


class TestCreateTaskUseCase:
    """Pruebas unitarias para CreateTaskUseCase"""

    @pytest.fixture
    def mock_task_gateway(self):
        """Mock del gateway de tareas"""
        gateway = Mock()
        gateway.save = AsyncMock()
        return gateway

    @pytest.fixture
    def mock_user_gateway(self):
        """Mock del gateway de usuarios"""
        gateway = Mock()
        return gateway

    @pytest.fixture
    def active_user(self):
        """Usuario activo para pruebas"""
        return User(
            user_id=1,
            name="test_user",
            status=UserStatus.ACTIVE
        )

    @pytest.fixture
    def inactive_user(self):
        """Usuario inactivo para pruebas"""
        return User(
            user_id=2,
            name="inactive_user",
            status=UserStatus.INACTIVE
        )

    @pytest.fixture
    def use_case(self, mock_task_gateway, mock_user_gateway):
        """Instancia del caso de uso con mocks"""
        return CreateTaskUseCase(mock_task_gateway, mock_user_gateway)

    @pytest.mark.asyncio
    async def test_create_task_success(self, use_case, mock_task_gateway, mock_user_gateway, active_user):
        """Test: Crear tarea exitosamente"""
        # Arrange
        title = "Nueva tarea"
        description = "Descripción de la tarea"
        user_id = 1
        
        mock_user_gateway.get_by_id.return_value = active_user
        mock_task_gateway.save.return_value = None

        # Act
        result = await use_case.execute(title, description, user_id)

        # Assert
        assert isinstance(result, Task)
        assert result.title == title
        assert result.description == description
        assert result.user_id == user_id
        assert result.status.value == "NEW"
        assert result.completed_at is None
        
        mock_user_gateway.get_by_id.assert_called_once_with(user_id)
        mock_task_gateway.save.assert_called_once_with(result)

    @pytest.mark.asyncio
    async def test_create_task_user_not_found(self, use_case, mock_user_gateway):
        """Test: Error cuando el usuario no existe"""
        # Arrange
        title = "Nueva tarea"
        description = "Descripción de la tarea"
        user_id = 999
        
        mock_user_gateway.get_by_id.return_value = None

        # Act & Assert
        with pytest.raises(ValueError, match="Usuario no existe o está inactivo"):
            await use_case.execute(title, description, user_id)

        mock_user_gateway.get_by_id.assert_called_once_with(user_id)

    @pytest.mark.asyncio
    async def test_create_task_user_inactive(self, use_case, mock_user_gateway, inactive_user):
        """Test: Error cuando el usuario está inactivo"""
        # Arrange
        title = "Nueva tarea"
        description = "Descripción de la tarea"
        user_id = 2
        
        mock_user_gateway.get_by_id.return_value = inactive_user

        # Act & Assert
        with pytest.raises(ValueError, match="Usuario no existe o está inactivo"):
            await use_case.execute(title, description, user_id)

        mock_user_gateway.get_by_id.assert_called_once_with(user_id)

    @pytest.mark.asyncio
    async def test_create_task_invalid_data(self, use_case, mock_task_gateway, mock_user_gateway, active_user):
        """Test: Error con datos inválidos (usuario inexistente)"""
        # Arrange
        title = "Tarea válida"
        description = "Descripción de la tarea"
        user_id = 999  # Usuario inexistente
        
        mock_user_gateway.get_by_id.return_value = None

        # Act & Assert
        with pytest.raises(ValueError, match="Usuario no existe o está inactivo"):
            await use_case.execute(title, description, user_id)

    @pytest.mark.asyncio
    async def test_create_task_save_error(self, use_case, mock_task_gateway, mock_user_gateway, active_user):
        """Test: Error al guardar la tarea"""
        # Arrange
        title = "Nueva tarea"
        description = "Descripción de la tarea"
        user_id = 1
        
        mock_user_gateway.get_by_id.return_value = active_user
        mock_task_gateway.save.side_effect = Exception("Error de base de datos")

        # Act & Assert
        with pytest.raises(Exception, match="Error de base de datos"):
            await use_case.execute(title, description, user_id)

        mock_user_gateway.get_by_id.assert_called_once_with(user_id)
        mock_task_gateway.save.assert_called_once()

    @pytest.mark.asyncio
    async def test_create_task_with_empty_description(self, use_case, mock_task_gateway, mock_user_gateway, active_user):
        """Test: Crear tarea con descripción vacía"""
        # Arrange
        title = "Tarea sin descripción"
        description = ""
        user_id = 1
        
        mock_user_gateway.get_by_id.return_value = active_user
        mock_task_gateway.save.return_value = None

        # Act
        result = await use_case.execute(title, description, user_id)

        # Assert
        assert result.title == title
        assert result.description == description
        assert result.user_id == user_id

    @pytest.mark.asyncio
    async def test_create_task_generates_unique_id(self, use_case, mock_task_gateway, mock_user_gateway, active_user):
        """Test: Verificar que se genera un ID único para cada tarea"""
        # Arrange
        title = "Tarea 1"
        description = "Descripción 1"
        user_id = 1
        
        mock_user_gateway.get_by_id.return_value = active_user
        mock_task_gateway.save.return_value = None

        # Act
        result1 = await use_case.execute(title, description, user_id)
        result2 = await use_case.execute(title, description, user_id)

        # Assert
        assert result1.task_id != result2.task_id
        assert isinstance(result1.task_id, uuid4().__class__)
        assert isinstance(result2.task_id, uuid4().__class__) 