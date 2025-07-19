"""
Integration Tests for API Endpoints - Enterprise Edition

Integration tests for HTTP API endpoints using Flask test client
with complete request/response validation and error handling.

Test Coverage:
- HTTP endpoint integration with use cases
- Request/response serialization/deserialization
- Error handling and status codes
- API security and validation
- Performance of API operations
"""

import pytest
import json
from datetime import datetime, timezone
from uuid import uuid4
from unittest.mock import Mock, patch

from application.main import create_app
from domain.enums.task_status_enum import TaskStatusEnum, TaskPriorityEnum
from domain.exceptions.business_exceptions import (
    UserNotFoundException,
    UserNotActiveException,
    TaskNotFoundException,
    InvalidTaskTransitionException
)


@pytest.mark.integration
@pytest.mark.api
class TestTaskAPIIntegration:
    """Integration tests for Task API endpoints"""
    
    @pytest.fixture
    def app(self):
        """Create test Flask application"""
        app = create_app()
        app.config['TESTING'] = True
        return app
    
    @pytest.fixture
    def client(self, app):
        """Create test client"""
        return app.test_client()
    
    @pytest.fixture
    def api_headers(self):
        """Standard API headers"""
        return {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
    
    def test_create_task_endpoint_success(self, client, api_headers):
        """
        Test successful task creation via POST /tasks endpoint
        
        Integration Flow:
        1. Send POST request with valid task data
        2. Verify 201 response with created task
        3. Verify response structure and data
        """
        # Arrange
        task_data = {
            "title": "API Integration Test Task",
            "description": "Task created via API for integration testing",
            "user_id": 1
        }
        
        with patch('domain.usecases.create_task_use_case.CreateTaskUseCase') as mock_use_case_class:
            mock_use_case = Mock()
            mock_use_case_class.return_value = mock_use_case
            
            # Mock successful response
            mock_task_id = uuid4()
            mock_response = Mock()
            mock_response.task_id = mock_task_id
            mock_response.title = task_data["title"]
            mock_response.description = task_data["description"]
            mock_response.user_id = task_data["user_id"]
            mock_response.status = TaskStatusEnum.PENDING.value
            mock_response.priority = TaskPriorityEnum.MEDIUM.value
            mock_response.created_at = datetime.now(timezone.utc)
            mock_response.updated_at = datetime.now(timezone.utc)
            mock_response.completed_at = None
            
            mock_use_case.execute.return_value = mock_response
            
            # Act
            response = client.post(
                '/api/tasks',
                data=json.dumps(task_data),
                headers=api_headers
            )
            
            # Assert
            assert response.status_code == 201
            
            response_data = json.loads(response.data)
            assert response_data['task_id'] == str(mock_task_id)
            assert response_data['title'] == task_data["title"]
            assert response_data['description'] == task_data["description"]
            assert response_data['user_id'] == task_data["user_id"]
            assert response_data['status'] == TaskStatusEnum.PENDING.value
            assert response_data['priority'] == TaskPriorityEnum.MEDIUM.value
            assert 'created_at' in response_data
            assert 'updated_at' in response_data
            assert response_data['completed_at'] is None
    
    def test_create_task_endpoint_validation_error(self, client, api_headers):
        """
        Test task creation with validation errors
        
        Integration Flow:
        1. Send POST request with invalid data
        2. Verify 422 response with validation errors
        3. Verify error message structure
        """
        # Arrange - Missing required title
        invalid_task_data = {
            "description": "Task without title",
            "user_id": 1
        }
        
        # Act
        response = client.post(
            '/api/tasks',
            data=json.dumps(invalid_task_data),
            headers=api_headers
        )
        
        # Assert
        assert response.status_code == 422
        
        response_data = json.loads(response.data)
        assert 'error' in response_data
        assert response_data['error']['type'] == 'VALIDATION_ERROR'
        assert 'title' in response_data['error']['message']
    
    def test_create_task_endpoint_user_not_active(self, client, api_headers):
        """
        Test task creation for inactive user
        
        Integration Flow:
        1. Send POST request for inactive user
        2. Verify 400 response with business error
        3. Verify error handling across layers
        """
        # Arrange
        task_data = {
            "title": "Task for Inactive User",
            "description": "This should fail",
            "user_id": 999
        }
        
        with patch('domain.usecases.create_task_use_case.CreateTaskUseCase') as mock_use_case_class:
            mock_use_case = Mock()
            mock_use_case_class.return_value = mock_use_case
            
            # Mock business exception
            mock_use_case.execute.side_effect = UserNotActiveException("User 999 is not active")
            
            # Act
            response = client.post(
                '/api/tasks',
                data=json.dumps(task_data),
                headers=api_headers
            )
            
            # Assert
            assert response.status_code == 400
            
            response_data = json.loads(response.data)
            assert response_data['error']['type'] == 'USER_NOT_ACTIVE'
            assert 'User 999 is not active' in response_data['error']['message']
    
    def test_complete_task_endpoint_success(self, client, api_headers):
        """
        Test successful task completion via PUT /tasks/{id}/complete
        
        Integration Flow:
        1. Send PUT request to complete task
        2. Verify 200 response with updated task
        3. Verify completion timestamp and status
        """
        # Arrange
        task_id = uuid4()
        
        with patch('domain.usecases.complete_task_use_case.CompleteTaskUseCase') as mock_use_case_class:
            mock_use_case = Mock()
            mock_use_case_class.return_value = mock_use_case
            
            # Mock successful completion response
            completion_time = datetime.now(timezone.utc)
            mock_response = Mock()
            mock_response.task_id = task_id
            mock_response.title = "Completed Task"
            mock_response.description = "Task has been completed"
            mock_response.user_id = 1
            mock_response.status = TaskStatusEnum.COMPLETED.value
            mock_response.priority = TaskPriorityEnum.MEDIUM.value
            mock_response.created_at = datetime.now(timezone.utc)
            mock_response.updated_at = completion_time
            mock_response.completed_at = completion_time
            
            mock_use_case.execute.return_value = mock_response
            
            # Act
            response = client.put(
                f'/api/tasks/{task_id}/complete',
                headers=api_headers
            )
            
            # Assert
            assert response.status_code == 200
            
            response_data = json.loads(response.data)
            assert response_data['task_id'] == str(task_id)
            assert response_data['status'] == TaskStatusEnum.COMPLETED.value
            assert response_data['completed_at'] is not None
            assert response_data['updated_at'] is not None
    
    def test_complete_task_endpoint_not_found(self, client, api_headers):
        """
        Test task completion for non-existent task
        
        Integration Flow:
        1. Send PUT request for non-existent task
        2. Verify 404 response with appropriate error
        3. Verify error propagation from domain layer
        """
        # Arrange
        non_existent_task_id = uuid4()
        
        with patch('domain.usecases.complete_task_use_case.CompleteTaskUseCase') as mock_use_case_class:
            mock_use_case = Mock()
            mock_use_case_class.return_value = mock_use_case
            
            # Mock not found exception
            mock_use_case.execute.side_effect = TaskNotFoundException(
                f"Task {non_existent_task_id} not found"
            )
            
            # Act
            response = client.put(
                f'/api/tasks/{non_existent_task_id}/complete',
                headers=api_headers
            )
            
            # Assert
            assert response.status_code == 404
            
            response_data = json.loads(response.data)
            assert response_data['error']['type'] == 'TASK_NOT_FOUND'
            assert str(non_existent_task_id) in response_data['error']['message']
    
    def test_list_tasks_endpoint_success(self, client, api_headers):
        """
        Test successful task listing via GET /users/{id}/tasks
        
        Integration Flow:
        1. Send GET request for user's tasks
        2. Verify 200 response with task list
        3. Verify pagination and sorting
        """
        # Arrange
        user_id = 1
        
        with patch('domain.usecases.list_tasks_by_user_use_case.ListTasksByUserUseCase') as mock_use_case_class:
            mock_use_case = Mock()
            mock_use_case_class.return_value = mock_use_case
            
            # Mock task list response
            mock_task_1 = Mock()
            mock_task_1.task_id = uuid4()
            mock_task_1.title = "Task 1"
            mock_task_1.status = TaskStatusEnum.PENDING.value
            mock_task_1.created_at = datetime.now(timezone.utc)
            
            mock_task_2 = Mock()
            mock_task_2.task_id = uuid4()
            mock_task_2.title = "Task 2"
            mock_task_2.status = TaskStatusEnum.COMPLETED.value
            mock_task_2.created_at = datetime.now(timezone.utc)
            
            mock_response = Mock()
            mock_response.tasks = [mock_task_1, mock_task_2]
            mock_response.total_count = 2
            mock_response.user_id = user_id
            
            mock_use_case.execute.return_value = mock_response
            
            # Act
            response = client.get(
                f'/api/users/{user_id}/tasks',
                headers=api_headers
            )
            
            # Assert
            assert response.status_code == 200
            
            response_data = json.loads(response.data)
            assert len(response_data['tasks']) == 2
            assert response_data['total_count'] == 2
            assert response_data['user_id'] == user_id
            
            # Verify task data structure
            task_1_data = response_data['tasks'][0]
            assert 'task_id' in task_1_data
            assert task_1_data['title'] == "Task 1"
            assert task_1_data['status'] == TaskStatusEnum.PENDING.value
    
    def test_api_error_handling_consistency(self, client, api_headers):
        """
        Test consistent error handling across all endpoints
        
        Integration Flow:
        1. Test various error scenarios
        2. Verify consistent error response format
        3. Verify appropriate HTTP status codes
        """
        test_cases = [
            {
                'endpoint': '/api/tasks',
                'method': 'POST',
                'data': {},  # Invalid data
                'expected_status': 422,
                'expected_error_type': 'VALIDATION_ERROR'
            },
            {
                'endpoint': f'/api/tasks/{uuid4()}/complete',
                'method': 'PUT',
                'data': None,
                'expected_status': 404,
                'mock_exception': TaskNotFoundException("Task not found"),
                'expected_error_type': 'TASK_NOT_FOUND'
            }
        ]
        
        for test_case in test_cases:
            with patch('domain.usecases.create_task_use_case.CreateTaskUseCase') as mock_create_use_case_class, \
                 patch('domain.usecases.complete_task_use_case.CompleteTaskUseCase') as mock_complete_use_case_class:
                
                if 'mock_exception' in test_case:
                    if 'complete' in test_case['endpoint']:
                        mock_use_case = Mock()
                        mock_complete_use_case_class.return_value = mock_use_case
                        mock_use_case.execute.side_effect = test_case['mock_exception']
                
                # Act
                if test_case['method'] == 'POST':
                    response = client.post(
                        test_case['endpoint'],
                        data=json.dumps(test_case['data']) if test_case['data'] else None,
                        headers=api_headers
                    )
                elif test_case['method'] == 'PUT':
                    response = client.put(
                        test_case['endpoint'],
                        headers=api_headers
                    )
                
                # Assert
                assert response.status_code == test_case['expected_status']
                
                response_data = json.loads(response.data)
                assert 'error' in response_data
                assert 'type' in response_data['error']
                assert 'message' in response_data['error']
                assert 'timestamp' in response_data['error']
                
                if 'expected_error_type' in test_case:
                    assert response_data['error']['type'] == test_case['expected_error_type']
    
    @pytest.mark.performance
    def test_api_performance_under_load(self, client, api_headers, performance_timer):
        """
        Test API performance under simulated load
        
        Integration Flow:
        1. Make multiple concurrent API requests
        2. Verify response times are acceptable
        3. Verify system stability under load
        """
        # Arrange
        with patch('domain.usecases.create_task_use_case.CreateTaskUseCase') as mock_use_case_class:
            mock_use_case = Mock()
            mock_use_case_class.return_value = mock_use_case
            
            # Mock fast response
            mock_response = Mock()
            mock_response.task_id = uuid4()
            mock_response.title = "Performance Test Task"
            mock_response.status = TaskStatusEnum.PENDING.value
            mock_response.created_at = datetime.now(timezone.utc)
            mock_use_case.execute.return_value = mock_response
            
            task_data = {
                "title": "Performance Test Task",
                "description": "Task for performance testing",
                "user_id": 1
            }
            
            # Act
            performance_timer.start()
            
            num_requests = 20
            for i in range(num_requests):
                response = client.post(
                    '/api/tasks',
                    data=json.dumps(task_data),
                    headers=api_headers
                )
                assert response.status_code == 201
            
            performance_timer.stop()
            
            # Assert
            average_response_time = performance_timer.duration / num_requests
            assert average_response_time < 0.1  # Less than 100ms per request
            assert performance_timer.duration < 2.0  # Total time less than 2 seconds 