"""
Flask Application Entry Point - Enterprise Edition

This module provides the main Flask application factory with enterprise-grade
configuration, middleware integration, error handling, structured logging,
and dependency injection.

Key Features:
- Environment-based configuration
- Structured logging with context management
- Enterprise middleware stack
- Professional dependency injection
- Comprehensive error handling
- Health check and version endpoints
- CORS configuration for API access
"""

import time
from datetime import datetime, timezone
from typing import Any, Dict

from flask import Flask, jsonify, request
from flask_cors import CORS

from application.config.environment import EnvironmentEnum, settings
from application.container import container
from infrastructure.entrypoints.http import task_routes, user_routes
from infrastructure.helpers.database.connection import database_connection
from infrastructure.helpers.logger.logger_config import get_logger
from infrastructure.helpers.middleware.http_middleware import (
    configure_middleware_stack,
)

# Initialize structured logger
logger = get_logger(__name__)


def create_app() -> Flask:
    """
    Application factory for creating Flask instances.

    This pattern allows for creating different app instances for
    production, development, and testing.
    """
    # Initialize Flask app
    app = Flask(__name__)

    # Load configuration from container
    app.config.from_object(container.config)

    # Configure dependency injection container
    app.container = container

    # Capture startup time for performance monitoring
    app.start_time = time.time()

    return app


def _configure_middleware(app: Flask) -> None:
    """Configure middleware components and dependency injection"""
    logger.debug("configuring_middleware")

    # Configure complete middleware stack
    configure_middleware_stack(app)

    logger.debug("middleware_configuration_completed")


def _configure_cors(app: Flask) -> None:
    """Configure CORS settings with environment-specific configuration"""
    logger.debug(
        "configuring_cors",
        origins=settings.api.cors_origins,
        environment=settings.application.environment,
    )

    # Configuración específica por entorno
    if settings.application.environment == EnvironmentEnum.PRODUCTION:
        _configure_production_cors(app)
    else:
        _configure_development_cors(app)

    logger.debug("cors_configuration_completed")


def _configure_production_cors(app: Flask) -> None:
    """Configure CORS for production environment with strict security"""
    logger.debug(
        "configuring_production_cors",
        origins=settings.api.cors_origins,
        methods=settings.api.cors_methods,
    )

    CORS(
        app,
        origins=settings.api.cors_origins,
        methods=settings.api.cors_methods,
        allow_headers=settings.api.cors_headers,
        expose_headers=settings.api.cors_expose_headers,
        supports_credentials=settings.api.cors_supports_credentials,
        max_age=settings.api.cors_max_age,
    )

    # Agregar headers de seguridad para producción
    @app.after_request
    def add_security_headers(response):
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = (
            "max-age=31536000; includeSubDomains"
        )
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Permissions-Policy"] = (
            "geolocation=(), microphone=(), camera=()"
        )
        return response


def _configure_development_cors(app: Flask) -> None:
    """Configure CORS for development environment with permissive settings"""
    logger.debug(
        "configuring_development_cors",
        origins=settings.api.cors_origins,
        methods=settings.api.cors_methods,
    )

    CORS(
        app,
        origins=settings.api.cors_origins,
        methods=settings.api.cors_methods,
        allow_headers=settings.api.cors_headers,
        expose_headers=settings.api.cors_expose_headers,
        supports_credentials=settings.api.cors_supports_credentials,
        max_age=settings.api.cors_max_age,
    )

    # Headers de seguridad básicos para desarrollo
    @app.after_request
    def add_security_headers(response):
        response.headers["X-Content-Type-Options"] = "nosniff"
        return response


def _register_blueprints(app: Flask) -> None:
    """Register application blueprints"""
    logger.debug("registering_blueprints")

    # Task management endpoints
    app.register_blueprint(task_routes.task_blueprint, url_prefix="/api/tasks")
    logger.debug("task_routes_registered", url_prefix="/api/tasks")

    # User management endpoints
    app.register_blueprint(user_routes.user_blueprint, url_prefix="/api/users")
    logger.debug("user_routes_registered", url_prefix="/api/users")


def _register_health_endpoints(app: Flask) -> None:
    """Register health check and version endpoints"""
    logger.debug("registering_health_endpoints")

    @app.route("/api/health")
    def health_check():
        """Basic health check with database connectivity"""
        logger.debug("health_check_requested")

        try:
            # Check database connectivity
            db_status = _check_database_health()

            health_data = {
                "status": (
                    "healthy" if db_status["status"] == "healthy" else "unhealthy"
                ),
                "service": "task-manager",
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "database": db_status,
            }

            status_code = 200 if health_data["status"] == "healthy" else 503
            logger.info("health_check_completed", status=health_data["status"])

            return jsonify(health_data), status_code

        except Exception as e:
            logger.error("health_check_failed", error=str(e))
            return (
                jsonify(
                    {
                        "status": "unhealthy",
                        "error": str(e),
                        "timestamp": datetime.now(timezone.utc).isoformat(),
                    }
                ),
                503,
            )

    @app.route("/api/version")
    def version_info():
        """Get application version information"""
        return jsonify(
            {
                "version": "1.0.0",
                "environment": settings.application.environment.value,
                "service": "task-manager",
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }
        )


def _configure_error_handlers(app: Flask) -> None:
    """Configure application error handlers"""
    logger.debug("configuring_error_handlers")

    # Import HTTPErrorHandler and error response utilities
    from infrastructure.helpers.errors.error_handlers import HTTPErrorHandler, create_error_response

    @app.errorhandler(404)
    def handle_not_found(error):
        """Handle 404 Not Found errors"""
        logger.warning("not_found_error", path=request.path, method=request.method)

        response_dict, status_code = create_error_response(
            error_type="NOT_FOUND",
            error_code="RESOURCE_NOT_FOUND",
            message=f"The requested resource '{request.path}' was not found",
            status_code=404
        )
        
        return jsonify(response_dict), status_code

    @app.errorhandler(405)
    def handle_method_not_allowed(error):
        """Handle 405 Method Not Allowed errors"""
        logger.warning(
            "method_not_allowed",
            path=request.path,
            method=request.method,
            allowed_methods=getattr(error, "valid_methods", []),
        )

        response_dict, status_code = create_error_response(
            error_type="METHOD_NOT_ALLOWED",
            error_code="INVALID_HTTP_METHOD",
            message=f"Method '{request.method}' not allowed for '{request.path}'",
            status_code=405
        )
        
        return jsonify(response_dict), status_code

    @app.errorhandler(Exception)
    def handle_general_exception(error):
        """Handle all unhandled exceptions using HTTPErrorHandler"""
        # Agregar más información de depuración
        logger.error(
            "unhandled_exception", 
            error=str(error), 
            error_type=type(error).__name__,
            error_class=error.__class__.__name__,
            exc_info=True
        )

        # Use HTTPErrorHandler to get proper response
        response_dict, status_code = HTTPErrorHandler.handle_exception(error)

        return jsonify(response_dict), status_code


def _check_database_health() -> Dict[str, Any]:
    """Check database health connectivity"""
    try:
        # Basic database connectivity check
        is_healthy = database_connection.health_check()

        if is_healthy:
            return {"status": "healthy"}
        else:
            return {"status": "unhealthy", "error": "Database connectivity failed"}
    except Exception as e:
        logger.error("database_health_check_failed", error=str(e))
        return {"status": "unhealthy", "error": str(e)}


def create_application() -> Flask:
    """
    Create and configure the Flask application

    Returns:
        Configured Flask application instance
    """
    logger.info("creating_application", environment=settings.application.environment)

    # Create Flask app
    app = create_app()

    # Configure middleware (must be first)
    _configure_middleware(app)

    # Configure CORS
    _configure_cors(app)

    # Register blueprints
    _register_blueprints(app)

    # Register health endpoints
    _register_health_endpoints(app)

    # Configure error handlers
    _configure_error_handlers(app)

    logger.info("application_created_successfully")
    return app


# Create the application instance
app = create_application()


if __name__ == "__main__":
    logger.info(
        "starting_application",
        host=settings.api.host,
        port=settings.api.port,
        environment=settings.application.environment,
    )

    # Suprimir warning del servidor de desarrollo en modo debug
    if settings.application.debug:
        import warnings

        warnings.filterwarnings("ignore", message="This is a development server")

    app.run(
        host=settings.api.host,
        port=settings.api.port,
        debug=settings.application.debug,
    )
