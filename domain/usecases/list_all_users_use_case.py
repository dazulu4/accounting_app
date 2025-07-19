"""
List All Users Use Case - Application Layer

This module implements the List All Users use case following Clean Architecture principles
with enterprise patterns including filtering, DTOs, and comprehensive error handling.

Key Features:
- Synchronous operation (optimized for Lambda)
- Status filtering capabilities
- DTOs for response contracts
- Statistics and summary information
- Structured logging
"""

import logging
from typing import List, Optional

from domain.gateways.user_gateway import UserGateway
from domain.enums.task_status_enum import UserStatusEnum
from domain.exceptions.business_exceptions import ValidationException

# Configure logger
logger = logging.getLogger(__name__)


class ListAllUsersUseCase:
    """
    Use case for retrieving all users in the system
    
    This use case handles the complete workflow of user retrieval including:
    - Optional status filtering
    - Response formatting
    - Statistics calculation
    
    Features:
    - Returns all users or filtered by status
    - Provides user count and statistics
    - Validates filter parameters
    """
    
    def __init__(self, user_gateway: UserGateway):
        """
        Initialize use case with required dependencies
        
        Args:
            user_gateway: Gateway for user operations
        """
        self._user_gateway = user_gateway
    
    def execute(self, status_filter: Optional[UserStatusEnum] = None) -> dict:
        """
        Execute list all users use case
        
        Args:
            status_filter: Optional status to filter users by
            
        Returns:
            Dictionary containing users list and metadata
            
        Raises:
            ValidationException: If parameters are invalid
        """
        logger.info(
            "list_all_users_started",
            extra={
                "status_filter": status_filter.value if status_filter else "all"
            }
        )
        
        try:
            # Step 1: Validate input parameters
            self._validate_parameters(status_filter)
            
            # Step 2: Retrieve users based on filter
            users = self._retrieve_users(status_filter)
            
            # Step 3: Calculate statistics
            stats = self._calculate_user_statistics()
            
            # Step 4: Create response
            response = self._create_response(users, stats, status_filter)
            
            logger.info(
                "list_all_users_completed",
                extra={
                    "users_returned": len(users),
                    "status_filter": status_filter.value if status_filter else "all",
                    "total_users_in_system": stats["total_users"]
                }
            )
            
            return response
            
        except Exception as e:
            logger.error(
                "list_all_users_failed",
                extra={
                    "status_filter": status_filter.value if status_filter else "all",
                    "error_type": type(e).__name__,
                    "error_message": str(e)
                }
            )
            raise
    
    def _validate_parameters(self, status_filter: Optional[UserStatusEnum]) -> None:
        """
        Validate input parameters
        
        Args:
            status_filter: Status filter to validate
            
        Raises:
            ValidationException: If validation fails
        """
        if status_filter is not None and not isinstance(status_filter, UserStatusEnum):
            raise ValidationException(
                message="Invalid status filter provided",
                field_name="status_filter",
                field_value=str(status_filter)
            )
    
    def _retrieve_users(self, status_filter: Optional[UserStatusEnum]) -> List:
        """
        Retrieve users based on filter criteria
        
        Args:
            status_filter: Optional status filter
            
        Returns:
            List of user entities
        """
        if status_filter:
            users = self._user_gateway.find_users_by_status(status_filter)
            logger.debug(
                "users_filtered_by_status",
                extra={
                    "status": status_filter.value,
                    "count": len(users)
                }
            )
        else:
            users = self._user_gateway.find_all_users()
            logger.debug(
                "all_users_retrieved",
                extra={"count": len(users)}
            )
        
        return users
    
    def _calculate_user_statistics(self) -> dict:
        """
        Calculate user statistics for the response
        
        Returns:
            Dictionary with user statistics
        """
        try:
            # Get counts by status
            total_users = len(self._user_gateway.find_all_users())
            active_users = self._user_gateway.count_users_by_status(UserStatusEnum.ACTIVE)
            inactive_users = self._user_gateway.count_users_by_status(UserStatusEnum.INACTIVE)
            suspended_users = self._user_gateway.count_users_by_status(UserStatusEnum.SUSPENDED)
            
            # Calculate percentages
            active_percentage = (active_users / total_users * 100) if total_users > 0 else 0
            
            return {
                "total_users": total_users,
                "active_users": active_users,
                "inactive_users": inactive_users,
                "suspended_users": suspended_users,
                "active_percentage": round(active_percentage, 2)
            }
            
        except Exception as e:
            logger.warning(
                "user_statistics_calculation_failed",
                extra={"error": str(e)}
            )
            # Return empty stats if calculation fails
            return {
                "total_users": 0,
                "active_users": 0,
                "inactive_users": 0,
                "suspended_users": 0,
                "active_percentage": 0.0
            }
    
    def _create_response(
        self, 
        users: List, 
        stats: dict, 
        status_filter: Optional[UserStatusEnum]
    ) -> dict:
        """
        Create response dictionary with users and metadata
        
        Args:
            users: List of user entities
            stats: User statistics
            status_filter: Applied status filter
            
        Returns:
            Response dictionary
        """
        # Convert users to dict format (assuming they have a to_dict method)
        users_data = []
        for user in users:
            try:
                if hasattr(user, 'to_dict'):
                    users_data.append(user.to_dict())
                else:
                    # Fallback for basic user objects
                    users_data.append({
                        "user_id": getattr(user, 'user_id', getattr(user, 'id', 'unknown')),
                        "name": getattr(user, 'name', 'Unknown'),
                        "email": getattr(user, 'email', 'unknown@example.com'),
                        "status": getattr(user, 'status', 'unknown'),
                        "is_active": getattr(user, 'is_active', lambda: False)()
                    })
            except Exception as e:
                logger.warning(
                    "user_serialization_failed",
                    extra={
                        "user": str(user),
                        "error": str(e)
                    }
                )
                # Skip problematic users
                continue
        
        return {
            "users": users_data,
            "metadata": {
                "returned_count": len(users_data),
                "status_filter": status_filter.value if status_filter else None,
                "statistics": stats
            },
            "success": True,
            "message": f"Retrieved {len(users_data)} users successfully"
        }


class GetUserStatsUseCase:
    """
    Use case for getting detailed user statistics
    
    Provides comprehensive statistics about users in the system
    including distribution by status, activity metrics, etc.
    """
    
    def __init__(self, user_gateway: UserGateway):
        """
        Initialize use case with dependencies
        
        Args:
            user_gateway: Gateway for user operations
        """
        self._user_gateway = user_gateway
    
    def execute(self) -> dict:
        """
        Execute get user statistics use case
        
        Returns:
            Dictionary with comprehensive user statistics
        """
        logger.info("get_user_stats_started")
        
        try:
            # Get all users for detailed analysis
            all_users = self._user_gateway.find_all_users()
            
            # Calculate comprehensive statistics
            stats = self._calculate_comprehensive_statistics(all_users)
            
            logger.info(
                "get_user_stats_completed",
                extra={"total_users": stats["total_users"]}
            )
            
            return stats
            
        except Exception as e:
            logger.error(
                "get_user_stats_failed",
                extra={
                    "error_type": type(e).__name__,
                    "error_message": str(e)
                }
            )
            raise
    
    def _calculate_comprehensive_statistics(self, users: List) -> dict:
        """
        Calculate comprehensive user statistics
        
        Args:
            users: List of all users
            
        Returns:
            Dictionary with detailed statistics
        """
        total_users = len(users)
        
        if total_users == 0:
            return {
                "total_users": 0,
                "active_users": 0,
                "inactive_users": 0,
                "suspended_users": 0,
                "active_percentage": 0.0,
                "registration_stats": {},
                "activity_distribution": {}
            }
        
        # Count by status
        active_count = sum(1 for user in users if getattr(user, 'status', None) == UserStatusEnum.ACTIVE)
        inactive_count = sum(1 for user in users if getattr(user, 'status', None) == UserStatusEnum.INACTIVE)
        suspended_count = sum(1 for user in users if getattr(user, 'status', None) == UserStatusEnum.SUSPENDED)
        
        # Calculate percentages
        active_percentage = (active_count / total_users * 100)
        inactive_percentage = (inactive_count / total_users * 100)
        suspended_percentage = (suspended_count / total_users * 100)
        
        return {
            "total_users": total_users,
            "active_users": active_count,
            "inactive_users": inactive_count,
            "suspended_users": suspended_count,
            "status_distribution": {
                "active_percentage": round(active_percentage, 2),
                "inactive_percentage": round(inactive_percentage, 2),
                "suspended_percentage": round(suspended_percentage, 2)
            },
            "health_score": round(active_percentage, 2),  # Simple health metric
            "timestamp": None  # Will be set by the API layer
        } 