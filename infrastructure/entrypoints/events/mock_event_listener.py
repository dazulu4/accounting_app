from uuid import UUID
from domain.models.user import UserStatus
from infrastructure.driven_adapters.repositories.user_repository_fake import FAKE_USERS


def on_user_activated_event(user_id: UUID):
    user = FAKE_USERS.get(user_id)
    if user:
        user.status = UserStatus.ACTIVE
        print(f"[EVENT RECEIVED] Usuario {user_id} activado")
    else:
        print(f"[EVENT RECEIVED] Usuario {user_id} no encontrado")


def on_user_deactivated_event(user_id: UUID):
    user = FAKE_USERS.get(user_id)
    if user:
        user.status = UserStatus.INACTIVE
        print(f"[EVENT RECEIVED] Usuario {user_id} inactivado")
    else:
        print(f"[EVENT RECEIVED] Usuario {user_id} no encontrado")
