"""
Validation Utilities - Infrastructure Layer

This module provides reusable validation functions for common data types
and formats used throughout the application.
"""

from typing import Tuple, Union
from uuid import UUID

from flask import jsonify
from infrastructure.helpers.errors.error_handlers import HTTPErrorHandler


def validate_uuid(uuid_str: str) -> Tuple[Union[UUID, None], Union[tuple, None]]:
    """
    Validate a string as a UUID and return the UUID object or an error response.
    
    Args:
        uuid_str: The string to validate as a UUID
        
    Returns:
        Tuple containing:
        - UUID object if valid, None if invalid
        - Error response tuple (response_dict, status_code) if invalid, None if valid
    """
    try:
        # Intentar convertir directamente a UUID
        uuid_obj = UUID(uuid_str)
        return uuid_obj, None
    except ValueError:
        # Si falla la conversión, devolver error
        error = ValueError(f"Invalid UUID format: {uuid_str}")
        response_data, status_code = HTTPErrorHandler.handle_exception(error)
        return None, (response_data, status_code) 