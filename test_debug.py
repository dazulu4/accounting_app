import pytest
from domain.entities.user_entity import UserEntity
from domain.enums.user_status_enum import UserStatusEnum

def test_debug():
    user = UserEntity(
        user_id=1, 
        name="Test User", 
        email="test@test.com", 
        status=UserStatusEnum.ACTIVE
    )
    
    print("User created successfully")
    
    with pytest.raises(ValueError):
        user.change_name("")
        print("This should not be reached")
    
    print("Test passed")

if __name__ == "__main__":
    test_debug() 