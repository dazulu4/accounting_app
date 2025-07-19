"""
Unit Tests for Task Entity - Enterprise Edition

Professional unit tests for TaskEntity following enterprise patterns
with comprehensive coverage and AAA structure.

Note: This file will be deprecated in favor of the new testing structure
under tests/unit/domain/entities/ directory.
"""

from uuid import uuid4
from datetime import datetime, timezone

from domain.entities.task_entity import TaskEntity
from domain.enums.task_status_enum import TaskStatusEnum, TaskPriorityEnum


class TestTaskEntity:
    """Test suite for TaskEntity - Legacy compatibility tests"""
    
    def test_task_creation_with_defaults(self):
        """Test task creation with default values"""
        # Arrange
        task_id = uuid4()
        
        # Act
        task = TaskEntity(
            task_id=task_id,
            title="Test Task",
            description="Sample description",
            user_id=1,
            status=TaskStatusEnum.PENDING,
            priority=TaskPriorityEnum.MEDIUM,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        )
        
        # Assert
        assert task.task_id == task_id
        assert task.title == "Test Task"
        assert task.description == "Sample description"
        assert task.user_id == 1
        assert task.status == TaskStatusEnum.PENDING
        assert task.priority == TaskPriorityEnum.MEDIUM
        assert task.completed_at is None
    
    def test_task_completion_updates_status(self):
        """Test task completion changes status"""
        # Arrange
        task = TaskEntity(
            task_id=uuid4(),
            title="Test Task",
            description="Sample description",
            user_id=1,
            status=TaskStatusEnum.PENDING,
            priority=TaskPriorityEnum.MEDIUM,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        )
        
        # Act
        task.mark_as_completed()
        
        # Assert
        assert task.status == TaskStatusEnum.COMPLETED
        assert task.completed_at is not None
        assert isinstance(task.completed_at, datetime)


# Legacy compatibility functions (deprecated)
def test_task_creation_defaults():
    """Legacy test function - use TestTaskEntity class instead"""
    task = TaskEntity(
        task_id=uuid4(),
        title="Test Task",
        description="Sample description",
        user_id=1,
        status=TaskStatusEnum.PENDING,
        priority=TaskPriorityEnum.MEDIUM,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc)
    )
    assert task.status == TaskStatusEnum.PENDING
    assert task.completed_at is None


def test_task_completion_sets_status():
    """Legacy test function - use TestTaskEntity class instead"""
    task = TaskEntity(
        task_id=uuid4(),
        title="Test Task",
        description="Sample description",
        user_id=1,
        status=TaskStatusEnum.PENDING,
        priority=TaskPriorityEnum.MEDIUM,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc)
    )
    task.mark_as_completed()
    assert task.status == TaskStatusEnum.COMPLETED
    assert task.completed_at is not None
