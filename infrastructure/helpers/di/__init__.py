"""
Dependency Injection Package

Simple, clean DI container for enterprise applications.

Components:
- dependency_container.py: Core DI container implementation
- service_registration.py: Service registration configuration
- flask_integration.py: Flask application integration
"""

from .dependency_container import (
    DependencyContainer,
    ServiceLifetime,
    ServiceNotRegisteredException,
    ServiceResolutionException,
    get_container
)
from .service_registration import (
    configure_services,
    get_configured_container
)
from .flask_integration import (
    FlaskDIIntegration,
    resolve_service,
    get_current_container
)

__all__ = [
    'DependencyContainer',
    'ServiceLifetime',
    'ServiceNotRegisteredException',
    'ServiceResolutionException',
    'get_container',
    'configure_services',
    'get_configured_container',
    'FlaskDIIntegration',
    'resolve_service',
    'get_current_container'
] 