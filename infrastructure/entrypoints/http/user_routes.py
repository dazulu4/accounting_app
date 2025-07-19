"""
User HTTP Routes - Enterprise Edition

This module provides HTTP endpoints for user management using Flask
with enterprise use cases, structured error handling, and sync operations.

Key Features:
- Enterprise use cases with sync operations
- Structured error handling and logging
- Pydantic validation for request/response
- Strategic logging at endpoint level
"""

from flask import Blueprint, jsonify, request
from typing import List

from infrastructure.entrypoints.events.mock_event_listener import on_user_deactivated_event, on_user_activated_event
from application.di_container import get_list_all_users_usecase
from domain.usecases.list_all_users_use_case import ListAllUsersUseCase

# Import Pydantic schemas
from application.schemas.user_schema import UserResponse, UserListResponse
from pydantic import ValidationError

# Import enterprise logging and error handling
from infrastructure.helpers.logger.logger_config import get_logger
from infrastructure.helpers.middleware.http_middleware import log_endpoint_access

# Configure logger
logger = get_logger(__name__)

# Create Blueprint
blueprint = Blueprint('users', __name__)


@blueprint.route("", methods=['GET'])
@log_endpoint_access('list_all_users')
def list_users():
    """
    List all users using enterprise use case
    
    Returns:
        JSON response with all users or error
    """
    try:
        # Get enterprise use case
        usecase = get_list_all_users_usecase()
        
        # Execute use case (sync)
        users_response = usecase.execute()
        
        # Convert to HTTP response schema
        response_users = [
            UserResponse.model_validate({
                "user_id": user.user_id,
                "name": user.name,
                "email": user.email,
                "status": user.status,
                "created_at": user.created_at.isoformat() if hasattr(user, 'created_at') and user.created_at else None
            })
            for user in users_response.users
        ]
        
        user_list_response = UserListResponse(
            users=response_users,
            total_count=len(response_users)
        )
        
        return jsonify(user_list_response.model_dump()), 200
        
    except Exception as e:
        # Let error handling middleware handle exceptions
        logger.error(
            "list_all_users_endpoint_error",
            error_type=type(e).__name__,
            error_message=str(e)
        )
        raise


@blueprint.route("/<int:user_id>/deactivate", methods=['PUT'])
@log_endpoint_access('deactivate_user')
def deactivate_user(user_id: int):
    """
    Deactivate a user and trigger event
    
    Args:
        user_id: ID of the user to deactivate
        
    Returns:
        JSON response with success message
    """
    try:
        # Trigger deactivation event
        on_user_deactivated_event(user_id)
        
        logger.info(
            "user_deactivated_successfully",
            user_id=user_id
        )
        
        return jsonify({
            "message": f"User {user_id} deactivated successfully",
            "user_id": user_id,
            "status": "deactivated"
        }), 200
        
    except Exception as e:
        # Let error handling middleware handle exceptions
        logger.error(
            "deactivate_user_endpoint_error",
            user_id=user_id,
            error_type=type(e).__name__,
            error_message=str(e)
        )
        raise


@blueprint.route("/<int:user_id>/activate", methods=['PUT'])
@log_endpoint_access('activate_user')
def activate_user(user_id: int):
    """
    Activate a user and trigger event
    
    Args:
        user_id: ID of the user to activate
        
    Returns:
        JSON response with success message
    """
    try:
        # Trigger activation event
        on_user_activated_event(user_id)
        
        logger.info(
            "user_activated_successfully",
            user_id=user_id
        )
        
        return jsonify({
            "message": f"User {user_id} activated successfully",
            "user_id": user_id,
            "status": "activated"
        }), 200
        
    except Exception as e:
        # Let error handling middleware handle exceptions
        logger.error(
            "activate_user_endpoint_error",
            user_id=user_id,
            error_type=type(e).__name__,
            error_message=str(e)
        )
        raise
