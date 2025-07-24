"""
User Gateway Interface - Domain Layer

This module defines the abstract interface for user data operations
following the Gateway pattern from Clean Architecture. This interface
allows the domain layer to depend on abstractions rather than concrete
implementations.

Key Features:
- Abstract interface for dependency inversion
- Enterprise naming conventions
- Comprehensive user operations
- Clean separation between domain and infrastructure
"""

from abc import ABC, abstractmethod
from typing import List, Optional
from uuid import UUID

# Note: We'll need to create UserEntity later, for now using a placeholder
# from domain.entities.user_entity import UserEntity
from domain.enums.task_status_enum import UserStatusEnum


class UserGateway(ABC):
    """
    Abstract gateway interface for user data operations

    This interface defines all the data operations needed by the domain layer
    for user management. Concrete implementations in the infrastructure layer
    will provide the actual data persistence logic.
    """

    @abstractmethod
    def find_user_by_id(self, user_id: int) -> Optional["UserEntity"]:
        """
        Find a user by their unique identifier

        Args:
            user_id: ID of the user to find

        Returns:
            UserEntity if found, None otherwise

        Raises:
            Exception: If database operation fails
        """
        pass

    @abstractmethod
    def find_all_users(self) -> List["UserEntity"]:
        """
        Find all users in the system

        Returns:
            List of UserEntity objects

        Raises:
            Exception: If database operation fails
        """
        pass

    @abstractmethod
    def find_users_by_status(self, status: UserStatusEnum) -> List["UserEntity"]:
        """
        Find all users with a specific status

        Args:
            status: UserStatusEnum to filter by

        Returns:
            List of UserEntity objects with the specified status

        Raises:
            Exception: If database operation fails
        """
        pass

    @abstractmethod
    def find_active_users(self) -> List["UserEntity"]:
        """
        Find all active users in the system

        Returns:
            List of active UserEntity objects

        Raises:
            Exception: If database operation fails
        """
        pass

    @abstractmethod
    def save_user(self, user: "UserEntity") -> None:
        """
        Save or update a user

        Args:
            user: UserEntity to save

        Raises:
            Exception: If save operation fails
        """
        pass

    @abstractmethod
    def delete_user(self, user_id: int) -> bool:
        """
        Delete a user from the system

        Args:
            user_id: ID of the user to delete

        Returns:
            bool: True if user was deleted, False if not found

        Raises:
            Exception: If database operation fails
        """
        pass

    @abstractmethod
    def user_exists(self, user_id: int) -> bool:
        """
        Check if a user exists in the system

        Args:
            user_id: ID of the user to check

        Returns:
            bool: True if user exists, False otherwise

        Raises:
            Exception: If database operation fails
        """
        pass

    @abstractmethod
    def count_users_by_status(self, status: UserStatusEnum) -> int:
        """
        Count the number of users with a specific status

        Args:
            status: UserStatusEnum to count

        Returns:
            int: Number of users with the specified status

        Raises:
            Exception: If database operation fails
        """
        pass
