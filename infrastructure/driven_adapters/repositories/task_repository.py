from typing import List
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from domain.models.task import Task, TaskStatus
from domain.gateways.task_gateway import TaskGateway
from infrastructure.driven_adapters.repositories.base import Base
from sqlalchemy.orm import Mapped, mapped_column


class TaskModel(Base):
    __tablename__ = "tasks"

    task_id: Mapped[UUID] = mapped_column(primary_key=True)
    title: Mapped[str]
    description: Mapped[str]
    user_id: Mapped[int]
    status: Mapped[str]
    created_at: Mapped[str]
    completed_at: Mapped[str | None]


def task_to_model(task: Task) -> TaskModel:
    return TaskModel(
        task_id=task.task_id,
        title=task.title,
        description=task.description,
        user_id=task.user_id,
        status=task.status.value,
        created_at=task.created_at.isoformat(),
        completed_at=task.completed_at.isoformat() if task.completed_at else None,
    )


def model_to_task(model: TaskModel) -> Task:
    task = Task(
        task_id=model.task_id,
        title=model.title,
        description=model.description,
        user_id=model.user_id,
    )
    task.status = TaskStatus(model.status)
    task.created_at = model.created_at
    task.completed_at = model.completed_at
    return task


class SQLAlchemyTaskRepository(TaskGateway):
    def __init__(self, db_session: AsyncSession):
        self.db = db_session

    async def save(self, task: Task) -> None:
        model = await self.db.get(TaskModel, task.task_id)
        if model:
            # Update
            model.title = task.title
            model.description = task.description
            model.status = task.status.value
            model.completed_at = (
                task.completed_at.isoformat() if task.completed_at else None
            )
        else:
            self.db.add(task_to_model(task))
        await self.db.commit()

    async def get_by_id(self, task_id: UUID) -> Task | None:
        model = await self.db.get(TaskModel, task_id)
        return model_to_task(model) if model else None

    async def list_by_user(self, user_id: int) -> List[Task]:
        result = await self.db.execute(
            select(TaskModel).where(TaskModel.user_id == user_id)
        )
        return [model_to_task(m) for m in result.scalars().all()]
