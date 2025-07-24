"""
Schemas Pydantic para la aplicación

Este módulo centraliza la exportación de los esquemas Pydantic
para facilitar su importación en otras partes de la aplicación.
"""

from .task_schema import (
    CompleteTaskRequest,
    CompleteTaskResponse,
    CreateTaskRequest,
    CreateTaskResponse,
    TaskListResponse,
    TaskResponse,
)
from .user_schema import (
    CreateUserRequest,
    UpdateUserStatusRequest,
    UserListResponse,
    UserResponse,
    UserStatsResponse,
)

# Exportar todos los schemas para facilitar las importaciones
__all__ = [
    # User schemas
    "UserResponse",
    "UserListResponse",
    "CreateUserRequest",
    "UpdateUserStatusRequest",
    "UserStatsResponse",
    # Task schemas
    "CreateTaskRequest",
    "CreateTaskResponse",
    "CompleteTaskRequest",
    "CompleteTaskResponse",
    "TaskResponse",
    "TaskListResponse",
]
