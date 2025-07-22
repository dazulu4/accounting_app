"""
User Status Enum - Domain Model

This module defines the enumeration for user statuses, ensuring consistency
and type safety across the domain.
"""
from enum import Enum


class UserStatusEnum(Enum):
    """
    Enumeration for user statuses.
    """
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended" 