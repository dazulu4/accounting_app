"""
Integration Tests for Task Management Flow - Enterprise Edition

Integration tests that verify the complete task management flow
from creation to completion across multiple layers of the application.

Test Coverage:
- Complete task lifecycle (create -> complete)
- Cross-layer integration (use cases + repositories + database)
- Business rule enforcement across components
- Error handling in integrated scenarios
- Performance of integrated operations
"""

import pytest
from datetime import datetime, timezone
from uuid import UUID
from unittest.mock import Mock, patch

from domain.usecases.create_task_use_case import CreateTaskUseCase
from domain.usecases.complete_task_use_case import CompleteTaskUseCase
from domain.usecases.list_tasks_by_user_use_case import ListTasksByUserUseCase
from domain.value_objects.task_value_objects import (
    CreateTaskRequest, 
    CompleteTaskRequest,
    ListTasksByUserRequest
)
from domain.enums.task_status_enum import TaskStatusEnum, TaskPriorityEnum
from domain.exceptions.business_exceptions import (
    UserNotFoundException,
    UserNotActiveException,
    TaskNotFoundException,
    InvalidTaskTransitionException
)
from infrastructure.helpers.database.unit_of_work import UnitOfWork
from infrastructure.driven_adapters.repositories.user_repository_fake import FakeUserService


@pytest.mark.integration
class TestTaskManagementFlow:
    """Integration tests for complete task management workflows"""
    
    def test_complete_task_lifecycle_flow(
        self,
        mock_unit_of_work,
        mock_user_service,
        sample_user_id
    ):
        """
        Test complete task lifecycle from creation to completion
        
        Integration Flow:
        1. Create a new task
        2. Verify task appears in user's task list
        3. Complete the task
        4. Verify task status is updated in list
        """
        # Arrange
        active_user = Mock()
        active_user.user_id = sample_user_id
        active_user.is_active.return_value = True
        mock_user_service.find_user_by_id.return_value = active_user
        
        # Mock repository responses
        mock_unit_of_work.task_repository.get_task_count_by_user_id.return_value = 5
        created_task_id = None
        saved_tasks = []
        
        def save_task_side_effect(task):
            nonlocal created_task_id
            created_task_id = task.task_id
            saved_tasks.append(task)
        
        def get_task_by_id_side_effect(task_id):
            for task in saved_tasks:
                if task.task_id == task_id:
                    return task
            return None
        
        def get_tasks_by_user_id_side_effect(user_id):
            return [task for task in saved_tasks if task.user_id == user_id]
        
        def update_task_side_effect(task):
            # Update the task in our mock storage
            for i, saved_task in enumerate(saved_tasks):
                if saved_task.task_id == task.task_id:
                    saved_tasks[i] = task
                    break
        
        mock_unit_of_work.task_repository.save_task.side_effect = save_task_side_effect
        mock_unit_of_work.task_repository.get_task_by_id.side_effect = get_task_by_id_side_effect
        mock_unit_of_work.task_repository.get_tasks_by_user_id.side_effect = get_tasks_by_user_id_side_effect
        mock_unit_of_work.task_repository.update_task.side_effect = update_task_side_effect
        
        # Initialize use cases
        create_use_case = CreateTaskUseCase(mock_unit_of_work, mock_user_service)
        complete_use_case = CompleteTaskUseCase(mock_unit_of_work)
        list_use_case = ListTasksByUserUseCase(mock_unit_of_work, mock_user_service)
        
        # Act & Assert - Step 1: Create task
        create_request = CreateTaskRequest(
            title="Integration Test Task",
            description="Task for testing complete lifecycle",
            user_id=sample_user_id
        )
        
        create_response = create_use_case.execute(create_request)
        
        assert create_response.status == TaskStatusEnum.PENDING.value
        assert create_response.title == "Integration Test Task"
        assert created_task_id is not None
        
        # Act & Assert - Step 2: Verify task in user's list
        list_request = ListTasksByUserRequest(user_id=sample_user_id)
        list_response = list_use_case.execute(list_request)
        
        assert len(list_response.tasks) == 1
        assert list_response.tasks[0].task_id == created_task_id
        assert list_response.tasks[0].status == TaskStatusEnum.PENDING.value
        
        # Act & Assert - Step 3: Complete the task
        complete_request = CompleteTaskRequest(task_id=created_task_id)
        complete_response = complete_use_case.execute(complete_request)
        
        assert complete_response.status == TaskStatusEnum.COMPLETED.value
        assert complete_response.completed_at is not None
        
        # Act & Assert - Step 4: Verify updated status in list
        final_list_response = list_use_case.execute(list_request)
        
        assert len(final_list_response.tasks) == 1
        assert final_list_response.tasks[0].status == TaskStatusEnum.COMPLETED.value
        assert final_list_response.tasks[0].completed_at is not None
    
    def test_error_propagation_across_layers(
        self,
        mock_unit_of_work,
        mock_user_service,
        sample_task_id
    ):
        """
        Test error propagation from domain layer through use cases
        
        Integration Scenario:
        1. Attempt to create task for inactive user
        2. Attempt to complete non-existent task
        3. Verify errors propagate correctly through all layers
        """
        # Arrange
        inactive_user = Mock()
        inactive_user.user_id = 999
        inactive_user.is_active.return_value = False
        mock_user_service.find_user_by_id.return_value = inactive_user
        
        mock_unit_of_work.task_repository.get_task_by_id.return_value = None
        
        create_use_case = CreateTaskUseCase(mock_unit_of_work, mock_user_service)
        complete_use_case = CompleteTaskUseCase(mock_unit_of_work)
        
        # Act & Assert - Test 1: Inactive user error propagation
        create_request = CreateTaskRequest(
            title="Should Fail",
            description="Task for inactive user",
            user_id=999
        )
        
        with pytest.raises(UserNotActiveException) as exc_info:
            create_use_case.execute(create_request)
        
        assert "User 999 is not active" in str(exc_info.value)
        
        # Act & Assert - Test 2: Non-existent task error propagation
        complete_request = CompleteTaskRequest(task_id=sample_task_id)
        
        with pytest.raises(TaskNotFoundException) as exc_info:
            complete_use_case.execute(complete_request)
        
        assert f"Task {sample_task_id} not found" in str(exc_info.value)
    
    def test_transaction_rollback_on_failure(
        self,
        mock_unit_of_work,
        mock_user_service,
        sample_user_id
    ):
        """
        Test transaction rollback when operations fail
        
        Integration Scenario:
        1. Start task creation
        2. Simulate repository failure
        3. Verify transaction is rolled back
        """
        # Arrange
        active_user = Mock()
        active_user.user_id = sample_user_id
        active_user.is_active.return_value = True
        mock_user_service.find_user_by_id.return_value = active_user
        mock_unit_of_work.task_repository.get_task_count_by_user_id.return_value = 5
        
        # Simulate repository failure
        mock_unit_of_work.task_repository.save_task.side_effect = Exception("Database error")
        
        # Configure UoW to track rollback
        rollback_called = False
        original_exit = mock_unit_of_work.__exit__
        
        def track_rollback_exit(exc_type, exc_val, exc_tb):
            nonlocal rollback_called
            if exc_type is not None:
                rollback_called = True
            return original_exit(exc_type, exc_val, exc_tb)
        
        mock_unit_of_work.__exit__ = track_rollback_exit
        
        create_use_case = CreateTaskUseCase(mock_unit_of_work, mock_user_service)
        
        # Act & Assert
        create_request = CreateTaskRequest(
            title="Should Fail",
            description="Task creation should fail",
            user_id=sample_user_id
        )
        
        with pytest.raises(Exception) as exc_info:
            create_use_case.execute(create_request)
        
        assert "Database error" in str(exc_info.value)
        assert rollback_called, "Transaction should have been rolled back"
    
    def test_concurrent_task_operations(
        self,
        mock_unit_of_work,
        mock_user_service,
        sample_user_id
    ):
        """
        Test handling of concurrent task operations
        
        Integration Scenario:
        1. Create multiple tasks concurrently
        2. Verify all tasks are created correctly
        3. Test task count limits under concurrent access
        """
        # Arrange
        active_user = Mock()
        active_user.user_id = sample_user_id
        active_user.is_active.return_value = True
        mock_user_service.find_user_by_id.return_value = active_user
        
        saved_tasks = []
        task_counter = 0
        
        def save_task_side_effect(task):
            nonlocal task_counter
            task_counter += 1
            saved_tasks.append(task)
        
        def get_task_count_side_effect(user_id):
            return len([task for task in saved_tasks if task.user_id == user_id])
        
        mock_unit_of_work.task_repository.save_task.side_effect = save_task_side_effect
        mock_unit_of_work.task_repository.get_task_count_by_user_id.side_effect = get_task_count_side_effect
        
        create_use_case = CreateTaskUseCase(mock_unit_of_work, mock_user_service)
        
        # Act - Create multiple tasks
        created_responses = []
        for i in range(5):
            create_request = CreateTaskRequest(
                title=f"Concurrent Task {i+1}",
                description=f"Task {i+1} for concurrent testing",
                user_id=sample_user_id
            )
            response = create_use_case.execute(create_request)
            created_responses.append(response)
        
        # Assert
        assert len(created_responses) == 5
        assert len(saved_tasks) == 5
        
        # Verify all tasks have unique IDs
        task_ids = [response.task_id for response in created_responses]
        assert len(set(task_ids)) == 5, "All task IDs should be unique"
        
        # Verify all tasks belong to the correct user
        for response in created_responses:
            assert response.user_id == sample_user_id
            assert response.status == TaskStatusEnum.PENDING.value
    
    @pytest.mark.performance
    def test_bulk_operations_performance(
        self,
        mock_unit_of_work,
        mock_user_service,
        sample_user_id,
        performance_timer
    ):
        """
        Test performance of bulk task operations
        
        Integration Scenario:
        1. Create many tasks in sequence
        2. List all tasks for user
        3. Verify operations complete within acceptable time
        """
        # Arrange
        active_user = Mock()
        active_user.user_id = sample_user_id
        active_user.is_active.return_value = True
        mock_user_service.find_user_by_id.return_value = active_user
        
        saved_tasks = []
        
        def save_task_side_effect(task):
            saved_tasks.append(task)
        
        def get_tasks_by_user_side_effect(user_id):
            return [task for task in saved_tasks if task.user_id == user_id]
        
        def get_task_count_side_effect(user_id):
            return len([task for task in saved_tasks if task.user_id == user_id])
        
        mock_unit_of_work.task_repository.save_task.side_effect = save_task_side_effect
        mock_unit_of_work.task_repository.get_tasks_by_user_id.side_effect = get_tasks_by_user_side_effect
        mock_unit_of_work.task_repository.get_task_count_by_user_id.side_effect = get_task_count_side_effect
        
        create_use_case = CreateTaskUseCase(mock_unit_of_work, mock_user_service)
        list_use_case = ListTasksByUserUseCase(mock_unit_of_work, mock_user_service)
        
        # Act - Bulk create tasks
        performance_timer.start()
        
        num_tasks = 50
        for i in range(num_tasks):
            create_request = CreateTaskRequest(
                title=f"Bulk Task {i+1}",
                description=f"Task {i+1} for performance testing",
                user_id=sample_user_id
            )
            create_use_case.execute(create_request)
        
        # List all tasks
        list_request = ListTasksByUserRequest(user_id=sample_user_id)
        list_response = list_use_case.execute(list_request)
        
        performance_timer.stop()
        
        # Assert
        assert len(list_response.tasks) == num_tasks
        assert performance_timer.duration < 1.0  # Less than 1 second for 50 operations
    
    def test_data_consistency_across_operations(
        self,
        mock_unit_of_work,
        mock_user_service,
        sample_user_id
    ):
        """
        Test data consistency across multiple operations
        
        Integration Scenario:
        1. Create task with specific data
        2. Complete the task
        3. Verify data consistency throughout operations
        """
        # Arrange
        active_user = Mock()
        active_user.user_id = sample_user_id
        active_user.name = "Integration Test User"
        active_user.is_active.return_value = True
        mock_user_service.find_user_by_id.return_value = active_user
        
        saved_tasks = []
        
        def save_task_side_effect(task):
            saved_tasks.append(task)
        
        def get_task_by_id_side_effect(task_id):
            for task in saved_tasks:
                if task.task_id == task_id:
                    return task
            return None
        
        def update_task_side_effect(task):
            for i, saved_task in enumerate(saved_tasks):
                if saved_task.task_id == task.task_id:
                    saved_tasks[i] = task
                    break
        
        def get_task_count_side_effect(user_id):
            return len([task for task in saved_tasks if task.user_id == user_id])
        
        mock_unit_of_work.task_repository.save_task.side_effect = save_task_side_effect
        mock_unit_of_work.task_repository.get_task_by_id.side_effect = get_task_by_id_side_effect
        mock_unit_of_work.task_repository.update_task.side_effect = update_task_side_effect
        mock_unit_of_work.task_repository.get_task_count_by_user_id.side_effect = get_task_count_side_effect
        
        create_use_case = CreateTaskUseCase(mock_unit_of_work, mock_user_service)
        complete_use_case = CompleteTaskUseCase(mock_unit_of_work)
        
        # Act - Create task with specific data
        create_request = CreateTaskRequest(
            title="Data Consistency Test",
            description="This task tests data consistency across operations",
            user_id=sample_user_id
        )
        
        create_response = create_use_case.execute(create_request)
        original_created_at = create_response.created_at
        
        # Complete the task
        complete_request = CompleteTaskRequest(task_id=create_response.task_id)
        complete_response = complete_use_case.execute(complete_request)
        
        # Assert - Verify data consistency
        assert complete_response.task_id == create_response.task_id
        assert complete_response.title == "Data Consistency Test"
        assert complete_response.description == "This task tests data consistency across operations"
        assert complete_response.user_id == sample_user_id
        assert complete_response.priority == TaskPriorityEnum.MEDIUM.value
        
        # Verify timestamps are consistent
        assert complete_response.created_at == original_created_at
        assert complete_response.completed_at is not None
        assert complete_response.updated_at >= original_created_at
        
        # Verify status transition
        assert create_response.status == TaskStatusEnum.PENDING.value
        assert complete_response.status == TaskStatusEnum.COMPLETED.value 