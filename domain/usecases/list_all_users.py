from domain.gateways.user_gateway import UserGateway
from domain.models.user import User
from typing import List


class ListAllUsersUseCase:
    def __init__(self, user_gateway: UserGateway):
        self.user_gateway = user_gateway

    def execute(self) -> List[User]:
        return self.user_gateway.get_all() 