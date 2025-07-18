"""
Pruebas unitarias para el modelo Task

Estas pruebas validan:
- Creación de tareas con valores por defecto
- Comportamiento del método complete()
- Transiciones de estado
- Timestamps de completado
- Completado múltiple
"""

import pytest
from datetime import datetime, timezone
from uuid import uuid4
from domain.models.task import Task, TaskStatus


class TestTaskCreation:
    """Pruebas para la creación de tareas"""
    
    @pytest.mark.unit
    def test_task_creation_defaults(self, sample_task):
        """Prueba que una tarea nueva tenga los valores por defecto correctos"""
        task = sample_task
        
        assert task.title == "Tarea de prueba"
        assert task.description == "Descripción de prueba"
        assert task.user_id == 1
        assert task.status == TaskStatus.NEW
        assert task.completed_at is None
        assert isinstance(task.created_at, datetime)
        assert task.created_at.tzinfo == timezone.utc
    
    @pytest.mark.unit
    def test_task_creation_with_custom_values(self):
        """Prueba crear una tarea con valores personalizados"""
        task_id = uuid4()
        custom_title = "Tarea personalizada"
        custom_description = "Descripción personalizada"
        custom_user_id = 999
        
        task = Task(
            task_id=task_id,
            title=custom_title,
            description=custom_description,
            user_id=custom_user_id
        )
        
        assert task.task_id == task_id
        assert task.title == custom_title
        assert task.description == custom_description
        assert task.user_id == custom_user_id
        assert task.status == TaskStatus.NEW
        assert task.completed_at is None


class TestTaskCompletion:
    """Pruebas para el comportamiento de completado de tareas"""
    
    @pytest.mark.unit
    def test_task_completion_behavior(self, sample_task):
        """Prueba que el método complete() funcione correctamente"""
        task = sample_task
        
        # Verificar estado inicial
        assert task.status == TaskStatus.NEW
        assert task.completed_at is None
        
        # Completar la tarea
        task.complete()
        
        # Verificar cambios
        assert task.status == TaskStatus.COMPLETED
        assert task.completed_at is not None
        assert isinstance(task.completed_at, datetime)
        assert task.completed_at.tzinfo == timezone.utc
    
    @pytest.mark.unit
    def test_task_completion_timestamp(self, sample_task, current_timestamp):
        """Prueba que el timestamp de completado se establezca correctamente"""
        task = sample_task
        
        # Completar la tarea
        task.complete()
        
        # Verificar que el timestamp es reciente (dentro de 1 segundo)
        time_diff = abs((task.completed_at - current_timestamp).total_seconds())
        assert time_diff < 1
    
    @pytest.mark.unit
    def test_task_double_completion(self, sample_task):
        """Prueba que completar una tarea ya completada no cause problemas"""
        task = sample_task
        
        # Primera completación
        task.complete()
        first_completion_time = task.completed_at
        
        # Segunda completación
        task.complete()
        second_completion_time = task.completed_at
        
        # Verificar que el estado sigue siendo COMPLETED
        assert task.status == TaskStatus.COMPLETED
        
        # Verificar que el timestamp no cambió (no se actualiza si ya está completada)
        assert second_completion_time == first_completion_time
    
    @pytest.mark.unit
    def test_task_completion_from_different_statuses(self):
        """Prueba completar tareas desde diferentes estados"""
        # Crear tarea y cambiar a diferentes estados
        task = Task(
            task_id=uuid4(),
            title="Tarea de prueba",
            description="Descripción",
            user_id=1
        )
        
        # Completar desde NEW
        task.complete()
        assert task.status == TaskStatus.COMPLETED
        
        # Cambiar manualmente a otros estados y completar
        task.status = TaskStatus.ASSIGNED
        task.complete()
        assert task.status == TaskStatus.COMPLETED
        
        task.status = TaskStatus.IN_PROGRESS
        task.complete()
        assert task.status == TaskStatus.COMPLETED


class TestTaskStatusTransitions:
    """Pruebas para las transiciones de estado de tareas"""
    
    @pytest.mark.unit
    def test_task_status_transitions(self, sample_task):
        """Prueba las transiciones de estado de una tarea"""
        task = sample_task
        
        # Estado inicial
        assert task.status == TaskStatus.NEW
        
        # Cambiar a ASSIGNED
        task.status = TaskStatus.ASSIGNED
        assert task.status == TaskStatus.ASSIGNED
        
        # Cambiar a IN_PROGRESS
        task.status = TaskStatus.IN_PROGRESS
        assert task.status == TaskStatus.IN_PROGRESS
        
        # Completar
        task.complete()
        assert task.status == TaskStatus.COMPLETED
    
    @pytest.mark.unit
    def test_task_status_enum_values(self, task_status_enum_values):
        """Prueba que todos los valores del enum TaskStatus sean correctos"""
        expected_values = ["NEW", "ASSIGNED", "IN_PROGRESS", "COMPLETED"]
        assert task_status_enum_values == expected_values
    
    @pytest.mark.unit
    def test_task_status_enum_comparison(self):
        """Prueba comparaciones de estados de tarea"""
        assert TaskStatus.NEW == "NEW"
        assert TaskStatus.COMPLETED == "COMPLETED"
        assert TaskStatus.NEW != TaskStatus.COMPLETED


class TestTaskProperties:
    """Pruebas para las propiedades de las tareas"""
    
    @pytest.mark.unit
    def test_task_properties_immutability(self, sample_task):
        """Prueba que las propiedades básicas no cambien después de completar"""
        task = sample_task
        
        # Guardar valores originales
        original_task_id = task.task_id
        original_title = task.title
        original_description = task.description
        original_user_id = task.user_id
        original_created_at = task.created_at
        
        # Completar la tarea
        task.complete()
        
        # Verificar que las propiedades básicas no cambiaron
        assert task.task_id == original_task_id
        assert task.title == original_title
        assert task.description == original_description
        assert task.user_id == original_user_id
        assert task.created_at == original_created_at
    
    @pytest.mark.unit
    def test_task_string_representation(self, sample_task):
        """Prueba la representación en string de una tarea"""
        task = sample_task
        
        # Verificar que la representación contiene información relevante
        task_str = str(task)
        assert "Task" in task_str
        # La representación por defecto de Python incluye la dirección de memoria
        assert "object at" in task_str
    
    @pytest.mark.unit
    def test_task_equality(self):
        """Prueba la igualdad entre tareas"""
        task1 = Task(
            task_id=uuid4(),
            title="Tarea 1",
            description="Descripción 1",
            user_id=1
        )
        
        task2 = Task(
            task_id=task1.task_id,  # Mismo ID
            title="Tarea 2",  # Diferente título
            description="Descripción 2",
            user_id=2
        )
        
        # Las tareas con el mismo ID deberían ser iguales
        assert task1.task_id == task2.task_id
        # Pero con diferentes propiedades
        assert task1.title != task2.title
        assert task1.user_id != task2.user_id


class TestTaskEdgeCases:
    """Pruebas para casos edge de las tareas"""
    
    @pytest.mark.unit
    def test_task_with_empty_strings(self):
        """Prueba crear una tarea con strings vacíos"""
        task = Task(
            task_id=uuid4(),
            title="",
            description="",
            user_id=1
        )
        
        assert task.title == ""
        assert task.description == ""
        assert task.status == TaskStatus.NEW
    
    @pytest.mark.unit
    def test_task_with_very_long_strings(self):
        """Prueba crear una tarea con strings muy largos"""
        long_title = "A" * 1000
        long_description = "B" * 2000
        
        task = Task(
            task_id=uuid4(),
            title=long_title,
            description=long_description,
            user_id=1
        )
        
        assert task.title == long_title
        assert task.description == long_description
        assert task.status == TaskStatus.NEW
    
    @pytest.mark.unit
    def test_task_with_negative_user_id(self):
        """Prueba crear una tarea con user_id negativo"""
        task = Task(
            task_id=uuid4(),
            title="Tarea con user_id negativo",
            description="Descripción",
            user_id=-1
        )
        
        assert task.user_id == -1
        assert task.status == TaskStatus.NEW 