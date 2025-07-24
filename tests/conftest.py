"""
Test Configuration - Enterprise Edition

Professional test configuration for unit testing with fixtures,
mocks, and utilities for unit tests.

Key Features:
- Enterprise testing setup
- Professional fixtures with proper cleanup
- Mock services and dependencies
- Performance testing support
- Coverage configuration integration
"""

import asyncio
from datetime import datetime, timezone
from unittest.mock import MagicMock, Mock, patch
from uuid import UUID, uuid4

import pytest

# Import enterprise components
from application.schemas.task_schema import (
    CreateTaskRequest,
    CreateTaskResponse,
)
from domain.entities.task_entity import TaskEntity
from domain.enums.task_status_enum import TaskPriorityEnum, TaskStatusEnum
from domain.gateways.task_gateway import TaskGateway
from domain.gateways.user_gateway import UserGateway
from infrastructure.helpers.database.unit_of_work import UnitOfWork

# =============================================================================
# Test Configuration
# =============================================================================


def pytest_configure(config):
    """Configure pytest with enterprise markers and settings"""
    config.addinivalue_line("markers", "unit: Unit tests (fast, isolated)")
    config.addinivalue_line("markers", "database: Tests requiring database")
    config.addinivalue_line("markers", "api: Tests for API endpoints")
    config.addinivalue_line("markers", "performance: Performance and load tests")


def pytest_runtest_setup(item):
    """Setup for each test run with environment configuration"""
    # Ensure test environment
    import os

    os.environ["APP_ENVIRONMENT"] = "test"
    os.environ["DATABASE_NAME"] = "accounting_test"


# =============================================================================
# Core Fixtures
# =============================================================================


@pytest.fixture(scope="session")
def event_loop():
    """Create event loop for async tests"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def mock_datetime():
    """Mock datetime for consistent testing"""
    fixed_time = datetime(2025, 1, 19, 14, 30, 0, tzinfo=timezone.utc)
    with patch("datetime.datetime") as mock_dt:
        mock_dt.now.return_value = fixed_time
        mock_dt.utcnow.return_value = fixed_time
        yield fixed_time


# =============================================================================
# Entity Fixtures
# =============================================================================


@pytest.fixture
def sample_task_id() -> UUID:
    """Sample task UUID for testing"""
    return uuid4()


@pytest.fixture
def sample_user_id() -> int:
    """Sample user ID for testing"""
    return 1


@pytest.fixture
def sample_task_entity(sample_task_id: UUID, sample_user_id: int) -> TaskEntity:
    """Sample task entity for testing"""
    return TaskEntity(
        task_id=sample_task_id,
        title="Sample Task",
        description="This is a sample task for testing",
        user_id=sample_user_id,
        status=TaskStatusEnum.PENDING,
        priority=TaskPriorityEnum.MEDIUM,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )


@pytest.fixture
def completed_task_entity(sample_task_entity: TaskEntity) -> TaskEntity:
    """Completed task entity for testing"""
    # Create a new task with completed status
    task = TaskEntity(
        task_id=sample_task_entity.task_id,
        title=sample_task_entity.title,
        description=sample_task_entity.description,
        user_id=sample_task_entity.user_id,
        status=TaskStatusEnum.COMPLETED,
        priority=sample_task_entity.priority,
        created_at=sample_task_entity.created_at,
        completed_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )
    return task


# =============================================================================
# Value Object Fixtures
# =============================================================================


@pytest.fixture
def create_task_request(sample_user_id: int) -> CreateTaskRequest:
    """Sample create task request"""
    return CreateTaskRequest(
        title="Test Task",
        description="Test task description",
        user_id=sample_user_id,
    )


@pytest.fixture
def create_task_response(
    sample_task_id: UUID, sample_user_id: int
) -> CreateTaskResponse:
    """Sample create task response"""
    return CreateTaskResponse(
        task_id=sample_task_id,
        title="Test Task",
        description="Test task description",
        user_id=sample_user_id,
        status=TaskStatusEnum.PENDING.value,
        priority=TaskPriorityEnum.MEDIUM.value,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )


# =============================================================================
# Mock Service Fixtures
# =============================================================================


@pytest.fixture
def mock_user_gateway() -> MagicMock:
    """Mock user gateway for testing"""
    return MagicMock(spec=UserGateway)


@pytest.fixture
def mock_task_gateway() -> MagicMock:
    """Mock task gateway for testing"""
    return MagicMock(spec=TaskGateway)


@pytest.fixture
def mock_user_service() -> MagicMock:
    """Mock user service for testing"""
    mock_service = MagicMock()

    # Configure default behaviors
    mock_service.get_user_by_id.return_value = None
    mock_service.get_all_users.return_value = []
    mock_service.is_user_active.return_value = True

    return mock_service


@pytest.fixture
def mock_unit_of_work():
    """Mock Unit of Work for testing"""
    mock_uow = Mock(spec=UnitOfWork)

    # Configure mock repository
    mock_task_repo = Mock()
    mock_uow.task_repository = mock_task_repo

    # Configure context manager behavior
    mock_uow.__enter__ = Mock(return_value=mock_uow)
    mock_uow.__exit__ = Mock(return_value=None)

    return mock_uow


@pytest.fixture
def mock_task_repository():
    """Mock task repository for testing"""
    mock_repo = Mock()

    # Configure default behaviors
    mock_repo.save_task.return_value = None
    mock_repo.get_task_by_id.return_value = None
    mock_repo.get_tasks_by_user_id.return_value = []
    mock_repo.update_task.return_value = None
    mock_repo.delete_task.return_value = None

    return mock_repo


# =============================================================================
# Performance Testing Fixtures
# =============================================================================


@pytest.fixture
def performance_timer():
    """Timer fixture for performance testing"""
    import time

    class Timer:
        def __init__(self):
            self.start_time = None
            self.end_time = None

        def start(self):
            self.start_time = time.time()

        def stop(self):
            self.end_time = time.time()

        @property
        def duration(self) -> float:
            if self.start_time and self.end_time:
                return self.end_time - self.start_time
            return 0.0

    return Timer()


# =============================================================================
# Test Data Factories
# =============================================================================


class TaskFactory:
    """Factory for creating test task entities"""

    @staticmethod
    def create_pending_task(**kwargs) -> TaskEntity:
        """Create a pending task with optional overrides"""
        defaults = {
            "task_id": uuid4(),
            "title": "Test Task",
            "description": "Test Description",
            "user_id": 1,
            "status": TaskStatusEnum.PENDING,
            "priority": TaskPriorityEnum.MEDIUM,
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc),
        }
        defaults.update(kwargs)
        return TaskEntity(**defaults)

    @staticmethod
    def create_completed_task(**kwargs) -> TaskEntity:
        """Create a completed task with optional overrides"""
        now = datetime.now(timezone.utc)
        defaults = {"status": TaskStatusEnum.COMPLETED, "completed_at": now}
        defaults.update(kwargs)
        return TaskFactory.create_pending_task(**defaults)


@pytest.fixture
def task_factory():
    """Task factory fixture"""
    return TaskFactory


# =============================================================================
# Cleanup and Utilities
# =============================================================================


@pytest.fixture(autouse=True)
def cleanup_test_environment():
    """Automatic cleanup after each test"""
    yield
    # Perform any necessary cleanup
    # Clear caches, reset mocks, etc.


def pytest_collection_modifyitems(config, items):
    """Modify test collection to add markers automatically"""
    for item in items:
        # Add markers based on test file location
        if "unit" in str(item.fspath):
            item.add_marker(pytest.mark.unit)

        # Add database marker for database-related tests
        if "database" in str(item.fspath) or "repository" in str(item.fspath):
            item.add_marker(pytest.mark.database)
