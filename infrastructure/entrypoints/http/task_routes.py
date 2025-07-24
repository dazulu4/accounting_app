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
from infrastructure.helpers.logger.logger_config import get_logger, logging_context

# Crear un Blueprint para las rutas de tareas
task_blueprint = Blueprint('tasks', __name__)

# Initialize structured logger
logger = get_logger(__name__)


@task_blueprint.route('/tasks', methods=['POST'])
def create_task():
    """Crea una nueva tarea."""
    # Get request context
    request_id = getattr(request, 'request_id', 'unknown')
    user_agent = request.headers.get('User-Agent', 'unknown')
    remote_addr = request.remote_addr
    
    logger.info(
        "create_task_request_received",
        request_id=request_id,
        user_agent=user_agent,
        remote_addr=remote_addr
    )
    
    try:
        # Validate request data
        data = CreateTaskRequest(**request.json)
        
        logger.info(
            "create_task_data_validated",
            request_id=request_id,
            user_id=data.user_id,
            title=data.title[:50] + "..." if len(data.title) > 50 else data.title
        )
        
        # Obtener el caso de uso desde el contenedor
        use_case = current_app.container.create_task_use_case
        response_dto = use_case.execute(data)
        
        logger.info(
            "create_task_successful",
            request_id=request_id,
            task_id=response_dto.id,
            user_id=data.user_id
        )
        
        return jsonify(response_dto.model_dump()), 201
        
    except ValidationError as e:
        logger.warning(
            "create_task_validation_error",
            request_id=request_id,
            errors=str(e.errors()),
            user_agent=user_agent
        )
        response_data, status_code = HTTPErrorHandler.handle_exception(e)
        return jsonify(response_data), status_code
        
    except UserNotFoundException as e:
        logger.warning(
            "create_task_user_not_found",
            request_id=request_id,
            user_id=data.user_id if 'data' in locals() else 'unknown'
        )
        response_data, status_code = HTTPErrorHandler.handle_exception(e)
        return jsonify(response_data), status_code
        
    except UserNotActiveException as e:
        logger.warning(
            "create_task_user_inactive",
            request_id=request_id,
            user_id=data.user_id if 'data' in locals() else 'unknown'
        )
        response_data, status_code = HTTPErrorHandler.handle_exception(e)
        return jsonify(response_data), status_code
        
    except Exception as e:
        logger.error(
            "create_task_unexpected_error",
            request_id=request_id,
            error_type=type(e).__name__,
            error_message=str(e)
        )
        response_data, status_code = HTTPErrorHandler.handle_exception(e)
        return jsonify(response_data), status_code


@task_blueprint.route('/tasks/<uuid:task_id>/complete', methods=['PUT'])
def complete_task(task_id: UUID):
    """Marca una tarea como completada."""
    # Get request context
    request_id = getattr(request, 'request_id', 'unknown')
    user_agent = request.headers.get('User-Agent', 'unknown')
    remote_addr = request.remote_addr
    
    logger.info(
        "complete_task_request_received",
        request_id=request_id,
        task_id=str(task_id),
        user_agent=user_agent,
        remote_addr=remote_addr
    )
    
    try:
        # Validate request data
        request_dto = CompleteTaskRequest(task_id=task_id)
        
        logger.info(
            "complete_task_data_validated",
            request_id=request_id,
            task_id=str(task_id)
        )
        
        # Obtener el caso de uso desde el contenedor
        use_case = current_app.container.complete_task_use_case
        response_dto = use_case.execute(request_dto)
        
        logger.info(
            "complete_task_successful",
            request_id=request_id,
            task_id=str(task_id),
            completion_time=response_dto.completed_at.isoformat() if response_dto.completed_at else None
        )
        
        return jsonify(response_dto.model_dump()), 200
        
    except ValidationError as e:
        logger.warning(
            "complete_task_validation_error",
            request_id=request_id,
            task_id=str(task_id),
            errors=str(e.errors())
        )
        response_data, status_code = HTTPErrorHandler.handle_exception(e)
        return jsonify(response_data), status_code
        
    except TaskNotFoundException as e:
        logger.warning(
            "complete_task_not_found",
            request_id=request_id,
            task_id=str(task_id)
        )
        response_data, status_code = HTTPErrorHandler.handle_exception(e)
        return jsonify(response_data), status_code
        
    except TaskAlreadyCompletedException as e:
        logger.info(
            "complete_task_already_completed",
            request_id=request_id,
            task_id=str(task_id)
        )
        response_data, status_code = HTTPErrorHandler.handle_exception(e)
        return jsonify(response_data), status_code
        
    except InvalidTaskTransitionException as e:
        logger.warning(
            "complete_task_invalid_transition",
            request_id=request_id,
            task_id=str(task_id),
            current_status=getattr(e, 'current_status', 'unknown')
        )
        response_data, status_code = HTTPErrorHandler.handle_exception(e)
        return jsonify(response_data), status_code
        
    except Exception as e:
        logger.error(
            "complete_task_unexpected_error",
            request_id=request_id,
            task_id=str(task_id),
            error_type=type(e).__name__,
            error_message=str(e)
        )
        response_data, status_code = HTTPErrorHandler.handle_exception(e)
        return jsonify(response_data), status_code