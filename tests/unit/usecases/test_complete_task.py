import pytest
from unittest.mock import Mock, AsyncMock
from uuid import uuid4
from datetime import datetime
from domain.usecases.complete_task import CompleteTaskUseCase
from domain.models.task import Task, TaskStatus
from domain.models.user import User, UserStatus


class TestCompleteTaskUseCase:
    """Pruebas unitarias para CompleteTaskUseCase"""

    @pytest.fixture
    def mock_task_gateway(self):
        """Mock del gateway de tareas"""
        gateway = Mock()
        gateway.get_by_id = AsyncMock()
        gateway.save = AsyncMock()
        return gateway

    @pytest.fixture
    def mock_event_bus(self):
        """Mock del bus de eventos"""
        event_bus = Mock()
        event_bus.send_task_completed = Mock()
        return event_bus

    @pytest.fixture
    def pending_task(self):
        """Tarea pendiente para pruebas"""
        return Task(
            task_id=uuid4(),
            title="Tarea pendiente",
            description="Descripción de la tarea",
            user_id=1
        )

    @pytest.fixture
    def completed_task(self):
        """Tarea completada para pruebas"""
        task = Task(
            task_id=uuid4(),
            title="Tarea completada",
            description="Descripción de la tarea",
            user_id=1
        )
        task.complete()
        return task

    @pytest.fixture
    def use_case_with_event_bus(self, mock_task_gateway, mock_event_bus):
        """Instancia del caso de uso con bus de eventos"""
        return CompleteTaskUseCase(mock_task_gateway, mock_event_bus)

    @pytest.fixture
    def use_case_without_event_bus(self, mock_task_gateway):
        """Instancia del caso de uso sin bus de eventos"""
        return CompleteTaskUseCase(mock_task_gateway)

    @pytest.mark.asyncio
    async def test_complete_task_success(self, use_case_without_event_bus, mock_task_gateway, pending_task):
        """Test: Completar tarea exitosamente"""
        # Arrange
        task_id = pending_task.task_id
        mock_task_gateway.get_by_id.return_value = pending_task
        mock_task_gateway.save.return_value = None

        # Act
        await use_case_without_event_bus.execute(task_id)

        # Assert
        assert pending_task.status == TaskStatus.COMPLETED
        assert pending_task.completed_at is not None
        assert isinstance(pending_task.completed_at, datetime)
        
        mock_task_gateway.get_by_id.assert_called_once_with(task_id)
        mock_task_gateway.save.assert_called_once_with(pending_task)

    @pytest.mark.asyncio
    async def test_complete_task_not_found(self, use_case_without_event_bus, mock_task_gateway):
        """Test: Error cuando la tarea no existe"""
        # Arrange
        task_id = uuid4()
        mock_task_gateway.get_by_id.return_value = None

        # Act & Assert
        with pytest.raises(ValueError, match="Tarea no encontrada"):
            await use_case_without_event_bus.execute(task_id)

        mock_task_gateway.get_by_id.assert_called_once_with(task_id)
        mock_task_gateway.save.assert_not_called()

    @pytest.mark.asyncio
    async def test_complete_task_with_event_bus(self, use_case_with_event_bus, mock_task_gateway, mock_event_bus, pending_task):
        """Test: Completar tarea con emisión de eventos"""
        # Arrange
        task_id = pending_task.task_id
        user_id = pending_task.user_id
        mock_task_gateway.get_by_id.return_value = pending_task
        mock_task_gateway.save.return_value = None

        # Act
        await use_case_with_event_bus.execute(task_id)

        # Assert
        assert pending_task.status == TaskStatus.COMPLETED
        mock_task_gateway.save.assert_called_once_with(pending_task)
        mock_event_bus.send_task_completed.assert_called_once_with(task_id, user_id)

    @pytest.mark.asyncio
    async def test_complete_task_without_event_bus(self, use_case_without_event_bus, mock_task_gateway, pending_task):
        """Test: Completar tarea sin emisión de eventos"""
        # Arrange
        task_id = pending_task.task_id
        mock_task_gateway.get_by_id.return_value = pending_task
        mock_task_gateway.save.return_value = None

        # Act
        await use_case_without_event_bus.execute(task_id)

        # Assert
        assert pending_task.status == TaskStatus.COMPLETED
        mock_task_gateway.save.assert_called_once_with(pending_task)

    @pytest.mark.asyncio
    async def test_complete_task_save_error(self, use_case_without_event_bus, mock_task_gateway, pending_task):
        """Test: Error al guardar la tarea completada"""
        # Arrange
        task_id = pending_task.task_id
        mock_task_gateway.get_by_id.return_value = pending_task
        mock_task_gateway.save.side_effect = Exception("Error de base de datos")

        # Act & Assert
        with pytest.raises(Exception, match="Error de base de datos"):
            await use_case_without_event_bus.execute(task_id)

        mock_task_gateway.get_by_id.assert_called_once_with(task_id)
        mock_task_gateway.save.assert_called_once_with(pending_task)

    @pytest.mark.asyncio
    async def test_complete_already_completed_task(self, use_case_without_event_bus, mock_task_gateway, completed_task):
        """Test: Completar una tarea ya completada"""
        # Arrange
        task_id = completed_task.task_id
        original_completed_at = completed_task.completed_at
        mock_task_gateway.get_by_id.return_value = completed_task
        mock_task_gateway.save.return_value = None

        # Act
        await use_case_without_event_bus.execute(task_id)

        # Assert
        assert completed_task.status == TaskStatus.COMPLETED
        # El timestamp de completado no debería cambiar
        assert completed_task.completed_at == original_completed_at
        mock_task_gateway.save.assert_called_once_with(completed_task)

    @pytest.mark.asyncio
    async def test_complete_task_get_by_id_error(self, use_case_without_event_bus, mock_task_gateway):
        """Test: Error al obtener la tarea"""
        # Arrange
        task_id = uuid4()
        mock_task_gateway.get_by_id.side_effect = Exception("Error de conexión")

        # Act & Assert
        with pytest.raises(Exception, match="Error de conexión"):
            await use_case_without_event_bus.execute(task_id)

        mock_task_gateway.get_by_id.assert_called_once_with(task_id)
        mock_task_gateway.save.assert_not_called()

    @pytest.mark.asyncio
    async def test_complete_task_event_bus_error(self, use_case_with_event_bus, mock_task_gateway, mock_event_bus, pending_task):
        """Test: Error en el bus de eventos no afecta la completación"""
        # Arrange
        task_id = pending_task.task_id
        mock_task_gateway.get_by_id.return_value = pending_task
        mock_task_gateway.save.return_value = None
        mock_event_bus.send_task_completed.side_effect = Exception("Error del bus de eventos")

        # Act & Assert
        with pytest.raises(Exception, match="Error del bus de eventos"):
            await use_case_with_event_bus.execute(task_id)

        # La tarea debería haberse completado antes del error del bus
        assert pending_task.status == TaskStatus.COMPLETED
        mock_task_gateway.save.assert_called_once_with(pending_task) 