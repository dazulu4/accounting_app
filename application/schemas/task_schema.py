"""
Schemas Pydantic para la entidad Task

Conceptos importantes que verás aquí:
- UUID: Tipo especial para identificadores únicos
- datetime: Para fechas y timestamps
- Enums: Para valores predefinidos (como estados)
- Validaciones complejas: Combinando múltiples reglas
"""

from pydantic import BaseModel, Field, field_validator
from typing import Optional
from datetime import datetime
from uuid import UUID
from domain.models.task import TaskStatus


class TaskBase(BaseModel):
    """
    Schema base para Task - campos comunes para crear y actualizar
    
    ¿Qué es validator?
    - Es un decorador que permite validaciones personalizadas
    - Se ejecuta después de la validación automática de tipos
    - Puede acceder a todos los campos del modelo
    """
    title: str = Field(..., description="Título de la tarea", min_length=1, max_length=200)
    description: str = Field(..., description="Descripción de la tarea", min_length=1, max_length=1000)
    user_id: int = Field(..., description="ID del usuario asignado", gt=0)
    
    @field_validator('title')
    @classmethod
    def title_must_not_be_empty(cls, v):
        """
        Validador personalizado para el título
        
        ¿Qué hace este validador?
        - Verifica que el título no esté vacío después de quitar espacios
        - Lanza una excepción si la validación falla
        - Pydantic captura la excepción y la convierte en error de validación
        """
        if not v.strip():
            raise ValueError('El título no puede estar vacío')
        return v.strip()


class TaskCreate(TaskBase):
    """
    Schema para crear una nueva tarea
    
    ¿Por qué no incluir task_id?
    - El ID se genera automáticamente en el dominio
    - No queremos que el usuario lo especifique
    - Mantiene la integridad del sistema
    """
    pass


class TaskUpdate(BaseModel):
    """
    Schema para actualizar una tarea existente
    
    ¿Por qué todos los campos son Optional?
    - Permite actualizar solo algunos campos
    - Más flexible para operaciones PATCH
    - Mantiene los valores existentes si no se envían
    """
    title: Optional[str] = Field(None, description="Título de la tarea", min_length=1, max_length=200)
    description: Optional[str] = Field(None, description="Descripción de la tarea", min_length=1, max_length=1000)
    user_id: Optional[int] = Field(None, description="ID del usuario asignado", gt=0)
    status: Optional[TaskStatus] = Field(None, description="Estado de la tarea")
    
    @field_validator('title')
    @classmethod
    def title_must_not_be_empty(cls, v):
        if v is not None and not v.strip():
            raise ValueError('El título no puede estar vacío')
        return v.strip() if v else v


class TaskResponse(TaskBase):
    """
    Schema para respuestas de API - incluye todos los campos de la tarea
    
    ¿Qué es UUID?
    - Es un identificador único universal
    - Más seguro que IDs secuenciales
    - Se usa para evitar colisiones en sistemas distribuidos
    """
    task_id: UUID = Field(..., description="ID único de la tarea")
    status: TaskStatus = Field(..., description="Estado actual de la tarea")
    created_at: datetime = Field(..., description="Fecha de creación")
    completed_at: Optional[datetime] = Field(None, description="Fecha de completado")
    
    model_config = {
        "from_attributes": True
    }


class TaskListResponse(BaseModel):
    """
    Schema para listar tareas con paginación
    """
    tasks: list[TaskResponse] = Field(..., description="Lista de tareas")
    total: int = Field(..., description="Total de tareas")
    page: int = Field(..., description="Página actual")
    per_page: int = Field(..., description="Tareas por página")


class TaskCompleteRequest(BaseModel):
    """
    Schema específico para completar una tarea
    
    ¿Por qué un schema separado?
    - Operación específica con lógica de negocio
    - Puede tener validaciones especiales
    - Más claro en la documentación de la API
    """
    pass  # No necesita campos adicionales para completar 