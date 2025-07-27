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

from application.config.environment import settings
from domain.gateways.task_gateway import TaskGateway
from domain.gateways.user_gateway import UserGateway
from domain.usecases.complete_task_use_case import CompleteTaskUseCase
from domain.usecases.create_task_use_case import CreateTaskUseCase
from domain.usecases.list_all_users_use_case import ListAllUsersUseCase
from domain.usecases.list_tasks_by_user_use_case import ListTasksByUserUseCase
from infrastructure.driven_adapters.repositories.task_repository import (
    TaskRepository,
)
from infrastructure.driven_adapters.repositories.user_repository_fake import (
    FakeUserService,
)


class Container:
    """
    Contenedor que gestiona la instanciación de las dependencias.
    """

    def __init__(self):
        # --- Singletons o servicios compartidos ---
        # Se crean una sola vez y se reutilizan.
        self.user_service: UserGateway = FakeUserService()
        self.config = settings

        # --- Gateways ---
        # Los gateways se crean bajo demanda para evitar problemas de sesión
        self._task_gateway = None
        self._user_gateway = None

        # --- Casos de Uso ---
        # Los casos de uso son transitorios por naturaleza (no guardan estado),
        # por lo que los creamos bajo demanda a través de propiedades.
        self._create_task_use_case = None
        self._complete_task_use_case = None
        self._list_tasks_by_user_use_case = None
        self._list_all_users_use_case = None

    @property
    def create_task_use_case(self) -> CreateTaskUseCase:
        if self._create_task_use_case is None:
            self._create_task_use_case = CreateTaskUseCase(
                task_gateway=self.task_gateway, user_gateway=self.user_gateway
            )
        return self._create_task_use_case

    @create_task_use_case.setter
    def create_task_use_case(self, value):
        self._create_task_use_case = value

    @create_task_use_case.deleter
    def create_task_use_case(self):
        self._create_task_use_case = None

    @property
    def complete_task_use_case(self) -> CompleteTaskUseCase:
        if self._complete_task_use_case is None:
            self._complete_task_use_case = CompleteTaskUseCase(
                task_gateway=self.task_gateway
            )
        return self._complete_task_use_case

    @complete_task_use_case.setter
    def complete_task_use_case(self, value):
        self._complete_task_use_case = value

    @complete_task_use_case.deleter
    def complete_task_use_case(self):
        self._complete_task_use_case = None

    @property
    def list_tasks_by_user_use_case(self) -> ListTasksByUserUseCase:
        if self._list_tasks_by_user_use_case is None:
            self._list_tasks_by_user_use_case = ListTasksByUserUseCase(
                task_gateway=self.task_gateway,
                user_gateway=self.user_gateway,
            )
        return self._list_tasks_by_user_use_case

    @list_tasks_by_user_use_case.setter
    def list_tasks_by_user_use_case(self, value):
        self._list_tasks_by_user_use_case = value

    @list_tasks_by_user_use_case.deleter
    def list_tasks_by_user_use_case(self):
        self._list_tasks_by_user_use_case = None

    @property
    def list_all_users_use_case(self) -> ListAllUsersUseCase:
        if self._list_all_users_use_case is None:
            self._list_all_users_use_case = ListAllUsersUseCase(
                user_gateway=self.user_gateway
            )
        return self._list_all_users_use_case

    @list_all_users_use_case.setter
    def list_all_users_use_case(self, value):
        self._list_all_users_use_case = value

    @list_all_users_use_case.deleter
    def list_all_users_use_case(self):
        self._list_all_users_use_case = None

    # --- Gateways ---
    @property
    def task_gateway(self) -> TaskGateway:
        if self._task_gateway is None:
            from infrastructure.helpers.database.connection import (
                get_database_session,
            )

            session = get_database_session()
            self._task_gateway = TaskRepository(session)
        return self._task_gateway

    @task_gateway.setter
    def task_gateway(self, value):
        self._task_gateway = value

    @task_gateway.deleter
    def task_gateway(self):
        self._task_gateway = None

    @property
    def user_gateway(self) -> UserGateway:
        if self._user_gateway is None:
            self._user_gateway = FakeUserService()
        return self._user_gateway

    @user_gateway.setter
    def user_gateway(self, value):
        self._user_gateway = value

    @user_gateway.deleter
    def user_gateway(self):
        self._user_gateway = None


# Instancia global del contenedor que será usada por la aplicación.
container = Container()
