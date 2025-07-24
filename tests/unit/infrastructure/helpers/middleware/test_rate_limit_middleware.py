"""
Tests for Rate Limiting Middleware

Tests the rate limiting functionality including IP detection,
request tracking, and rate limit enforcement.
"""

import time
import pytest
from unittest.mock import Mock, patch
from flask import Flask, request
from infrastructure.helpers.middleware.rate_limit_middleware import RateLimitMiddleware


class TestRateLimitMiddleware:
    """Test rate limiting middleware functionality"""

    def test_rate_limit_middleware_initialization(self):
        """Test middleware initialization"""
        mock_app = Mock()
        middleware = RateLimitMiddleware(mock_app)
        assert middleware.requests_per_second == 10
        assert middleware.window_size == 60
        assert middleware.app == mock_app

    def test_get_client_ip_with_x_forwarded_for(self):
        """Test client IP extraction with X-Forwarded-For"""
        mock_app = Mock()
        middleware = RateLimitMiddleware(mock_app)

        environ = {
            "HTTP_X_FORWARDED_FOR": "192.168.1.1, 10.0.0.1",
            "REMOTE_ADDR": "127.0.0.1",
        }

        client_ip = middleware._get_client_ip(environ)
        assert client_ip == "192.168.1.1"

    def test_get_client_ip_with_x_real_ip(self):
        """Test client IP extraction with X-Real-IP"""
        mock_app = Mock()
        middleware = RateLimitMiddleware(mock_app)

        environ = {"HTTP_X_REAL_IP": "192.168.1.2", "REMOTE_ADDR": "127.0.0.1"}

        client_ip = middleware._get_client_ip(environ)
        assert client_ip == "192.168.1.2"

    def test_get_client_ip_fallback(self):
        """Test client IP extraction fallback"""
        mock_app = Mock()
        middleware = RateLimitMiddleware(mock_app)

        environ = {"REMOTE_ADDR": "192.168.1.3"}

        client_ip = middleware._get_client_ip(environ)
        assert client_ip == "192.168.1.3"

    def test_get_client_ip_unknown(self):
        """Test client IP extraction when remote_addr is None"""
        mock_app = Mock()
        middleware = RateLimitMiddleware(mock_app)

        environ = {}

        client_ip = middleware._get_client_ip(environ)
        assert client_ip == "unknown"

    def test_rate_limit_not_exceeded(self):
        """Test rate limit not exceeded"""
        mock_app = Mock()
        middleware = RateLimitMiddleware(mock_app)
        middleware.requests_per_second = 5
        client_ip = "192.168.1.1"

        # Make 3 requests (under limit)
        for i in range(3):
            is_limited, headers = middleware._is_rate_limited(client_ip)
            assert not is_limited
            assert headers["remaining"] == 5 - (i + 1)

    def test_rate_limit_exceeded(self):
        """Test rate limit exceeded"""
        mock_app = Mock()
        middleware = RateLimitMiddleware(mock_app)
        middleware.requests_per_second = 2
        client_ip = "192.168.1.1"

        # Make 2 requests (at limit)
        for i in range(2):
            is_limited, headers = middleware._is_rate_limited(client_ip)
            assert not is_limited

        # Make 3rd request (over limit)
        is_limited, headers = middleware._is_rate_limited(client_ip)
        assert is_limited
        assert headers["remaining"] == 0

    def test_rate_limit_window_cleanup(self):
        """Test old requests cleanup"""
        mock_app = Mock()
        middleware = RateLimitMiddleware(mock_app)
        middleware.requests_per_second = 5
        middleware.window_size = 1
        client_ip = "192.168.1.1"

        # Make requests
        for i in range(3):
            middleware._is_rate_limited(client_ip)

        # Wait for window to expire
        time.sleep(1.1)

        # Should be able to make requests again
        is_limited, headers = middleware._is_rate_limited(client_ip)
        assert not is_limited
        assert headers["remaining"] == 4

    def test_rate_limit_different_ips(self):
        """Test rate limiting for different IP addresses"""
        mock_app = Mock()
        middleware = RateLimitMiddleware(mock_app)
        middleware.requests_per_second = 2
        ip1 = "192.168.1.1"
        ip2 = "192.168.1.2"

        # Make requests for IP1
        for i in range(2):
            is_limited, headers = middleware._is_rate_limited(ip1)
            assert not is_limited

        # IP1 should be limited
        is_limited, headers = middleware._is_rate_limited(ip1)
        assert is_limited

        # IP2 should not be limited
        is_limited, headers = middleware._is_rate_limited(ip2)
        assert not is_limited
        assert headers["remaining"] == 1

    def test_rate_limit_headers_structure(self):
        """Test rate limit headers structure"""
        mock_app = Mock()
        middleware = RateLimitMiddleware(mock_app)
        client_ip = "192.168.1.1"

        is_limited, headers = middleware._is_rate_limited(client_ip)

        assert "limit" in headers
        assert "remaining" in headers
        assert "reset_time" in headers
        assert headers["limit"] == 10
        assert headers["remaining"] == 9
        assert isinstance(headers["reset_time"], int)

    def test_rate_limit_skip_health_endpoints(self):
        """Test that health endpoints are skipped"""
        mock_app = Mock()
        middleware = RateLimitMiddleware(mock_app)

        # Mock the app to return a response
        mock_app.return_value = [b'{"status": "ok"}']

        environ = {"PATH_INFO": "/api/health", "REMOTE_ADDR": "192.168.1.1"}
        start_response = Mock()

        # Should not be rate limited
        result = middleware(environ, start_response)
        assert result == [b'{"status": "ok"}']


class TestRateLimitConfig:
    """Test rate limiting configuration"""

    def test_valid_rate_limit_config(self):
        """Test valid rate limit configuration"""
        from application.config.environment import RateLimitConfig

        config = RateLimitConfig(
            enabled=True, requests_per_second=10, window_size_seconds=60, burst_limit=20
        )
        assert config.enabled is True
        assert config.requests_per_second == 10
        assert config.window_size_seconds == 60
        assert config.burst_limit == 20

    def test_invalid_burst_limit_raises_error(self):
        """Test invalid burst limit raises error"""
        from application.config.environment import RateLimitConfig
        from pydantic import ValidationError

        with pytest.raises(ValidationError) as exc_info:
            RateLimitConfig(
                requests_per_second=10, burst_limit=5  # Less than requests_per_second
            )
        assert "Burst limit must be >= requests per second" in str(exc_info.value)

    def test_rate_limit_config_defaults(self):
        """Test rate limit configuration defaults"""
        from application.config.environment import RateLimitConfig

        config = RateLimitConfig()
        assert config.enabled is True
        assert config.requests_per_second == 10
        assert config.window_size_seconds == 60
        assert config.burst_limit == 20

    def test_rate_limit_config_validation(self):
        """Test rate limit configuration validation"""
        from application.config.environment import RateLimitConfig
        from pydantic import ValidationError

        # Test minimum values
        with pytest.raises(ValidationError):
            RateLimitConfig(requests_per_second=0)

        with pytest.raises(ValidationError):
            RateLimitConfig(window_size_seconds=5)  # Less than 10

        with pytest.raises(ValidationError):
            RateLimitConfig(burst_limit=0)

        # Test maximum values
        with pytest.raises(ValidationError):
            RateLimitConfig(requests_per_second=1001)  # More than 1000

        with pytest.raises(ValidationError):
            RateLimitConfig(window_size_seconds=3601)  # More than 3600

        with pytest.raises(ValidationError):
            RateLimitConfig(burst_limit=1001)  # More than 1000
