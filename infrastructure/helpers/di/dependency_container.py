"""
Dependency Injection Container - Enterprise Edition

Simple, clean, and professional DI container for enterprise applications.
Follows SOLID principles and clean architecture patterns.

Key Features:
- Service lifecycle management (Singleton, Scoped, Transient)
- Type-safe dependency resolution
- Scope management for request-level services
- Clean resource disposal
- Simple interface without over-engineering
"""

from typing import TypeVar, Type, Callable, Dict, Any, Optional
from contextlib import contextmanager
from enum import Enum
import inspect

from infrastructure.helpers.logger.logger_config import get_logger

T = TypeVar('T')
logger = get_logger(__name__)


class ServiceLifetime(Enum):
    """Service lifetime management options"""
    SINGLETON = "singleton"  # One instance for application lifetime
    SCOPED = "scoped"       # One instance per request/scope
    TRANSIENT = "transient"  # New instance every time


class ServiceDescriptor:
    """Describes how a service should be created and managed"""
    
    def __init__(self, interface: Type, factory: Callable, lifetime: ServiceLifetime):
        self.interface = interface
        self.factory = factory
        self.lifetime = lifetime


class DependencyContainer:
    """
    Professional DI container with lifecycle management
    
    Simple, clean implementation focusing on essential features:
    - Service registration with different lifetimes
    - Automatic dependency resolution
    - Request-scoped services
    - Clean resource management
    """
    
    def __init__(self):
        self._services: Dict[Type, ServiceDescriptor] = {}
        self._singletons: Dict[Type, Any] = {}
        self._scoped_instances: Dict[Type, Any] = {}
    
    def register_singleton(self, interface: Type[T], factory: Callable[[], T]) -> None:
        """
        Register a singleton service
        
        Args:
            interface: Service interface/type
            factory: Function that creates the service instance
        """
        self._services[interface] = ServiceDescriptor(interface, factory, ServiceLifetime.SINGLETON)
        logger.debug("service_registered", interface=interface.__name__, lifetime="singleton")
    
    def register_scoped(self, interface: Type[T], factory: Callable[[], T]) -> None:
        """
        Register a scoped service (one per request)
        
        Args:
            interface: Service interface/type
            factory: Function that creates the service instance
        """
        self._services[interface] = ServiceDescriptor(interface, factory, ServiceLifetime.SCOPED)
        logger.debug("service_registered", interface=interface.__name__, lifetime="scoped")
    
    def register_transient(self, interface: Type[T], factory: Callable[[], T]) -> None:
        """
        Register a transient service (new instance every time)
        
        Args:
            interface: Service interface/type
            factory: Function that creates the service instance
        """
        self._services[interface] = ServiceDescriptor(interface, factory, ServiceLifetime.TRANSIENT)
        logger.debug("service_registered", interface=interface.__name__, lifetime="transient")
    
    def resolve(self, interface: Type[T]) -> T:
        """
        Resolve a service instance
        
        Args:
            interface: Service interface/type to resolve
            
        Returns:
            Service instance
            
        Raises:
            ServiceNotRegisteredException: If service is not registered
        """
        if interface not in self._services:
            raise ServiceNotRegisteredException(f"Service {interface.__name__} is not registered")
        
        descriptor = self._services[interface]
        
        try:
            if descriptor.lifetime == ServiceLifetime.SINGLETON:
                return self._resolve_singleton(interface, descriptor)
            elif descriptor.lifetime == ServiceLifetime.SCOPED:
                return self._resolve_scoped(interface, descriptor)
            else:  # TRANSIENT
                return self._resolve_transient(descriptor)
                
        except Exception as e:
            logger.error(
                "service_resolution_failed",
                interface=interface.__name__,
                error_type=type(e).__name__,
                error_message=str(e)
            )
            raise ServiceResolutionException(f"Failed to resolve {interface.__name__}: {str(e)}") from e
    
    def _resolve_singleton(self, interface: Type[T], descriptor: ServiceDescriptor) -> T:
        """Resolve singleton service"""
        if interface not in self._singletons:
            self._singletons[interface] = descriptor.factory()
            logger.debug("singleton_created", interface=interface.__name__)
        return self._singletons[interface]
    
    def _resolve_scoped(self, interface: Type[T], descriptor: ServiceDescriptor) -> T:
        """Resolve scoped service"""
        if interface not in self._scoped_instances:
            self._scoped_instances[interface] = descriptor.factory()
            logger.debug("scoped_instance_created", interface=interface.__name__)
        return self._scoped_instances[interface]
    
    def _resolve_transient(self, descriptor: ServiceDescriptor) -> T:
        """Resolve transient service"""
        instance = descriptor.factory()
        logger.debug("transient_instance_created", interface=descriptor.interface.__name__)
        return instance
    
    @contextmanager
    def create_scope(self):
        """
        Create a new scope for scoped services
        
        Usage:
            with container.create_scope() as scoped_container:
                service = scoped_container.resolve(SomeService)
        """
        # Save current scoped instances
        original_scoped = self._scoped_instances.copy()
        self._scoped_instances.clear()
        
        logger.debug("dependency_scope_created")
        
        try:
            yield self
        finally:
            # Clean up scoped instances
            self._cleanup_scoped_instances()
            
            # Restore original scoped instances
            self._scoped_instances = original_scoped
            
            logger.debug("dependency_scope_disposed")
    
    def _cleanup_scoped_instances(self):
        """Clean up scoped instances that implement dispose methods"""
        for interface, instance in self._scoped_instances.items():
            if hasattr(instance, 'dispose'):
                try:
                    instance.dispose()
                    logger.debug("scoped_instance_disposed", interface=interface.__name__)
                except Exception as e:
                    logger.warning(
                        "scoped_instance_disposal_failed",
                        interface=interface.__name__,
                        error=str(e)
                    )
    
    def get_registered_services(self) -> Dict[str, str]:
        """
        Get list of registered services for debugging
        
        Returns:
            Dictionary mapping service names to their lifetimes
        """
        return {
            service.__name__: descriptor.lifetime.value
            for service, descriptor in self._services.items()
        }


class ServiceNotRegisteredException(Exception):
    """Raised when trying to resolve an unregistered service"""
    pass


class ServiceResolutionException(Exception):
    """Raised when service resolution fails"""
    pass


# Global container instance
_container = DependencyContainer()


def get_container() -> DependencyContainer:
    """
    Get the global DI container instance
    
    Returns:
        Global DependencyContainer instance
    """
    return _container 