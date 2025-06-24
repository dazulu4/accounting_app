from uuid import uuid4
from domain.models.task import Task, TaskStatus


def test_task_creation_defaults():
    task = Task(
        task_id=uuid4(),
        title="Test Task",
        description="Sample",
        user_id=1,
    )
    assert task.status == TaskStatus.NEW
    assert task.completed_at is None


def test_task_completion_sets_status():
    task = Task(
        task_id=uuid4(),
        title="Test Task",
        description="Sample",
        user_id=1,
    )
    task.complete()
    assert task.status == TaskStatus.COMPLETED
    assert task.completed_at is not None
