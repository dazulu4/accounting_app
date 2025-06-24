from fastapi import APIRouter, Depends
from uuid import UUID
from infrastructure.entrypoints.events.mock_event_listener import on_user_deactivated_event, on_user_activated_event
from application.di_container import get_list_all_users_usecase
from domain.usecases.list_all_users import ListAllUsersUseCase

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("")
async def list_all_users(usecase: ListAllUsersUseCase = Depends(get_list_all_users_usecase)):
    users = usecase.execute()
    return [
        {
            "user_id": user.user_id,
            "name": user.name,
            "status": user.status.value
        }
        for user in users
    ]


@router.post("/{user_id}/activate")
async def simulate_user_activation(user_id: int):
    on_user_activated_event(user_id)
    return {"message": f"Evento de activación recibido para usuario {user_id}"}


@router.post("/{user_id}/deactivate")
async def simulate_user_deactivation(user_id: int):
    on_user_deactivated_event(user_id)
    return {"message": f"Evento de inactivación recibido para usuario {user_id}"}
