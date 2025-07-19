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

from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field, SecretStr, validator
from typing import Optional, List
from enum import Enum


class EnvironmentEnum(str, Enum):
    """Application environment enumeration"""
    DEVELOPMENT = "development"
    STAGING = "staging"
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
    - DATABASE_HOST: Database host (default: localhost)
    - DATABASE_PORT: Database port (default: 3306)
    - DATABASE_NAME: Database name (default: accounting)
    - DATABASE_USERNAME: Database username (required)
    - DATABASE_PASSWORD: Database password (required, secret)
    - DATABASE_CONNECTION_TIMEOUT: Connection timeout in seconds (default: 30)
    - DATABASE_POOL_SIZE: Connection pool size (default: 10)
    - DATABASE_MAX_OVERFLOW: Max pool overflow (default: 20)
    - DATABASE_ECHO: Show SQL queries in logs (default: false)
    """
    
    host: str = Field(default="localhost", env="DB_HOST")
    port: int = Field(default=3306, env="DB_PORT", ge=1, le=65535)
    name: str = Field(default="accounting", env="DB_NAME", min_length=1)
    username: str = Field(default="admin", env="DB_USER", min_length=1)
    password: SecretStr = Field(default="admin", env="DB_PASSWORD", min_length=1)
    
    # Connection pool configuration
    connection_timeout: int = Field(default=30, env="DATABASE_CONNECTION_TIMEOUT", ge=5, le=300)
    pool_size: int = Field(default=10, env="DATABASE_POOL_SIZE", ge=1, le=50)
    max_overflow: int = Field(default=20, env="DATABASE_MAX_OVERFLOW", ge=0, le=100)
    echo: bool = Field(default=False, env="DATABASE_ECHO")
    
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
    Application configuration
    
    Environment Variables:
    - APP_ENVIRONMENT: Application environment (development/staging/production)
    - APP_DEBUG: Debug mode (default: false)
    - APP_VERSION: Application version (default: 1.0.0)
    - LOG_LEVEL: Logging level (default: INFO)
    - LOG_FORMAT: Log format (json/text, default: json)
    """
    
    environment: EnvironmentEnum = Field(default=EnvironmentEnum.DEVELOPMENT, env="APP_ENVIRONMENT")
    debug: bool = Field(default=False, env="APP_DEBUG")
    version: str = Field(default="1.0.0", env="APP_VERSION")
    
    # Logging configuration
    log_level: LogLevelEnum = Field(default=LogLevelEnum.INFO, env="LOG_LEVEL")
    log_format: str = Field(default="json", env="LOG_FORMAT", pattern="^(json|text)$")
    
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
    API configuration
    
    Environment Variables:
    - API_HOST: API host (default: 0.0.0.0)
    - API_PORT: API port (default: 8000)
    - API_PREFIX: API URL prefix (default: /api)
    - CORS_ORIGINS: Allowed CORS origins (comma-separated)
    - CORS_METHODS: Allowed CORS methods (comma-separated)
    - CORS_HEADERS: Allowed CORS headers (comma-separated)
    """
    
    host: str = Field(default="0.0.0.0", env="API_HOST")
    port: int = Field(default=8000, env="API_PORT", ge=1, le=65535)
    prefix: str = Field(default="/api", env="API_PREFIX", pattern="^/.*")
    
    # CORS configuration
    cors_origins: List[str] = Field(default=["*"], env="CORS_ORIGINS")
    cors_methods: List[str] = Field(default=["GET", "POST", "PUT", "DELETE", "OPTIONS"], env="CORS_METHODS")
    cors_headers: List[str] = Field(default=["*"], env="CORS_HEADERS")
    
    @validator('cors_origins', 'cors_methods', 'cors_headers', pre=True)
    def split_comma_separated(cls, value):
        """Convert comma-separated string to list"""
        if isinstance(value, str):
            return [item.strip() for item in value.split(',') if item.strip()]
        return value


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
    
    region: str = Field(default="us-east-1", env="AWS_REGION")
    account_id: Optional[str] = Field(default=None, env="AWS_ACCOUNT_ID")
    
    # Lambda-specific configuration
    lambda_function_name: Optional[str] = Field(default=None, env="LAMBDA_FUNCTION_NAME")
    lambda_memory_size: Optional[int] = Field(default=512, env="LAMBDA_MEMORY_SIZE", ge=128, le=10240)
    lambda_timeout: Optional[int] = Field(default=30, env="LAMBDA_TIMEOUT", ge=1, le=900)


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
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",  # Ignore unknown environment variables
        validate_default=True
    )
    
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