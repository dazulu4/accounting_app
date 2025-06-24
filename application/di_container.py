from infrastructure.driven_adapters.repositories.task_repository import SQLAlchemyTaskRepository
from infrastructure.driven_adapters.repositories.user_repository_fake import FakeUserService
from domain.usecases.create_task import CreateTaskUseCase
from infrastructure.driven_adapters.repositories.base import SessionLocal
from domain.usecases.complete_task import CompleteTaskUseCase
from domain.usecases.list_tasks_by_user import ListTasksByUserUseCase
from domain.usecases.list_all_users import ListAllUsersUseCase
from infrastructure.driven_adapters.event_sender.mock_event_bus import MockEventBus

def get_create_task_usecase():
    db_session = SessionLocal()
    task_repo = SQLAlchemyTaskRepository(db_session)
    user_gateway = FakeUserService()
    return CreateTaskUseCase(task_repo, user_gateway)


def get_complete_task_usecase():
    db_session = SessionLocal()
    task_repo = SQLAlchemyTaskRepository(db_session)
    event_bus = MockEventBus()
    return CompleteTaskUseCase(task_repo, event_bus)


def get_list_tasks_usecase():
    db_session = SessionLocal()
    task_repo = SQLAlchemyTaskRepository(db_session)
    return ListTasksByUserUseCase(task_repo)


def get_list_all_users_usecase():
    user_gateway = FakeUserService()
    return ListAllUsersUseCase(user_gateway)