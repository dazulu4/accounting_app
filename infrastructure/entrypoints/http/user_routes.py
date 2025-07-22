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

from flask import Blueprint, jsonify, current_app

from application.schemas.user_schema import UserListResponse
from application.schemas.task_schema import TaskListResponse
from domain.exceptions.business_exceptions import UserNotFoundException

# Crear un Blueprint para las rutas de usuarios
user_blueprint = Blueprint('users', __name__)

@user_blueprint.route('/users', methods=['GET'])
def list_all_users():
    """Lista todos los usuarios."""
    # Obtener el caso de uso desde el contenedor
    use_case = current_app.container.list_all_users_use_case
    
    # El caso de uso ahora devuelve entidades
    user_entities = use_case.execute()
    
    # La ruta es responsable de la serialización
    response_schema = UserListResponse.from_entities(user_entities)
    
    return jsonify(response_schema.model_dump()), 200

@user_blueprint.route('/users/<int:user_id>/tasks', methods=['GET'])
def list_tasks_by_user(user_id: int):
    """Lista las tareas de un usuario específico."""
    try:
        # Obtener el caso de uso desde el contenedor
        use_case = current_app.container.list_tasks_by_user_use_case
        
        # El caso de uso ahora devuelve entidades
        task_entities = use_case.execute(user_id)
        
        # La ruta es responsable de la serialización
        response_schema = TaskListResponse.from_entities(
            tasks=task_entities, 
            user_id=user_id
        )
        
        return jsonify(response_schema.model_dump()), 200
    except UserNotFoundException as e:
        return jsonify({"error": {"type": "USER_NOT_FOUND", "message": str(e)}}), 404
