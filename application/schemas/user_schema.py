"""
User Schemas - Enterprise Edition

Professional Pydantic schemas for user-related data validation and serialization
with comprehensive validation rules and enterprise patterns.

Key Features:
- Input validation for API requests
- Output serialization for API responses
- Enterprise naming conventions
- Comprehensive validation rules
- Factory methods for entity conversion
"""

from typing import List, Optional
from pydantic import BaseModel, Field, EmailStr, field_validator, ConfigDict
from datetime import datetime

from domain.enums.user_status_enum import UserStatusEnum
from domain.entities.user_entity import UserEntity


class UserResponse(BaseModel):
    """
    User response schema for API outputs

    Used for serializing user data in API responses with proper
    typing and validation for client consumption.
    """

    user_id: int = Field(..., description="Unique user identifier")
    name: str = Field(..., description="User full name")
    email: str = Field(..., description="User email address")
    status: str = Field(..., description="User status")

    @classmethod
    def from_entity(cls, user: UserEntity) -> "UserResponse":
        """
        Create response from user entity

        Args:
            user: User entity to convert

        Returns:
            UserResponse instance
        """
        return cls(
            user_id=user.user_id,
            name=user.name,
            email=user.email,
            status=user.status.value,
        )

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "user_id": 1,
                "name": "Juan Pérez",
                "email": "juan.perez@company.com",
                "status": "active",
            }
        },
    )


class UserListResponse(BaseModel):
    """
    User list response schema for API outputs

    Used for serializing multiple users in API responses with
    metadata about the collection.
    """

    users: List[UserResponse] = Field(..., description="List of users")
    total_count: int = Field(..., description="Total number of users")
    active_count: int = Field(..., description="Number of active users")
    inactive_count: int = Field(..., description="Number of inactive users")

    @classmethod
    def from_entities(cls, users: List[UserEntity]) -> "UserListResponse":
        """
        Create response from user entities

        Args:
            users: List of user entities to convert

        Returns:
            UserListResponse instance
        """
        user_responses = [UserResponse.from_entity(user) for user in users]
        active_count = len(
            [user for user in users if user.status == UserStatusEnum.ACTIVE]
        )
        inactive_count = len(users) - active_count

        return cls(
            users=user_responses,
            total_count=len(users),
            active_count=active_count,
            inactive_count=inactive_count,
        )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "users": [
                    {
                        "user_id": 1,
                        "name": "Juan Pérez",
                        "email": "juan.perez@company.com",
                        "status": "active",
                    },
                    {
                        "user_id": 2,
                        "name": "María García",
                        "email": "maria.garcia@company.com",
                        "status": "active",
                    },
                ],
                "total_count": 2,
                "active_count": 2,
                "inactive_count": 0,
            }
        }
    )


class CreateUserRequest(BaseModel):
    """
    Create user request schema for API inputs

    Used for validating user creation requests with comprehensive
    validation rules and business constraints.
    """

    name: str = Field(..., min_length=2, max_length=100, description="User full name")
    email: EmailStr = Field(..., description="User email address")

    @field_validator("name")
    def validate_name(cls, v):
        """Validate user name format"""
        if not v.strip():
            raise ValueError("Name cannot be empty or whitespace only")

        if any(char.isdigit() for char in v):
            raise ValueError("Name cannot contain numbers")

        return v.strip()

    model_config = ConfigDict(
        json_schema_extra={
            "example": {"name": "Juan Pérez", "email": "juan.perez@company.com"}
        }
    )


class UpdateUserStatusRequest(BaseModel):
    """
    Update user status request schema for API inputs

    Used for validating user status change requests with
    proper status validation.
    """

    status: UserStatusEnum = Field(..., description="New user status")

    model_config = ConfigDict(
        use_enum_values=True, json_schema_extra={"example": {"status": "active"}}
    )


class UserStatsResponse(BaseModel):
    """
    User statistics response schema

    Used for providing user-related statistics and metrics.
    """

    total_users: int = Field(..., description="Total number of users")
    active_users: int = Field(..., description="Number of active users")
    inactive_users: int = Field(..., description="Number of inactive users")
    users_created_today: int = Field(..., description="Users created today")
    users_created_this_week: int = Field(..., description="Users created this week")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "total_users": 10,
                "active_users": 8,
                "inactive_users": 2,
                "users_created_today": 2,
                "users_created_this_week": 5,
            }
        }
    )
