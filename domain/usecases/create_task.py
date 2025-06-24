from uuid import UUID, uuid4
from domain.models.task import Task
from domain.gateways.task_gateway import TaskGateway
from domain.gateways.user_gateway import UserGateway


class CreateTaskUseCase:
    def __init__(self, task_gateway: TaskGateway, user_gateway: UserGateway):
        self.task_gateway = task_gateway
        self.user_gateway = user_gateway

    async def execute(self, title: str, description: str, user_id: UUID) -> Task:
        user = self.user_gateway.get_by_id(user_id)
        if user is None or not user.is_active():
            raise ValueError("Usuario no existe o está inactivo")

        task = Task(
            task_id=uuid4(),
            title=title,
            description=description,
            user_id=user_id,
        )
        await self.task_gateway.save(task)
        return task
