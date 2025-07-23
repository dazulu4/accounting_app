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
from infrastructure.helpers.errors.error_handlers import HTTPErrorHandler

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
    except Exception as e:
        # Usar manejo centralizado de errores
        response_data, status_code = HTTPErrorHandler.handle_exception(e)
        return jsonify(response_data), status_code

@task_blueprint.route('/tasks/<uuid:task_id>/complete', methods=['PUT'])
def complete_task(task_id: UUID):
    """Marca una tarea como completada."""
    try:
        request_dto = CompleteTaskRequest(task_id=task_id)
        
        # Obtener el caso de uso desde el contenedor
        use_case = current_app.container.complete_task_use_case
        response_dto = use_case.execute(request_dto)
        
        return jsonify(response_dto.model_dump()), 200
    except Exception as e:
        # Usar manejo centralizado de errores
        response_data, status_code = HTTPErrorHandler.handle_exception(e)
        return jsonify(response_data), status_code