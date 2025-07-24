"""
User Entity - Domain Model

This module contains the core User entity following Domain-Driven Design principles,
with validation and business logic encapsulated within the entity.
"""

from __future__ import annotations

from pydantic import BaseModel, EmailStr, Field, field_validator

from ..enums.user_status_enum import UserStatusEnum


class UserEntity(BaseModel):
    """
    Represents a user in the domain using Pydantic for data validation.
    """

    user_id: int = Field(..., gt=0, description="The unique identifier for the user.")
    name: str = Field(..., min_length=1, description="The name of the user.")
    email: EmailStr = Field(..., description="The email address of the user.")
    status: UserStatusEnum = Field(..., description="The current status of the user.")

    @field_validator("name")
    @classmethod
    def name_must_not_be_empty(cls, v: str) -> str:
        """Validates that the name is not empty or just whitespace."""
        if not v.strip():
            raise ValueError("User name cannot be empty or whitespace.")
        return v.strip()

    def is_active(self) -> bool:
        """Checks if the user is active."""
        return self.status == UserStatusEnum.ACTIVE

    def activate(self):
        """Sets the user status to ACTIVE."""
        self.status = UserStatusEnum.ACTIVE

    def deactivate(self):
        """Sets the user status to INACTIVE."""
        self.status = UserStatusEnum.INACTIVE

    def suspend(self):
        """Sets the user status to SUSPENDED."""
        self.status = UserStatusEnum.SUSPENDED

    def change_name(self, new_name: str):
        """Changes the user's name after validation."""
        # Validate the new name manually
        if not new_name or not new_name.strip():
            raise ValueError("User name cannot be empty or whitespace.")
        self.name = new_name.strip()

    def change_email(self, new_email: str):
        """Changes the user's email after validation."""
        from pydantic import EmailStr, TypeAdapter, ValidationError

        try:
            validated_email = TypeAdapter(EmailStr).validate_python(new_email)
        except ValidationError as e:
            raise ValueError("Invalid email format") from e
        self.email = validated_email
