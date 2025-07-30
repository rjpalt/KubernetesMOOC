"""Integration tests for request logging middleware.

Tests that every request/response is properly logged with structured
information suitable for Grafana monitoring.
"""

import json
import logging
from io import StringIO

import pytest
from httpx import AsyncClient


class TestRequestLoggingMiddleware:
    """Test request logging middleware functionality."""

    @pytest.fixture
    def log_capture(self):
        """Capture log output for testing."""
        log_capture_string = StringIO()
        ch = logging.StreamHandler(log_capture_string)
        ch.setLevel(logging.INFO)
        
        # Get the request logger
        logger = logging.getLogger("request_logger")
        logger.addHandler(ch)
        logger.setLevel(logging.INFO)
        
        yield log_capture_string
        
        # Cleanup
        logger.removeHandler(ch)

    async def test_successful_request_logged(self, test_client: AsyncClient, log_capture):
        """Test that successful requests are logged with structured data."""
        response = await test_client.post("/todos", json={"text": "Test todo"})
        assert response.status_code == 201
        
        log_contents = log_capture.getvalue()
        
        # Should contain request and response logs
        assert "REQUEST" in log_contents
        assert "RESPONSE" in log_contents
        
        # Should contain method and path
        assert "POST" in log_contents
        assert "/todos" in log_contents
        
        # Should contain status code
        assert "201" in log_contents

    async def test_validation_error_logged(self, test_client: AsyncClient, log_capture):
        """Test that validation errors are logged for monitoring."""
        # Send request with text too long (141+ characters)
        long_text = "a" * 141
        response = await test_client.post("/todos", json={"text": long_text})
        assert response.status_code == 422
        
        log_contents = log_capture.getvalue()
        
        # Should log validation failure
        assert "VALIDATION_ERROR" in log_contents
        assert "422" in log_contents
        assert "error" in log_contents

    async def test_not_found_error_logged(self, test_client: AsyncClient, log_capture):
        """Test that 404 errors are logged for monitoring."""
        response = await test_client.get("/todos/nonexistent-id")
        assert response.status_code == 404
        
        log_contents = log_capture.getvalue()
        
        # Should log not found error
        assert "NOT_FOUND" in log_contents or "404" in log_contents
        assert "error" in log_contents

    async def test_all_error_types_logged(self, test_client: AsyncClient, log_capture):
        """Test that all HTTP error types are properly categorized."""
        # Test 422 validation error
        response = await test_client.post("/todos", json={"text": "a" * 141})
        assert response.status_code == 422
        
        # Test 404 not found
        response = await test_client.get("/todos/nonexistent")
        assert response.status_code == 404
        
        log_contents = log_capture.getvalue()
        
        # Should contain error classifications
        assert "VALIDATION_ERROR" in log_contents
        assert any(error_type in log_contents for error_type in ["NOT_FOUND", "404"])
        
        # All errors should be marked as errors
        assert log_contents.count('"error": true') >= 2

    async def test_request_logging_includes_response_time(self, test_client: AsyncClient, log_capture):
        """Test that request logs include response time for performance monitoring."""
        response = await test_client.get("/todos")
        assert response.status_code == 200
        
        log_contents = log_capture.getvalue()
        
        # Should contain response time information
        assert any(keyword in log_contents for keyword in ["response_time", "duration", "ms"])

    async def test_request_logging_json_structured(self, test_client: AsyncClient, log_capture):
        """Test that logs are in JSON format for Grafana parsing."""
        response = await test_client.get("/be-health")
        assert response.status_code == 200
        
        log_contents = log_capture.getvalue()
        log_lines = [line.strip() for line in log_contents.split('\n') if line.strip()]
        
        # At least one log line should be valid JSON
        json_found = False
        for line in log_lines:
            try:
                parsed = json.loads(line)
                if "method" in parsed or "path" in parsed or "status_code" in parsed:
                    json_found = True
                    break
            except json.JSONDecodeError:
                continue
        
        assert json_found, f"No JSON-structured logs found in: {log_contents}"

    async def test_request_logging_contains_required_fields(self, test_client: AsyncClient, log_capture):
        """Test that request logs contain all required fields for monitoring."""
        response = await test_client.get("/todos")
        assert response.status_code == 200
        
        log_contents = log_capture.getvalue()
        
        # Required fields for Grafana monitoring
        required_fields = ["method", "path", "status_code", "timestamp"]
        
        for field in required_fields:
            assert field in log_contents or field.upper() in log_contents, f"Missing required field: {field}"

    async def test_large_request_body_logged_safely(self, test_client: AsyncClient, log_capture):
        """Test that large request bodies are handled safely in logs."""
        # Create a todo with maximum allowed length
        max_text = "a" * 140
        response = await test_client.post("/todos", json={"text": max_text})
        assert response.status_code == 201
        
        log_contents = log_capture.getvalue()
        
        # Should not log the entire body (privacy/performance)
        # But should log that a request was made
        assert "POST" in log_contents
        assert "/todos" in log_contents
        
        # Body should be truncated or not included entirely
        full_body_count = log_contents.count(max_text)
        assert full_body_count <= 1, "Request body should not appear multiple times in logs"
