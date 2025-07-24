"""
Database Base Configuration - Legacy Compatibility

This module provides backward compatibility by re-exporting the enterprise
database configuration from helpers. This maintains existing imports while
using the centralized enterprise configuration.

Note: This is a compatibility layer. New code should import directly from
infrastructure.helpers.database.connection
"""

# Re-export enterprise configuration for backward compatibility
from infrastructure.helpers.database.connection import (
    Base,
    DatabaseConnection,
    database_connection,
    get_database_session,
)

# Legacy compatibility aliases
engine = database_connection._engine
SessionLocal = database_connection.create_session

__all__ = [
    "Base",
    "engine",
    "SessionLocal",
    "DatabaseConnection",
    "database_connection",
    "get_database_session",
]
