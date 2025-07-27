"""
Alembic Environment Configuration

Database migration configuration with environment variable support
and proper error handling for the Task Manager application.
"""

from logging.config import fileConfig

from alembic import context
from sqlalchemy import create_engine, pool

# Import configuration and models
from application.config.environment import settings

# Alembic configuration object
config = context.config

# Configure logging from alembic.ini if available
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Import models for autogenerate support
from infrastructure.driven_adapters.repositories.base import Base

# Set target metadata for autogenerate
target_metadata = Base.metadata

# Import all models to ensure they're registered
try:
    from infrastructure.driven_adapters.repositories.task_repository import TaskModel
except ImportError:
    pass  # Models may not be available during initial setup


def get_database_url() -> str:
    """Get database URL from configuration with fallback."""
    try:
        return settings.get_database_url()
    except Exception:
        # Fallback to alembic.ini configuration
        fallback_url = config.get_main_option("sqlalchemy.url")
        if fallback_url:
            return fallback_url
        raise RuntimeError("Unable to configure database URL")


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode (generate SQL without database connection)."""
    url = get_database_url()

    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
        compare_server_default=True,
        render_as_batch=True,  # For MySQL compatibility
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode (with database connection)."""
    database_url = get_database_url()
    config.set_main_option("sqlalchemy.url", database_url)

    # Crear el motor con la configuración de la aplicación
    connectable = create_engine(
        database_url,
        poolclass=pool.NullPool,
        echo=settings.application.debug,  # Usar el modo debug de la app
        pool_pre_ping=True,  # Verify connections before use
        pool_recycle=3600,  # Recycle connections after 1 hour
        connect_args={
            "charset": "utf8mb4",
            "use_unicode": True,
            "autocommit": False,
        },
    )

    try:
        with connectable.connect() as connection:
            context.configure(
                connection=connection,
                target_metadata=target_metadata,
                compare_type=True,
                compare_server_default=True,
                render_as_batch=True,  # For MySQL compatibility
            )

            with context.begin_transaction():
                context.run_migrations()
    finally:
        connectable.dispose()


# Execute migrations based on mode
if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
