"""
Task Repository - Infrastructure Layer

This module provides data persistence for Task entities using SQLAlchemy ORM
with enterprise patterns including proper mapping, error handling, and
synchronous operations optimized for AWS Lambda.

Key Features:
- Synchronous SQLAlchemy operations
- Entity-Model mapping with validation
- Enterprise naming conventions
- Proper error handling and logging
- Repository pattern implementation
"""

from typing import List, Optional
from uuid import UUID
from sqlalchemy import String, DateTime, Integer, Text, Index
from sqlalchemy.orm import Mapped, mapped_column, Session
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from datetime import datetime
import logging

from infrastructure.helpers.database.connection import Base
from domain.entities.task_entity import TaskEntity, TaskDomainException
from domain.enums.task_status_enum import TaskStatusEnum, TaskPriorityEnum
from domain.gateways.task_gateway import TaskGateway
from domain.constants.task_constants import TaskDatabaseConstants

# Configure logger
logger = logging.getLogger(__name__)


class TaskModel(Base):
    """
    SQLAlchemy model for Task entity
    
    This model represents the database schema for tasks with proper
    indexing, constraints, and enterprise naming conventions.
    """
    
    __tablename__ = TaskDatabaseConstants.TABLE_NAME
    
    # Primary key
    task_id: Mapped[UUID] = mapped_column(
        primary_key=True,
        name=TaskDatabaseConstants.TASK_ID_COLUMN
    )
    
    # Required fields
    title: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
        name=TaskDatabaseConstants.TITLE_COLUMN
    )
    
    description: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        name=TaskDatabaseConstants.DESCRIPTION_COLUMN
    )
    
    user_id: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        name=TaskDatabaseConstants.USER_ID_COLUMN
    )
    
    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        name=TaskDatabaseConstants.STATUS_COLUMN
    )
    
    priority: Mapped[str] = mapped_column(
        String(10),
        nullable=False,
        default=TaskPriorityEnum.MEDIUM.value
    )
    
    # Timestamp fields
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        name=TaskDatabaseConstants.CREATED_AT_COLUMN
    )
    
    completed_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime,
        nullable=True,
        name=TaskDatabaseConstants.COMPLETED_AT_COLUMN
    )
    
    updated_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime,
        nullable=True,
        name=TaskDatabaseConstants.UPDATED_AT_COLUMN
    )
    
    # Database indexes for performance
    __table_args__ = (
        Index(TaskDatabaseConstants.USER_ID_INDEX, user_id),
        Index(TaskDatabaseConstants.STATUS_INDEX, status),
        Index(TaskDatabaseConstants.CREATED_AT_INDEX, created_at),
    )


class TaskModelMapper:
    """
    Mapper class for converting between TaskEntity and TaskModel
    
    This class encapsulates the mapping logic between domain entities
    and database models, ensuring clean separation of concerns.
    """
    
    @staticmethod
    def entity_to_model(entity: TaskEntity) -> TaskModel:
        """
        Convert TaskEntity to TaskModel for database persistence
        
        Args:
            entity: TaskEntity to convert
            
        Returns:
            TaskModel: Database model instance
        """
        return TaskModel(
            task_id=entity.task_id,
            title=entity.title,
            description=entity.description,
            user_id=entity.user_id,
            status=entity.status.value,
            priority=entity.priority.value,
            created_at=entity.created_at,
            completed_at=entity.completed_at,
            updated_at=entity.updated_at
        )
    
    @staticmethod
    def model_to_entity(model: TaskModel) -> TaskEntity:
        """
        Convert TaskModel to TaskEntity for domain operations
        
        Args:
            model: TaskModel from database
            
        Returns:
            TaskEntity: Domain entity instance
            
        Raises:
            TaskDomainException: If model data is invalid
        """
        try:
            # Convert enum values with validation
            status = TaskStatusEnum(model.status)
            priority = TaskPriorityEnum(model.priority)
            
            return TaskEntity(
                task_id=model.task_id,
                title=model.title,
                description=model.description,
                user_id=model.user_id,
                status=status,
                priority=priority,
                created_at=model.created_at,
                completed_at=model.completed_at,
                updated_at=model.updated_at
            )
        except (ValueError, TypeError) as e:
            logger.error(
                "Failed to convert TaskModel to TaskEntity",
                extra={
                    "task_id": str(model.task_id),
                    "error": str(e)
                }
            )
            raise TaskDomainException(f"Invalid task data in database: {e}")


class TaskRepository(TaskGateway):
    """
    Repository implementation for Task entities
    
    This class implements the TaskGateway interface providing data persistence
    operations for Task entities using SQLAlchemy with enterprise patterns.
    """
    
    def __init__(self, session: Session):
        """
        Initialize repository with database session
        
        Args:
            session: SQLAlchemy session for database operations
        """
        self._session = session
        self._mapper = TaskModelMapper()
    
    def save_task(self, task: TaskEntity) -> None:
        """
        Save or update a task in the database
        
        Args:
            task: TaskEntity to save
            
        Raises:
            TaskDomainException: If save operation fails
        """
        try:
            model = self._mapper.entity_to_model(task)
            
            # Use merge for upsert behavior (insert or update)
            self._session.merge(model)
            self._session.commit()
            
            logger.info(
                "Task saved successfully",
                extra={
                    "task_id": str(task.task_id),
                    "title": task.title,
                    "status": task.status.value
                }
            )
            
        except IntegrityError as e:
            self._session.rollback()
            logger.error(
                "Database integrity error saving task",
                extra={
                    "task_id": str(task.task_id),
                    "error": str(e)
                }
            )
            raise TaskDomainException(f"Failed to save task due to data integrity: {e}")
        
        except SQLAlchemyError as e:
            self._session.rollback()
            logger.error(
                "Database error saving task",
                extra={
                    "task_id": str(task.task_id),
                    "error": str(e)
                }
            )
            raise TaskDomainException(f"Database error saving task: {e}")
    
    def find_task_by_id(self, task_id: UUID) -> Optional[TaskEntity]:
        """
        Find a task by its ID
        
        Args:
            task_id: UUID of the task to find
            
        Returns:
            TaskEntity if found, None otherwise
            
        Raises:
            TaskDomainException: If database error occurs
        """
        try:
            model = self._session.get(TaskModel, task_id)
            
            if model is None:
                logger.debug(
                    "Task not found",
                    extra={"task_id": str(task_id)}
                )
                return None
            
            return self._mapper.model_to_entity(model)
            
        except SQLAlchemyError as e:
            logger.error(
                "Database error finding task",
                extra={
                    "task_id": str(task_id),
                    "error": str(e)
                }
            )
            raise TaskDomainException(f"Database error finding task: {e}")
    
    def find_tasks_by_user_id(self, user_id: int) -> List[TaskEntity]:
        """
        Find all tasks assigned to a specific user
        
        Args:
            user_id: ID of the user
            
        Returns:
            List of TaskEntity objects
            
        Raises:
            TaskDomainException: If database error occurs
        """
        try:
            models = (
                self._session.query(TaskModel)
                .filter(TaskModel.user_id == user_id)
                .order_by(TaskModel.created_at.desc())
                .all()
            )
            
            tasks = [self._mapper.model_to_entity(model) for model in models]
            
            logger.debug(
                "Found tasks for user",
                extra={
                    "user_id": user_id,
                    "task_count": len(tasks)
                }
            )
            
            return tasks
            
        except SQLAlchemyError as e:
            logger.error(
                "Database error finding tasks by user",
                extra={
                    "user_id": user_id,
                    "error": str(e)
                }
            )
            raise TaskDomainException(f"Database error finding tasks: {e}")
    
    def find_tasks_by_status(self, status: TaskStatusEnum) -> List[TaskEntity]:
        """
        Find all tasks with a specific status
        
        Args:
            status: TaskStatusEnum to filter by
            
        Returns:
            List of TaskEntity objects
            
        Raises:
            TaskDomainException: If database error occurs
        """
        try:
            models = (
                self._session.query(TaskModel)
                .filter(TaskModel.status == status.value)
                .order_by(TaskModel.created_at.desc())
                .all()
            )
            
            tasks = [self._mapper.model_to_entity(model) for model in models]
            
            logger.debug(
                "Found tasks by status",
                extra={
                    "status": status.value,
                    "task_count": len(tasks)
                }
            )
            
            return tasks
            
        except SQLAlchemyError as e:
            logger.error(
                "Database error finding tasks by status",
                extra={
                    "status": status.value,
                    "error": str(e)
                }
            )
            raise TaskDomainException(f"Database error finding tasks: {e}")
    
    def delete_task(self, task_id: UUID) -> bool:
        """
        Delete a task from the database
        
        Args:
            task_id: UUID of the task to delete
            
        Returns:
            bool: True if task was deleted, False if not found
            
        Raises:
            TaskDomainException: If database error occurs
        """
        try:
            model = self._session.get(TaskModel, task_id)
            
            if model is None:
                logger.debug(
                    "Task not found for deletion",
                    extra={"task_id": str(task_id)}
                )
                return False
            
            self._session.delete(model)
            self._session.commit()
            
            logger.info(
                "Task deleted successfully",
                extra={"task_id": str(task_id)}
            )
            
            return True
            
        except SQLAlchemyError as e:
            self._session.rollback()
            logger.error(
                "Database error deleting task",
                extra={
                    "task_id": str(task_id),
                    "error": str(e)
                }
            )
            raise TaskDomainException(f"Database error deleting task: {e}")
    
    def count_tasks_by_user(self, user_id: int) -> int:
        """
        Count the number of active tasks for a user
        
        Args:
            user_id: ID of the user
            
        Returns:
            int: Number of active tasks
            
        Raises:
            TaskDomainException: If database error occurs
        """
        try:
            active_statuses = [status.value for status in TaskStatusEnum.get_active_statuses()]
            
            count = (
                self._session.query(TaskModel)
                .filter(TaskModel.user_id == user_id)
                .filter(TaskModel.status.in_(active_statuses))
                .count()
            )
            
            logger.debug(
                "Counted active tasks for user",
                extra={
                    "user_id": user_id,
                    "active_task_count": count
                }
            )
            
            return count
            
        except SQLAlchemyError as e:
            logger.error(
                "Database error counting tasks",
                extra={
                    "user_id": user_id,
                    "error": str(e)
                }
            )
            raise TaskDomainException(f"Database error counting tasks: {e}") 