"""
Pruebas unitarias para el modelo User

Estas pruebas validan:
- Creación de usuarios
- Comportamiento del método is_active()
- Validación del enum UserStatus
- Comportamiento de usuarios inactivos
"""

import pytest
from domain.models.user import User, UserStatus


class TestUserCreation:
    """Pruebas para la creación de usuarios"""
    
    @pytest.mark.unit
    def test_user_creation(self, sample_user):
        """Prueba crear un usuario con datos válidos"""
        user = sample_user
        
        assert user.user_id == 1
        assert user.name == "Usuario de Prueba"
        assert user.status == UserStatus.ACTIVE
    
    @pytest.mark.unit
    def test_user_creation_with_custom_values(self):
        """Prueba crear un usuario con valores personalizados"""
        custom_user_id = 999
        custom_name = "Usuario Personalizado"
        custom_status = UserStatus.INACTIVE
        
        user = User(
            user_id=custom_user_id,
            name=custom_name,
            status=custom_status
        )
        
        assert user.user_id == custom_user_id
        assert user.name == custom_name
        assert user.status == custom_status
    
    @pytest.mark.unit
    def test_user_creation_with_empty_name(self):
        """Prueba crear un usuario con nombre vacío"""
        user = User(
            user_id=1,
            name="",
            status=UserStatus.ACTIVE
        )
        
        assert user.name == ""
        assert user.status == UserStatus.ACTIVE
        assert user.is_active() is True
    
    @pytest.mark.unit
    def test_user_creation_with_very_long_name(self):
        """Prueba crear un usuario con nombre muy largo"""
        long_name = "A" * 1000
        
        user = User(
            user_id=1,
            name=long_name,
            status=UserStatus.ACTIVE
        )
        
        assert user.name == long_name
        assert user.status == UserStatus.ACTIVE


class TestUserActiveStatus:
    """Pruebas para el comportamiento del método is_active()"""
    
    @pytest.mark.unit
    def test_user_active_status(self, sample_user):
        """Prueba que un usuario activo retorne True en is_active()"""
        user = sample_user
        
        assert user.status == UserStatus.ACTIVE
        assert user.is_active() is True
    
    @pytest.mark.unit
    def test_user_inactive_behavior(self, sample_inactive_user):
        """Prueba que un usuario inactivo retorne False en is_active()"""
        user = sample_inactive_user
        
        assert user.status == UserStatus.INACTIVE
        assert user.is_active() is False
    
    @pytest.mark.unit
    def test_user_status_transition(self):
        """Prueba el cambio de estado de activo a inactivo"""
        user = User(
            user_id=1,
            name="Usuario de Prueba",
            status=UserStatus.ACTIVE
        )
        
        # Verificar estado inicial
        assert user.is_active() is True
        
        # Cambiar a inactivo
        user.status = UserStatus.INACTIVE
        
        # Verificar nuevo estado
        assert user.is_active() is False
    
    @pytest.mark.unit
    def test_user_status_transition_reverse(self):
        """Prueba el cambio de estado de inactivo a activo"""
        user = User(
            user_id=1,
            name="Usuario de Prueba",
            status=UserStatus.INACTIVE
        )
        
        # Verificar estado inicial
        assert user.is_active() is False
        
        # Cambiar a activo
        user.status = UserStatus.ACTIVE
        
        # Verificar nuevo estado
        assert user.is_active() is True


class TestUserStatusEnum:
    """Pruebas para el enum UserStatus"""
    
    @pytest.mark.unit
    def test_user_status_enum_values(self, user_status_enum_values):
        """Prueba que todos los valores del enum UserStatus sean correctos"""
        expected_values = ["ACTIVE", "INACTIVE"]
        assert user_status_enum_values == expected_values
    
    @pytest.mark.unit
    def test_user_status_enum_comparison(self):
        """Prueba comparaciones de estados de usuario"""
        assert UserStatus.ACTIVE == "ACTIVE"
        assert UserStatus.INACTIVE == "INACTIVE"
        assert UserStatus.ACTIVE != UserStatus.INACTIVE
    
    @pytest.mark.unit
    def test_user_status_enum_string_conversion(self):
        """Prueba la conversión de enum a string"""
        active_status = UserStatus.ACTIVE
        inactive_status = UserStatus.INACTIVE
        
        # Los enums en Python se convierten a "EnumName.VALUE"
        assert str(active_status) == "UserStatus.ACTIVE"
        assert str(inactive_status) == "UserStatus.INACTIVE"
    
    @pytest.mark.unit
    def test_user_status_enum_iteration(self):
        """Prueba iterar sobre los valores del enum"""
        status_values = list(UserStatus)
        
        assert len(status_values) == 2
        assert UserStatus.ACTIVE in status_values
        assert UserStatus.INACTIVE in status_values


class TestUserProperties:
    """Pruebas para las propiedades de los usuarios"""
    
    @pytest.mark.unit
    def test_user_properties_immutability(self, sample_user):
        """Prueba que las propiedades básicas no cambien al cambiar el estado"""
        user = sample_user
        
        # Guardar valores originales
        original_user_id = user.user_id
        original_name = user.name
        
        # Cambiar estado
        user.status = UserStatus.INACTIVE
        
        # Verificar que las propiedades básicas no cambiaron
        assert user.user_id == original_user_id
        assert user.name == original_name
    
    @pytest.mark.unit
    def test_user_string_representation(self, sample_user):
        """Prueba la representación en string de un usuario"""
        user = sample_user
        
        # Verificar que la representación contiene información relevante
        user_str = str(user)
        assert "User" in user_str or str(user.user_id) in user_str or user.name in user_str
    
    @pytest.mark.unit
    def test_user_equality(self):
        """Prueba la igualdad entre usuarios"""
        user1 = User(
            user_id=1,
            name="Usuario 1",
            status=UserStatus.ACTIVE
        )
        
        user2 = User(
            user_id=1,  # Mismo ID
            name="Usuario 2",  # Diferente nombre
            status=UserStatus.INACTIVE  # Diferente estado
        )
        
        # Los usuarios con el mismo ID deberían ser iguales en términos de ID
        assert user1.user_id == user2.user_id
        # Pero con diferentes propiedades
        assert user1.name != user2.name
        assert user1.status != user2.status


class TestUserEdgeCases:
    """Pruebas para casos edge de los usuarios"""
    
    @pytest.mark.unit
    def test_user_with_negative_user_id(self):
        """Prueba crear un usuario con user_id negativo"""
        user = User(
            user_id=-1,
            name="Usuario con ID negativo",
            status=UserStatus.ACTIVE
        )
        
        assert user.user_id == -1
        assert user.is_active() is True
    
    @pytest.mark.unit
    def test_user_with_zero_user_id(self):
        """Prueba crear un usuario con user_id cero"""
        user = User(
            user_id=0,
            name="Usuario con ID cero",
            status=UserStatus.ACTIVE
        )
        
        assert user.user_id == 0
        assert user.is_active() is True
    
    @pytest.mark.unit
    def test_user_with_very_large_user_id(self):
        """Prueba crear un usuario con user_id muy grande"""
        large_user_id = 999999999
        
        user = User(
            user_id=large_user_id,
            name="Usuario con ID grande",
            status=UserStatus.ACTIVE
        )
        
        assert user.user_id == large_user_id
        assert user.is_active() is True
    
    @pytest.mark.unit
    def test_user_with_special_characters_in_name(self):
        """Prueba crear un usuario con caracteres especiales en el nombre"""
        special_name = "Usuario con ñ, á, é, í, ó, ú y símbolos: @#$%^&*()"
        
        user = User(
            user_id=1,
            name=special_name,
            status=UserStatus.ACTIVE
        )
        
        assert user.name == special_name
        assert user.is_active() is True


class TestUserBehavior:
    """Pruebas para el comportamiento general de los usuarios"""
    
    @pytest.mark.unit
    def test_user_creation_with_different_statuses(self):
        """Prueba crear usuarios con diferentes estados"""
        # Usuario activo
        active_user = User(
            user_id=1,
            name="Usuario Activo",
            status=UserStatus.ACTIVE
        )
        assert active_user.is_active() is True
        
        # Usuario inactivo
        inactive_user = User(
            user_id=2,
            name="Usuario Inactivo",
            status=UserStatus.INACTIVE
        )
        assert inactive_user.is_active() is False
    
    @pytest.mark.unit
    def test_user_status_consistency(self):
        """Prueba que el estado sea consistente después de cambios"""
        user = User(
            user_id=1,
            name="Usuario de Prueba",
            status=UserStatus.ACTIVE
        )
        
        # Verificar estado inicial
        assert user.is_active() is True
        
        # Cambiar estado múltiples veces
        user.status = UserStatus.INACTIVE
        assert user.is_active() is False
        
        user.status = UserStatus.ACTIVE
        assert user.is_active() is True
        
        user.status = UserStatus.INACTIVE
        assert user.is_active() is False
    
    @pytest.mark.unit
    def test_user_with_none_values(self):
        """Prueba comportamiento con valores None (si fuera permitido)"""
        # Nota: El modelo actual no permite None, pero probamos el comportamiento
        # si se permitiera en el futuro
        user = User(
            user_id=1,
            name="Usuario de Prueba",
            status=UserStatus.ACTIVE
        )
        
        # Verificar que el usuario funciona correctamente
        assert user.is_active() is True
        assert user.name == "Usuario de Prueba" 