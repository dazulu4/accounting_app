"""
User HTTP Routes - Enterprise Edition

This module provides HTTP endpoints for user management using Flask
with enterprise use cases, structured error handling, and sync operations.

Key Features:
- Enterprise use cases with sync operations
- Structured error handling and logging
- Pydantic validation for request/response
- Strategic logging at endpoint level
"""

from flask import Blueprint, current_app, jsonify, request

from application.schemas.task_schema import TaskListResponse
from application.schemas.user_schema import UserListResponse
from domain.exceptions.business_exceptions import UserNotFoundException
from infrastructure.helpers.errors.error_handlers import HTTPErrorHandler
from infrastructure.helpers.logger.logger_config import get_logger

# Crear un Blueprint para las rutas de usuarios
user_blueprint = Blueprint("users", __name__)

# Initialize structured logger
logger = get_logger(__name__)


@user_blueprint.route("", methods=["GET"])
def list_all_users():
    """Lista todos los usuarios."""
    # Get request context
    request_id = getattr(request, "request_id", "unknown")
    user_agent = request.headers.get("User-Agent", "unknown")
    remote_addr = request.remote_addr

    logger.info(
        "list_all_users_request_received",
        request_id=request_id,
        user_agent=user_agent,
        remote_addr=remote_addr,
    )

    try:
        # Obtener el caso de uso desde el contenedor
        use_case = current_app.container.list_all_users_use_case

        logger.debug("list_all_users_executing_use_case", request_id=request_id)

        # El caso de uso ahora devuelve entidades
        user_entities = use_case.execute()

        logger.info(
            "list_all_users_successful",
            request_id=request_id,
            user_count=len(user_entities),
        )

        # La ruta es responsable de la serialización
        response_schema = UserListResponse.from_entities(user_entities)

        return jsonify(response_schema.model_dump()), 200

    except Exception as e:
        logger.error(
            "list_all_users_unexpected_error",
            request_id=request_id,
            error_type=type(e).__name__,
            error_message=str(e),
        )
        response_data, status_code = HTTPErrorHandler.handle_exception(e)
        return jsonify(response_data), status_code


@user_blueprint.route("/<int:user_id>/tasks", methods=["GET"])
def list_tasks_by_user(user_id: int):
    """Lista las tareas de un usuario específico."""
    # Get request context
    request_id = getattr(request, "request_id", "unknown")
    user_agent = request.headers.get("User-Agent", "unknown")
    remote_addr = request.remote_addr

    logger.info(
        "list_tasks_by_user_request_received",
        request_id=request_id,
        user_id=user_id,
        user_agent=user_agent,
        remote_addr=remote_addr,
    )

    try:
        # Obtener el caso de uso desde el contenedor
        use_case = current_app.container.list_tasks_by_user_use_case

        logger.debug(
            "list_tasks_by_user_executing_use_case",
            request_id=request_id,
            user_id=user_id,
        )

        # El caso de uso ahora devuelve entidades
        task_entities = use_case.execute(user_id)

        logger.info(
            "list_tasks_by_user_successful",
            request_id=request_id,
            user_id=user_id,
            task_count=len(task_entities),
        )

        # La ruta es responsable de la serialización
        response_schema = TaskListResponse.from_entities(
            tasks=task_entities, user_id=user_id
        )

        return jsonify(response_schema.model_dump()), 200

    except UserNotFoundException as e:
        logger.warning(
            "list_tasks_by_user_not_found",
            request_id=request_id,
            user_id=user_id,
        )
        response_data, status_code = HTTPErrorHandler.handle_exception(e)
        return jsonify(response_data), status_code

    except Exception as e:
        logger.error(
            "list_tasks_by_user_unexpected_error",
            request_id=request_id,
            user_id=user_id,
            error_type=type(e).__name__,
            error_message=str(e),
        )
        response_data, status_code = HTTPErrorHandler.handle_exception(e)
        return jsonify(response_data), status_code
