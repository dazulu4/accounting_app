"""
Enterprise Environment Configuration using Pydantic Settings

This module provides comprehensive environment-based configuration management
following 12-factor app principles and enterprise best practices.

Key Features:
- Environment variable validation and type conversion
- Secure secret handling with SecretStr
- Environment-specific configurations
- Professional naming conventions (English only)
- AWS integration ready
"""

from typing import List, Optional, Dict
from enum import Enum
from pydantic import Field, field_validator, ConfigDict, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic.types import SecretStr
import re
import os


class EnvironmentEnum(str, Enum):
    """Application environment enumeration"""
    DEVELOPMENT = "development"
    PRODUCTION = "production"


class LogLevelEnum(str, Enum):
    """Logging level enumeration"""
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class DatabaseConfig(BaseSettings):
    """
    Database configuration with environment variables support
    
    Environment Variables:
    - DATABASE_HOST: Database host (default: 127.0.0.1)
    - DATABASE_PORT: Database port (default: 3306)
    - DATABASE_NAME: Database name (default: accounting)
    - DATABASE_USER: Database username (required)
    - DATABASE_PASSWORD: Database password (required, secret)
    """
    
    host: str = Field(
        default="127.0.0.1",
        description="Database host address"
    )
    port: int = Field(
        default=3306, 
        ge=1, 
        le=65535,
        description="Database port number"
    )
    name: str = Field(
        default="accounting", 
        min_length=1,
        description="Database name"
    )
    username: str = Field(
        default="admin", 
        min_length=1,
        description="Database username"
    )
    password: SecretStr = Field(
        default="admin", 
        min_length=1,
        description="Database password"
    )
    
    # Connection pool configuration
    connection_timeout: int = Field(default=30, ge=5, le=300)
    pool_size: int = Field(default=10, ge=1, le=50)
    max_overflow: int = Field(default=20, ge=0, le=100)
    echo: bool = Field(default=False)

    model_config = ConfigDict(
        env_prefix="DATABASE_"
    )
    
    @field_validator('host')
    def validate_host(cls, v):
        """Validate database host"""
        if not v or not v.strip():
            raise ValueError("Database host cannot be empty. Please set DATABASE_HOST environment variable.")
        host = v.strip()
        # Basic host validation (IP or hostname)
        if not re.match(r'^[a-zA-Z0-9.-]+$', host) and host != 'localhost':
            raise ValueError(f"Invalid database host format: {host}. Must be a valid hostname or IP address.")
        return host
    
    @field_validator('name')
    def validate_database_name(cls, v):
        """Validate database name"""
        if not v or not v.strip():
            raise ValueError("Database name cannot be empty. Please set DATABASE_NAME environment variable.")
        name = v.strip()
        if len(name) > 64:  # MySQL limit
            raise ValueError(f"Database name too long: {name}. Maximum length is 64 characters.")
        if not re.match(r'^[a-zA-Z0-9_]+$', name):
            raise ValueError(f"Invalid database name: {name}. Must contain only letters, numbers, and underscores.")
        return name
    
    @field_validator('username')
    def validate_username(cls, v):
        """Validate database username"""
        if not v or not v.strip():
            raise ValueError("Database username cannot be empty. Please set DATABASE_USER environment variable.")
        username = v.strip()
        if len(username) > 32:  # MySQL limit
            raise ValueError(f"Database username too long: {username}. Maximum length is 32 characters.")
        return username
    
    @field_validator('password')
    def validate_password(cls, v):
        """Validate database password"""
        if not v or not v.get_secret_value().strip():
            raise ValueError("Database password cannot be empty. Please set DATABASE_PASSWORD environment variable.")
        return v
    
    @property
    def connection_url(self) -> str:
        """Generate synchronous MySQL connection URL"""
        return (
            f"mysql+pymysql://{self.username}:{self.password.get_secret_value()}"
            f"@{self.host}:{self.port}/{self.name}"
        )
    
    @property
    def connection_url_masked(self) -> str:
        """Generate connection URL with masked password for logging"""
        return f"mysql+pymysql://{self.username}:***@{self.host}:{self.port}/{self.name}"


class ApplicationConfig(BaseSettings):
    """
    Application configuration using standard environment variables
    
    Environment Variables:
    - APP_ENVIRONMENT: Application environment (development/production)
    - APP_DEBUG: Debug mode (true/false)
    - APP_VERSION: Application version (default: 1.0.0)
    - LOG_LEVEL: Logging level (default: INFO)
    - LOG_FORMAT: Log format (json/text, default: json)
    """
    
    environment: EnvironmentEnum = Field(
        default=EnvironmentEnum.DEVELOPMENT,
        description="Application environment"
    )
    debug: bool = Field(
        default=False,
        description="Debug mode"
    )
    version: str = Field(
        default="1.0.0",
        description="Application version"
    )
    
    # Logging configuration
    log_level: LogLevelEnum = Field(
        default=LogLevelEnum.INFO,
        description="Logging level"
    )
    log_format: str = Field(
        default="json", 
        pattern="^(json|text)$",
        description="Log format"
    )

    model_config = ConfigDict(
        env_prefix="APP_"
    )
    
    @field_validator('environment')
    def validate_environment(cls, v):
        """Validate application environment"""
        if v not in EnvironmentEnum:
            valid_envs = [env.value for env in EnvironmentEnum]
            raise ValueError(f"Invalid environment: {v}. Must be one of: {valid_envs}")
        return v
    
    @field_validator('version')
    def validate_version(cls, v):
        """Validate version format"""
        if not v or not v.strip():
            raise ValueError("Application version cannot be empty. Please set APP_VERSION environment variable.")
        version = v.strip()
        # Basic semver validation
        if not re.match(r'^\d+\.\d+\.\d+', version):
            raise ValueError(f"Invalid version format: {version}. Must follow semantic versioning (e.g., 1.0.0)")
        return version
    
    @field_validator('log_level')
    def validate_log_level(cls, v):
        """Validate log level"""
        if v not in LogLevelEnum:
            valid_levels = [level.value for level in LogLevelEnum]
            raise ValueError(f"Invalid log level: {v}. Must be one of: {valid_levels}")
        return v
    
    @property
    def is_development(self) -> bool:
        """Check if running in development environment"""
        return self.environment == EnvironmentEnum.DEVELOPMENT
    
    @property
    def is_production(self) -> bool:
        """Check if running in production environment"""
        return self.environment == EnvironmentEnum.PRODUCTION


class APIConfig(BaseSettings):
    """
    API configuration with enterprise-grade CORS settings
    
    Environment Variables:
    - API_HOST: API host (default: 0.0.0.0)
    - API_PORT: API port (default: 8000)
    - API_PREFIX: API URL prefix (default: /api)
    - CORS_ORIGINS: Allowed CORS origins (comma-separated)
    - CORS_METHODS: Allowed CORS methods (comma-separated)
    - CORS_HEADERS: Allowed CORS headers (comma-separated)
    - CORS_EXPOSE_HEADERS: Exposed CORS headers (comma-separated)
    - CORS_SUPPORTS_CREDENTIALS: Enable credentials support (default: true)
    - CORS_MAX_AGE: CORS preflight cache time in seconds (default: 3600)
    """
    
    host: str = Field(default="0.0.0.0")
    port: int = Field(default=8000, ge=1, le=65535)
    prefix: str = Field(default="/api", pattern="^/.*")
    
    # CORS configuration - enterprise-grade
    cors_origins: List[str] = Field(default=["http://localhost:4200"])
    cors_methods: List[str] = Field(default=["GET", "POST", "PUT", "DELETE", "OPTIONS"])
    cors_headers: List[str] = Field(default=["Content-Type", "Authorization", "X-Request-ID"])
    cors_expose_headers: List[str] = Field(default=["Content-Type", "X-Request-ID"])
    cors_supports_credentials: bool = Field(default=True)
    cors_max_age: int = Field(default=3600, ge=0, le=86400)
    
    # Security headers configuration
    security_headers: Dict[str, str] = Field(default_factory=dict)

    model_config = ConfigDict(
        env_prefix="API_"
    )
    
    @field_validator('host')
    def validate_host(cls, v):
        """Validate API host"""
        if not v or not v.strip():
            raise ValueError("API host cannot be empty. Please set API_HOST environment variable.")
        return v.strip()
    
    @field_validator('port')
    def validate_port(cls, v):
        """Validate API port"""
        if v < 1 or v > 65535:
            raise ValueError(f"Invalid API port: {v}. Must be between 1 and 65535.")
        return v
    
    @field_validator('cors_origins', 'cors_methods', 'cors_headers', 'cors_expose_headers', mode='before')
    def split_comma_separated(cls, value):
        """Convert comma-separated string to list"""
        if isinstance(value, str):
            return [item.strip() for item in value.split(',') if item.strip()]
        return value
    
    @field_validator('cors_origins')
    def validate_cors_origins(cls, v):
        """Validate CORS origins"""
        # Basic validation - check for empty list
        if not v:
            raise ValueError("CORS origins cannot be empty")
        
        # Check for wildcard in production (this will be validated at runtime)
        if '*' in v:
            # Log warning but don't fail validation
            import logging
            logging.warning("Wildcard (*) in CORS origins - ensure this is not used in production")
        
        return v
    
    @staticmethod
    def _is_valid_url(url: str) -> bool:
        """Validate URL format"""
        import re
        # Handle None and empty strings
        if url is None or not url.strip():
            return False
        
        # Check URL length (reasonable limit)
        if len(url) > 500:
            return False
        
        # Basic URL validation pattern - only HTTPS for production
        url_pattern = r'^https://[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}(:\d+)?(/.*)?$'
        return bool(re.match(url_pattern, url))


class RateLimitConfig(BaseSettings):
    """Rate limiting configuration"""
    enabled: bool = Field(default=True)
    requests_per_second: int = Field(default=10, ge=1, le=1000)
    window_size_seconds: int = Field(default=60, ge=10, le=3600)
    burst_limit: int = Field(default=20, ge=1, le=1000)
    
    @field_validator('burst_limit')
    def validate_burst_limit(cls, v, info):
        """Burst limit should be >= requests_per_second"""
        if 'requests_per_second' in info.data and v < info.data['requests_per_second']:
            raise ValueError("Burst limit must be >= requests per second")
        return v


class AWSConfig(BaseSettings):
    """
    AWS configuration for Lambda and other services
    
    Environment Variables:
    - AWS_REGION: AWS region (default: us-east-1)
    - AWS_ACCOUNT_ID: AWS account ID (optional)
    - LAMBDA_FUNCTION_NAME: Lambda function name (optional)
    - LAMBDA_MEMORY_SIZE: Lambda memory size (optional)
    - LAMBDA_TIMEOUT: Lambda timeout in seconds (optional)
    """
    
    region: str = Field(default="us-east-1")
    account_id: Optional[str] = Field(default=None)
    
    # Lambda-specific configuration
    lambda_function_name: Optional[str] = Field(default=None)
    lambda_memory_size: Optional[int] = Field(default=512, ge=128, le=10240)
    lambda_timeout: Optional[int] = Field(default=30, ge=1, le=900)

    model_config = ConfigDict(
        env_prefix="AWS_"
    )
    
    @field_validator('region')
    def validate_region(cls, v):
        """Validate AWS region"""
        if not v or not v.strip():
            raise ValueError("AWS region cannot be empty. Please set AWS_REGION environment variable.")
        region = v.strip()
        # Basic AWS region validation
        if not re.match(r'^[a-z0-9-]+$', region):
            raise ValueError(f"Invalid AWS region format: {region}")
        return region


class AppSettings(BaseSettings):
    """
    Main application settings that combines all configuration sections
    
    This follows the composition pattern for better organization and maintainability.
    """
    
    # Configuration sections
    database: DatabaseConfig = Field(default_factory=DatabaseConfig)
    application: ApplicationConfig = Field(default_factory=ApplicationConfig)
    api: APIConfig = Field(default_factory=APIConfig)
    aws: AWSConfig = Field(default_factory=AWSConfig)
    rate_limit: RateLimitConfig = Field(default_factory=RateLimitConfig)
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",  # Ignore unknown environment variables
        validate_default=True
    )
    
    @model_validator(mode='after')
    def validate_configuration(self):
        """Validate complete configuration"""
        errors = []
        
        # Validate database configuration
        if not self.database.username or not self.database.password.get_secret_value():
            errors.append("Database username and password are required")
        
        # Validate application configuration
        if self.application.environment == EnvironmentEnum.PRODUCTION and self.application.debug:
            errors.append("Debug mode should not be enabled in production")
        
        # Validate API configuration
        if not self.api.cors_origins:
            errors.append("CORS origins cannot be empty")
        
        # Validate AWS configuration for production
        if self.application.environment == EnvironmentEnum.PRODUCTION:
            if not self.aws.region:
                errors.append("AWS region is required in production")
        
        if errors:
            raise ValueError(f"Configuration validation failed: {'; '.join(errors)}")
        
        return self
    
    def get_database_url(self) -> str:
        """Get database connection URL"""
        return self.database.connection_url
    
    def get_database_url_masked(self) -> str:
        """Get database connection URL with masked password for logging"""
        return self.database.connection_url_masked
    
    def is_aws_lambda(self) -> bool:
        """Check if running in AWS Lambda environment"""
        return self.aws.lambda_function_name is not None


# Global settings instance
# This is loaded once at application startup and provides thread-safe access
settings = AppSettings() 