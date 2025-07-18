"""
Schemas Pydantic para la entidad User

¿Qué es un Schema Pydantic?
- Es una clase que define la estructura de datos para validación y serialización
- Hereda de BaseModel (clase base de Pydantic)
- Define los campos y sus tipos usando type hints de Python
- Pydantic validará automáticamente los datos y convertirá tipos si es posible
"""

from pydantic import BaseModel, Field
from typing import Optional
from domain.models.user import UserStatus


class UserBase(BaseModel):
    """
    Schema base para User - contiene campos comunes para crear y actualizar
    
    ¿Qué es BaseModel?
    - Es la clase base de Pydantic que proporciona toda la funcionalidad
    - Permite validación automática, serialización JSON, etc.
    """
    name: str = Field(..., description="Nombre del usuario", min_length=1, max_length=100)
    status: UserStatus = Field(default=UserStatus.ACTIVE, description="Estado del usuario")


class UserCreate(UserBase):
    """
    Schema para crear un nuevo usuario
    
    ¿Por qué heredar de UserBase?
    - Reutiliza la lógica común
    - Puede agregar campos específicos para creación
    - Mantiene consistencia en la API
    """
    pass  # No necesitamos campos adicionales para crear


class UserUpdate(BaseModel):
    """
    Schema para actualizar un usuario existente
    
    ¿Por qué usar Optional?
    - Permite actualizar solo algunos campos
    - Los campos no enviados no se modifican
    - Más flexible para operaciones PATCH
    """
    name: Optional[str] = Field(None, description="Nombre del usuario", min_length=1, max_length=100)
    status: Optional[UserStatus] = Field(None, description="Estado del usuario")


class UserResponse(UserBase):
    """
    Schema para respuestas de API - incluye el ID del usuario
    
    ¿Qué es Field(...)?
    - Los tres puntos (...) indican que el campo es obligatorio
    - Field permite agregar metadatos como descripción, validaciones, etc.
    """
    user_id: int = Field(..., description="ID único del usuario")
    
    model_config = {
        "from_attributes": True
    }


class UserListResponse(BaseModel):
    """
    Schema para listar usuarios - puede incluir metadatos de paginación
    """
    users: list[UserResponse] = Field(..., description="Lista de usuarios")
    total: int = Field(..., description="Total de usuarios")
    page: int = Field(..., description="Página actual")
    per_page: int = Field(..., description="Usuarios por página") 