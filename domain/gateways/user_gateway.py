from abc import ABC, abstractmethod
from uuid import UUID
from domain.models.user import User
from typing import List


class UserGateway(ABC):
    @abstractmethod
    def get_by_id(self, user_id: int) -> User | None:
        pass

    @abstractmethod
    def get_all(self) -> List[User]:
        pass
