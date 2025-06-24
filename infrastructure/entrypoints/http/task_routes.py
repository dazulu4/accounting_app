from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from uuid import UUID
from application.di_container import get_create_task_usecase, get_complete_task_usecase, get_list_tasks_usecase
from domain.usecases.create_task import CreateTaskUseCase
from domain.usecases.complete_task import CompleteTaskUseCase
from domain.usecases.list_tasks_by_user import ListTasksByUserUseCase

router = APIRouter(prefix="/tasks", tags=["Tasks"])


class TaskCreateInput(BaseModel):
    title: str
    description: str
    user_id: int


@router.post("")
async def create_task(
    payload: TaskCreateInput,
    usecase: CreateTaskUseCase = Depends(get_create_task_usecase),
):
    try:
        task = await usecase.execute(payload.title, payload.description, payload.user_id)
        return {
            "task_id": str(task.task_id),
            "title": task.title,
            "description": task.description,
            "status": task.status,
            "created_at": str(task.created_at),
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{user_id}")
async def list_tasks_by_user(
    user_id: int,
    usecase: ListTasksByUserUseCase = Depends(get_list_tasks_usecase),
):
    tasks = await usecase.execute(user_id)
    return [
        {
            "task_id": str(t.task_id),
            "title": t.title,
            "description": t.description,
            "status": t.status,
            "created_at": str(t.created_at),
            "completed_at": str(t.completed_at) if t.completed_at else None,
        }
        for t in tasks
    ]


@router.put("/{task_id}/complete")
async def complete_task(
    task_id: UUID,
    usecase: CompleteTaskUseCase = Depends(get_complete_task_usecase),
):
    try:
        await usecase.execute(task_id)
        return {"message": f"Tarea {task_id} completada"}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))