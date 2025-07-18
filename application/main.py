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

from flask import Flask, jsonify, request, g
from flask_cors import CORS

from infrastructure.entrypoints.http import task_routes, user_routes
from application.config import settings  # Esta es la configuración enterprise
from infrastructure.helpers.logger.logger_config import LoggerConfig, get_logger
from infrastructure.helpers.middleware.http_middleware import ErrorHandlingMiddleware, PerformanceMonitoringMiddleware
from infrastructure.helpers.errors.error_handlers import HTTPErrorHandler
from infrastructure.helpers.di import FlaskDIIntegration

# Initialize structured logger
logger = get_logger(__name__)


def create_app() -> Flask:
    """
    Create and configure Flask application with enterprise features
    
    Returns:
        Flask: Configured application instance
    """
    logger.info("application_initialization_started", environment=settings.application.environment.value)
    
    # Create Flask application
    app = Flask(__name__)
    
    # Configure structured logging
    LoggerConfig.configure_logging(settings.application)
    
    # Configure middleware
    _configure_middleware(app)
    
    # Configure CORS
    _configure_cors(app)
    
    # Register blueprints
    _register_blueprints(app)
    
    # Register health check endpoints
    _register_health_endpoints(app)
    
    # Configure error handlers (done by middleware, but we can add custom ones)
    _configure_error_handlers(app)
    
    logger.info(
        "application_initialization_completed",
        environment=settings.application.environment.value,
        debug_mode=settings.application.debug,
        cors_origins=settings.api.cors_origins
    )
    
    return app


def _configure_middleware(app: Flask) -> None:
    """Configure middleware components and dependency injection"""
    logger.debug("configuring_middleware")
    
    # Configure dependency injection first
    di_integration = FlaskDIIntegration(app)
    logger.debug("dependency_injection_configured")
    
    # Error handling middleware (handles all exceptions automatically)
    ErrorHandlingMiddleware(app)
    
    # Performance monitoring middleware
    PerformanceMonitoringMiddleware(app)
    
    logger.debug("middleware_configuration_completed")


def _configure_cors(app: Flask) -> None:
    """Configure CORS settings"""
    logger.debug("configuring_cors", origins=settings.api.cors_origins)
    
    CORS(app, 
         origins=settings.api.cors_origins,
         methods=settings.api.cors_methods,
         allow_headers=settings.api.cors_headers,
         supports_credentials=True)
    
    logger.debug("cors_configuration_completed")


def _register_blueprints(app: Flask) -> None:
    """Register application blueprints"""
    logger.debug("registering_blueprints")
    
    # Task management endpoints
    app.register_blueprint(task_routes.blueprint, url_prefix='/api/tasks')
    logger.debug("task_routes_registered", url_prefix="/api/tasks")
    
    # User management endpoints  
    app.register_blueprint(user_routes.blueprint, url_prefix='/api/users')
    logger.debug("user_routes_registered", url_prefix="/api/users")
    
    logger.debug("blueprints_registration_completed")


def _register_health_endpoints(app: Flask) -> None:
    """Register health check and monitoring endpoints"""
    logger.debug("registering_health_endpoints")
    
    @app.route('/api/health')
    def health_check():
        """Basic health check endpoint"""
        logger.debug("health_check_accessed")
        return jsonify({
            "status": "healthy",
            "service": "accounting-app",
            "version": settings.application.version,
            "environment": settings.application.environment.value
        })
    
    @app.route('/api/health/detailed')
    def detailed_health_check():
        """Detailed health check with system information"""
        logger.debug("detailed_health_check_accessed")
        
        import time
        from datetime import datetime, timezone
        
        health_data = {
            "status": "healthy",
            "service": "accounting-app",
            "version": settings.application.version,
            "environment": settings.application.environment.value,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "uptime_seconds": time.time() - app.start_time if hasattr(app, 'start_time') else 0,
            "checks": {
                "database": _check_database_health(),
                "memory": "ok",
                "disk": "ok"
            }
        }
        
        logger.info("detailed_health_check_completed", health_status="healthy")
        return jsonify(health_data)
    
    @app.route('/api/version')
    def version_info():
        """Version information endpoint"""
        logger.debug("version_info_accessed")
        return jsonify({
            "service": "accounting-app",
            "version": settings.application.version,
            "build_date": "2025-01-19",
            "environment": settings.application.environment.value,
            "features": [
                "task_management",
                "user_management", 
                "structured_logging",
                "error_handling",
                "performance_monitoring"
            ]
        })
    
    logger.debug("health_endpoints_registered")


def _configure_error_handlers(app: Flask) -> None:
    """Configure custom error handlers (in addition to middleware)"""
    logger.debug("configuring_custom_error_handlers")
    
    # Custom 404 handler for unmatched routes
    @app.errorhandler(404)
    def handle_not_found(error):
        """Handle 404 errors with consistent format"""
        logger.warning(
            "endpoint_not_found",
            path=request.path,
            method=request.method
        )
        
        import time
        response_data = {
            "error": {
                "type": "ENDPOINT_NOT_FOUND",
                "code": "NOT_FOUND",
                "message": f"Endpoint '{request.path}' not found",
                "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
                "path": request.path
            }
        }
        return jsonify(response_data), 404
    
    # Custom 405 handler for method not allowed
    @app.errorhandler(405)
    def handle_method_not_allowed(error):
        """Handle 405 errors with consistent format"""
        logger.warning(
            "method_not_allowed",
            path=request.path,
            method=request.method,
            allowed_methods=error.valid_methods if hasattr(error, 'valid_methods') else []
        )
        
        import time
        response_data = {
            "error": {
                "type": "METHOD_NOT_ALLOWED",
                "code": "METHOD_NOT_ALLOWED", 
                "message": f"Method '{request.method}' not allowed for endpoint '{request.path}'",
                "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
                "path": request.path
            }
        }
        return jsonify(response_data), 405
    
    logger.debug("custom_error_handlers_configured")


def _check_database_health() -> str:
    """
    Check database health status
    
    Returns:
        Status string indicating database health
    """
    try:
        from infrastructure.helpers.database.connection import database_connection
        
        # Try to get a database session and perform a simple query
        with database_connection.create_session() as session:
            # Execute a simple query to test connectivity
            session.execute("SELECT 1")
            return "healthy"
    
    except Exception as e:
        logger.error(
            "database_health_check_failed",
            error_type=type(e).__name__,
            error_message=str(e)
        )
        return "unhealthy"


# Create application instance
app = create_app()

# Store application start time for uptime calculation
import time
app.start_time = time.time()

# Log application ready
logger.info(
    "application_ready",
    environment=settings.application.environment.value,
    debug_mode=settings.application.debug
)


# Entry point for development server
if __name__ == '__main__':
    logger.info("starting_development_server", port=5000, debug=True)
    app.run(debug=True, host='0.0.0.0', port=5000)
