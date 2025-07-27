"""
Test Health Check Endpoints - Application Layer

Tests for simplified health check and version endpoints in main.py
following the refactorization plan.

Key Features:
- Test simplified health check endpoint
- Test version endpoint
- Test database connectivity check
- Mock database dependencies for unit testing
"""

import json
from datetime import datetime
from unittest.mock import patch

import pytest

from application.main import create_application


class TestHealthCheckEndpoints:
    """Test simplified health check endpoints"""

    @pytest.fixture
    def app(self):
        """Create test Flask application"""
        with patch("application.main.database_connection") as mock_db:
            # Mock database connection for testing
            mock_db.health_check.return_value = True
            app = create_application()
            app.config["TESTING"] = True
            yield app.test_client()

    def test_health_check_success(self, app):
        """Test successful health check with healthy database"""
        with patch("application.main.database_connection") as mock_db:
            mock_db.health_check.return_value = True

            response = app.get("/api/health")

            assert response.status_code == 200
            data = json.loads(response.data)

            assert data["status"] == "healthy"
            assert data["service"] == "task-manager"
            assert "timestamp" in data
            assert data["database"]["status"] == "healthy"

    def test_health_check_database_failure(self, app):
        """Test health check with database connection failure"""
        with patch("application.main.database_connection") as mock_db:
            mock_db.health_check.return_value = False

            response = app.get("/api/health")

            assert response.status_code == 503
            data = json.loads(response.data)

            assert data["status"] == "unhealthy"
            assert data["service"] == "task-manager"
            assert "timestamp" in data
            assert data["database"]["status"] == "unhealthy"

    def test_health_check_database_exception(self, app):
        """Test health check when database raises exception"""
        with patch("application.main.database_connection") as mock_db:
            mock_db.health_check.side_effect = Exception("Database connection error")

            response = app.get("/api/health")

            assert response.status_code == 503
            data = json.loads(response.data)

            assert data["status"] == "unhealthy"
            assert "error" in data["database"]
            assert "timestamp" in data

    def test_version_endpoint(self, app):
        """Test version information endpoint"""
        response = app.get("/api/version")

        assert response.status_code == 200
        data = json.loads(response.data)

        assert data["version"] == "1.0.0"
        assert data["service"] == "task-manager"
        assert "environment" in data
        assert "timestamp" in data

    def test_health_check_response_format(self, app):
        """Test that health check response has correct format"""
        with patch("application.main.database_connection") as mock_db:
            mock_db.health_check.return_value = True

            response = app.get("/api/health")
            data = json.loads(response.data)

            # Verify required fields are present
            required_fields = ["status", "service", "timestamp", "database"]
            for field in required_fields:
                assert field in data

            # Verify database field structure
            assert "status" in data["database"]

            # Verify timestamp format (ISO format)
            timestamp = data["timestamp"]
            datetime.fromisoformat(timestamp.replace("Z", "+00:00"))

    def test_health_check_content_type(self, app):
        """Test that health check returns JSON content type"""
        with patch("application.main.database_connection") as mock_db:
            mock_db.health_check.return_value = True

            response = app.get("/api/health")

            assert "application/json" in response.content_type


class TestDeprecatedEndpoints:
    """Test that deprecated endpoints no longer exist"""

    @pytest.fixture
    def app(self):
        """Create test Flask application"""
        with patch("application.main.database_connection") as mock_db:
            mock_db.health_check.return_value = True
            app = create_application()
            app.config["TESTING"] = True
            yield app.test_client()

    def test_detailed_health_check_removed(self, app):
        """Test that /api/health/detailed endpoint was removed"""
        response = app.get("/api/health/detailed")
        assert response.status_code == 404

    def test_test_error_endpoints_removed(self, app):
        """Test that /api/test/error endpoints were removed"""
        error_types = ["validation", "not_found", "business", "internal"]

        for error_type in error_types:
            response = app.get(f"/api/test/error/{error_type}")
            assert response.status_code == 404
