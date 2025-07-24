import pytest
from pydantic import ValidationError

from application.schemas.user_schema import (
    CreateUserRequest,
    UpdateUserStatusRequest,
    UserListResponse,
    UserResponse,
)
from domain.entities.user_entity import UserEntity
from domain.enums.user_status_enum import UserStatusEnum


class TestCreateUserRequest:
    """Test suite for the CreateUserRequest schema."""

    def test_create_user_request_success(self):
        """Test successful creation of a CreateUserRequest."""
        data = {"name": "John Doe", "email": "john.doe@example.com"}
        req = CreateUserRequest(**data)
        assert req.name == "John Doe"
        assert req.email == "john.doe@example.com"

    @pytest.mark.parametrize(
        "invalid_data",
        [
            {"name": " ", "email": "a@b.com"},
            {"name": "J", "email": "a@b.com"},  # Too short
            {"name": "John Doe", "email": "not-an-email"},
        ],
    )
    def test_create_user_request_validation_error(self, invalid_data):
        """Test validation errors for CreateUserRequest."""
        with pytest.raises(ValidationError):
            CreateUserRequest(**invalid_data)


class TestUserResponseSchemas:
    """Test suite for user response schemas."""

    @pytest.fixture
    def user_entity(self) -> UserEntity:
        """Fixture for a sample UserEntity."""
        return UserEntity(
            user_id=1,
            name="Jane Doe",
            email="jane.doe@example.com",
            status=UserStatusEnum.ACTIVE,
        )

    def test_user_response_from_entity(self, user_entity):
        """Test UserResponse.from_entity."""
        res = UserResponse.from_entity(user_entity)
        assert res.user_id == user_entity.user_id
        assert res.status == UserStatusEnum.ACTIVE.value

    def test_user_list_response_from_entities(self, user_entity):
        """Test UserListResponse.from_entities."""
        users = [user_entity]
        res = UserListResponse.from_entities(users)
        assert len(res.users) == 1
        assert res.total_count == 1
        assert res.active_count == 1
        assert res.inactive_count == 0


class TestUpdateUserStatusRequest:
    """Test suite for the UpdateUserStatusRequest schema."""

    def test_update_user_status_request_success(self):
        """Test successful creation of an UpdateUserStatusRequest."""
        req = UpdateUserStatusRequest(status=UserStatusEnum.ACTIVE)
        assert req.status == "active"

    def test_update_user_status_invalid_status(self):
        """Test that an invalid status raises a validation error."""
        with pytest.raises(ValidationError):
            UpdateUserStatusRequest(status="INVALID_STATUS")
