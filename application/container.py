"""
Contenedor de Dependencias - Edición Simplificada

Este módulo proporciona un contenedor simple y explícito para la inyección de
dependencias (DI) de la aplicación, siguiendo el patrón "DI a mano".

Características:
- **Explícito:** Todas las dependencias se construyen y conectan a mano.
- **Centralizado:** Un único lugar para entender el grafo de dependencias.
- **Sin Magia:** No hay auto-registro ni scopes complejos.
- **Fácil de Probar:** Permite sobreescribir dependencias fácilmente en los tests.
"""

from domain.gateways.user_gateway import UserGateway
from domain.usecases.create_task_use_case import CreateTaskUseCase
from domain.usecases.complete_task_use_case import CompleteTaskUseCase
from domain.usecases.list_tasks_by_user_use_case import ListTasksByUserUseCase
from domain.usecases.list_all_users_use_case import ListAllUsersUseCase
from infrastructure.driven_adapters.repositories.user_repository_fake import FakeUserService
from infrastructure.helpers.database.unit_of_work import UnitOfWork
from application.config import settings


class Container:
    """
    Contenedor que gestiona la instanciación de las dependencias.
    """
    def __init__(self):
        # --- Singletons o servicios compartidos ---
        # Se crean una sola vez y se reutilizan.
        self.user_service: UserGateway = FakeUserService()
        self.config = settings
    
    # --- Casos de Uso ---
    # Los casos de uso son transitorios por naturaleza (no guardan estado),
    # por lo que los creamos bajo demanda a través de propiedades.

    @property
    def create_task_use_case(self) -> CreateTaskUseCase:
        return CreateTaskUseCase(
            unit_of_work=UnitOfWork(),
            user_service=self.user_service
        )
    
    @property
    def complete_task_use_case(self) -> CompleteTaskUseCase:
        return CompleteTaskUseCase(
            unit_of_work=UnitOfWork()
        )
        
    @property
    def list_tasks_by_user_use_case(self) -> ListTasksByUserUseCase:
        return ListTasksByUserUseCase(
            unit_of_work=UnitOfWork(),
            user_service=self.user_service
        )

    @property
    def list_all_users_use_case(self) -> ListAllUsersUseCase:
        return ListAllUsersUseCase(
            user_service=self.user_service
        )

# Instancia global del contenedor que será usada por la aplicación.
container = Container() 