from fastapi import APIRouter
from uuid import UUID
from infrastructure.entrypoints.events.mock_event_listener import on_user_deactivated_event, on_user_activated_event

router = APIRouter(prefix="/users", tags=["Users"])


@router.post("/{user_id}/activate")
async def simulate_user_activation(user_id: UUID):
    on_user_activated_event(user_id)
    return {"message": f"Evento de activación recibido para usuario {user_id}"}


@router.post("/{user_id}/deactivate")
async def simulate_user_deactivation(user_id: UUID):
    on_user_deactivated_event(user_id)
    return {"message": f"Evento de inactivación recibido para usuario {user_id}"}
