"""
Task HTTP Routes - Enterprise Edition

This module provides HTTP endpoints for task management using Flask
with enterprise use cases, structured error handling, and sync operations.

Key Features:
- Enterprise use cases with Unit of Work pattern
- Synchronous operations optimized for AWS Lambda
- Structured error handling and logging
- Pydantic validation for request/response
- Strategic logging at endpoint level
"""

from flask import Blueprint, jsonify, request
from typing import List
from uuid import UUID

from application.di_container import get_create_task_usecase, get_complete_task_usecase, get_list_tasks_usecase
from domain.usecases.create_task_use_case import CreateTaskUseCase
from domain.usecases.complete_task_use_case import CompleteTaskUseCase
from domain.usecases.list_tasks_by_user_use_case import ListTasksByUserUseCase

# Import enterprise value objects
from domain.value_objects.task_value_objects import (
    CreateTaskRequest,
    CreateTaskResponse,
    CompleteTaskRequest,
    CompleteTaskResponse
)

# Import Pydantic schemas for HTTP layer
from application.schemas.task_schema import (
    TaskCreate,
    TaskResponse,
    TaskListResponse,
    TaskCompleteRequest
)
from pydantic import ValidationError

# Import enterprise logging and error handling
from infrastructure.helpers.logger.logger_config import get_logger
from infrastructure.helpers.middleware.http_middleware import log_endpoint_access, require_json
from infrastructure.helpers.errors.error_handlers import create_validation_error_response

# Configure logger
logger = get_logger(__name__)

# Create Blueprint
task_blueprint = Blueprint('tasks', __name__)


@task_blueprint.route("", methods=['POST'])
@log_endpoint_access('create_task')
@require_json()
def create_task():
    """
    Create a new task using enterprise use case
    
    Returns:
        JSON response with created task or error
    """
    try:
        # Get request data
        data = request.get_json()
        if not data:
            response_data, status_code = create_validation_error_response(
                "No JSON data provided"
            )
            return jsonify(response_data), status_code
        
        # Validate data with Pydantic
        try:
            task_create = TaskCreate(**data)
        except ValidationError as e:
            response_data, status_code = create_validation_error_response(
                "Invalid data provided",
                {field: error['msg'] for error in e.errors() for field in [error['loc'][-1]]}
            )
            return jsonify(response_data), status_code
        
        # Create request value object
        create_request = CreateTaskRequest(
            title=task_create.title,
            description=task_create.description,
            user_id=task_create.user_id
        )
        
        # Get enterprise use case
        usecase = get_create_task_usecase()
        
        # Execute use case (sync)
        create_response = usecase.execute(create_request)
        
        # Convert to HTTP response schema
        response_task = TaskResponse.model_validate({
            "task_id": str(create_response.task_id),
            "title": create_response.title,
            "description": create_response.description,
            "user_id": create_response.user_id,
            "status": create_response.status,
            "priority": create_response.priority,
            "created_at": create_response.created_at.isoformat(),
            "completed_at": create_response.completed_at.isoformat() if create_response.completed_at else None
        })
        
        return jsonify(response_task.model_dump()), 201
        
    except Exception as e:
        # Let error handling middleware handle exceptions
        logger.error(
            "create_task_endpoint_error",
            error_type=type(e).__name__,
            error_message=str(e)
        )
        raise


@task_blueprint.route("/<task_id>/complete", methods=['PUT'])
@log_endpoint_access('complete_task')
@require_json()
def complete_task(task_id: str):
    """
    Complete a task using enterprise use case
    
    Args:
        task_id: UUID of the task to complete
        
    Returns:
        JSON response with completed task or error
    """
    try:
        # Validate task_id format
        try:
            task_uuid = UUID(task_id)
        except ValueError:
            response_data, status_code = create_validation_error_response(
                "Invalid task ID format"
            )
            return jsonify(response_data), status_code
        
        # Create request value object
        complete_request = CompleteTaskRequest(task_id=task_uuid)
        
        # Get enterprise use case
        usecase = get_complete_task_usecase()
        
        # Execute use case (sync)
        complete_response = usecase.execute(complete_request)
        
        # Convert to HTTP response schema
        response_task = TaskResponse.model_validate({
            "task_id": str(complete_response.task_id),
            "title": complete_response.title,
            "description": complete_response.description,
            "user_id": complete_response.user_id,
            "status": complete_response.status,
            "priority": complete_response.priority,
            "created_at": complete_response.created_at.isoformat(),
            "completed_at": complete_response.completed_at.isoformat() if complete_response.completed_at else None
        })
        
        return jsonify(response_task.model_dump()), 200
        
    except Exception as e:
        # Let error handling middleware handle exceptions
        logger.error(
            "complete_task_endpoint_error",
            task_id=task_id,
            error_type=type(e).__name__,
            error_message=str(e)
        )
        raise


@task_blueprint.route("/user/<int:user_id>", methods=['GET'])
@log_endpoint_access('list_tasks_by_user')
def list_tasks_by_user(user_id: int):
    """
    List all tasks for a specific user using enterprise use case
    
    Args:
        user_id: ID of the user
        
    Returns:
        JSON response with user tasks or error
    """
    try:
        # Get enterprise use case
        usecase = get_list_tasks_usecase()
        
        # Execute use case (sync) - assuming it takes user_id parameter
        tasks_response = usecase.execute(user_id)
        
        # Convert to HTTP response schema
        response_tasks = [
            TaskResponse.model_validate({
                "task_id": str(task.task_id),
                "title": task.title,
                "description": task.description,
                "user_id": task.user_id,
                "status": task.status,
                "priority": task.priority,
                "created_at": task.created_at.isoformat(),
                "completed_at": task.completed_at.isoformat() if task.completed_at else None
            })
            for task in tasks_response.tasks
        ]
        
        task_list_response = TaskListResponse(
            tasks=response_tasks,
            total_count=len(response_tasks)
        )
        
        return jsonify(task_list_response.model_dump()), 200
        
    except Exception as e:
        # Let error handling middleware handle exceptions
        logger.error(
            "list_tasks_by_user_endpoint_error",
            user_id=user_id,
            error_type=type(e).__name__,
            error_message=str(e)
        )
        raise