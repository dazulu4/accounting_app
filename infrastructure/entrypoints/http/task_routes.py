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

from flask import Blueprint, request, jsonify, current_app
from uuid import UUID
from pydantic import ValidationError

from application.schemas.task_schema import CreateTaskRequest, CompleteTaskRequest
from domain.exceptions.business_exceptions import (
    UserNotFoundException, 
    UserNotActiveException,
    TaskNotFoundException,
    InvalidTaskTransitionException,
    TaskAlreadyCompletedException
)

# Crear un Blueprint para las rutas de tareas
task_blueprint = Blueprint('tasks', __name__)

@task_blueprint.route('/tasks', methods=['POST'])
def create_task():
    """Crea una nueva tarea."""
    try:
        data = CreateTaskRequest(**request.json)
        
        # Obtener el caso de uso desde el contenedor
        use_case = current_app.container.create_task_use_case
        response_dto = use_case.execute(data)
        
        return jsonify(response_dto.model_dump()), 201
    except ValidationError as e:
        return jsonify({"error": {"type": "VALIDATION_ERROR", "message": e.errors()}}), 422
    except (UserNotFoundException, UserNotActiveException) as e:
        return jsonify({"error": {"type": type(e).__name__, "message": str(e)}}), 400

@task_blueprint.route('/tasks/<uuid:task_id>/complete', methods=['PUT'])
def complete_task(task_id: UUID):
    """Marca una tarea como completada."""
    try:
        request_dto = CompleteTaskRequest(task_id=task_id)
        
        # Obtener el caso de uso desde el contenedor
        use_case = current_app.container.complete_task_use_case
        response_dto = use_case.execute(request_dto)
        
        return jsonify(response_dto.model_dump()), 200
    except TaskNotFoundException as e:
        return jsonify({"error": {"type": "TASK_NOT_FOUND", "message": str(e)}}), 404
    except (InvalidTaskTransitionException, TaskAlreadyCompletedException) as e:
        return jsonify({"error": {"type": type(e).__name__, "message": str(e)}}), 409