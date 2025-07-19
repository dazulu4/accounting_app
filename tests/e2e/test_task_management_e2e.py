"""
End-to-End Tests for Task Management - Enterprise Edition

Complete E2E tests that verify the entire task management system
from HTTP requests through all layers to the database level.

Test Coverage:
- Complete user journey from task creation to completion
- Real database operations (with test database)
- API authentication and authorization
- Cross-system integration scenarios
- Performance under realistic conditions
"""

import pytest
import json
import time
from datetime import datetime, timezone
from uuid import UUID
from unittest.mock import patch

from application.main import create_app


@pytest.mark.e2e
class TestTaskManagementE2E:
    """End-to-end tests for complete task management workflows"""
    
    @pytest.fixture(scope="class")
    def app(self):
        """Create test application with real configuration"""
        app = create_app()
        app.config['TESTING'] = True
        app.config['DATABASE_NAME'] = 'accounting_test'
        return app
    
    @pytest.fixture(scope="class")
    def client(self, app):
        """Create test client for E2E testing"""
        return app.test_client()
    
    @pytest.fixture
    def api_headers(self):
        """Standard API headers for E2E testing"""
        return {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
    
    def test_complete_task_lifecycle_e2e(self, client, api_headers):
        """
        Test complete task lifecycle end-to-end
        
        E2E Journey:
        1. Create a new task via API
        2. Verify task appears in user's task list
        3. Complete the task via API
        4. Verify task status is updated
        5. Verify timestamps and data consistency
        """
        # Step 1: Create a new task
        task_data = {
            "title": "E2E Test Task",
            "description": "Complete end-to-end test task",
            "user_id": 1
        }
        
        create_response = client.post(
            '/api/tasks',
            data=json.dumps(task_data),
            headers=api_headers
        )
        
        assert create_response.status_code == 201
        create_data = json.loads(create_response.data)
        task_id = create_data['task_id']
        
        # Verify created task data
        assert create_data['title'] == task_data['title']
        assert create_data['description'] == task_data['description']
        assert create_data['user_id'] == task_data['user_id']
        assert create_data['status'] == 'pending'
        assert create_data['priority'] == 'medium'
        assert create_data['completed_at'] is None
        assert 'created_at' in create_data
        assert 'updated_at' in create_data
        
        # Step 2: Verify task appears in user's task list
        list_response = client.get(
            f'/api/users/{task_data["user_id"]}/tasks',
            headers=api_headers
        )
        
        assert list_response.status_code == 200
        list_data = json.loads(list_response.data)
        
        # Find our created task in the list
        created_task_in_list = None
        for task in list_data['tasks']:
            if task['task_id'] == task_id:
                created_task_in_list = task
                break
        
        assert created_task_in_list is not None
        assert created_task_in_list['status'] == 'pending'
        assert created_task_in_list['title'] == task_data['title']
        
        # Step 3: Complete the task
        complete_response = client.put(
            f'/api/tasks/{task_id}/complete',
            headers=api_headers
        )
        
        assert complete_response.status_code == 200
        complete_data = json.loads(complete_response.data)
        
        # Verify completion data
        assert complete_data['task_id'] == task_id
        assert complete_data['status'] == 'completed'
        assert complete_data['completed_at'] is not None
        assert complete_data['updated_at'] is not None
        
        # Verify data consistency
        assert complete_data['title'] == task_data['title']
        assert complete_data['description'] == task_data['description']
        assert complete_data['user_id'] == task_data['user_id']
        assert complete_data['created_at'] == create_data['created_at']
        
        # Step 4: Verify updated task in list
        updated_list_response = client.get(
            f'/api/users/{task_data["user_id"]}/tasks',
            headers=api_headers
        )
        
        assert updated_list_response.status_code == 200
        updated_list_data = json.loads(updated_list_response.data)
        
        # Find completed task in the list
        completed_task_in_list = None
        for task in updated_list_data['tasks']:
            if task['task_id'] == task_id:
                completed_task_in_list = task
                break
        
        assert completed_task_in_list is not None
        assert completed_task_in_list['status'] == 'completed'
        assert completed_task_in_list['completed_at'] is not None
        
        # Step 5: Verify timestamps are logical
        created_at = datetime.fromisoformat(create_data['created_at'].replace('Z', '+00:00'))
        completed_at = datetime.fromisoformat(complete_data['completed_at'].replace('Z', '+00:00'))
        updated_at = datetime.fromisoformat(complete_data['updated_at'].replace('Z', '+00:00'))
        
        assert completed_at >= created_at
        assert updated_at >= created_at
        assert abs((completed_at - updated_at).total_seconds()) < 1  # Should be very close
    
    def test_error_handling_e2e(self, client, api_headers):
        """
        Test error handling across the complete system
        
        E2E Error Scenarios:
        1. Create task with invalid data
        2. Complete non-existent task
        3. Create task for inactive user
        4. Verify consistent error responses
        """
        # Scenario 1: Invalid task creation
        invalid_task_data = {
            "description": "Task without title",
            "user_id": 1
        }
        
        invalid_create_response = client.post(
            '/api/tasks',
            data=json.dumps(invalid_task_data),
            headers=api_headers
        )
        
        assert invalid_create_response.status_code == 422
        error_data = json.loads(invalid_create_response.data)
        assert 'error' in error_data
        assert error_data['error']['type'] == 'VALIDATION_ERROR'
        
        # Scenario 2: Complete non-existent task
        fake_task_id = "00000000-0000-0000-0000-000000000000"
        
        nonexistent_complete_response = client.put(
            f'/api/tasks/{fake_task_id}/complete',
            headers=api_headers
        )
        
        assert nonexistent_complete_response.status_code == 404
        error_data = json.loads(nonexistent_complete_response.data)
        assert error_data['error']['type'] == 'TASK_NOT_FOUND'
        
        # Scenario 3: Create task for inactive user (if implemented)
        inactive_user_task = {
            "title": "Task for Inactive User",
            "description": "This should fail",
            "user_id": 999  # Assuming this user doesn't exist or is inactive
        }
        
        inactive_user_response = client.post(
            '/api/tasks',
            data=json.dumps(inactive_user_task),
            headers=api_headers
        )
        
        # Should fail with appropriate error
        assert inactive_user_response.status_code in [400, 404]
        error_data = json.loads(inactive_user_response.data)
        assert 'error' in error_data
    
    def test_multiple_users_isolation_e2e(self, client, api_headers):
        """
        Test data isolation between different users
        
        E2E Isolation Test:
        1. Create tasks for different users
        2. Verify each user only sees their own tasks
        3. Verify operations don't affect other users' data
        """
        # Create tasks for user 1
        user1_task1 = {
            "title": "User 1 Task 1",
            "description": "First task for user 1",
            "user_id": 1
        }
        
        user1_task2 = {
            "title": "User 1 Task 2", 
            "description": "Second task for user 1",
            "user_id": 1
        }
        
        # Create tasks for user 2
        user2_task1 = {
            "title": "User 2 Task 1",
            "description": "First task for user 2",
            "user_id": 2
        }
        
        # Create all tasks
        u1t1_response = client.post('/api/tasks', data=json.dumps(user1_task1), headers=api_headers)
        u1t2_response = client.post('/api/tasks', data=json.dumps(user1_task2), headers=api_headers)
        u2t1_response = client.post('/api/tasks', data=json.dumps(user2_task1), headers=api_headers)
        
        assert u1t1_response.status_code == 201
        assert u1t2_response.status_code == 201
        assert u2t1_response.status_code == 201
        
        u1t1_data = json.loads(u1t1_response.data)
        u1t2_data = json.loads(u1t2_response.data)
        u2t1_data = json.loads(u2t1_response.data)
        
        # Verify user 1 sees only their tasks
        user1_list_response = client.get('/api/users/1/tasks', headers=api_headers)
        assert user1_list_response.status_code == 200
        user1_tasks = json.loads(user1_list_response.data)['tasks']
        
        user1_task_ids = [task['task_id'] for task in user1_tasks]
        assert u1t1_data['task_id'] in user1_task_ids
        assert u1t2_data['task_id'] in user1_task_ids
        assert u2t1_data['task_id'] not in user1_task_ids
        
        # Verify user 2 sees only their tasks
        user2_list_response = client.get('/api/users/2/tasks', headers=api_headers)
        assert user2_list_response.status_code == 200
        user2_tasks = json.loads(user2_list_response.data)['tasks']
        
        user2_task_ids = [task['task_id'] for task in user2_tasks]
        assert u2t1_data['task_id'] in user2_task_ids
        assert u1t1_data['task_id'] not in user2_task_ids
        assert u1t2_data['task_id'] not in user2_task_ids
        
        # Complete a task for user 1 and verify it doesn't affect user 2
        complete_response = client.put(
            f'/api/tasks/{u1t1_data["task_id"]}/complete',
            headers=api_headers
        )
        assert complete_response.status_code == 200
        
        # Verify user 2's tasks are unchanged
        user2_list_after = client.get('/api/users/2/tasks', headers=api_headers)
        user2_tasks_after = json.loads(user2_list_after.data)['tasks']
        
        for task in user2_tasks_after:
            if task['task_id'] == u2t1_data['task_id']:
                assert task['status'] == 'pending'  # Should still be pending
    
    @pytest.mark.performance
    def test_system_performance_e2e(self, client, api_headers, performance_timer):
        """
        Test system performance under realistic E2E conditions
        
        E2E Performance Test:
        1. Create multiple tasks rapidly
        2. Perform various operations
        3. Verify system responds within acceptable time
        """
        performance_timer.start()
        
        # Create 10 tasks rapidly
        created_task_ids = []
        for i in range(10):
            task_data = {
                "title": f"Performance Test Task {i+1}",
                "description": f"Task {i+1} for performance testing",
                "user_id": 1
            }
            
            response = client.post(
                '/api/tasks',
                data=json.dumps(task_data),
                headers=api_headers
            )
            
            assert response.status_code == 201
            task_id = json.loads(response.data)['task_id']
            created_task_ids.append(task_id)
        
        # List tasks
        list_response = client.get('/api/users/1/tasks', headers=api_headers)
        assert list_response.status_code == 200
        
        # Complete half of the tasks
        for i in range(0, len(created_task_ids), 2):
            complete_response = client.put(
                f'/api/tasks/{created_task_ids[i]}/complete',
                headers=api_headers
            )
            assert complete_response.status_code == 200
        
        # Final list to verify state
        final_list_response = client.get('/api/users/1/tasks', headers=api_headers)
        assert final_list_response.status_code == 200
        
        performance_timer.stop()
        
        # Assert performance criteria
        assert performance_timer.duration < 5.0  # Total operations under 5 seconds
        
        # Verify data integrity
        final_tasks = json.loads(final_list_response.data)['tasks']
        completed_count = sum(1 for task in final_tasks if task['status'] == 'completed')
        pending_count = sum(1 for task in final_tasks if task['status'] == 'pending')
        
        assert completed_count >= 5  # At least 5 completed
        assert pending_count >= 5   # At least 5 pending
    
    def test_data_persistence_e2e(self, client, api_headers):
        """
        Test data persistence across requests
        
        E2E Persistence Test:
        1. Create task and verify immediate persistence
        2. Perform operations and verify changes persist
        3. Verify data consistency across multiple requests
        """
        # Create a task
        task_data = {
            "title": "Persistence Test Task",
            "description": "Testing data persistence across requests",
            "user_id": 1
        }
        
        create_response = client.post(
            '/api/tasks',
            data=json.dumps(task_data),
            headers=api_headers
        )
        
        assert create_response.status_code == 201
        created_task = json.loads(create_response.data)
        task_id = created_task['task_id']
        
        # Verify immediate retrieval
        immediate_list = client.get('/api/users/1/tasks', headers=api_headers)
        immediate_tasks = json.loads(immediate_list.data)['tasks']
        
        immediate_task = next((t for t in immediate_tasks if t['task_id'] == task_id), None)
        assert immediate_task is not None
        assert immediate_task['title'] == task_data['title']
        assert immediate_task['status'] == 'pending'
        
        # Wait a moment to simulate real-world delay
        time.sleep(0.1)
        
        # Complete the task
        complete_response = client.put(
            f'/api/tasks/{task_id}/complete',
            headers=api_headers
        )
        assert complete_response.status_code == 200
        
        # Verify persistence of completion
        completed_list = client.get('/api/users/1/tasks', headers=api_headers)
        completed_tasks = json.loads(completed_list.data)['tasks']
        
        completed_task = next((t for t in completed_tasks if t['task_id'] == task_id), None)
        assert completed_task is not None
        assert completed_task['status'] == 'completed'
        assert completed_task['completed_at'] is not None
        
        # Verify persistence across another request
        time.sleep(0.1)
        final_list = client.get('/api/users/1/tasks', headers=api_headers)
        final_tasks = json.loads(final_list.data)['tasks']
        
        final_task = next((t for t in final_tasks if t['task_id'] == task_id), None)
        assert final_task is not None
        assert final_task['status'] == 'completed'
        assert final_task['completed_at'] == completed_task['completed_at'] 