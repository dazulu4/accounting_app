"""
Tests for error handlers
"""

from unittest.mock import Mock, patch

import pytest

from domain.exceptions.business_exceptions import (
    TaskNotFoundException,
    UserNotActiveException,
    UserNotFoundException,
    ValidationException,
)
from infrastructure.helpers.errors.error_handlers import (
    ErrorResponseBuilder,
    HTTPErrorHandler,
    create_not_found_error_response,
    create_validation_error_response,
)


class TestHTTPErrorHandler:
    """Test HTTP error handler"""

    def test_handle_business_exception(self):
        """Test handling business exceptions"""
        exception = UserNotFoundException("User not found")

        # Mock request context
        mock_request = Mock()
        mock_request.path = "/api/users/123"
        mock_request.method = "GET"
        mock_request.request_id = "test-request-id"

        with patch(
            "infrastructure.helpers.errors.error_handlers.request",
            mock_request,
        ):
            response_data, status_code = HTTPErrorHandler.handle_exception(exception)

            assert status_code == 404
            assert response_data["error"]["type"] == "USER_NOT_FOUND"
            assert (
                response_data["error"]["message"]
                == "[USER_NOT_FOUND] User with ID 'User not found' not found"
            )
            assert response_data["error"]["request_id"] == "test-request-id"
            assert response_data["error"]["path"] == "/api/users/123"
            assert response_data["error"]["method"] == "GET"
            assert "timestamp" in response_data["error"]

    def test_handle_unknown_exception(self):
        """Test handling unknown exceptions"""
        exception = ValueError("Invalid value")

        # Mock request context
        mock_request = Mock()
        mock_request.path = "/api/tasks"
        mock_request.method = "POST"
        mock_request.request_id = "test-request-id"

        with patch(
            "infrastructure.helpers.errors.error_handlers.request",
            mock_request,
        ):
            response_data, status_code = HTTPErrorHandler.handle_exception(exception)

            assert status_code == 400
            assert response_data["error"]["type"] == "INVALID_REQUEST"
            assert (
                response_data["error"]["message"]
                == "The request contains invalid data."
            )
            assert response_data["error"]["request_id"] == "test-request-id"
            assert response_data["error"]["path"] == "/api/tasks"
            assert response_data["error"]["method"] == "POST"

    def test_handle_exception_without_request_context(self):
        """Test handling exceptions without request context"""
        exception = TaskNotFoundException("Task not found")

        with patch("infrastructure.helpers.errors.error_handlers.request", None):
            response_data, status_code = HTTPErrorHandler.handle_exception(exception)

            assert status_code == 404
            assert response_data["error"]["type"] == "TASK_NOT_FOUND"
            assert response_data["error"]["request_id"] is None
            assert response_data["error"]["path"] is None
            assert response_data["error"]["method"] is None

    def test_generate_request_id_when_not_exists(self):
        """Test generating request ID when not exists"""
        exception = UserNotActiveException("User is not active")

        # Mock request context without request_id initially
        mock_request = Mock()
        mock_request.path = "/api/users/123"
        mock_request.method = "GET"
        # Remove request_id attribute to simulate it doesn't exist
        delattr(mock_request, "request_id")

        with patch(
            "infrastructure.helpers.errors.error_handlers.request",
            mock_request,
        ):
            response_data, status_code = HTTPErrorHandler.handle_exception(exception)

            assert status_code == 422
            assert response_data["error"]["request_id"] is not None
            assert len(response_data["error"]["request_id"]) > 0
            # Verify request_id was set on request object
            assert hasattr(mock_request, "request_id")

    def test_handle_validation_exception(self):
        """Test handling validation exceptions"""
        exception = ValidationException("Validation failed")

        # Mock request context
        mock_request = Mock()
        mock_request.path = "/api/tasks"
        mock_request.method = "POST"
        mock_request.request_id = "test-request-id"

        with patch(
            "infrastructure.helpers.errors.error_handlers.request",
            mock_request,
        ):
            response_data, status_code = HTTPErrorHandler.handle_exception(exception)

            assert status_code == 422
            assert response_data["error"]["type"] == "VALIDATION_ERROR"
            assert (
                response_data["error"]["message"]
                == "[VALIDATION_ERROR] Validation failed"
            )

    def test_handle_internal_error_without_details(self):
        """Test handling internal errors without exposing details"""
        exception = Exception("Internal error")

        # Mock request context
        mock_request = Mock()
        mock_request.path = "/api/tasks"
        mock_request.method = "POST"
        mock_request.request_id = "test-request-id"

        with patch(
            "infrastructure.helpers.errors.error_handlers.request",
            mock_request,
        ):
            # Mock _should_include_details to return False (production mode)
            with patch.object(
                HTTPErrorHandler, "_should_include_details", return_value=False
            ):
                response_data, status_code = HTTPErrorHandler.handle_exception(
                    exception
                )

                assert status_code == 500
                assert response_data["error"]["type"] == "INTERNAL_ERROR"
                assert (
                    response_data["error"]["message"]
                    == "An internal server error occurred. Please try again later."
                )
                assert "exception_type" not in response_data["error"]
                assert "exception_message" not in response_data["error"]

    def test_handle_internal_error_with_details_in_development(self):
        """Test handling internal errors with details in development"""
        exception = Exception("Internal error")

        # Mock request context
        mock_request = Mock()
        mock_request.path = "/api/tasks"
        mock_request.method = "POST"
        mock_request.request_id = "test-request-id"

        with patch(
            "infrastructure.helpers.errors.error_handlers.request",
            mock_request,
        ):
            # Mock _should_include_details to return True (development mode)
            with patch.object(
                HTTPErrorHandler, "_should_include_details", return_value=True
            ):
                response_data, status_code = HTTPErrorHandler.handle_exception(
                    exception
                )

                assert status_code == 500
                assert response_data["error"]["type"] == "INTERNAL_ERROR"
                assert (
                    response_data["error"]["message"]
                    == "An internal server error occurred. Please try again later."
                )
                assert response_data["error"]["exception_type"] == "Exception"
                assert response_data["error"]["exception_message"] == "Internal error"


class TestErrorResponseBuilder:
    """Test error response builder"""

    def test_build_valid_error_response(self):
        """Test building valid error response"""
        # Mock request context
        mock_request = Mock()
        mock_request.path = "/api/test"
        mock_request.method = "GET"
        mock_request.request_id = "test-request-id"

        with patch(
            "infrastructure.helpers.errors.error_handlers.request",
            mock_request,
        ):
            builder = ErrorResponseBuilder()
            response_data, status_code = (
                builder.with_type("TEST_ERROR")
                .with_code("TEST_CODE")
                .with_message("Test error message")
                .with_status_code(400)
                .with_details({"field": "value"})
                .build()
            )

            assert status_code == 400
            assert response_data["error"]["type"] == "TEST_ERROR"
            assert response_data["error"]["code"] == "TEST_CODE"
            assert response_data["error"]["message"] == "Test error message"
            assert response_data["error"]["request_id"] == "test-request-id"
            assert response_data["error"]["path"] == "/api/test"
            assert response_data["error"]["method"] == "GET"
            assert response_data["error"]["details"] == {"field": "value"}
            assert "timestamp" in response_data["error"]

    def test_build_error_response_without_required_fields(self):
        """Test building error response without required fields"""
        builder = ErrorResponseBuilder()

        with pytest.raises(ValueError, match="Error type and message are required"):
            builder.build()

    def test_build_error_response_without_code(self):
        """Test building error response without code (should use type as code)"""
        # Mock request context
        mock_request = Mock()
        mock_request.path = "/api/test"
        mock_request.method = "GET"
        mock_request.request_id = "test-request-id"

        with patch(
            "infrastructure.helpers.errors.error_handlers.request",
            mock_request,
        ):
            builder = ErrorResponseBuilder()
            response_data, status_code = (
                builder.with_type("TEST_ERROR")
                .with_message("Test error message")
                .with_status_code(400)
                .build()
            )

            assert response_data["error"]["code"] == "TEST_ERROR"  # Uses type as code


class TestErrorResponseHelpers:
    """Test error response helper functions"""

    def test_create_validation_error_response(self):
        """Test creating validation error response"""
        # Mock request context
        mock_request = Mock()
        mock_request.path = "/api/tasks"
        mock_request.method = "POST"
        mock_request.request_id = "test-request-id"

        with patch(
            "infrastructure.helpers.errors.error_handlers.request",
            mock_request,
        ):
            field_errors = {
                "title": "Title is required",
                "description": "Description is required",
            }
            response_data, status_code = create_validation_error_response(
                "Validation failed", field_errors
            )

            assert status_code == 422
            assert response_data["error"]["type"] == "VALIDATION_ERROR"
            assert response_data["error"]["message"] == "Validation failed"
            assert response_data["error"]["details"]["field_errors"] == field_errors

    def test_create_not_found_error_response(self):
        """Test creating not found error response"""
        # Mock request context
        mock_request = Mock()
        mock_request.path = "/api/users/123"
        mock_request.method = "GET"
        mock_request.request_id = "test-request-id"

        with patch(
            "infrastructure.helpers.errors.error_handlers.request",
            mock_request,
        ):
            response_data, status_code = create_not_found_error_response("User", 123)

            assert status_code == 404
            assert response_data["error"]["type"] == "RESOURCE_NOT_FOUND"
            assert response_data["error"]["message"] == "User with ID '123' not found"
            assert response_data["error"]["details"]["resource_type"] == "User"
            assert response_data["error"]["details"]["resource_id"] == "123"
