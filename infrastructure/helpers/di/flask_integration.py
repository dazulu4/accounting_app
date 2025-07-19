"""
Flask DI Integration - Enterprise Edition

Simple and clean integration between Flask and the DI container.
Manages request-scoped services automatically.

Key Features:
- Automatic scope management per request
- Clean resource disposal
- Request context integration
- Error handling and logging
"""

from flask import Flask, g, request
from contextlib import contextmanager

from infrastructure.helpers.di.dependency_container import DependencyContainer
from infrastructure.helpers.di.service_registration import get_configured_container
from infrastructure.helpers.logger.logger_config import get_logger

logger = get_logger(__name__)


class FlaskDIIntegration:
    """
    Clean Flask DI integration
    
    Manages DI container lifecycle with Flask request handling.
    Simple implementation without over-engineering.
    """
    
    def __init__(self, app: Flask = None):
        self.container = get_configured_container()
        if app is not None:
            self.init_app(app)
    
    def init_app(self, app: Flask) -> None:
        """
        Initialize DI integration with Flask app
        
        Args:
            app: Flask application instance
        """
        app.before_request(self._before_request)
        app.teardown_request(self._teardown_request)
        
        # Store container in app context for easy access
        app.di_container = self.container
        
        logger.info("flask_di_integration_initialized")
    
    def _before_request(self):
        """Create DI scope for each request"""
        try:
            g.di_scope = self.container.create_scope()
            g.di_container = g.di_scope.__enter__()
            
            logger.debug(
                "request_di_scope_created",
                request_id=getattr(g, 'request_id', None),
                path=request.path
            )
            
        except Exception as e:
            logger.error(
                "failed_to_create_di_scope",
                error_type=type(e).__name__,
                error_message=str(e)
            )
            raise
    
    def _teardown_request(self, exception=None):
        """Clean up DI scope after request"""
        try:
            if hasattr(g, 'di_scope'):
                g.di_scope.__exit__(None, None, None)
                
                logger.debug(
                    "request_di_scope_disposed",
                    request_id=getattr(g, 'request_id', None),
                    exception_occurred=exception is not None
                )
                
        except Exception as e:
            logger.warning(
                "failed_to_dispose_di_scope",
                error_type=type(e).__name__,
                error_message=str(e)
            )


def resolve_service(service_type):
    """
    Resolve a service from the current request scope
    
    Args:
        service_type: Type of service to resolve
        
    Returns:
        Service instance
        
    Raises:
        RuntimeError: If called outside request context
    """
    if not hasattr(g, 'di_container'):
        raise RuntimeError("DI container not available. Make sure you're in a request context.")
    
    return g.di_container.resolve(service_type)


def get_current_container() -> DependencyContainer:
    """
    Get the current DI container
    
    Returns:
        Current DependencyContainer instance
        
    Raises:
        RuntimeError: If called outside request context
    """
    if hasattr(g, 'di_container'):
        return g.di_container
    
    # Fallback to global container if outside request context
    return get_configured_container() 