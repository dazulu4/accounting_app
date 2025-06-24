from uuid import UUID
from domain.gateways.task_gateway import TaskGateway
from domain.models.task import Task
from typing import List


class ListTasksByUserUseCase:
    def __init__(self, task_gateway: TaskGateway):
        self.task_gateway = task_gateway

    async def execute(self, user_id: UUID) -> List[Task]:
        return await self.task_gateway.list_by_user(user_id)
