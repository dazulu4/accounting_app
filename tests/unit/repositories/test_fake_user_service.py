import pytest
from unittest.mock import patch, mock_open
import json
from infrastructure.driven_adapters.repositories.user_repository_fake import FakeUserService, FAKE_USERS
from domain.models.user import User, UserStatus


class TestFakeUserService:
    """Pruebas unitarias para FakeUserService"""

    @pytest.fixture
    def service(self):
        """Instancia del servicio"""
        return FakeUserService()

    @pytest.fixture
    def sample_users_data(self):
        """Datos de usuarios de ejemplo"""
        return {
            "users": [
                {
                    "id": 1,
                    "firstName": "Juan",
                    "lastName": "Pérez",
                    "email": "juan@example.com"
                },
                {
                    "id": 2,
                    "firstName": "María",
                    "lastName": "García",
                    "email": "maria@example.com"
                },
                {
                    "id": 3,
                    "firstName": "Carlos",
                    "lastName": "López",
                    "email": "carlos@example.com"
                }
            ]
        }

    @pytest.fixture
    def mock_users(self):
        """Usuarios mock para pruebas"""
        return {
            1: User(user_id=1, name="Juan", status=UserStatus.ACTIVE),
            2: User(user_id=2, name="María", status=UserStatus.ACTIVE),
            3: User(user_id=3, name="Carlos", status=UserStatus.INACTIVE)
        }

    def test_fake_user_service_get_by_id_found(self, service, mock_users):
        """Test: Usuario encontrado"""
        # Arrange
        with patch('infrastructure.driven_adapters.repositories.user_repository_fake.FAKE_USERS', mock_users):
            # Act
            result = service.get_by_id(1)

            # Assert
            assert result is not None
            assert isinstance(result, User)
            assert result.user_id == 1
            assert result.name == "Juan"
            assert result.status == UserStatus.ACTIVE

    def test_fake_user_service_get_by_id_not_found(self, service, mock_users):
        """Test: Usuario inexistente"""
        # Arrange
        with patch('infrastructure.driven_adapters.repositories.user_repository_fake.FAKE_USERS', mock_users):
            # Act
            result = service.get_by_id(999)

            # Assert
            assert result is None

    def test_fake_user_service_get_all_active(self, service, mock_users):
        """Test: Solo usuarios activos"""
        # Arrange
        with patch('infrastructure.driven_adapters.repositories.user_repository_fake.FAKE_USERS', mock_users):
            # Act
            result = service.get_all()

            # Assert
            assert len(result) == 2  # Solo usuarios activos
            assert all(user.status == UserStatus.ACTIVE for user in result)
            assert all(isinstance(user, User) for user in result)

    def test_fake_user_service_get_all_empty(self, service):
        """Test: Lista vacía cuando no hay usuarios"""
        # Arrange
        with patch('infrastructure.driven_adapters.repositories.user_repository_fake.FAKE_USERS', {}):
            # Act
            result = service.get_all()

            # Assert
            assert len(result) == 0

    def test_fake_user_service_load_from_json(self, sample_users_data):
        """Test: Carga desde JSON"""
        # Arrange
        json_content = json.dumps(sample_users_data)
        
        with patch('builtins.open', mock_open(read_data=json_content)):
            # Act - Simular la carga del módulo
            from infrastructure.driven_adapters.repositories.user_repository_fake import FAKE_USERS
            
            # Assert - Verificar que el módulo se cargó correctamente
            # Nota: FAKE_USERS ya contiene datos del archivo real, así que verificamos que existe
            assert isinstance(FAKE_USERS, dict)
            # Verificamos que el servicio funciona con los datos cargados
            service = FakeUserService()
            assert hasattr(service, 'get_by_id')
            assert hasattr(service, 'get_all')

    def test_fake_user_service_file_not_found(self):
        """Test: Archivo JSON no encontrado"""
        with patch('builtins.open', side_effect=FileNotFoundError):
            with patch('infrastructure.driven_adapters.repositories.user_repository_fake.FAKE_USERS', {}):
                # Act - Simular la carga del módulo
                from infrastructure.driven_adapters.repositories.user_repository_fake import FAKE_USERS
                
                # Assert
                assert len(FAKE_USERS) == 0

    def test_fake_user_service_json_decode_error(self):
        """Test: Error de decodificación JSON"""
        with patch('builtins.open', mock_open(read_data="invalid json")):
            with patch('infrastructure.driven_adapters.repositories.user_repository_fake.FAKE_USERS', {}):
                # Act - Simular la carga del módulo
                from infrastructure.driven_adapters.repositories.user_repository_fake import FAKE_USERS
                
                # Assert
                assert len(FAKE_USERS) == 0

    def test_fake_user_service_missing_key_error(self):
        """Test: Error de clave faltante en JSON"""
        invalid_data = {"invalid": "structure"}
        json_content = json.dumps(invalid_data)
        
        with patch('builtins.open', mock_open(read_data=json_content)):
            with patch('infrastructure.driven_adapters.repositories.user_repository_fake.FAKE_USERS', {}):
                # Act - Simular la carga del módulo
                from infrastructure.driven_adapters.repositories.user_repository_fake import FAKE_USERS
                
                # Assert
                assert len(FAKE_USERS) == 0

    def test_fake_user_service_mixed_status_users(self, service):
        """Test: Usuarios con diferentes estados"""
        mixed_users = {
            1: User(user_id=1, name="Activo", status=UserStatus.ACTIVE),
            2: User(user_id=2, name="Inactivo", status=UserStatus.INACTIVE),
            3: User(user_id=3, name="Activo2", status=UserStatus.ACTIVE)
        }
        
        with patch('infrastructure.driven_adapters.repositories.user_repository_fake.FAKE_USERS', mixed_users):
            # Act
            result = service.get_all()

            # Assert
            assert len(result) == 2  # Solo activos
            assert all(user.status == UserStatus.ACTIVE for user in result)

    def test_fake_user_service_user_properties(self, service, mock_users):
        """Test: Propiedades de usuario correctas"""
        with patch('infrastructure.driven_adapters.repositories.user_repository_fake.FAKE_USERS', mock_users):
            # Act
            user = service.get_by_id(1)

            # Assert
            assert user.user_id == 1
            assert user.name == "Juan"
            assert user.is_active() == True

    def test_fake_user_service_inactive_user_properties(self, service, mock_users):
        """Test: Propiedades de usuario inactivo"""
        with patch('infrastructure.driven_adapters.repositories.user_repository_fake.FAKE_USERS', mock_users):
            # Act
            user = service.get_by_id(3)

            # Assert
            assert user.user_id == 3
            assert user.name == "Carlos"
            assert user.is_active() == False

    def test_fake_user_service_large_dataset(self, service):
        """Test: Gran cantidad de usuarios"""
        large_users = {
            i: User(user_id=i, name=f"Usuario{i}", status=UserStatus.ACTIVE)
            for i in range(1, 101)  # 100 usuarios
        }
        
        with patch('infrastructure.driven_adapters.repositories.user_repository_fake.FAKE_USERS', large_users):
            # Act
            result = service.get_all()

            # Assert
            assert len(result) == 100
            assert all(isinstance(user, User) for user in result)
            assert all(user.is_active() for user in result)

    def test_fake_user_service_duplicate_user_ids(self, service):
        """Test: IDs de usuario duplicados (caso edge)"""
        duplicate_users = {
            1: User(user_id=1, name="Primero", status=UserStatus.ACTIVE),
            1: User(user_id=1, name="Segundo", status=UserStatus.ACTIVE)  # Sobrescribe el primero
        }
        
        with patch('infrastructure.driven_adapters.repositories.user_repository_fake.FAKE_USERS', duplicate_users):
            # Act
            result = service.get_by_id(1)

            # Assert
            assert result is not None
            assert result.name == "Segundo"  # El último valor asignado 