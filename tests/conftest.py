"""
Fixtures globales para las pruebas

Este archivo contiene fixtures que pueden ser utilizadas en todas las pruebas
del proyecto, incluyendo mocks, datos de prueba y configuraciones comunes.
"""

import pytest
from datetime import datetime, timezone
from uuid import uuid4
from domain.models.task import Task, TaskStatus
from domain.models.user import User, UserStatus


@pytest.fixture
def sample_task():
    """Fixture que proporciona una tarea de ejemplo"""
    return Task(
        task_id=uuid4(),
        title="Tarea de prueba",
        description="Descripción de prueba",
        user_id=1
    )


@pytest.fixture
def sample_completed_task():
    """Fixture que proporciona una tarea completada de ejemplo"""
    task = Task(
        task_id=uuid4(),
        title="Tarea completada",
        description="Descripción de tarea completada",
        user_id=1
    )
    task.complete()
    return task


@pytest.fixture
def sample_user():
    """Fixture que proporciona un usuario activo de ejemplo"""
    return User(
        user_id=1,
        name="Usuario de Prueba",
        status=UserStatus.ACTIVE
    )


@pytest.fixture
def sample_inactive_user():
    """Fixture que proporciona un usuario inactivo de ejemplo"""
    return User(
        user_id=2,
        name="Usuario Inactivo",
        status=UserStatus.INACTIVE
    )


@pytest.fixture
def sample_task_data():
    """Fixture que proporciona datos de tarea para testing"""
    return {
        "title": "Nueva tarea",
        "description": "Descripción de nueva tarea",
        "user_id": 1
    }


@pytest.fixture
def sample_user_data():
    """Fixture que proporciona datos de usuario para testing"""
    return {
        "name": "Nuevo Usuario",
        "status": UserStatus.ACTIVE
    }


@pytest.fixture
def mock_task_gateway(mocker):
    """Fixture que proporciona un mock del TaskGateway"""
    return mocker.Mock()


@pytest.fixture
def mock_user_gateway(mocker):
    """Fixture que proporciona un mock del UserGateway"""
    return mocker.Mock()


@pytest.fixture
def mock_event_bus(mocker):
    """Fixture que proporciona un mock del EventBus"""
    return mocker.Mock()


@pytest.fixture
def sample_task_list():
    """Fixture que proporciona una lista de tareas de ejemplo"""
    return [
        Task(
            task_id=uuid4(),
            title=f"Tarea {i}",
            description=f"Descripción de tarea {i}",
            user_id=1
        )
        for i in range(1, 4)
    ]


@pytest.fixture
def sample_user_list():
    """Fixture que proporciona una lista de usuarios de ejemplo"""
    return [
        User(user_id=1, name="Usuario 1", status=UserStatus.ACTIVE),
        User(user_id=2, name="Usuario 2", status=UserStatus.ACTIVE),
        User(user_id=3, name="Usuario 3", status=UserStatus.INACTIVE),
    ]


@pytest.fixture
def current_timestamp():
    """Fixture que proporciona el timestamp actual"""
    return datetime.now(timezone.utc)


@pytest.fixture
def task_status_enum_values():
    """Fixture que proporciona todos los valores del enum TaskStatus"""
    return [status.value for status in TaskStatus]


@pytest.fixture
def user_status_enum_values():
    """Fixture que proporciona todos los valores del enum UserStatus"""
    return [status.value for status in UserStatus] 