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

from uuid import UUID

from flask import Blueprint, current_app, jsonify, request
from pydantic import ValidationError

from application.schemas.task_schema import (
    CompleteTaskRequest,
    CreateTaskRequest,
)
from domain.exceptions.business_exceptions import (
    InvalidTaskTransitionException,
    TaskAlreadyCompletedException,
    TaskNotFoundException,
    UserNotActiveException,
    UserNotFoundException,
)
from infrastructure.helpers.errors.error_handlers import HTTPErrorHandler
from infrastructure.helpers.logger.logger_config import get_logger

# Crear un Blueprint para las rutas de tareas
task_blueprint = Blueprint("tasks", __name__)

# Initialize structured logger
logger = get_logger(__name__)


@task_blueprint.route("", methods=["POST"])
def create_task():
    """Crea una nueva tarea."""
    logger.debug("create_task_request_received")

    try:
        # Validate request data
        data = CreateTaskRequest(**request.json)

        # Obtener el caso de uso desde el contenedor
        use_case = current_app.container.create_task_use_case
        response_dto = use_case.execute(data)

        logger.info(
            "task_created_successfully",
            task_id=response_dto.id,
            user_id=data.user_id,
        )

        return jsonify(response_dto.model_dump()), 201

    except ValidationError as e:
        logger.warning("task_creation_validation_error", errors=str(e.errors()))
        response_data, status_code = HTTPErrorHandler.handle_exception(e)
        return jsonify(response_data), status_code

    except UserNotFoundException as e:
        logger.warning("task_creation_user_not_found")
        response_data, status_code = HTTPErrorHandler.handle_exception(e)
        return jsonify(response_data), status_code

    except UserNotActiveException as e:
        logger.warning("task_creation_user_not_active")
        response_data, status_code = HTTPErrorHandler.handle_exception(e)
        return jsonify(response_data), status_code

    except Exception as e:
        logger.error("task_creation_unexpected_error", error_type=type(e).__name__)
        response_data, status_code = HTTPErrorHandler.handle_exception(e)
        return jsonify(response_data), status_code


@task_blueprint.route("/<uuid:task_id>/complete", methods=["PUT"])
def complete_task(task_id: UUID):
    """Marca una tarea como completada."""
    logger.debug("complete_task_request_received", task_id=str(task_id))

    try:
        # Validate request data
        request_dto = CompleteTaskRequest(task_id=task_id)

        # Obtener el caso de uso desde el contenedor
        use_case = current_app.container.complete_task_use_case
        response_dto = use_case.execute(request_dto)

        logger.info("task_completed_successfully", task_id=str(task_id))

        return jsonify(response_dto.model_dump()), 200

    except ValidationError as e:
        logger.warning("task_completion_validation_error", task_id=str(task_id))
        response_data, status_code = HTTPErrorHandler.handle_exception(e)
        return jsonify(response_data), status_code

    except TaskNotFoundException as e:
        logger.warning(
            "complete_task_not_found",
            request_id=request_id,
            task_id=str(task_id),
        )
        response_data, status_code = HTTPErrorHandler.handle_exception(e)
        return jsonify(response_data), status_code

    except TaskAlreadyCompletedException as e:
        logger.info(
            "complete_task_already_completed",
            request_id=request_id,
            task_id=str(task_id),
        )
        response_data, status_code = HTTPErrorHandler.handle_exception(e)
        return jsonify(response_data), status_code

    except InvalidTaskTransitionException as e:
        logger.warning(
            "complete_task_invalid_transition",
            request_id=request_id,
            task_id=str(task_id),
            current_status=getattr(e, "current_status", "unknown"),
        )
        response_data, status_code = HTTPErrorHandler.handle_exception(e)
        return jsonify(response_data), status_code

    except Exception as e:
        logger.error(
            "complete_task_unexpected_error",
            request_id=request_id,
            task_id=str(task_id),
            error_type=type(e).__name__,
            error_message=str(e),
        )
        response_data, status_code = HTTPErrorHandler.handle_exception(e)
        return jsonify(response_data), status_code
