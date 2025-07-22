"""
Schemas Pydantic para la aplicación

Este módulo centraliza la exportación de los esquemas Pydantic
para facilitar su importación en otras partes de la aplicación.
"""

from .user_schema import (
    UserResponse,
    UserListResponse,
    CreateUserRequest,
    UpdateUserStatusRequest,
    UserStatsResponse,
)

from .task_schema import (
    CreateTaskRequest,
    CreateTaskResponse,
    CompleteTaskRequest,
    CompleteTaskResponse,
    TaskResponse,
    TaskListResponse,
)

# Exportar todos los schemas para facilitar las importaciones
__all__ = [
    # User schemas
    'UserResponse',
    'UserListResponse',
    'CreateUserRequest',
    'UpdateUserStatusRequest',
    'UserStatsResponse',
    
    # Task schemas
    'CreateTaskRequest',
    'CreateTaskResponse',
    'CompleteTaskRequest',
    'CompleteTaskResponse',
    'TaskResponse',
    'TaskListResponse',
] 