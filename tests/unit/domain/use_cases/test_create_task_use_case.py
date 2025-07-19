"""
Unit Tests for CreateTaskUseCase - Enterprise Edition

Comprehensive unit tests following AAA pattern (Arrange, Act, Assert)
with proper mocking, edge cases, and business rule validation.

Test Categories:
- Happy path scenarios
- Business rule violations
- Edge cases and error conditions
- Performance and behavior validation
"""

import pytest
from datetime import datetime, timezone
from uuid import UUID
from unittest.mock import Mock, patch

from domain.usecases.create_task_use_case import CreateTaskUseCase
from domain.value_objects.task_value_objects import CreateTaskRequest, CreateTaskResponse
from domain.entities.task_entity import TaskEntity
from domain.enums.task_status_enum import TaskStatusEnum, TaskPriorityEnum
from domain.exceptions.business_exceptions import (
    UserNotFoundException,
    UserNotActiveException,
    MaxTasksExceededException,
    ValidationException
)
from infrastructure.helpers.database.unit_of_work import UnitOfWork
from domain.gateways.user_gateway import UserGateway


class TestCreateTaskUseCase:
    """Test suite for CreateTaskUseCase following AAA pattern"""
    
    def test_execute_should_create_task_when_user_is_active(
        self, 
        mock_unit_of_work, 
        mock_user_service,
        create_task_request,
        sample_task_id
    ):
        """
        Test successful task creation for active user
        
        Scenario: Valid user creates a task
        Expected: Task is created with correct data and saved
        """
        # Arrange
        active_user = Mock()
        active_user.user_id = 1
        active_user.name = "John Doe"
        active_user.is_active.return_value = True
        
        mock_user_service.find_user_by_id.return_value = active_user
        mock_unit_of_work.task_repository.get_task_count_by_user_id.return_value = 5
        
        use_case = CreateTaskUseCase(mock_unit_of_work, mock_user_service)
        
        with patch('uuid.uuid4', return_value=sample_task_id):
            # Act
            response = use_case.execute(create_task_request)
        
        # Assert
        assert isinstance(response, CreateTaskResponse)
        assert response.task_id == sample_task_id
        assert response.title == create_task_request.title
        assert response.description == create_task_request.description
        assert response.user_id == create_task_request.user_id
        assert response.status == TaskStatusEnum.PENDING.value
        assert response.priority == TaskPriorityEnum.MEDIUM.value
        assert response.created_at is not None
        assert response.updated_at is not None
        assert response.completed_at is None
        
        # Verify interactions
        mock_user_service.find_user_by_id.assert_called_once_with(create_task_request.user_id)
        mock_unit_of_work.task_repository.save_task.assert_called_once()
        
        # Verify task was created with correct data
        saved_task_call = mock_unit_of_work.task_repository.save_task.call_args[0][0]
        assert isinstance(saved_task_call, TaskEntity)
        assert saved_task_call.title == create_task_request.title
        assert saved_task_call.user_id == create_task_request.user_id
    
    def test_execute_should_raise_exception_when_user_not_found(
        self,
        mock_unit_of_work,
        mock_user_service,
        create_task_request
    ):
        """
        Test task creation fails when user doesn't exist
        
        Scenario: User ID doesn't exist in system
        Expected: UserNotFoundException is raised
        """
        # Arrange
        mock_user_service.find_user_by_id.return_value = None
        use_case = CreateTaskUseCase(mock_unit_of_work, mock_user_service)
        
        # Act & Assert
        with pytest.raises(UserNotFoundException) as exc_info:
            use_case.execute(create_task_request)
        
        assert f"User {create_task_request.user_id} not found" in str(exc_info.value)
        
        # Verify no task was saved
        mock_unit_of_work.task_repository.save_task.assert_not_called()
    
    def test_execute_should_raise_exception_when_user_is_inactive(
        self,
        mock_unit_of_work,
        mock_user_service,
        create_task_request
    ):
        """
        Test task creation fails when user is inactive
        
        Scenario: User exists but is deactivated
        Expected: UserNotActiveException is raised
        """
        # Arrange
        inactive_user = Mock()
        inactive_user.user_id = 1
        inactive_user.name = "Inactive User"
        inactive_user.is_active.return_value = False
        
        mock_user_service.find_user_by_id.return_value = inactive_user
        use_case = CreateTaskUseCase(mock_unit_of_work, mock_user_service)
        
        # Act & Assert
        with pytest.raises(UserNotActiveException) as exc_info:
            use_case.execute(create_task_request)
        
        assert f"User {create_task_request.user_id} is not active" in str(exc_info.value)
        
        # Verify no task was saved
        mock_unit_of_work.task_repository.save_task.assert_not_called()
    
    def test_execute_should_raise_exception_when_max_tasks_exceeded(
        self,
        mock_unit_of_work,
        mock_user_service,
        create_task_request
    ):
        """
        Test task creation fails when user has too many tasks
        
        Scenario: User has reached maximum task limit
        Expected: MaxTasksExceededException is raised
        """
        # Arrange
        active_user = Mock()
        active_user.user_id = 1
        active_user.is_active.return_value = True
        
        mock_user_service.find_user_by_id.return_value = active_user
        # User has reached max tasks (100)
        mock_unit_of_work.task_repository.get_task_count_by_user_id.return_value = 100
        
        use_case = CreateTaskUseCase(mock_unit_of_work, mock_user_service)
        
        # Act & Assert
        with pytest.raises(MaxTasksExceededException) as exc_info:
            use_case.execute(create_task_request)
        
        assert f"User {create_task_request.user_id} has reached maximum task limit" in str(exc_info.value)
        
        # Verify no task was saved
        mock_unit_of_work.task_repository.save_task.assert_not_called()
    
    def test_execute_should_validate_title_length(
        self,
        mock_unit_of_work,
        mock_user_service,
        sample_user_id
    ):
        """
        Test task creation validates title length constraints
        
        Scenario: Title exceeds maximum length
        Expected: ValidationException is raised
        """
        # Arrange
        active_user = Mock()
        active_user.is_active.return_value = True
        mock_user_service.find_user_by_id.return_value = active_user
        
        # Title too long (over 200 characters)
        long_title = "A" * 201
        invalid_request = CreateTaskRequest(
            title=long_title,
            description="Valid description",
            user_id=sample_user_id
        )
        
        use_case = CreateTaskUseCase(mock_unit_of_work, mock_user_service)
        
        # Act & Assert
        with pytest.raises(ValidationException) as exc_info:
            use_case.execute(invalid_request)
        
        assert "Title must be between 1 and 200 characters" in str(exc_info.value)
    
    def test_execute_should_validate_empty_title(
        self,
        mock_unit_of_work,
        mock_user_service,
        sample_user_id
    ):
        """
        Test task creation validates empty title
        
        Scenario: Title is empty or whitespace only
        Expected: ValidationException is raised
        """
        # Arrange
        active_user = Mock()
        active_user.is_active.return_value = True
        mock_user_service.find_user_by_id.return_value = active_user
        
        invalid_request = CreateTaskRequest(
            title="   ",  # Whitespace only
            description="Valid description",
            user_id=sample_user_id
        )
        
        use_case = CreateTaskUseCase(mock_unit_of_work, mock_user_service)
        
        # Act & Assert
        with pytest.raises(ValidationException) as exc_info:
            use_case.execute(invalid_request)
        
        assert "Title cannot be empty" in str(exc_info.value)
    
    def test_execute_should_use_unit_of_work_transaction(
        self,
        mock_unit_of_work,
        mock_user_service,
        create_task_request,
        sample_task_id
    ):
        """
        Test task creation uses Unit of Work transaction correctly
        
        Scenario: Successful task creation
        Expected: UoW context manager is used for transaction
        """
        # Arrange
        active_user = Mock()
        active_user.is_active.return_value = True
        mock_user_service.find_user_by_id.return_value = active_user
        mock_unit_of_work.task_repository.get_task_count_by_user_id.return_value = 5
        
        use_case = CreateTaskUseCase(mock_unit_of_work, mock_user_service)
        
        with patch('uuid.uuid4', return_value=sample_task_id):
            # Act
            use_case.execute(create_task_request)
        
        # Assert
        # Verify UoW context manager was used
        mock_unit_of_work.__enter__.assert_called_once()
        mock_unit_of_work.__exit__.assert_called_once()
    
    def test_execute_should_log_task_creation(
        self,
        mock_unit_of_work,
        mock_user_service,
        create_task_request,
        sample_task_id
    ):
        """
        Test task creation includes proper logging
        
        Scenario: Successful task creation
        Expected: Appropriate log messages are generated
        """
        # Arrange
        active_user = Mock()
        active_user.is_active.return_value = True
        mock_user_service.find_user_by_id.return_value = active_user
        mock_unit_of_work.task_repository.get_task_count_by_user_id.return_value = 5
        
        use_case = CreateTaskUseCase(mock_unit_of_work, mock_user_service)
        
        with patch('uuid.uuid4', return_value=sample_task_id), \
             patch.object(use_case, '_logger') as mock_logger:
            
            # Act
            use_case.execute(create_task_request)
            
            # Assert
            # Verify success log was called
            mock_logger.info.assert_called_with(
                "task_created_successfully",
                task_id=str(sample_task_id),
                user_id=create_task_request.user_id
            )
    
    @pytest.mark.performance
    def test_execute_performance_within_acceptable_limits(
        self,
        mock_unit_of_work,
        mock_user_service,
        create_task_request,
        performance_timer
    ):
        """
        Test task creation performance is within acceptable limits
        
        Scenario: Task creation under normal conditions
        Expected: Execution time is under 100ms
        """
        # Arrange
        active_user = Mock()
        active_user.is_active.return_value = True
        mock_user_service.find_user_by_id.return_value = active_user
        mock_unit_of_work.task_repository.get_task_count_by_user_id.return_value = 5
        
        use_case = CreateTaskUseCase(mock_unit_of_work, mock_user_service)
        
        # Act
        performance_timer.start()
        use_case.execute(create_task_request)
        performance_timer.stop()
        
        # Assert
        assert performance_timer.duration < 0.1  # Less than 100ms 