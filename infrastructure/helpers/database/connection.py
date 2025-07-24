"""
Enterprise Database Connection Configuration

This module provides synchronous database connectivity with enterprise-grade
features including connection pooling, environment-based configuration,
and proper resource management.

Key Features:
- Synchronous SQLAlchemy (simplified for Lambda)
- Environment-based configuration
- Connection pooling with proper settings
- Transaction management ready
- Health check capabilities
"""

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session, declarative_base
from sqlalchemy.engine import Engine
from sqlalchemy.pool import QueuePool
from typing import Generator, Optional
import logging
from contextlib import contextmanager

from application.config.environment import settings, DatabaseConfig
from domain.constants.task_constants import TransactionConstants

# Configure logger
logger = logging.getLogger(__name__)

# Declarative base for all models
Base = declarative_base()


class DatabaseConnection:
    """
    Enterprise database connection manager

    Provides centralized database connection management with proper
    configuration, pooling, and health monitoring.
    """

    def __init__(self, config: DatabaseConfig):
        self._config = config
        self._engine: Optional[Engine] = None
        self._session_factory: Optional[sessionmaker] = None
        self._initialize_engine()

    def _initialize_engine(self) -> None:
        """Initialize SQLAlchemy engine with enterprise configuration"""
        try:
            logger.info(
                "Initializing database engine",
                extra={
                    "database_host": self._config.host,
                    "database_name": self._config.name,
                    "pool_size": self._config.pool_size,
                },
            )

            self._engine = create_engine(
                self._config.connection_url,
                # Connection pool configuration
                poolclass=QueuePool,
                pool_size=self._config.pool_size,
                max_overflow=self._config.max_overflow,
                pool_timeout=self._config.connection_timeout,
                pool_pre_ping=True,  # Verify connections before use
                pool_recycle=3600,  # Recycle connections every hour
                # Logging and debugging
                echo=self._config.echo,
                echo_pool=(
                    self._config.echo if settings.application.is_development else False
                ),
                # Connection arguments
                connect_args={
                    "connect_timeout": self._config.connection_timeout,
                    "read_timeout": self._config.connection_timeout,
                    "write_timeout": self._config.connection_timeout,
                },
            )

            # Create session factory
            self._session_factory = sessionmaker(
                bind=self._engine,
                autocommit=False,
                autoflush=False,
                expire_on_commit=False,
            )

            logger.info("Database engine initialized successfully")

        except Exception as e:
            logger.error(
                "Failed to initialize database engine",
                extra={
                    "error": str(e),
                    "database_url_masked": self._config.connection_url_masked,
                },
            )
            raise

    @property
    def engine(self) -> Engine:
        """Get SQLAlchemy engine"""
        if self._engine is None:
            raise RuntimeError("Database engine not initialized")
        return self._engine

    def create_session(self) -> Session:
        """
        Create a new database session

        Returns:
            Session: SQLAlchemy session instance

        Note:
            Remember to close the session when done or use within context manager
        """
        if self._session_factory is None:
            raise RuntimeError("Session factory not initialized")

        session = self._session_factory()
        self._configure_session(session)
        return session

    def _configure_session(self, session: Session) -> None:
        """Configure session with enterprise settings"""
        try:
            # Set transaction timeout
            session.execute(
                text(
                    f"SET SESSION innodb_lock_wait_timeout = {TransactionConstants.DEFAULT_TIMEOUT}"
                )
            )

            # Set isolation level (if not default)
            if TransactionConstants.READ_COMMITTED != "READ_COMMITTED":
                session.execute(
                    text(
                        f"SET SESSION TRANSACTION ISOLATION LEVEL {TransactionConstants.READ_COMMITTED}"
                    )
                )

        except Exception as e:
            logger.warning(
                "Failed to configure session settings", extra={"error": str(e)}
            )
            # Don't fail session creation for configuration issues

    @contextmanager
    def get_session(self) -> Generator[Session, None, None]:
        """
        Context manager for database sessions

        Automatically handles session lifecycle:
        - Creates session
        - Commits on success
        - Rolls back on exception
        - Closes session in finally block

        Usage:
            with db_connection.get_session() as session:
                # Use session here
                session.add(model)
                # Auto-commit on success
        """
        session = self.create_session()
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

    def health_check(self) -> bool:
        """
        Perform database health check

        Returns:
            bool: True if database is healthy, False otherwise
        """
        try:
            with self.get_session() as session:
                session.execute(text("SELECT 1"))
            return True
        except Exception as e:
            logger.error("Database health check failed", extra={"error": str(e)})
            return False

    def close(self) -> None:
        """Close database engine and all connections"""
        if self._engine:
            self._engine.dispose()
            logger.info("Database engine closed")


# Global database connection instance
# Initialized once at application startup
database_connection = DatabaseConnection(settings.database)


def get_database_session() -> Session:
    """
    Get a database session

    This is a convenience function for dependency injection.
    Use with caution - remember to close the session.

    Returns:
        Session: SQLAlchemy session
    """
    return database_connection.create_session()


def get_database_engine() -> Engine:
    """
    Get the database engine

    Returns:
        Engine: SQLAlchemy engine
    """
    return database_connection.engine
