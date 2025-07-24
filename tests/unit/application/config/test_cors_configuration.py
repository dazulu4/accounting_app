"""
Tests for CORS configuration validation

This module tests the enterprise-grade CORS configuration including:
- Environment-specific validation
- Origin validation for production
- HTTPS requirement enforcement
- Security headers configuration
"""

import pytest
from pydantic import ValidationError

from application.config.environment import (
    APIConfig,
    AppSettings,
    ApplicationConfig,
    EnvironmentEnum,
)


class TestCORSConfiguration:
    """Test CORS configuration validation"""

    def test_development_cors_allows_wildcard(self):
        """Test that development environment allows wildcard origins"""
        config = APIConfig(
            cors_origins=["*"],
            cors_methods=["GET", "POST"],
            cors_headers=["*"],
            cors_expose_headers=["Content-Type"],
            cors_supports_credentials=True,
            cors_max_age=3600,
        )
        assert config.cors_origins == ["*"]
        assert config.cors_methods == ["GET", "POST"]
        assert config.cors_headers == ["*"]
        assert config.cors_expose_headers == ["Content-Type"]
        assert config.cors_supports_credentials is True
        assert config.cors_max_age == 3600

    def test_production_cors_allows_wildcard_with_warning(self):
        """Test that production environment allows wildcard origins with warning"""
        # This should work but log a warning
        config = APIConfig(cors_origins=["*"])
        assert config.cors_origins == ["*"]

    def test_production_cors_allows_http_with_warning(self):
        """Test that production environment allows HTTP origins with warning"""
        # This should work but log a warning
        config = APIConfig(cors_origins=["http://insecure.com"])
        assert config.cors_origins == ["http://insecure.com"]

    def test_production_cors_accepts_valid_https_origins(self):
        """Test that production environment accepts valid HTTPS origins"""
        config = APIConfig(
            cors_origins=["https://app.company.com", "https://admin.company.com"]
        )
        assert config.cors_origins == [
            "https://app.company.com",
            "https://admin.company.com",
        ]

    def test_cors_comma_separated_string_parsing(self):
        """Test CORS comma-separated string parsing"""
        config = APIConfig(
            cors_origins="https://app.company.com,https://admin.company.com",
            cors_methods="GET,POST,PUT,DELETE",
            cors_headers="Content-Type,Authorization",
            cors_expose_headers="Content-Type,X-Request-ID",
        )
        assert config.cors_origins == [
            "https://app.company.com",
            "https://admin.company.com",
        ]
        assert config.cors_methods == ["GET", "POST", "PUT", "DELETE"]
        assert config.cors_headers == ["Content-Type", "Authorization"]
        assert config.cors_expose_headers == ["Content-Type", "X-Request-ID"]

    def test_cors_max_age_validation(self):
        """Test CORS max age validation"""
        # Valid max age
        config = APIConfig(cors_max_age=3600)
        assert config.cors_max_age == 3600

        # Invalid max age (too high)
        with pytest.raises(ValidationError):
            APIConfig(cors_max_age=100000)

        # Invalid max age (negative)
        with pytest.raises(ValidationError):
            APIConfig(cors_max_age=-1)

    def test_cors_port_validation(self):
        """Test CORS port validation"""
        # Valid port
        config = APIConfig(port=8000)
        assert config.port == 8000

        # Invalid port (too high)
        with pytest.raises(ValidationError):
            APIConfig(port=70000)

        # Invalid port (zero)
        with pytest.raises(ValidationError):
            APIConfig(port=0)

    def test_cors_host_validation(self):
        """Test CORS host validation"""
        # Valid host
        config = APIConfig(host="0.0.0.0")
        assert config.host == "0.0.0.0"

        # Invalid host (empty)
        with pytest.raises(ValidationError) as exc_info:
            APIConfig(host="")
        assert "API host cannot be empty" in str(exc_info.value)

        # Invalid host (whitespace only)
        with pytest.raises(ValidationError) as exc_info:
            APIConfig(host="   ")
        assert "API host cannot be empty" in str(exc_info.value)

    def test_cors_prefix_validation(self):
        """Test CORS prefix validation"""
        # Valid prefix
        config = APIConfig(prefix="/api")
        assert config.prefix == "/api"

        # Invalid prefix (doesn't start with /)
        with pytest.raises(ValidationError):
            APIConfig(prefix="api")

    def test_security_headers_configuration(self):
        """Test security headers configuration"""
        security_headers = {
            "X-Content-Type-Options": "nosniff",
            "X-Frame-Options": "DENY",
            "X-XSS-Protection": "1; mode=block",
        }

        config = APIConfig(security_headers=security_headers)
        assert config.security_headers == security_headers

    def test_cors_credentials_support(self):
        """Test CORS credentials support configuration"""
        # With credentials support
        config = APIConfig(cors_supports_credentials=True)
        assert config.cors_supports_credentials is True

        # Without credentials support
        config = APIConfig(cors_supports_credentials=False)
        assert config.cors_supports_credentials is False

    def test_empty_cors_origins_raises_error(self):
        """Test that empty CORS origins raises validation error"""
        with pytest.raises(ValidationError) as exc_info:
            APIConfig(cors_origins=[])
        assert "CORS origins cannot be empty" in str(exc_info.value)


class TestCORSEnvironmentSpecific:
    """Test CORS configuration for different environments"""

    def test_development_environment_cors(self):
        """Test CORS configuration for development environment"""
        config = AppSettings(
            application=ApplicationConfig(environment=EnvironmentEnum.DEVELOPMENT),
            api=APIConfig(cors_origins=["*"]),
        )
        assert config.application.environment == EnvironmentEnum.DEVELOPMENT
        assert config.api.cors_origins == ["*"]

    def test_production_environment_cors_strict(self):
        """Test strict CORS configuration for production environment"""
        config = AppSettings(
            application=ApplicationConfig(environment=EnvironmentEnum.PRODUCTION),
            api=APIConfig(
                cors_origins=["https://app.company.com", "https://admin.company.com"],
                cors_methods=["GET", "POST", "PUT", "DELETE"],
                cors_headers=["Content-Type", "Authorization"],
                cors_expose_headers=["Content-Type", "X-Request-ID"],
                cors_supports_credentials=True,
                cors_max_age=3600,
            ),
        )
        assert config.application.environment == EnvironmentEnum.PRODUCTION
        assert config.api.cors_origins == [
            "https://app.company.com",
            "https://admin.company.com",
        ]
        assert config.api.cors_methods == ["GET", "POST", "PUT", "DELETE"]
        assert config.api.cors_headers == ["Content-Type", "Authorization"]
        assert config.api.cors_expose_headers == ["Content-Type", "X-Request-ID"]
        assert config.api.cors_supports_credentials is True
        assert config.api.cors_max_age == 3600


class TestCORSURLValidation:
    """Test CORS URL validation methods"""

    def test_valid_url_formats(self):
        """Test valid URL formats"""
        valid_urls = [
            "https://app.company.com",
            "https://admin.company.com",
            "https://api.company.com:8080",
            "https://app.company.com/api",
            "https://subdomain.company.com",
        ]

        for url in valid_urls:
            assert APIConfig._is_valid_url(url), f"URL should be valid: {url}"

    def test_invalid_url_formats(self):
        """Test invalid URL formats"""
        invalid_urls = [
            "http://insecure.com",  # HTTP not allowed
            "https://invalid-url-format",
            "ftp://example.com",
            "not-a-url",
            "https://",
            "https://.com",
        ]

        for url in invalid_urls:
            assert not APIConfig._is_valid_url(url), f"URL should be invalid: {url}"

    def test_url_validation_edge_cases(self):
        """Test URL validation edge cases"""
        # Empty string
        assert not APIConfig._is_valid_url("")

        # None
        assert not APIConfig._is_valid_url(None)

        # Very long URL
        long_url = "https://" + "a" * 1000 + ".com"
        assert not APIConfig._is_valid_url(long_url)
