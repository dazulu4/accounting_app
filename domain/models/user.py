from enum import Enum
from uuid import UUID, uuid4


class UserStatus(str, Enum):
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"


class User:
    def __init__(self, user_id: int, name: str, status: UserStatus):
        self.user_id = user_id
        self.name = name
        self.status = status

    def is_active(self) -> bool:
        return self.status == UserStatus.ACTIVE
