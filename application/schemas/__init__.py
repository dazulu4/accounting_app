"""
Schemas Pydantic para la aplicación

Este módulo contiene todos los schemas de validación y serialización
para las entidades de la aplicación.

¿Qué hace este archivo __init__.py?
- Hace que el directorio sea un módulo Python
- Permite importar directamente desde application.schemas
- Centraliza las exportaciones públicas
"""

from .user_schema import (
    UserBase,
    UserCreate,
    UserUpdate,
    UserResponse,
    UserListResponse
)

from .task_schema import (
    TaskBase,
    TaskCreate,
    TaskUpdate,
    TaskResponse,
    TaskListResponse,
    TaskCompleteRequest
)

# Exportar todos los schemas para facilitar las importaciones
__all__ = [
    # User schemas
    'UserBase',
    'UserCreate', 
    'UserUpdate',
    'UserResponse',
    'UserListResponse',
    
    # Task schemas
    'TaskBase',
    'TaskCreate',
    'TaskUpdate',
    'TaskResponse',
    'TaskListResponse',
    'TaskCompleteRequest'
] 