"""
Unit Tests for UserEntity
"""

import pytest
from domain.entities.user_entity import UserEntity, UserValidationException
from domain.enums.user_status_enum import UserStatusEnum


class TestUserEntity:
    """
    Unit tests for the UserEntity domain model.
    These tests ensure the core business logic and rules of a user
    are correctly enforced.
    """

    def test_create_user_successfully(self):
        """
        Verify that a new user can be created successfully with valid data.
        """
        user = UserEntity(
            user_id=1,
            name="John Doe",
            email="john.doe@example.com",
            status=UserStatusEnum.ACTIVE,
        )
        assert user.user_id == 1
        assert user.name == "John Doe"
        assert user.email == "john.doe@example.com"
        assert user.status == UserStatusEnum.ACTIVE

    @pytest.mark.parametrize(
        "user_id, name, email",
        [
            (0, "John Doe", "email@test.com"),  # Invalid user_id
            (-1, "John Doe", "email@test.com"),  # Invalid user_id
            (1, "", "email@test.com"),  # Empty name
            (1, " ", "email@test.com"),  # Whitespace name
            (1, "John Doe", "invalid-email"),  # Invalid email
            (1, "John Doe", "email@.com"),  # Invalid email
        ],
    )
    def test_create_user_with_invalid_data_raises_exception(self, user_id, name, email):
        """
        Verify that creating a user with invalid data raises a validation exception.
        """
        with pytest.raises(ValueError):
            UserEntity(
                user_id=user_id, name=name, email=email, status=UserStatusEnum.ACTIVE
            )

    def test_is_active_logic(self):
        """
        Verify the is_active() method works correctly.
        """
        active_user = UserEntity(
            user_id=1,
            name="Active User",
            email="active@test.com",
            status=UserStatusEnum.ACTIVE,
        )
        inactive_user = UserEntity(
            user_id=2,
            name="Inactive User",
            email="inactive@test.com",
            status=UserStatusEnum.INACTIVE,
        )
        suspended_user = UserEntity(
            user_id=3,
            name="Suspended User",
            email="suspended@test.com",
            status=UserStatusEnum.SUSPENDED,
        )

        assert active_user.is_active()
        assert not inactive_user.is_active()
        assert not suspended_user.is_active()

    def test_deactivate_and_activate_user(self):
        """
        Verify that a user's status can be changed to INACTIVE and back to ACTIVE.
        """
        user = UserEntity(
            user_id=1,
            name="Test User",
            email="test@test.com",
            status=UserStatusEnum.ACTIVE,
        )
        assert user.is_active()

        user.deactivate()
        assert user.status == UserStatusEnum.INACTIVE
        assert not user.is_active()

        user.activate()
        assert user.status == UserStatusEnum.ACTIVE
        assert user.is_active()

    def test_suspend_user(self):
        """
        Verify that a user's status can be changed to SUSPENDED.
        """
        user = UserEntity(
            user_id=1,
            name="Test User",
            email="test@test.com",
            status=UserStatusEnum.ACTIVE,
        )
        user.suspend()
        assert user.status == UserStatusEnum.SUSPENDED
        assert not user.is_active()

    def test_change_name_and_email(self):
        """
        Verify that name and email can be updated with valid data.
        """
        user = UserEntity(
            user_id=1,
            name="Old Name",
            email="old@test.com",
            status=UserStatusEnum.ACTIVE,
        )

        user.change_name("New Valid Name")
        assert user.name == "New Valid Name"

        user.change_email("new.valid@email.com")
        assert user.email == "new.valid@email.com"

    def test_change_name_and_email_with_invalid_data_raises_exception(self):
        """
        Verify that updating name or email with invalid data raises an exception.
        """
        user = UserEntity(
            user_id=1,
            name="Test User",
            email="test@test.com",
            status=UserStatusEnum.ACTIVE,
        )

        with pytest.raises(ValueError):
            user.change_name("")

        user2 = UserEntity(
            user_id=2,
            name="Test User 2",
            email="test2@test.com",
            status=UserStatusEnum.ACTIVE,
        )

        with pytest.raises(Exception):  # Pydantic validation exception
            user2.change_email("invalid-email-format")
