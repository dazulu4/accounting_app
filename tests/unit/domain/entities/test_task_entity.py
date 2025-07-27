from datetime import datetime, timedelta, timezone

import pytest

from domain.entities.task_entity import TaskEntity
from domain.enums.task_status_enum import TaskPriorityEnum, TaskStatusEnum
from domain.exceptions.business_exceptions import (
    TaskAlreadyCancelledException,
    TaskAlreadyCompletedException,
)


class TestTaskEntity:
    """
    Unit tests for the TaskEntity domain model.
    These tests ensure that the core business logic and rules of a task
    are correctly enforced.
    """

    def test_create_new_task_successfully(self):
        """
        Verify that a new task can be created successfully with valid data.
        """
        task = TaskEntity.create_new_task(
            title="  Valid Title ",
            description="A valid description.",
            user_id=123,
            priority=TaskPriorityEnum.HIGH,
        )
        assert task.title == "Valid Title"  # Title is stripped by Pydantic validator
        assert task.description == "A valid description."
        assert task.user_id == 123
        assert task.priority == TaskPriorityEnum.HIGH
        assert task.status == TaskStatusEnum.PENDING
        assert isinstance(task.created_at, datetime)
        assert task.completed_at is None

    @pytest.mark.parametrize(
        "title, description, user_id",
        [
            ("", "Valid desc", 1),
            (" ", "Valid desc", 1),
            ("", "Valid desc", 1),  # Empty string should fail
            ("T" * 201, "Valid desc", 1),
            ("Valid title", "", 1),
            ("Valid title", " ", 1),
            ("Valid title", "d" * 2001, 1),
            ("Valid title", "Valid desc", 0),
            ("Valid title", "Valid desc", -1),
        ],
    )
    def test_create_task_with_invalid_data_raises_exception(
        self, title, description, user_id
    ):
        """
        Verify that creating a task with invalid data raises a validation exception.
        """
        with pytest.raises(ValueError):
            TaskEntity.create_new_task(
                title=title, description=description, user_id=user_id
            )

    def test_complete_task_sets_status_and_timestamp(self):
        """
        Verify that completing a task correctly updates its status and completion date.
        """
        task = TaskEntity.create_new_task("Test", "Desc", 1)
        # Can complete directly from pending according to the enum
        task.complete()

        assert task.status == TaskStatusEnum.COMPLETED
        assert isinstance(task.completed_at, datetime)
        assert task.updated_at > task.created_at

    def test_can_complete_a_pending_task_directly(self):
        """
        Verify that a task can be completed directly from pending.
        """
        task = TaskEntity.create_new_task("Test", "Desc", 1)
        task.complete()
        assert task.status == TaskStatusEnum.COMPLETED

    def test_cannot_complete_an_already_completed_task(self):
        """
        Verify that attempting to complete an already completed task raises an exception.
        """
        task = TaskEntity.create_new_task("Test", "Desc", 1)
        task.complete()  # Complete directly from pending
        with pytest.raises(TaskAlreadyCompletedException):
            task.complete()

    def test_start_task_transitions_status_correctly(self):
        """
        Verify that starting a task correctly changes its status to IN_PROGRESS.
        """
        task = TaskEntity.create_new_task("Test", "Desc", 1)
        task.start_task()
        assert task.status == TaskStatusEnum.IN_PROGRESS

    def test_cannot_start_a_terminal_task(self):
        """
        Verify that a completed or cancelled task cannot be started.
        """
        task = TaskEntity.create_new_task("Test", "Desc", 1)
        task.complete()  # Complete directly from pending
        with pytest.raises(TaskAlreadyCompletedException):
            task.start_task()

        task_cancelled = TaskEntity.create_new_task("Cancelled Task", "Desc", 2)
        task_cancelled.cancel_task()
        with pytest.raises(TaskAlreadyCancelledException):
            task_cancelled.start_task()

    def test_cancel_task_transitions_status_correctly(self):
        """
        Verify that cancelling a task correctly changes its status to CANCELLED.
        """
        task = TaskEntity.create_new_task("Test", "Desc", 1)
        task.cancel_task()
        assert task.status == TaskStatusEnum.CANCELLED

    def test_update_title_and_description_on_active_task(self):
        """
        Verify that title and description can be updated on an active task.
        """
        task = TaskEntity.create_new_task("Original Title", "Original Desc", 1)

        new_title = "Updated Title"
        task.update_task(title=new_title)
        assert task.title == new_title

        new_desc = "Updated Description which is long enough"
        task.update_task(description=new_desc)
        assert task.description == new_desc

    def test_cannot_update_terminal_task(self):
        """
        Verify that a completed or cancelled task's details cannot be updated.
        """
        task = TaskEntity.create_new_task("Test", "Desc", 1)
        task.complete()  # Complete directly from pending

        with pytest.raises(TaskAlreadyCompletedException):
            task.update_task(title="New Title")

        with pytest.raises(TaskAlreadyCompletedException):
            task.update_task(description="New Description")

    def test_is_overdue_logic(self):
        """
        Verify the overdue logic works as expected.
        """
        # A task created just now is not overdue
        task = TaskEntity.create_new_task("Test", "Desc", 1)
        assert not task.is_overdue()

        # A task created long ago is overdue
        old_task = TaskEntity.create_new_task("Old Task", "Old Desc", 2)
        old_task.created_at = datetime.now(timezone.utc) - timedelta(days=400)
        assert old_task.is_overdue()

        # A completed task is never overdue
        completed_old_task = TaskEntity.create_new_task("Old Completed", "Desc", 3)
        completed_old_task.created_at = datetime.now(timezone.utc) - timedelta(days=400)
        completed_old_task.complete()  # Complete directly from pending
        assert not completed_old_task.is_overdue()
