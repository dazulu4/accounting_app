"""
Unit of Work Pattern - Infrastructure Layer

This module implements the Unit of Work pattern for managing database transactions
with enterprise-grade features including automatic rollback, timeout management,
and proper resource cleanup.

Key Features:
- Automatic transaction management (commit/rollback)
- Session lifecycle management
- Timeout and retry policies
- Context manager support
- Repository access through single session
- ACID compliance
"""

from typing import Optional, Generator, Type, TypeVar
from contextlib import contextmanager
import logging
from time import sleep
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError, TimeoutError, DisconnectionError
from sqlalchemy import text

from infrastructure.helpers.database.connection import database_connection
from domain.constants.task_constants import TransactionConstants
from domain.entities.task_entity import TaskDomainException

# Configure logger
logger = logging.getLogger(__name__)

T = TypeVar('T')


class UnitOfWorkException(Exception):
    """Base exception for Unit of Work operations"""
    pass


class TransactionTimeoutException(UnitOfWorkException):
    """Raised when transaction exceeds timeout"""
    pass


class TransactionRetryExhaustedException(UnitOfWorkException):
    """Raised when all retry attempts are exhausted"""
    pass


class UnitOfWork:
    """
    Unit of Work implementation for managing database transactions
    
    This class provides a single entry point for all repository operations
    within a transaction boundary. It ensures ACID properties and proper
    resource management.
    
    Usage:
        # Context manager (recommended)
        with UnitOfWork() as uow:
            task = TaskEntity.create_new_task("Test", "Description", 1)
            uow.task_repository.save_task(task)
            # Auto-commit on success, auto-rollback on exception
        
        # Manual management
        uow = UnitOfWork()
        uow.begin()
        try:
            uow.task_repository.save_task(task)
            uow.commit()
        except Exception:
            uow.rollback()
        finally:
            uow.close()
    """
    
    def __init__(
        self, 
        timeout: int = TransactionConstants.DEFAULT_TIMEOUT,
        max_retries: int = TransactionConstants.MAX_RETRY_ATTEMPTS
    ):
        """
        Initialize Unit of Work
        
        Args:
            timeout: Transaction timeout in seconds
            max_retries: Maximum number of retry attempts
        """
        self._session: Optional[Session] = None
        self._timeout = timeout
        self._max_retries = max_retries
        self._is_active = False
        
        # Repository instances (lazy-loaded)
        self._task_repository: Optional[TaskRepository] = None
    
    def begin(self) -> None:
        """
        Begin a new transaction
        
        Raises:
            UnitOfWorkException: If transaction is already active
        """
        if self._is_active:
            raise UnitOfWorkException("Transaction is already active")
        
        try:
            self._session = database_connection.create_session()
            self._configure_transaction()
            self._is_active = True
            
            logger.debug(
                "Transaction started",
                extra={
                    "timeout": self._timeout,
                    "session_id": id(self._session)
                }
            )
            
        except Exception as e:
            logger.error(
                "Failed to start transaction",
                extra={"error": str(e)}
            )
            if self._session:
                self._session.close()
                self._session = None
            raise UnitOfWorkException(f"Failed to start transaction: {e}")
    
    def _configure_transaction(self) -> None:
        """Configure transaction-specific settings"""
        if not self._session:
            return
        
        try:
            # Set transaction timeout
            self._session.execute(
                text(f"SET SESSION innodb_lock_wait_timeout = {self._timeout}")
            )
            
            # Set isolation level
            self._session.execute(
                text(f"SET SESSION TRANSACTION ISOLATION LEVEL {TransactionConstants.READ_COMMITTED}")
            )
            
        except Exception as e:
            logger.warning(
                "Failed to configure transaction settings",
                extra={"error": str(e)}
            )
            # Don't fail transaction start for configuration issues
    
    def commit(self) -> None:
        """
        Commit the current transaction
        
        Raises:
            UnitOfWorkException: If no active transaction or commit fails
        """
        if not self._is_active or not self._session:
            raise UnitOfWorkException("No active transaction to commit")
        
        try:
            self._session.commit()
            logger.debug(
                "Transaction committed successfully",
                extra={"session_id": id(self._session)}
            )
            
        except Exception as e:
            logger.error(
                "Failed to commit transaction",
                extra={
                    "error": str(e),
                    "session_id": id(self._session)
                }
            )
            # Attempt rollback on commit failure
            try:
                self._session.rollback()
            except Exception:
                pass  # Ignore rollback errors during commit failure
            
            raise UnitOfWorkException(f"Failed to commit transaction: {e}")
    
    def rollback(self) -> None:
        """
        Rollback the current transaction
        
        Raises:
            UnitOfWorkException: If no active transaction
        """
        if not self._is_active or not self._session:
            raise UnitOfWorkException("No active transaction to rollback")
        
        try:
            self._session.rollback()
            logger.debug(
                "Transaction rolled back",
                extra={"session_id": id(self._session)}
            )
            
        except Exception as e:
            logger.error(
                "Failed to rollback transaction",
                extra={
                    "error": str(e),
                    "session_id": id(self._session)
                }
            )
            raise UnitOfWorkException(f"Failed to rollback transaction: {e}")
    
    def close(self) -> None:
        """Close the session and cleanup resources"""
        if self._session:
            try:
                self._session.close()
                logger.debug(
                    "Session closed",
                    extra={"session_id": id(self._session)}
                )
            except Exception as e:
                logger.warning(
                    "Error closing session",
                    extra={"error": str(e)}
                )
            finally:
                self._session = None
                self._is_active = False
                # Clear repository instances
                self._task_repository = None
    
    @property
    def task_repository(self):
        """
        Get task repository for current transaction
        
        Returns:
            TaskRepository: Repository instance bound to current session
            
        Raises:
            UnitOfWorkException: If no active transaction
        """
        if not self._is_active or not self._session:
            raise UnitOfWorkException("No active transaction")
        
        if self._task_repository is None:
            from infrastructure.driven_adapters.repositories.task_repository import TaskRepository
            self._task_repository = TaskRepository(self._session)
        
        return self._task_repository
    
    def __enter__(self) -> 'UnitOfWork':
        """Context manager entry"""
        self.begin()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """
        Context manager exit with automatic commit/rollback
        
        Args:
            exc_type: Exception type (None if no exception)
            exc_val: Exception value
            exc_tb: Exception traceback
        """
        try:
            if exc_type is None:
                # No exception occurred, commit the transaction
                self.commit()
            else:
                # Exception occurred, rollback the transaction
                logger.info(
                    "Rolling back transaction due to exception",
                    extra={
                        "exception_type": exc_type.__name__ if exc_type else None,
                        "exception_message": str(exc_val) if exc_val else None
                    }
                )
                self.rollback()
        finally:
            self.close()
    
    def execute_with_retry(self, operation, *args, **kwargs):
        """
        Execute an operation with retry logic for transient failures
        
        Args:
            operation: Function to execute
            *args: Positional arguments for the operation
            **kwargs: Keyword arguments for the operation
            
        Returns:
            Result of the operation
            
        Raises:
            TransactionRetryExhaustedException: If all retries are exhausted
        """
        last_exception = None
        
        for attempt in range(self._max_retries + 1):
            try:
                return operation(*args, **kwargs)
                
            except (TimeoutError, DisconnectionError) as e:
                last_exception = e
                logger.warning(
                    "Transient error in transaction, retrying",
                    extra={
                        "attempt": attempt + 1,
                        "max_retries": self._max_retries,
                        "error": str(e)
                    }
                )
                
                if attempt < self._max_retries:
                    # Wait before retry with exponential backoff
                    wait_time = TransactionConstants.RETRY_DELAY_SECONDS * (
                        TransactionConstants.BACKOFF_MULTIPLIER ** attempt
                    )
                    sleep(wait_time)
                    
                    # Reset session for retry
                    try:
                        self.rollback()
                        self.close()
                        self.begin()
                    except Exception:
                        pass  # Ignore errors during retry setup
                
            except Exception as e:
                # Non-transient error, don't retry
                logger.error(
                    "Non-transient error in transaction",
                    extra={"error": str(e)}
                )
                raise
        
        # All retries exhausted
        logger.error(
            "All retry attempts exhausted",
            extra={
                "attempts": self._max_retries + 1,
                "last_error": str(last_exception)
            }
        )
        raise TransactionRetryExhaustedException(
            f"Operation failed after {self._max_retries + 1} attempts: {last_exception}"
        )


@contextmanager
def create_unit_of_work(
    timeout: int = TransactionConstants.DEFAULT_TIMEOUT,
    max_retries: int = TransactionConstants.MAX_RETRY_ATTEMPTS
) -> Generator[UnitOfWork, None, None]:
    """
    Context manager factory for Unit of Work
    
    Args:
        timeout: Transaction timeout in seconds
        max_retries: Maximum retry attempts
        
    Yields:
        UnitOfWork: Configured Unit of Work instance
        
    Usage:
        with create_unit_of_work(timeout=60) as uow:
            uow.task_repository.save_task(task)
    """
    uow = UnitOfWork(timeout=timeout, max_retries=max_retries)
    with uow:
        yield uow 