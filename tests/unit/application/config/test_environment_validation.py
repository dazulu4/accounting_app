"""
Tests for environment configuration validation
"""

import pytest
from pydantic import ValidationError
from application.config.environment import (
    DatabaseConfig,
    ApplicationConfig,
    APIConfig,
    AWSConfig,
    AppSettings,
    EnvironmentEnum,
    LogLevelEnum,
)


class TestDatabaseConfigValidation:
    """Test database configuration validation"""

    def test_valid_database_config(self):
        """Test valid database configuration"""
        config = DatabaseConfig(
            host="localhost",
            port=3306,
            name="test_db",
            username="test_user",
            password="test_password",
        )
        assert config.host == "localhost"
        assert config.port == 3306
        assert config.name == "test_db"
        assert config.username == "test_user"
        assert config.password.get_secret_value() == "test_password"

    def test_empty_host_raises_error(self):
        """Test empty host raises validation error"""
        with pytest.raises(ValidationError) as exc_info:
            DatabaseConfig(host="")
        assert "Database host cannot be empty" in str(exc_info.value)

    def test_invalid_host_format_raises_error(self):
        """Test invalid host format raises validation error"""
        with pytest.raises(ValidationError) as exc_info:
            DatabaseConfig(host="invalid@host")
        assert "Invalid database host format" in str(exc_info.value)

    def test_empty_database_name_raises_error(self):
        """Test empty database name raises validation error"""
        with pytest.raises(ValidationError) as exc_info:
            DatabaseConfig(name="")
        # Pydantic validates min_length before our custom validator
        assert "String should have at least 1 character" in str(exc_info.value)

    def test_invalid_database_name_raises_error(self):
        """Test invalid database name raises validation error"""
        with pytest.raises(ValidationError) as exc_info:
            DatabaseConfig(name="invalid@name")
        assert "Invalid database name" in str(exc_info.value)

    def test_database_name_too_long_raises_error(self):
        """Test database name too long raises validation error"""
        long_name = "a" * 65  # 65 characters
        with pytest.raises(ValidationError) as exc_info:
            DatabaseConfig(name=long_name)
        assert "Database name too long" in str(exc_info.value)

    def test_empty_username_raises_error(self):
        """Test empty username raises validation error"""
        with pytest.raises(ValidationError) as exc_info:
            DatabaseConfig(username="")
        # Pydantic validates min_length before our custom validator
        assert "String should have at least 1 character" in str(exc_info.value)

    def test_username_too_long_raises_error(self):
        """Test username too long raises validation error"""
        long_username = "a" * 33  # 33 characters
        with pytest.raises(ValidationError) as exc_info:
            DatabaseConfig(username=long_username)
        assert "Database username too long" in str(exc_info.value)

    def test_empty_password_raises_error(self):
        """Test empty password raises validation error"""
        with pytest.raises(ValidationError) as exc_info:
            DatabaseConfig(password="")
        # Pydantic validates min_length before our custom validator
        assert "Value should have at least 1 item after validation" in str(
            exc_info.value
        )

    def test_connection_url_generation(self):
        """Test connection URL generation"""
        config = DatabaseConfig(
            host="localhost",
            port=3306,
            name="test_db",
            username="test_user",
            password="test_password",
        )
        expected_url = "mysql+pymysql://test_user:test_password@localhost:3306/test_db"
        assert config.connection_url == expected_url

    def test_connection_url_masked(self):
        """Test masked connection URL for logging"""
        config = DatabaseConfig(
            host="localhost",
            port=3306,
            name="test_db",
            username="test_user",
            password="test_password",
        )
        expected_url = "mysql+pymysql://test_user:***@localhost:3306/test_db"
        assert config.connection_url_masked == expected_url


class TestApplicationConfigValidation:
    """Test application configuration validation"""

    def test_valid_application_config(self):
        """Test valid application configuration"""
        config = ApplicationConfig(
            environment=EnvironmentEnum.DEVELOPMENT,
            debug=False,
            version="1.0.0",
            log_level=LogLevelEnum.INFO,
            log_format="json",
        )
        assert config.environment == EnvironmentEnum.DEVELOPMENT
        assert config.debug is False
        assert config.version == "1.0.0"
        assert config.log_level == LogLevelEnum.INFO
        assert config.log_format == "json"

    def test_invalid_environment_raises_error(self):
        """Test invalid environment raises validation error"""
        with pytest.raises(ValidationError) as exc_info:
            ApplicationConfig(environment="invalid")
        # Pydantic validates enum before our custom validator
        assert "Input should be 'development' or 'production'" in str(exc_info.value)

    def test_empty_version_raises_error(self):
        """Test empty version raises validation error"""
        with pytest.raises(ValidationError) as exc_info:
            ApplicationConfig(version="")
        assert "Application version cannot be empty" in str(exc_info.value)

    def test_invalid_version_format_raises_error(self):
        """Test invalid version format raises validation error"""
        with pytest.raises(ValidationError) as exc_info:
            ApplicationConfig(version="invalid")
        assert "Invalid version format" in str(exc_info.value)

    def test_invalid_log_level_raises_error(self):
        """Test invalid log level raises validation error"""
        with pytest.raises(ValidationError) as exc_info:
            ApplicationConfig(log_level="INVALID")
        # Pydantic validates enum before our custom validator
        assert (
            "Input should be 'DEBUG', 'INFO', 'WARNING', 'ERROR' or 'CRITICAL'"
            in str(exc_info.value)
        )

    def test_environment_properties(self):
        """Test environment properties"""
        dev_config = ApplicationConfig(environment=EnvironmentEnum.DEVELOPMENT)
        prod_config = ApplicationConfig(environment=EnvironmentEnum.PRODUCTION)

        assert dev_config.is_development is True
        assert dev_config.is_production is False
        assert prod_config.is_development is False
        assert prod_config.is_production is True


class TestAPIConfigValidation:
    """Test API configuration validation"""

    def test_valid_api_config(self):
        """Test valid API configuration"""
        config = APIConfig(
            host="0.0.0.0",
            port=8000,
            prefix="/api",
            cors_origins=["*"],
            cors_methods=["GET", "POST"],
            cors_headers=["*"],
        )
        assert config.host == "0.0.0.0"
        assert config.port == 8000
        assert config.prefix == "/api"
        assert config.cors_origins == ["*"]
        assert config.cors_methods == ["GET", "POST"]
        assert config.cors_headers == ["*"]

    def test_empty_host_raises_error(self):
        """Test empty host raises validation error"""
        with pytest.raises(ValidationError) as exc_info:
            APIConfig(host="")
        assert "API host cannot be empty" in str(exc_info.value)

    def test_invalid_port_raises_error(self):
        """Test invalid port raises validation error"""
        with pytest.raises(ValidationError) as exc_info:
            APIConfig(port=0)
        # Pydantic validates ge constraint before our custom validator
        assert "Input should be greater than or equal to 1" in str(exc_info.value)

    def test_cors_comma_separated_string(self):
        """Test CORS comma-separated string parsing"""
        config = APIConfig(cors_origins="http://localhost:3000,https://example.com")
        assert config.cors_origins == ["http://localhost:3000", "https://example.com"]


class TestAWSConfigValidation:
    """Test AWS configuration validation"""

    def test_valid_aws_config(self):
        """Test valid AWS configuration"""
        config = AWSConfig(
            region="us-east-1",
            account_id="123456789012",
            lambda_function_name="my-function",
            lambda_memory_size=512,
            lambda_timeout=30,
        )
        assert config.region == "us-east-1"
        assert config.account_id == "123456789012"
        assert config.lambda_function_name == "my-function"
        assert config.lambda_memory_size == 512
        assert config.lambda_timeout == 30

    def test_empty_region_raises_error(self):
        """Test empty region raises validation error"""
        with pytest.raises(ValidationError) as exc_info:
            AWSConfig(region="")
        assert "AWS region cannot be empty" in str(exc_info.value)

    def test_invalid_region_format_raises_error(self):
        """Test invalid region format raises validation error"""
        with pytest.raises(ValidationError) as exc_info:
            AWSConfig(region="invalid@region")
        assert "Invalid AWS region format" in str(exc_info.value)


class TestAppSettingsValidation:
    """Test complete application settings validation"""

    def test_valid_app_settings(self):
        """Test valid application settings"""
        # Use environment variables to avoid conflicts
        import os

        original_env = os.environ.get("APP_ENVIRONMENT")
        try:
            os.environ["APP_ENVIRONMENT"] = "development"
            settings = AppSettings()
            assert settings.database.host == "127.0.0.1"
            assert settings.application.environment == EnvironmentEnum.DEVELOPMENT
            assert settings.api.host == "0.0.0.0"
            assert settings.aws.region == "us-east-1"
        finally:
            if original_env:
                os.environ["APP_ENVIRONMENT"] = original_env
            else:
                os.environ.pop("APP_ENVIRONMENT", None)

    def test_production_with_debug_raises_error(self):
        """Test production with debug enabled raises validation error"""
        with pytest.raises(ValidationError) as exc_info:
            AppSettings(
                application=ApplicationConfig(
                    environment=EnvironmentEnum.PRODUCTION, debug=True
                )
            )
        assert "Debug mode should not be enabled in production" in str(exc_info.value)

    def test_empty_cors_origins_raises_error(self):
        """Test empty CORS origins raises validation error"""
        # Use environment variables to avoid conflicts
        import os

        original_env = os.environ.get("APP_ENVIRONMENT")
        try:
            os.environ["APP_ENVIRONMENT"] = "development"
            with pytest.raises(ValidationError) as exc_info:
                AppSettings(api=APIConfig(cors_origins=[]))
            assert "CORS origins cannot be empty" in str(exc_info.value)
        finally:
            if original_env:
                os.environ["APP_ENVIRONMENT"] = original_env
            else:
                os.environ.pop("APP_ENVIRONMENT", None)

    def test_database_url_methods(self):
        """Test database URL methods"""
        # Use environment variables to avoid conflicts
        import os

        original_env = os.environ.get("APP_ENVIRONMENT")
        try:
            os.environ["APP_ENVIRONMENT"] = "development"
            settings = AppSettings()
            assert "mysql+pymysql://" in settings.get_database_url()
            assert "***" in settings.get_database_url_masked()
        finally:
            if original_env:
                os.environ["APP_ENVIRONMENT"] = original_env
            else:
                os.environ.pop("APP_ENVIRONMENT", None)

    def test_aws_lambda_detection(self):
        """Test AWS Lambda environment detection"""
        # Use environment variables to avoid conflicts
        import os

        original_env = os.environ.get("APP_ENVIRONMENT")
        try:
            os.environ["APP_ENVIRONMENT"] = "development"
            settings = AppSettings()
            assert settings.is_aws_lambda() is False

            lambda_settings = AppSettings(
                aws=AWSConfig(lambda_function_name="my-function")
            )
            assert lambda_settings.is_aws_lambda() is True
        finally:
            if original_env:
                os.environ["APP_ENVIRONMENT"] = original_env
            else:
                os.environ.pop("APP_ENVIRONMENT", None)
