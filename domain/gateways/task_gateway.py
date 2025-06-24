from abc import ABC, abstractmethod
from typing import List
from uuid import UUID
from domain.models.task import Task


class TaskGateway(ABC):
    @abstractmethod
    def save(self, task: Task) -> None:
        pass

    @abstractmethod
    def get_by_id(self, task_id: UUID) -> Task | None:
        pass

    @abstractmethod
    def list_by_user(self, user_id: UUID) -> List[Task]:
        pass
