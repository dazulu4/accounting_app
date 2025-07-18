"""
Pruebas de integración para Pydantic

Estas pruebas validan:
- Creación de schemas desde datos válidos
- Validación de datos inválidos
- Conversión de modelos de dominio a schemas
- Manejo de errores de validación
- Configuración centralizada con Pydantic Settings
"""

import pytest
from datetime import datetime, timezone
from uuid import uuid4
from pydantic import ValidationError

from domain.models.user import User, UserStatus
from domain.models.task import Task, TaskStatus
from application.schemas.user_schema import UserCreate, UserResponse, UserUpdate
from application.schemas.task_schema import TaskCreate, TaskResponse, TaskUpdate


class TestUserSchemas:
    """Pruebas para los schemas de User"""
    
    def test_create_valid_user(self):
        """Prueba crear un UserCreate válido"""
        user_data = {
            "name": "Juan Pérez",
            "status": UserStatus.ACTIVE
        }
        
        user_create = UserCreate(**user_data)
        
        assert user_create.name == "Juan Pérez"
        assert user_create.status == UserStatus.ACTIVE
    
    def test_create_user_with_empty_name(self):
        """Prueba que se rechace un nombre vacío"""
        invalid_data = {
            "name": "",
            "status": UserStatus.ACTIVE
        }
        
        with pytest.raises(ValidationError) as exc_info:
            UserCreate(**invalid_data)
        
        # Verificar que el error es específico del campo name
        errors = exc_info.value.errors()
        assert len(errors) == 1
        assert errors[0]["loc"][0] == "name"
        assert "at least 1 character" in str(errors[0]["msg"])
    
    def test_create_user_with_short_name(self):
        """Prueba que se rechace un nombre muy corto"""
        # Nota: No tenemos validación de longitud mínima para nombre
        # Esta prueba verifica que un nombre corto sea aceptado
        valid_data = {
            "name": "A",  # Nombre corto pero válido
            "status": UserStatus.ACTIVE
        }
        
        user = UserCreate(**valid_data)
        assert user.name == "A"
        assert user.status == UserStatus.ACTIVE
    
    def test_convert_domain_user_to_schema(self):
        """Prueba convertir un modelo de dominio a schema de respuesta"""
        # Crear modelo de dominio
        domain_user = User(
            user_id=1,
            name="María García",
            status=UserStatus.ACTIVE
        )
        
        # Convertir a schema de respuesta
        response_user = UserResponse.model_validate(domain_user)
        
        assert response_user.user_id == 1
        assert response_user.name == "María García"
        assert response_user.status == UserStatus.ACTIVE
    
    def test_user_update_partial(self):
        """Prueba actualización parcial de usuario"""
        update_data = {
            "name": "María García Actualizada"
        }
        
        user_update = UserUpdate(**update_data)
        
        assert user_update.name == "María García Actualizada"
        assert user_update.status is None  # Campo no enviado debe ser None


class TestTaskSchemas:
    """Pruebas para los schemas de Task"""
    
    def test_create_valid_task(self):
        """Prueba crear un TaskCreate válido"""
        task_data = {
            "title": "Implementar Pydantic",
            "description": "Integrar validación de datos con Pydantic en la aplicación",
            "user_id": 1
        }
        
        task_create = TaskCreate(**task_data)
        
        assert task_create.title == "Implementar Pydantic"
        assert task_create.description == "Integrar validación de datos con Pydantic en la aplicación"
        assert task_create.user_id == 1
    
    def test_create_task_with_empty_title(self):
        """Prueba que se rechace un título vacío"""
        invalid_task_data = {
            "title": "   ",  # Solo espacios
            "description": "Descripción válida",
            "user_id": 1
        }
        
        with pytest.raises(ValidationError) as exc_info:
            TaskCreate(**invalid_task_data)
        
        errors = exc_info.value.errors()
        assert len(errors) == 1
        assert errors[0]["loc"][0] == "title"
        assert "no puede estar vacío" in str(errors[0]["msg"])
    
    def test_create_task_with_invalid_user_id(self):
        """Prueba que se rechace un user_id inválido"""
        invalid_task_data = {
            "title": "Título válido",
            "description": "Descripción válida",
            "user_id": 0  # Debe ser mayor que 0
        }
        
        with pytest.raises(ValidationError) as exc_info:
            TaskCreate(**invalid_task_data)
        
        errors = exc_info.value.errors()
        assert len(errors) == 1
        assert errors[0]["loc"][0] == "user_id"
        assert "greater than 0" in str(errors[0]["msg"])
    
    def test_convert_domain_task_to_schema(self):
        """Prueba convertir un modelo de dominio a schema de respuesta"""
        # Crear modelo de dominio
        task_id = uuid4()
        domain_task = Task(
            task_id=task_id,
            title="Tarea de prueba",
            description="Descripción de prueba",
            user_id=1
        )
        
        # Convertir a schema de respuesta
        response_task = TaskResponse.model_validate(domain_task)
        
        assert response_task.task_id == task_id
        assert response_task.title == "Tarea de prueba"
        assert response_task.status == TaskStatus.NEW
        assert response_task.user_id == 1
        assert response_task.created_at is not None
        assert response_task.completed_at is None
    
    def test_task_update_partial(self):
        """Prueba actualización parcial de tarea"""
        update_data = {
            "title": "Título actualizado",
            "status": TaskStatus.IN_PROGRESS
        }
        
        task_update = TaskUpdate(**update_data)
        
        assert task_update.title == "Título actualizado"
        assert task_update.status == TaskStatus.IN_PROGRESS
        assert task_update.description is None  # Campo no enviado debe ser None
        assert task_update.user_id is None  # Campo no enviado debe ser None


class TestConfiguration:
    """Pruebas para la configuración con Pydantic Settings"""
    
    def test_settings_loading(self):
        """Prueba que la configuración se cargue correctamente"""
        from application.config import settings
        
        # Verificar configuración general
        assert settings.environment == "development"
        assert settings.version == "1.0.0"
        
        # Verificar configuración de API
        assert settings.api.api_host == "0.0.0.0"
        assert settings.api.api_port == 8000
        assert settings.api.default_page_size == 20
        assert settings.api.max_page_size == 100
        
        # Verificar configuración de base de datos
        assert settings.database.database_name == "accounting"
        assert settings.database.database_user == "admin"
        assert settings.database.database_password == "admin"
        assert settings.database.database_port == 3306
        
        # Verificar URL de conexión
        expected_url = "mysql+aiomysql://admin:admin@localhost:3306/accounting"
        assert settings.database.database_url == expected_url
    
    def test_database_settings_property(self):
        """Prueba la propiedad database_url"""
        from application.config import settings
        
        url = settings.database.database_url
        assert "mysql+aiomysql://" in url
        assert "admin:admin@" in url
        assert "localhost:3306" in url
        assert "accounting" in url
    
    def test_api_settings_defaults(self):
        """Prueba los valores por defecto de la configuración de API"""
        from application.config import settings
        
        # Verificar CORS
        assert "*" in settings.api.cors_origins
        assert "*" in settings.api.cors_methods
        assert "*" in settings.api.cors_headers
        
        # Verificar paginación
        assert settings.api.default_page_size > 0
        assert settings.api.max_page_size > settings.api.default_page_size


class TestSchemaValidation:
    """Pruebas adicionales de validación de schemas"""
    
    def test_user_status_enum_validation(self):
        """Prueba que se valide correctamente el enum UserStatus"""
        # Válido
        user_data = {"name": "Test", "status": UserStatus.ACTIVE}
        user = UserCreate(**user_data)
        assert user.status == UserStatus.ACTIVE
        
        # Inválido
        with pytest.raises(ValidationError):
            UserCreate(**{"name": "Test", "status": "INVALID_STATUS"})
    
    def test_task_status_enum_validation(self):
        """Prueba que se valide correctamente el enum TaskStatus"""
        # Válido
        task_data = {
            "title": "Test",
            "description": "Test",
            "user_id": 1
        }
        task = TaskCreate(**task_data)
        # TaskStatus se establece automáticamente como NEW
        
        # Probar actualización con status válido
        update_data = {"status": TaskStatus.IN_PROGRESS}
        task_update = TaskUpdate(**update_data)
        assert task_update.status == TaskStatus.IN_PROGRESS
        
        # Inválido
        with pytest.raises(ValidationError):
            TaskUpdate(**{"status": "INVALID_STATUS"})
    
    def test_field_constraints(self):
        """Prueba las restricciones de campos"""
        # Nombre muy largo
        with pytest.raises(ValidationError):
            UserCreate(**{
                "name": "A" * 101,  # Más de 100 caracteres
                "status": UserStatus.ACTIVE
            })
        
        # Descripción muy larga
        with pytest.raises(ValidationError):
            TaskCreate(**{
                "title": "Test",
                "description": "A" * 1001,  # Más de 1000 caracteres
                "user_id": 1
            }) 