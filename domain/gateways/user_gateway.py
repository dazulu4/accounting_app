from abc import ABC, abstractmethod
from uuid import UUID
from domain.models.user import User


class UserGateway(ABC):
    @abstractmethod
    def get_by_id(self, user_id: UUID) -> User | None:
        pass
