"""
Alembic Environment Configuration - Enterprise Edition

Environment-aware database migration configuration using enterprise
patterns with proper environment variable handling and logging.

Key Features:
- Environment variable configuration
- Enterprise database connection
- Structured logging integration
- Multi-environment support
- Proper error handling
- Auto-generation support with all models
"""

import os
from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool, create_engine
from alembic import context

# Import enterprise configuration and models
from application.config import settings
from infrastructure.helpers.logger.logger_config import get_logger

# Configure logger
logger = get_logger(__name__)

# Alembic configuration object
config = context.config

# Configure logging from alembic.ini if available
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Import all models for autogenerate support
# This ensures all models are included in migration detection
from infrastructure.driven_adapters.repositories.task_repository import TaskModel
from infrastructure.driven_adapters.repositories.base import Base

# Set target metadata for autogenerate
target_metadata = Base.metadata

logger.info("alembic_environment_initialized", tables_count=len(target_metadata.tables))


def get_database_url() -> str:
    """
    Get database URL from environment configuration
    
    Returns:
        Database connection URL
    """
    try:
        # Usar la configuración centralizada de la aplicación
        db_config = settings.database
        
        # Construir la URL de conexión
        database_url = (
            f"mysql+pymysql://{db_config.username}:{db_config.password}"
            f"@{db_config.host}:{db_config.port}/{db_config.name}"
        )
        
        logger.info(
            "database_url_configured",
            host=db_config.host,
            port=db_config.port,
            database=db_config.name,
            username=db_config.username
        )
        
        return database_url
        
    except Exception as e:
        logger.error(
            "failed_to_configure_database_url",
            error_type=type(e).__name__,
            error_message=str(e)
        )
        
        # Fallback to alembic.ini configuration
        fallback_url = config.get_main_option("sqlalchemy.url")
        if fallback_url:
            logger.warning("using_fallback_database_url_from_alembic_ini")
            return fallback_url
        
        raise RuntimeError("Unable to configure database URL") from e


def run_migrations_offline() -> None:
    """
    Run migrations in 'offline' mode
    
    This configures the context with just a URL and not an Engine.
    Useful for generating SQL scripts without database connection.
    """
    logger.info("running_migrations_offline")
    
    url = get_database_url()
    
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
        compare_server_default=True,
        render_as_batch=True  # For MySQL compatibility
    )

    with context.begin_transaction():
        logger.info("executing_offline_migrations")
        context.run_migrations()
        logger.info("offline_migrations_completed")


def run_migrations_online() -> None:
    """
    Run migrations in 'online' mode
    
    Creates an Engine and associates a connection with the context.
    This is the standard mode for running migrations.
    """
    logger.info("running_migrations_online")
    
    # Override sqlalchemy.url in configuration
    database_url = get_database_url()
    config.set_main_option("sqlalchemy.url", database_url)
    
    # Crear el motor con la configuración de la aplicación
    connectable = create_engine(
        database_url,
        poolclass=pool.NullPool,
        echo=settings.application.debug, # Usar el modo debug de la app
        pool_pre_ping=True,  # Verify connections before use
        pool_recycle=3600,   # Recycle connections after 1 hour
        connect_args={
            "charset": "utf8mb4",
            "use_unicode": True,
            "autocommit": False
        }
    )

    try:
        with connectable.connect() as connection:
            logger.info("database_connection_established")
            
            context.configure(
                connection=connection,
                target_metadata=target_metadata,
                compare_type=True,           # Compare column types
                compare_server_default=True, # Compare default values
                render_as_batch=True,        # For MySQL compatibility
                include_name=lambda name, type_, parent_names: True,  # Include all objects
                include_object=lambda object_, name, type_, reflected, compare_to: True
            )

            with context.begin_transaction():
                logger.info("executing_online_migrations")
                context.run_migrations()
                logger.info("online_migrations_completed")
                
    except Exception as e:
        logger.error(
            "migration_execution_failed",
            error_type=type(e).__name__,
            error_message=str(e)
        )
        raise
    finally:
        connectable.dispose()
        logger.info("database_connection_disposed")


# Execute migrations based on mode
if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
