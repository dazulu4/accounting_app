"""
Task Gateway Interface - Domain Layer

This module defines the abstract interface for task data operations
following the Gateway pattern from Clean Architecture. This interface
allows the domain layer to depend on abstractions rather than concrete
implementations.

Key Features:
- Abstract interface for dependency inversion
- Enterprise naming conventions  
- Comprehensive CRUD operations
- Clean separation between domain and infrastructure
"""

from abc import ABC, abstractmethod
from typing import List, Optional
from uuid import UUID

from domain.entities.task_entity import TaskEntity
from domain.enums.task_status_enum import TaskStatusEnum


class TaskGateway(ABC):
    """
    Abstract gateway interface for task data operations
    
    This interface defines all the data operations needed by the domain layer
    for task management. Concrete implementations in the infrastructure layer
    will provide the actual data persistence logic.
    """
    
    @abstractmethod
    def save_task(self, task: TaskEntity) -> None:
        """
        Save or update a task
        
        Args:
            task: TaskEntity to save
            
        Raises:
            Exception: If save operation fails
        """
        pass
    
    @abstractmethod
    def find_task_by_id(self, task_id: UUID) -> Optional[TaskEntity]:
        """
        Find a task by its unique identifier
        
        Args:
            task_id: UUID of the task to find
            
        Returns:
            TaskEntity if found, None otherwise
            
        Raises:
            Exception: If database operation fails
        """
        pass
    
    @abstractmethod
    def find_tasks_by_user_id(self, user_id: int) -> List[TaskEntity]:
        """
        Find all tasks assigned to a specific user
        
        Args:
            user_id: ID of the user
            
        Returns:
            List of TaskEntity objects ordered by creation date (newest first)
            
        Raises:
            Exception: If database operation fails
        """
        pass
    
    @abstractmethod
    def find_tasks_by_status(self, status: TaskStatusEnum) -> List[TaskEntity]:
        """
        Find all tasks with a specific status
        
        Args:
            status: TaskStatusEnum to filter by
            
        Returns:
            List of TaskEntity objects ordered by creation date (newest first)
            
        Raises:
            Exception: If database operation fails
        """
        pass
    
    @abstractmethod
    def delete_task(self, task_id: UUID) -> bool:
        """
        Delete a task from the system
        
        Args:
            task_id: UUID of the task to delete
            
        Returns:
            bool: True if task was deleted, False if not found
            
        Raises:
            Exception: If database operation fails
        """
        pass
    
    @abstractmethod
    def count_tasks_by_user(self, user_id: int) -> int:
        """
        Count the number of active tasks for a user
        
        This is useful for implementing business rules like maximum tasks per user.
        
        Args:
            user_id: ID of the user
            
        Returns:
            int: Number of active (non-terminal) tasks for the user
            
        Raises:
            Exception: If database operation fails
        """
        pass
