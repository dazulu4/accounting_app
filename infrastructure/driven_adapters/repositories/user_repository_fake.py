import json
from uuid import UUID
from domain.gateways.user_gateway import UserGateway
from domain.models.user import User, UserStatus
from typing import List

# Cargar usuarios desde el archivo JSON al iniciar el módulo
FAKE_USERS = {}
try:
    with open("dummyusers.json", "r", encoding="utf-8") as f:
        data = json.load(f)
        for user_data in data.get("users", []):
            user = User(
                user_id=int(user_data["id"]),
                name=user_data["firstName"],
                status=UserStatus.ACTIVE,  # Asignar estado por defecto
            )
            FAKE_USERS[user.user_id] = user
except FileNotFoundError:
    print("Advertencia: dummyusers.json no encontrado. El servicio de usuarios falsos estará vacío.")
except (json.JSONDecodeError, KeyError) as e:
    print(f"Error al procesar dummyusers.json: {e}")


class FakeUserService(UserGateway):
    def get_by_id(self, user_id: int) -> User | None:
        return FAKE_USERS.get(user_id)

    def get_all(self) -> List[User]:
        return [user for user in FAKE_USERS.values() if user.is_active()]
