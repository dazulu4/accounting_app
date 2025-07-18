"""
Rutas HTTP para la gestión de usuarios usando Flask

¿Qué cambia con Flask?
- Usa Blueprint en lugar de APIRouter
- Manejo manual de JSON con jsonify
- Validaciones manuales con Pydantic
- Manejo manual de errores HTTP
"""

from flask import Blueprint, jsonify, request
from typing import List
from uuid import UUID

from infrastructure.entrypoints.events.mock_event_listener import on_user_deactivated_event, on_user_activated_event
from application.di_container import get_list_all_users_usecase
from domain.usecases.list_all_users import ListAllUsersUseCase

# Importar schemas Pydantic
from application.schemas.user_schema import UserResponse, UserListResponse
from pydantic import ValidationError

# Crear Blueprint (equivalente a APIRouter en FastAPI)
blueprint = Blueprint('users', __name__)


@blueprint.route("", methods=['GET'])
def list_all_users():
    """
    Lista todos los usuarios del sistema
    
    ¿Qué cambia con Flask?
    - No usa response_model automático
    - Validación manual con Pydantic
    - Manejo manual de errores
    """
    try:
        # Obtener caso de uso desde el contenedor de dependencias
        usecase = get_list_all_users_usecase()
        users = usecase.execute()
        
        # Convertir modelos de dominio a schemas Pydantic
        user_responses = [UserResponse.model_validate(user) for user in users]
        
        # Convertir a JSON
        return jsonify([user.model_dump() for user in user_responses])
        
    except Exception as e:
        # Manejo de errores mejorado
        return jsonify({"error": f"Error interno del servidor: {str(e)}"}), 500


@blueprint.route("/<int:user_id>/activate", methods=['POST'])
def simulate_user_activation(user_id: int):
    """
    Simula la activación de un usuario
    
    ¿Por qué no usar schema aquí?
    - Es una operación simple sin datos complejos
    - Solo necesita el user_id como parámetro de ruta
    - La respuesta es un mensaje simple
    """
    try:
        on_user_activated_event(user_id)
        return jsonify({"message": f"Evento de activación recibido para usuario {user_id}"})
    except Exception as e:
        return jsonify({"error": f"Error al activar usuario: {str(e)}"}), 500


@blueprint.route("/<int:user_id>/deactivate", methods=['POST'])
def simulate_user_deactivation(user_id: int):
    """
    Simula la desactivación de un usuario
    """
    try:
        on_user_deactivated_event(user_id)
        return jsonify({"message": f"Evento de inactivación recibido para usuario {user_id}"})
    except Exception as e:
        return jsonify({"error": f"Error al desactivar usuario: {str(e)}"}), 500
