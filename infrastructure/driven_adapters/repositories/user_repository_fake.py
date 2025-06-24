from uuid import UUID
from domain.gateways.user_gateway import UserGateway
from domain.models.user import User, UserStatus


# Simulamos una "base de datos" de usuarios
FAKE_USERS = {
    UUID("aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa"): User(
        user_id=UUID("aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa"),
        name="Alice",
        status=UserStatus.ACTIVE,
    ),
    UUID("bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb"): User(
        user_id=UUID("bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb"),
        name="Bob",
        status=UserStatus.INACTIVE,
    ),
}


class FakeUserService(UserGateway):
    def get_by_id(self, user_id: UUID) -> User | None:
        return FAKE_USERS.get(user_id)
