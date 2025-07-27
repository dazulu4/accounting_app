"""
List All Users Use Case - Domain Layer

This module implements a simple user listing use case following
Clean Architecture principles with consistent patterns.

Key Features:
- Simple user retrieval with optional filtering
- Clean Architecture compliance
- Consistent with other use cases
"""

import logging
from typing import List, Optional

from domain.entities.user_entity import UserEntity
from domain.enums.user_status_enum import UserStatusEnum
from domain.gateways.user_gateway import UserGateway

# Initialize logger
logger = logging.getLogger(__name__)


class ListAllUsersUseCase:
    """
    Use case for retrieving all users in the system.

    Simple implementation following the established pattern
    for consistency with other use cases.
    """

    def __init__(self, user_gateway: UserGateway):
        """
        Initialize the use case with required gateway.

        Args:
            user_gateway: Gateway for user operations
        """
        self.user_gateway = user_gateway

    def execute(
        self, status_filter: Optional[UserStatusEnum] = None
    ) -> List[UserEntity]:
        """
        Execute the list all users use case.

        Args:
            status_filter: Optional filter by user status

        Returns:
            List[UserEntity]: List of users (filtered if status provided)
        """
        logger.info(
            f"list_all_users_use_case_started status_filter={status_filter.value if status_filter else 'all'}"
        )

        try:
            # Get users with optional filtering
            if status_filter:
                users = self.user_gateway.find_users_by_status(status_filter)
            else:
                users = self.user_gateway.find_all_users()

            logger.info(f"list_all_users_use_case_completed users_found={len(users)}")
            return users

        except Exception as e:
            logger.error(f"list_all_users_use_case_unexpected_error error={str(e)}")
            raise
