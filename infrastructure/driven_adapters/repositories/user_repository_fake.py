"""
Fake User Repository for Development

Simple in-memory user repository for development and testing.
"""

from typing import List, Optional

from domain.entities.user_entity import UserEntity
from domain.enums.user_status_enum import UserStatusEnum
from domain.gateways.user_gateway import UserGateway


class FakeUserService(UserGateway):
    """Simple fake user service for development."""

    def __init__(self):
        """Initialize with sample users."""
        self._users = [
            UserEntity(
                user_id=1,
                name="Juan Pérez",
                email="juan.perez@company.com",
                status=UserStatusEnum.ACTIVE,
            ),
            UserEntity(
                user_id=2,
                name="María García",
                email="maria.garcia@company.com",
                status=UserStatusEnum.ACTIVE,
            ),
            UserEntity(
                user_id=3,
                name="Carlos López",
                email="carlos.lopez@company.com",
                status=UserStatusEnum.ACTIVE,
            ),
            UserEntity(
                user_id=4,
                name="Ana Martínez",
                email="ana.martinez@company.com",
                status=UserStatusEnum.INACTIVE,
            ),
            UserEntity(
                user_id=5,
                name="Luis Rodríguez",
                email="luis.rodriguez@company.com",
                status=UserStatusEnum.ACTIVE,
            ),
        ]

    def find_user_by_id(self, user_id: int) -> Optional[UserEntity]:
        """Find user by ID."""
        return next((user for user in self._users if user.user_id == user_id), None)

    def find_all_users(self) -> List[UserEntity]:
        """Get all users."""
        return self._users.copy()

    def find_active_users(self) -> List[UserEntity]:
        """Get all active users."""
        return [user for user in self._users if user.status == UserStatusEnum.ACTIVE]

    def find_users_by_status(self, status: UserStatusEnum) -> List[UserEntity]:
        """Get users by status."""
        return [user for user in self._users if user.status == status]

    def save_user(self, user: UserEntity) -> None:
        """Save or update a user."""
        existing_user = self.find_user_by_id(user.user_id)
        if existing_user:
            self._users.remove(existing_user)
        self._users.append(user)

    def delete_user(self, user_id: int) -> bool:
        """Delete a user."""
        user = self.find_user_by_id(user_id)
        if user:
            self._users.remove(user)
            return True
        return False

    def user_exists(self, user_id: int) -> bool:
        """Check if a user exists."""
        return any(user.user_id == user_id for user in self._users)

    def count_users_by_status(self, status: UserStatusEnum) -> int:
        """Count users by status."""
        return len([user for user in self._users if user.status == status])
