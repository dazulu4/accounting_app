import pytest
from unittest.mock import Mock, AsyncMock
from uuid import uuid4
from domain.usecases.list_tasks_by_user import ListTasksByUserUseCase
from domain.models.task import Task, TaskStatus
from domain.models.user import User, UserStatus


class TestListTasksByUserUseCase:
    """Pruebas unitarias para ListTasksByUserUseCase"""

    @pytest.fixture
    def mock_task_gateway(self):
        """Mock del gateway de tareas"""
        gateway = Mock()
        gateway.list_by_user = AsyncMock()
        return gateway

    @pytest.fixture
    def use_case(self, mock_task_gateway):
        """Instancia del caso de uso con mocks"""
        return ListTasksByUserUseCase(mock_task_gateway)

    @pytest.fixture
    def sample_tasks(self):
        """Tareas de ejemplo para pruebas"""
        return [
            Task(
                task_id=uuid4(),
                title="Tarea 1",
                description="Descripción 1",
                user_id=1
            ),
            Task(
                task_id=uuid4(),
                title="Tarea 2",
                description="Descripción 2",
                user_id=1
            ),
            Task(
                task_id=uuid4(),
                title="Tarea 3",
                description="Descripción 3",
                user_id=1
            )
        ]

    @pytest.fixture
    def completed_task(self):
        """Tarea completada para pruebas"""
        task = Task(
            task_id=uuid4(),
            title="Tarea completada",
            description="Descripción completada",
            user_id=1
        )
        task.complete()
        return task

    @pytest.mark.asyncio
    async def test_list_tasks_success(self, use_case, mock_task_gateway, sample_tasks):
        """Test: Listar tareas exitosamente"""
        # Arrange
        user_id = 1
        mock_task_gateway.list_by_user.return_value = sample_tasks

        # Act
        result = await use_case.execute(user_id)

        # Assert
        assert isinstance(result, list)
        assert len(result) == 3
        assert all(isinstance(task, Task) for task in result)
        assert all(task.user_id == user_id for task in result)
        
        mock_task_gateway.list_by_user.assert_called_once_with(user_id)

    @pytest.mark.asyncio
    async def test_list_tasks_empty(self, use_case, mock_task_gateway):
        """Test: Lista vacía cuando el usuario no tiene tareas"""
        # Arrange
        user_id = 1
        mock_task_gateway.list_by_user.return_value = []

        # Act
        result = await use_case.execute(user_id)

        # Assert
        assert isinstance(result, list)
        assert len(result) == 0
        
        mock_task_gateway.list_by_user.assert_called_once_with(user_id)

    @pytest.mark.asyncio
    async def test_list_tasks_repository_error(self, use_case, mock_task_gateway):
        """Test: Error del repositorio"""
        # Arrange
        user_id = 1
        mock_task_gateway.list_by_user.side_effect = Exception("Error de base de datos")

        # Act & Assert
        with pytest.raises(Exception, match="Error de base de datos"):
            await use_case.execute(user_id)

        mock_task_gateway.list_by_user.assert_called_once_with(user_id)

    @pytest.mark.asyncio
    async def test_list_tasks_mixed_status(self, use_case, mock_task_gateway, sample_tasks, completed_task):
        """Test: Listar tareas con diferentes estados"""
        # Arrange
        user_id = 1
        mixed_tasks = sample_tasks + [completed_task]
        mock_task_gateway.list_by_user.return_value = mixed_tasks

        # Act
        result = await use_case.execute(user_id)

        # Assert
        assert len(result) == 4
        assert any(task.status == TaskStatus.NEW for task in result)
        assert any(task.status == TaskStatus.COMPLETED for task in result)
        assert all(task.user_id == user_id for task in result)

    @pytest.mark.asyncio
    async def test_list_tasks_different_user(self, use_case, mock_task_gateway):
        """Test: Listar tareas de un usuario diferente"""
        # Arrange
        user_id = 999
        mock_task_gateway.list_by_user.return_value = []

        # Act
        result = await use_case.execute(user_id)

        # Assert
        assert isinstance(result, list)
        assert len(result) == 0
        mock_task_gateway.list_by_user.assert_called_once_with(user_id)

    @pytest.mark.asyncio
    async def test_list_tasks_with_none_user_id(self, use_case, mock_task_gateway):
        """Test: Listar tareas con user_id None"""
        # Arrange
        user_id = None
        mock_task_gateway.list_by_user.return_value = []

        # Act
        result = await use_case.execute(user_id)

        # Assert
        assert isinstance(result, list)
        assert len(result) == 0
        mock_task_gateway.list_by_user.assert_called_once_with(user_id)

    @pytest.mark.asyncio
    async def test_list_tasks_connection_timeout(self, use_case, mock_task_gateway):
        """Test: Timeout de conexión"""
        # Arrange
        user_id = 1
        mock_task_gateway.list_by_user.side_effect = TimeoutError("Timeout de conexión")

        # Act & Assert
        with pytest.raises(TimeoutError, match="Timeout de conexión"):
            await use_case.execute(user_id)

        mock_task_gateway.list_by_user.assert_called_once_with(user_id)

    @pytest.mark.asyncio
    async def test_list_tasks_database_unavailable(self, use_case, mock_task_gateway):
        """Test: Base de datos no disponible"""
        # Arrange
        user_id = 1
        mock_task_gateway.list_by_user.side_effect = ConnectionError("Base de datos no disponible")

        # Act & Assert
        with pytest.raises(ConnectionError, match="Base de datos no disponible"):
            await use_case.execute(user_id)

        mock_task_gateway.list_by_user.assert_called_once_with(user_id) 