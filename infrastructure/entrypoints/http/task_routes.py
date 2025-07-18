"""
Rutas HTTP para la gestión de tareas usando Flask

Beneficios de usar Flask:
- Más ligero y rápido
- Mayor control sobre el manejo de errores
- Mejor compatibilidad con AWS Lambda
- Validaciones manuales más flexibles
"""

from flask import Blueprint, jsonify, request
from typing import List
from uuid import UUID

from application.di_container import get_create_task_usecase, get_complete_task_usecase, get_list_tasks_usecase
from domain.usecases.create_task import CreateTaskUseCase
from domain.usecases.complete_task import CompleteTaskUseCase
from domain.usecases.list_tasks_by_user import ListTasksByUserUseCase

# Importar schemas Pydantic
from application.schemas.task_schema import (
    TaskCreate,
    TaskResponse,
    TaskListResponse,
    TaskCompleteRequest
)
from pydantic import ValidationError

# Crear Blueprint
blueprint = Blueprint('tasks', __name__)


@blueprint.route("", methods=['POST'])
def create_task():
    """
    Crea una nueva tarea
    
    ¿Qué cambia con Flask?
    - Validación manual de datos de entrada con Pydantic
    - Manejo manual de errores HTTP
    - Conversión manual a JSON
    """
    try:
        # Obtener datos del request
        data = request.get_json()
        if not data:
            return jsonify({"error": "No se proporcionaron datos JSON"}), 400
        
        # Validar datos con Pydantic
        try:
            task_create = TaskCreate(**data)
        except ValidationError as e:
            return jsonify({"error": "Datos inválidos", "details": e.errors()}), 400
        
        # Obtener caso de uso
        usecase = get_create_task_usecase()
        
        # Ejecutar caso de uso
        task = usecase.execute(task_create.title, task_create.description, task_create.user_id)
        
        # Convertir a schema de respuesta
        response_task = TaskResponse.model_validate(task)
        
        # Retornar JSON
        return jsonify(response_task.model_dump()), 201
        
    except ValueError as e:
        # Errores de lógica de negocio
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        # Errores inesperados
        return jsonify({"error": f"Error interno del servidor: {str(e)}"}), 500


@blueprint.route("/<int:user_id>", methods=['GET'])
def list_tasks_by_user(user_id: int):
    """
    Lista todas las tareas de un usuario específico
    
    ¿Qué cambia con Flask?
    - No usa response_model automático
    - Conversión manual a JSON
    - Manejo manual de errores
    """
    try:
        # Obtener caso de uso
        usecase = get_list_tasks_usecase()
        
        # Ejecutar caso de uso
        tasks = usecase.execute(user_id)
        
        # Convertir cada tarea a schema de respuesta
        task_responses = [TaskResponse.model_validate(task) for task in tasks]
        
        # Convertir a JSON
        return jsonify([task.model_dump() for task in task_responses])
        
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": f"Error interno del servidor: {str(e)}"}), 500


@blueprint.route("/<uuid:task_id>/complete", methods=['PUT'])
def complete_task(task_id: UUID):
    """
    Marca una tarea como completada
    
    ¿Qué cambia con Flask?
    - Manejo manual de UUID en la URL
    - Validación manual de parámetros
    - Manejo manual de errores HTTP
    """
    try:
        # Obtener caso de uso
        usecase = get_complete_task_usecase()
        
        # Ejecutar caso de uso
        usecase.execute(task_id)
        
        return jsonify({"message": f"Tarea {task_id} completada exitosamente"})
        
    except ValueError as e:
        # Tarea no encontrada o ya completada
        return jsonify({"error": str(e)}), 404
    except Exception as e:
        return jsonify({"error": f"Error interno del servidor: {str(e)}"}), 500