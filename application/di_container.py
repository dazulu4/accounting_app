"""
Dependency Injection Container - Enterprise Wrapper

Clean wrapper around the new enterprise DI container.
Maintains compatibility with existing route functions while using the new system.

Key Features:
- Backward compatibility with existing functions
- Uses new enterprise DI container under the hood
- Clean and simple implementation
- No dead code
"""

from infrastructure.helpers.di import resolve_service, get_current_container
from domain.usecases.create_task_use_case import CreateTaskUseCase
from domain.usecases.complete_task_use_case import CompleteTaskUseCase
from domain.usecases.list_tasks_by_user_use_case import ListTasksByUserUseCase
from domain.usecases.list_all_users_use_case import ListAllUsersUseCase


def get_create_task_usecase() -> CreateTaskUseCase:
    """Get CreateTaskUseCase from DI container"""
    return resolve_service(CreateTaskUseCase)


def get_complete_task_usecase() -> CompleteTaskUseCase:
    """Get CompleteTaskUseCase from DI container"""
    return resolve_service(CompleteTaskUseCase)


def get_list_tasks_usecase() -> ListTasksByUserUseCase:
    """Get ListTasksByUserUseCase from DI container"""
    return resolve_service(ListTasksByUserUseCase)


def get_list_all_users_usecase() -> ListAllUsersUseCase:
    """Get ListAllUsersUseCase from DI container"""
    return resolve_service(ListAllUsersUseCase)