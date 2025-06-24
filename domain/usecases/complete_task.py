from uuid import UUID
from domain.gateways.task_gateway import TaskGateway


class CompleteTaskUseCase:
    def __init__(self, task_gateway: TaskGateway, event_bus=None):
        self.task_gateway = task_gateway
        self.event_bus = event_bus

    async def execute(self, task_id: UUID) -> None:
        task = await self.task_gateway.get_by_id(task_id)
        if task is None:
            raise ValueError("Tarea no encontrada")
        task.complete()
        await self.task_gateway.save(task)

        if self.event_bus:
            self.event_bus.send_task_completed(task.task_id, task.user_id)
