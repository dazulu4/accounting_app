"""
Fake User Repository - Enterprise Edition

Professional fake user service implementation for testing and development
with enterprise patterns and comprehensive user management.
"""

from typing import List, Optional
from domain.entities.user_entity import UserEntity
from domain.enums.user_status_enum import UserStatusEnum
from domain.gateways.user_gateway import UserGateway
from infrastructure.helpers.logger.logger_config import get_logger

# Configure logger
logger = get_logger(__name__)


class FakeUserService(UserGateway):
    """
    Fake user service implementation for testing and development
    
    This service provides a complete implementation of UserGateway interface
    using in-memory data for development and testing purposes.
    
    Features:
    - Complete CRUD operations
    - Status management
    - Enterprise logging
    - Thread-safe operations
    """
    
    def __init__(self):
        """Initialize fake user service with sample data"""
        self._users = self._create_sample_users()
        self._next_id = max(user.user_id for user in self._users) + 1
        
        logger.info(
            "fake_user_service_initialized",
            total_users=len(self._users),
            active_users=len([u for u in self._users if u.status == UserStatusEnum.ACTIVE])
        )
    
    def _create_sample_users(self) -> List[UserEntity]:
        """Create sample users for testing"""
        return [
            UserEntity(
                user_id=1,
                name="Juan Pérez",
                email="juan.perez@company.com",
                status=UserStatusEnum.ACTIVE
            ),
            UserEntity(
                user_id=2,
                name="María García",
                email="maria.garcia@company.com",
                status=UserStatusEnum.ACTIVE
            ),
            UserEntity(
                user_id=3,
                name="Carlos López",
                email="carlos.lopez@company.com",
                status=UserStatusEnum.ACTIVE
            ),
            UserEntity(
                user_id=4,
                name="Ana Martínez",
                email="ana.martinez@company.com",
                status=UserStatusEnum.INACTIVE
            ),
            UserEntity(
                user_id=5,
                name="Luis Rodríguez",
                email="luis.rodriguez@company.com",
                status=UserStatusEnum.ACTIVE
            )
        ]
    
    def find_user_by_id(self, user_id: int) -> Optional[UserEntity]:
        """
        Find user by ID
        
        Args:
            user_id: User ID to search for
            
        Returns:
            UserEntity if found, None otherwise
        """
        logger.debug("finding_user_by_id", user_id=user_id)
        
        user = next((user for user in self._users if user.user_id == user_id), None)
        
        if user:
            logger.debug("user_found", user_id=user_id, user_name=user.name, status=user.status.value)
        else:
            logger.debug("user_not_found", user_id=user_id)
        
        return user
    
    def find_user_by_email(self, email: str) -> Optional[UserEntity]:
        """
        Find user by email
        
        Args:
            email: Email to search for
            
        Returns:
            UserEntity if found, None otherwise
        """
        logger.debug("finding_user_by_email", email=email)
        
        user = next((user for user in self._users if user.email == email), None)
        
        if user:
            logger.debug("user_found_by_email", user_id=user.user_id, email=email)
        else:
            logger.debug("user_not_found_by_email", email=email)
        
        return user
    
    def find_all_users(self) -> List[UserEntity]:
        """Get all users in the system"""
        logger.debug("getting_all_users", total_count=len(self._users))
        return self._users.copy()
    
    def find_active_users(self) -> List[UserEntity]:
        """Get all active users"""
        active_users = [user for user in self._users if user.status == UserStatusEnum.ACTIVE]
        logger.debug("getting_active_users", active_count=len(active_users))
        return active_users
    
    def find_users_by_status(self, status: UserStatusEnum) -> List[UserEntity]:
        """Get users by status"""
        filtered_users = [user for user in self._users if user.status == status]
        logger.debug("getting_users_by_status", status=status.value, count=len(filtered_users))
        return filtered_users
    
    def save_user(self, user: UserEntity) -> None:
        """Save or update a user"""
        existing_user = self.find_user_by_id(user.user_id)
        if existing_user:
            self._users.remove(existing_user)
        self._users.append(user)
        logger.info("user_saved", user_id=user.user_id, name=user.name)

    def delete_user(self, user_id: int) -> bool:
        """Delete a user"""
        user = self.find_user_by_id(user_id)
        if user:
            self._users.remove(user)
            logger.info("user_deleted", user_id=user_id)
            return True
        logger.warning("delete_user_failed_not_found", user_id=user_id)
        return False

    def user_exists(self, user_id: int) -> bool:
        """Check if a user exists"""
        return any(user.user_id == user_id for user in self._users)

    def count_users_by_status(self, status: UserStatusEnum) -> int:
        """Count users by status"""
        return len([user for user in self._users if user.status == status])
    
    def create_user(self, name: str, email: str) -> UserEntity:
        """
        Create a new user
        
        Args:
            name: User name
            email: User email
            
        Returns:
            Created user entity
        """
        new_user = UserEntity(
            user_id=self._next_id,
            name=name,
            email=email,
            status=UserStatusEnum.ACTIVE
        )
        
        self._users.append(new_user)
        self._next_id += 1
        
        logger.info("user_created", user_id=new_user.user_id, name=name, email=email)
        return new_user
    
    def update_user_status(self, user_id: int, new_status: UserStatusEnum) -> bool:
        """
        Update user status
        
        Args:
            user_id: User ID to update
            new_status: New status to set
            
        Returns:
            True if updated, False if user not found
        """
        user = self.find_user_by_id(user_id)
        if not user:
            logger.warning("update_user_status_failed_user_not_found", user_id=user_id)
            return False
        
        old_status = user.status
        user.status = new_status
        
        logger.info(
            "user_status_updated",
            user_id=user_id,
            old_status=old_status.value,
            new_status=new_status.value
        )
        
        return True
    
    def deactivate_user(self, user_id: int) -> bool:
        """
        Deactivate a user
        
        Args:
            user_id: User ID to deactivate
            
        Returns:
            True if deactivated, False if user not found
        """
        return self.update_user_status(user_id, UserStatusEnum.INACTIVE)
    
    def activate_user(self, user_id: int) -> bool:
        """
        Activate a user
        
        Args:
            user_id: User ID to activate
            
        Returns:
            True if activated, False if user not found
        """
        return self.update_user_status(user_id, UserStatusEnum.ACTIVE)
    
    def get_user_count(self) -> int:
        """Get total number of users"""
        return len(self._users)
    
    def get_active_user_count(self) -> int:
        """Get number of active users"""
        return len([user for user in self._users if user.status == UserStatusEnum.ACTIVE])
