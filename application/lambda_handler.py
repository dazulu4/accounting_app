"""
AWS Lambda Handler - Enterprise Edition

Professional Lambda handler for Flask application with enterprise features:
- Structured logging with context
- Error handling and monitoring
- Performance tracking
- Clean integration with AWS services
- Request/response optimization

Key Features:
- Enterprise logging with structured output
- Proper error handling and status codes
- Performance monitoring
- AWS context integration
- Clean code following best practices
"""

import json
import time
from typing import Dict, Any, Optional
from application.main import create_app
from application.config import settings
from infrastructure.helpers.logger.logger_config import get_logger

# Initialize enterprise logger
logger = get_logger(__name__)

# Create Flask application (cached for performance)
app = create_app()


def handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Enterprise Lambda handler for API Gateway events
    
    Args:
        event: API Gateway proxy event
        context: Lambda runtime context
        
    Returns:
        API Gateway proxy response
    """
    start_time = time.time()
    request_id = context.aws_request_id if context else "unknown"
    
    # Initialize request context
    logger.info(
        "lambda_request_started",
        request_id=request_id,
        function_name=context.function_name if context else "unknown",
        http_method=event.get('httpMethod'),
        path=event.get('path'),
        source_ip=_get_source_ip(event)
    )
    
    try:
        # Process request
        response = _process_request(event, context)
        
        # Log successful completion
        duration = round((time.time() - start_time) * 1000, 2)
        logger.info(
            "lambda_request_completed",
            request_id=request_id,
            status_code=response.get('statusCode'),
            duration_ms=duration
        )
        
        return response
        
    except Exception as e:
        # Log error
        duration = round((time.time() - start_time) * 1000, 2)
        logger.error(
            "lambda_request_failed",
            request_id=request_id,
            error_type=type(e).__name__,
            error_message=str(e),
            duration_ms=duration
        )
        
        # Return error response
        return _create_error_response(e, request_id)


def _process_request(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Process the API Gateway event with Flask application
    
    Args:
        event: API Gateway proxy event
        context: Lambda runtime context
        
    Returns:
        API Gateway proxy response
    """
    # Extract request information
    http_method = event.get('httpMethod', 'GET')
    path = event.get('path', '/')
    headers = event.get('headers', {})
    query_string = event.get('queryStringParameters') or {}
    body = event.get('body', '')
    is_base64_encoded = event.get('isBase64Encoded', False)
    
    # Convert query parameters to query string
    query_string_parts = []
    for key, value in query_string.items():
        if value is not None:
            query_string_parts.append(f"{key}={value}")
    query_string_str = "&".join(query_string_parts)
    
    # Add Lambda context to headers for debugging
    if context:
        headers['X-Lambda-Request-Id'] = context.aws_request_id
        headers['X-Lambda-Function-Name'] = context.function_name
    
    # Process request with Flask
    with app.test_request_context(
        path=path,
        method=http_method,
        headers=list(headers.items()),
        query_string=query_string_str,
        data=body if not is_base64_encoded else None
    ):
        try:
            # Execute Flask application
            flask_response = app.full_dispatch_request()
            
            # Convert Flask response to API Gateway format
            return _flask_to_api_gateway_response(flask_response)
            
        except Exception as e:
            logger.error(
                "flask_application_error",
                error_type=type(e).__name__,
                error_message=str(e),
                path=path,
                method=http_method
            )
            raise


def _flask_to_api_gateway_response(flask_response) -> Dict[str, Any]:
    """
    Convert Flask response to API Gateway proxy response format
    
    Args:
        flask_response: Flask response object
        
    Returns:
        API Gateway proxy response
    """
    # Extract response data
    status_code = flask_response.status_code
    headers = dict(flask_response.headers)
    body = flask_response.get_data(as_text=True)
    
    # Ensure CORS headers are present
    headers.update({
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'GET,POST,PUT,DELETE,OPTIONS,PATCH',
        'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token,X-Request-ID',
        'Content-Type': headers.get('Content-Type', 'application/json')
    })
    
    return {
        'statusCode': status_code,
        'headers': headers,
        'body': body,
        'isBase64Encoded': False
    }


def _create_error_response(error: Exception, request_id: str) -> Dict[str, Any]:
    """
    Create standardized error response for Lambda failures
    
    Args:
        error: Exception that occurred
        request_id: Lambda request ID for tracing
        
    Returns:
        API Gateway error response
    """
    # Determine status code based on error type
    if isinstance(error, (ValueError, TypeError)):
        status_code = 400
        error_type = "BAD_REQUEST"
    elif isinstance(error, PermissionError):
        status_code = 403
        error_type = "FORBIDDEN"
    elif isinstance(error, FileNotFoundError):
        status_code = 404
        error_type = "NOT_FOUND"
    elif isinstance(error, TimeoutError):
        status_code = 408
        error_type = "REQUEST_TIMEOUT"
    else:
        status_code = 500
        error_type = "INTERNAL_SERVER_ERROR"
    
    # Create error response body
    error_body = {
        "error": {
            "type": error_type,
            "message": "An internal server error occurred" if status_code >= 500 else str(error),
            "request_id": request_id,
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S.%fZ")
        }
    }
    
    # Include technical details in non-production environments
    if settings.application.environment != "production":
        error_body["error"]["technical_details"] = {
            "exception_type": type(error).__name__,
            "exception_message": str(error)
        }
    
    return {
        'statusCode': status_code,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'GET,POST,PUT,DELETE,OPTIONS,PATCH',
            'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token,X-Request-ID',
            'X-Request-ID': request_id
        },
        'body': json.dumps(error_body),
        'isBase64Encoded': False
    }


def _get_source_ip(event: Dict[str, Any]) -> Optional[str]:
    """
    Extract source IP from API Gateway event
    
    Args:
        event: API Gateway proxy event
        
    Returns:
        Source IP address or None
    """
    request_context = event.get('requestContext', {})
    identity = request_context.get('identity', {})
    return identity.get('sourceIp') 