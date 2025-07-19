"""
Service Registration - Enterprise Edition

Clean and simple service registration for the DI container.
Configures all application services with appropriate lifetimes.

Key Features:
- Clear service registration
- Proper lifetime management
- Clean factory functions
- Type-safe service creation
"""

from infrastructure.helpers.di.dependency_container import DependencyContainer
from infrastructure.helpers.database.unit_of_work import UnitOfWork
from infrastructure.helpers.database.connection import DatabaseConnection, get_database_session
from infrastructure.driven_adapters.repositories.user_repository_fake import FakeUserService
from domain.usecases.create_task_use_case import CreateTaskUseCase
from domain.usecases.complete_task_use_case import CompleteTaskUseCase
from domain.usecases.list_tasks_by_user_use_case import ListTasksByUserUseCase
from domain.usecases.list_all_users_use_case import ListAllUsersUseCase
from domain.gateways.user_gateway import UserGateway
from application.config import settings
from infrastructure.helpers.logger.logger_config import get_logger

logger = get_logger(__name__)


def configure_services(container: DependencyContainer) -> None:
    """
    Configure all services in the DI container
    
    Simple, clean configuration following enterprise patterns:
    - Database services as singletons
    - Repositories as scoped (per request)
    - Use cases as transient (stateless)
    - Services based on their nature
    
    Args:
        container: DI container to configure
    """
    logger.info("dependency_injection_configuration_started")
    
    # Database Services (Singleton - shared across application)
    container.register_singleton(
        DatabaseConnection,
        lambda: DatabaseConnection(settings.database)
    )
    
    # Unit of Work (Scoped - one per request for transaction consistency)
    container.register_scoped(
        UnitOfWork,
        lambda: UnitOfWork()
    )
    
    # User Service (Singleton - stateless service)
    container.register_singleton(
        UserGateway,
        lambda: FakeUserService()
    )
    
    # Use Cases (Transient - stateless operations)
    container.register_transient(
        CreateTaskUseCase,
        lambda: CreateTaskUseCase(
            container.resolve(UnitOfWork),
            container.resolve(UserGateway)
        )
    )
    
    container.register_transient(
        CompleteTaskUseCase,
        lambda: CompleteTaskUseCase(
            container.resolve(UnitOfWork)
        )
    )
    
    container.register_transient(
        ListTasksByUserUseCase,
        lambda: ListTasksByUserUseCase(
            container.resolve(UnitOfWork),
            container.resolve(UserGateway)
        )
    )
    
    container.register_transient(
        ListAllUsersUseCase,
        lambda: ListAllUsersUseCase(
            container.resolve(UserGateway)
        )
    )
    
    logger.info(
        "dependency_injection_configuration_completed",
        registered_services=container.get_registered_services()
    )


def get_configured_container() -> DependencyContainer:
    """
    Get a fully configured DI container
    
    Returns:
        Configured DependencyContainer instance
    """
    from infrastructure.helpers.di.dependency_container import get_container
    
    container = get_container()
    
    # Only configure if not already configured
    if not container.get_registered_services():
        configure_services(container)
    
    return container 