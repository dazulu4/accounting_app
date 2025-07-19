"""
Unit Tests for CompleteTaskUseCase - Enterprise Edition

Comprehensive unit tests following AAA pattern for task completion
with proper mocking, state validation, and business rule testing.

Test Categories:
- Happy path task completion
- Invalid state transitions
- Task not found scenarios
- Business rule violations
- Performance validation
"""

import pytest
from datetime import datetime, timezone
from uuid import UUID
from unittest.mock import Mock, patch

from domain.usecases.complete_task_use_case import CompleteTaskUseCase
from domain.value_objects.task_value_objects import CompleteTaskRequest, CompleteTaskResponse
from domain.entities.task_entity import TaskEntity
from domain.enums.task_status_enum import TaskStatusEnum, TaskPriorityEnum
from domain.exceptions.business_exceptions import (
    TaskNotFoundException,
    InvalidTaskTransitionException,
    TaskAlreadyCompletedException
)
from infrastructure.helpers.database.unit_of_work import UnitOfWork


class TestCompleteTaskUseCase:
    """Test suite for CompleteTaskUseCase following AAA pattern"""
    
    def test_execute_should_complete_pending_task(
        self,
        mock_unit_of_work,
        sample_task_id,
        mock_datetime
    ):
        """
        Test successful completion of a pending task
        
        Scenario: User completes a pending task
        Expected: Task status changes to completed with timestamp
        """
        # Arrange
        pending_task = TaskEntity(
            task_id=sample_task_id,
            title="Test Task",
            description="Test Description",
            user_id=1,
            status=TaskStatusEnum.PENDING,
            priority=TaskPriorityEnum.MEDIUM,
            created_at=datetime(2025, 1, 19, 10, 0, 0, tzinfo=timezone.utc),
            updated_at=datetime(2025, 1, 19, 10, 0, 0, tzinfo=timezone.utc)
        )
        
        mock_unit_of_work.task_repository.get_task_by_id.return_value = pending_task
        
        request = CompleteTaskRequest(task_id=sample_task_id)
        use_case = CompleteTaskUseCase(mock_unit_of_work)
        
        # Act
        response = use_case.execute(request)
        
        # Assert
        assert isinstance(response, CompleteTaskResponse)
        assert response.task_id == sample_task_id
        assert response.status == TaskStatusEnum.COMPLETED.value
        assert response.completed_at == mock_datetime
        assert response.updated_at == mock_datetime
        
        # Verify repository interactions
        mock_unit_of_work.task_repository.get_task_by_id.assert_called_once_with(sample_task_id)
        mock_unit_of_work.task_repository.update_task.assert_called_once()
        
        # Verify task was updated correctly
        updated_task_call = mock_unit_of_work.task_repository.update_task.call_args[0][0]
        assert updated_task_call.status == TaskStatusEnum.COMPLETED
        assert updated_task_call.completed_at == mock_datetime
    
    def test_execute_should_complete_in_progress_task(
        self,
        mock_unit_of_work,
        sample_task_id,
        mock_datetime
    ):
        """
        Test successful completion of an in-progress task
        
        Scenario: User completes a task that was in progress
        Expected: Task status changes to completed with timestamp
        """
        # Arrange
        in_progress_task = TaskEntity(
            task_id=sample_task_id,
            title="Test Task",
            description="Test Description",
            user_id=1,
            status=TaskStatusEnum.IN_PROGRESS,
            priority=TaskPriorityEnum.HIGH,
            created_at=datetime(2025, 1, 19, 10, 0, 0, tzinfo=timezone.utc),
            updated_at=datetime(2025, 1, 19, 11, 0, 0, tzinfo=timezone.utc)
        )
        
        mock_unit_of_work.task_repository.get_task_by_id.return_value = in_progress_task
        
        request = CompleteTaskRequest(task_id=sample_task_id)
        use_case = CompleteTaskUseCase(mock_unit_of_work)
        
        # Act
        response = use_case.execute(request)
        
        # Assert
        assert response.status == TaskStatusEnum.COMPLETED.value
        assert response.completed_at == mock_datetime
        
        # Verify task was updated
        mock_unit_of_work.task_repository.update_task.assert_called_once()
    
    def test_execute_should_raise_exception_when_task_not_found(
        self,
        mock_unit_of_work,
        sample_task_id
    ):
        """
        Test completion fails when task doesn't exist
        
        Scenario: User tries to complete non-existent task
        Expected: TaskNotFoundException is raised
        """
        # Arrange
        mock_unit_of_work.task_repository.get_task_by_id.return_value = None
        
        request = CompleteTaskRequest(task_id=sample_task_id)
        use_case = CompleteTaskUseCase(mock_unit_of_work)
        
        # Act & Assert
        with pytest.raises(TaskNotFoundException) as exc_info:
            use_case.execute(request)
        
        assert f"Task {sample_task_id} not found" in str(exc_info.value)
        
        # Verify no update was attempted
        mock_unit_of_work.task_repository.update_task.assert_not_called()
    
    def test_execute_should_raise_exception_when_task_already_completed(
        self,
        mock_unit_of_work,
        sample_task_id
    ):
        """
        Test completion fails when task is already completed
        
        Scenario: User tries to complete an already completed task
        Expected: TaskAlreadyCompletedException is raised
        """
        # Arrange
        completed_task = TaskEntity(
            task_id=sample_task_id,
            title="Test Task",
            description="Test Description",
            user_id=1,
            status=TaskStatusEnum.COMPLETED,
            priority=TaskPriorityEnum.MEDIUM,
            created_at=datetime(2025, 1, 19, 10, 0, 0, tzinfo=timezone.utc),
            updated_at=datetime(2025, 1, 19, 12, 0, 0, tzinfo=timezone.utc),
            completed_at=datetime(2025, 1, 19, 12, 0, 0, tzinfo=timezone.utc)
        )
        
        mock_unit_of_work.task_repository.get_task_by_id.return_value = completed_task
        
        request = CompleteTaskRequest(task_id=sample_task_id)
        use_case = CompleteTaskUseCase(mock_unit_of_work)
        
        # Act & Assert
        with pytest.raises(TaskAlreadyCompletedException) as exc_info:
            use_case.execute(request)
        
        assert f"Task {sample_task_id} is already completed" in str(exc_info.value)
        
        # Verify no update was attempted
        mock_unit_of_work.task_repository.update_task.assert_not_called()
    
    def test_execute_should_raise_exception_when_task_is_cancelled(
        self,
        mock_unit_of_work,
        sample_task_id
    ):
        """
        Test completion fails when task is cancelled
        
        Scenario: User tries to complete a cancelled task
        Expected: InvalidTaskTransitionException is raised
        """
        # Arrange
        cancelled_task = TaskEntity(
            task_id=sample_task_id,
            title="Test Task",
            description="Test Description",
            user_id=1,
            status=TaskStatusEnum.CANCELLED,
            priority=TaskPriorityEnum.LOW,
            created_at=datetime(2025, 1, 19, 10, 0, 0, tzinfo=timezone.utc),
            updated_at=datetime(2025, 1, 19, 11, 0, 0, tzinfo=timezone.utc)
        )
        
        mock_unit_of_work.task_repository.get_task_by_id.return_value = cancelled_task
        
        request = CompleteTaskRequest(task_id=sample_task_id)
        use_case = CompleteTaskUseCase(mock_unit_of_work)
        
        # Act & Assert
        with pytest.raises(InvalidTaskTransitionException) as exc_info:
            use_case.execute(request)
        
        assert "Cannot complete task in CANCELLED status" in str(exc_info.value)
        
        # Verify no update was attempted
        mock_unit_of_work.task_repository.update_task.assert_not_called()
    
    def test_execute_should_use_unit_of_work_transaction(
        self,
        mock_unit_of_work,
        sample_task_id,
        mock_datetime
    ):
        """
        Test task completion uses Unit of Work transaction correctly
        
        Scenario: Successful task completion
        Expected: UoW context manager is used for transaction
        """
        # Arrange
        pending_task = TaskEntity(
            task_id=sample_task_id,
            title="Test Task",
            description="Test Description",
            user_id=1,
            status=TaskStatusEnum.PENDING,
            priority=TaskPriorityEnum.MEDIUM,
            created_at=datetime(2025, 1, 19, 10, 0, 0, tzinfo=timezone.utc),
            updated_at=datetime(2025, 1, 19, 10, 0, 0, tzinfo=timezone.utc)
        )
        
        mock_unit_of_work.task_repository.get_task_by_id.return_value = pending_task
        
        request = CompleteTaskRequest(task_id=sample_task_id)
        use_case = CompleteTaskUseCase(mock_unit_of_work)
        
        # Act
        use_case.execute(request)
        
        # Assert
        # Verify UoW context manager was used
        mock_unit_of_work.__enter__.assert_called_once()
        mock_unit_of_work.__exit__.assert_called_once()
    
    def test_execute_should_log_task_completion(
        self,
        mock_unit_of_work,
        sample_task_id,
        mock_datetime
    ):
        """
        Test task completion includes proper logging
        
        Scenario: Successful task completion
        Expected: Appropriate log messages are generated
        """
        # Arrange
        pending_task = TaskEntity(
            task_id=sample_task_id,
            title="Test Task",
            description="Test Description",
            user_id=1,
            status=TaskStatusEnum.PENDING,
            priority=TaskPriorityEnum.MEDIUM,
            created_at=datetime(2025, 1, 19, 10, 0, 0, tzinfo=timezone.utc),
            updated_at=datetime(2025, 1, 19, 10, 0, 0, tzinfo=timezone.utc)
        )
        
        mock_unit_of_work.task_repository.get_task_by_id.return_value = pending_task
        
        request = CompleteTaskRequest(task_id=sample_task_id)
        use_case = CompleteTaskUseCase(mock_unit_of_work)
        
        with patch.object(use_case, '_logger') as mock_logger:
            # Act
            use_case.execute(request)
            
            # Assert
            # Verify success log was called
            mock_logger.info.assert_called_with(
                "task_completed_successfully",
                task_id=str(sample_task_id),
                previous_status=TaskStatusEnum.PENDING.value,
                completed_at=mock_datetime.isoformat()
            )
    
    def test_execute_should_preserve_task_metadata(
        self,
        mock_unit_of_work,
        sample_task_id,
        mock_datetime
    ):
        """
        Test task completion preserves all non-status metadata
        
        Scenario: User completes a task
        Expected: Only status and timestamps are updated
        """
        # Arrange
        original_task = TaskEntity(
            task_id=sample_task_id,
            title="Important Task",
            description="Detailed description",
            user_id=42,
            status=TaskStatusEnum.PENDING,
            priority=TaskPriorityEnum.URGENT,
            created_at=datetime(2025, 1, 19, 10, 0, 0, tzinfo=timezone.utc),
            updated_at=datetime(2025, 1, 19, 10, 0, 0, tzinfo=timezone.utc)
        )
        
        mock_unit_of_work.task_repository.get_task_by_id.return_value = original_task
        
        request = CompleteTaskRequest(task_id=sample_task_id)
        use_case = CompleteTaskUseCase(mock_unit_of_work)
        
        # Act
        response = use_case.execute(request)
        
        # Assert
        # Verify all original metadata is preserved
        assert response.title == "Important Task"
        assert response.description == "Detailed description"
        assert response.user_id == 42
        assert response.priority == TaskPriorityEnum.URGENT.value
        assert response.created_at == original_task.created_at
        
        # Verify only status and timestamps changed
        assert response.status == TaskStatusEnum.COMPLETED.value
        assert response.completed_at == mock_datetime
        assert response.updated_at == mock_datetime
    
    @pytest.mark.performance
    def test_execute_performance_within_acceptable_limits(
        self,
        mock_unit_of_work,
        sample_task_id,
        performance_timer
    ):
        """
        Test task completion performance is within acceptable limits
        
        Scenario: Task completion under normal conditions
        Expected: Execution time is under 50ms
        """
        # Arrange
        pending_task = TaskEntity(
            task_id=sample_task_id,
            title="Test Task",
            description="Test Description",
            user_id=1,
            status=TaskStatusEnum.PENDING,
            priority=TaskPriorityEnum.MEDIUM,
            created_at=datetime(2025, 1, 19, 10, 0, 0, tzinfo=timezone.utc),
            updated_at=datetime(2025, 1, 19, 10, 0, 0, tzinfo=timezone.utc)
        )
        
        mock_unit_of_work.task_repository.get_task_by_id.return_value = pending_task
        
        request = CompleteTaskRequest(task_id=sample_task_id)
        use_case = CompleteTaskUseCase(mock_unit_of_work)
        
        # Act
        performance_timer.start()
        use_case.execute(request)
        performance_timer.stop()
        
        # Assert
        assert performance_timer.duration < 0.05  # Less than 50ms 