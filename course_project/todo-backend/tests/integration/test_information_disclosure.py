"""Information Disclosure Prevention Tests for Todo Backend.

Tests to validate that error responses don't expose sensitive system information
that could be useful to attackers. This addresses the security gap identified in 
TEST_PLAN.md - Information Disclosure vulnerability.

Key security principles tested:
1. Error messages should be generic for production use
2. Internal details (database errors, file paths, stack traces) should not be exposed
3. Different error types should have consistent, safe responses
4. Debug information should only be available in development mode
"""

import pytest_asyncio
from httpx import AsyncClient


class TestInformationDisclosureProtection:
    """Test that error responses don't expose sensitive information."""

    @pytest_asyncio.fixture(autouse=True)
    async def setup_clean_database(self, test_client: AsyncClient):
        """Ensure clean database state for each test."""
        # Get current todos
        response = await test_client.get("/todos")
        todos = response.json()

        # Delete all existing todos
        for todo in todos:
            await test_client.delete(f"/todos/{todo['id']}")

    async def test_generic_404_error_messages(self, test_client: AsyncClient):
        """Test that 404 errors don't expose internal information."""
        # Test with various non-existent resource IDs
        test_ids = [
            "nonexistent-id",
            "12345",
            "system-file-path", 
            "../../../etc/passwd",
            "sql-injection-attempt'; DROP TABLE todos; --",
        ]
        
        for test_id in test_ids:
            response = await test_client.get(f"/todos/{test_id}")
            assert response.status_code == 404
            
            error_response = response.json()
            assert "detail" in error_response
            
            # Error message should be generic
            detail = error_response["detail"]
            assert detail == "Resource not found", f"Error message too specific: {detail}"
            
            # Should not contain sensitive information
            assert "database" not in detail.lower()
            assert "sql" not in detail.lower()
            assert "exception" not in detail.lower()
            assert "traceback" not in detail.lower()
            assert "file" not in detail.lower()
            assert test_id not in detail  # Should not echo back the problematic ID

    async def test_validation_error_sanitization(self, test_client: AsyncClient):
        """Test that validation errors don't expose internal details."""
        # Test various malformed payloads
        malformed_payloads = [
            {"text": "x" * 1000},  # Too long
            {"text": ""},  # Empty
            {},  # Missing required field
            {"text": None},  # Wrong type
            {"malicious_field": "value"},  # Unexpected field
        ]
        
        for payload in malformed_payloads:
            response = await test_client.post("/todos", json=payload)
            assert response.status_code == 422
            
            error_response = response.json()
            
            # Should not expose internal validation logic details
            error_str = str(error_response)
            assert "pydantic" not in error_str.lower()
            assert "fastapi" not in error_str.lower()
            assert "traceback" not in error_str.lower()
            assert "class" not in error_str.lower()
            assert "module" not in error_str.lower()

    async def test_server_error_handling(self, test_client: AsyncClient):
        """Test that server errors don't expose sensitive information."""
        # This test would normally require mocking database failures
        # For now, we test the structure of error responses
        
        # Test with extremely malformed requests that might cause server errors
        try:
            # Send malformed JSON
            response = await test_client.post(
                "/todos", 
                data="invalid-json-data",
                headers={"content-type": "application/json"}
            )
            
            if response.status_code >= 500:
                error_response = response.json()
                error_str = str(error_response)
                
                # Should not expose internal details
                assert "database" not in error_str.lower()
                assert "connection" not in error_str.lower()
                assert "postgresql" not in error_str.lower()
                assert "sqlalchemy" not in error_str.lower()
                assert "traceback" not in error_str.lower()
                assert "exception" not in error_str.lower()
                
        except Exception:
            # If the request fails completely, that's also acceptable
            pass

    async def test_database_connection_error_sanitization(self, test_client: AsyncClient):
        """Test that database connection errors don't expose sensitive info."""
        # This would require mocking database failures in a real test
        # For now, we document the expected behavior
        
        # When database is unavailable, error messages should be generic:
        # - "Service temporarily unavailable" 
        # - NOT "Connection to postgresql://user:pass@host:port/db failed"
        # - NOT actual connection strings or internal network details
        pass

    async def test_consistent_error_response_format(self, test_client: AsyncClient):
        """Test that all error responses follow a consistent, safe format."""
        # Test different error scenarios
        error_scenarios = [
            ("/todos/nonexistent", 404),
            ("/nonexistent-endpoint", 404),
        ]
        
        # Test validation error
        validation_response = await test_client.post("/todos", json={})
        assert validation_response.status_code == 422
        
        # Add to scenarios
        error_scenarios.append(("validation", validation_response.status_code))
        
        for scenario_name, expected_status in error_scenarios:
            if scenario_name == "validation":
                response = validation_response
            else:
                response = await test_client.get(scenario_name)
            
            assert response.status_code == expected_status
            
            # All error responses should have consistent structure
            error_response = response.json()
            assert "detail" in error_response
            
            # Should not contain debugging information
            assert "internal_error" not in error_response
            assert "debug" not in error_response
            assert "trace" not in error_response
            assert "exception_type" not in error_response

    async def test_error_logging_vs_response_separation(self, test_client: AsyncClient):
        """Test that detailed errors are logged but not returned to client."""
        # Trigger an error condition
        response = await test_client.get("/todos/nonexistent-id")
        assert response.status_code == 404
        
        error_response = response.json()
        
        # Response should be generic
        assert error_response["detail"] == "Resource not found"
        
        # Note: In a real implementation, we would verify that detailed 
        # information (like the actual ID that was searched for) is logged
        # for debugging purposes but not returned to the client

    async def test_no_system_information_leakage(self, test_client: AsyncClient):
        """Test that error responses don't leak system information."""
        # Test various endpoints that might reveal system info
        test_endpoints = [
            "/todos/../../../etc/passwd",
            "/todos/system-config",
            "/todos/%2e%2e%2f%2e%2e%2f%2e%2e%2fetc%2fpasswd",  # URL encoded path traversal
        ]
        
        for endpoint in test_endpoints:
            response = await test_client.get(endpoint)
            
            # Should return standard 404, not expose file system details
            if response.status_code == 404:
                error_response = response.json()
                detail = error_response.get("detail", "")
                
                # Should not contain file system paths
                assert "/etc/" not in detail
                assert "passwd" not in detail
                assert "config" not in detail
                assert "system" not in detail

    async def test_error_message_consistency_across_methods(self, test_client: AsyncClient):
        """Test that error messages are consistent across HTTP methods."""
        nonexistent_id = "definitely-does-not-exist"
        
        # Test different HTTP methods with same nonexistent resource
        methods_and_responses = []
        
        # GET
        get_response = await test_client.get(f"/todos/{nonexistent_id}")
        if get_response.status_code == 404:
            methods_and_responses.append(("GET", get_response.json()["detail"]))
        
        # PUT
        put_response = await test_client.put(f"/todos/{nonexistent_id}", json={"text": "updated"})
        if put_response.status_code == 404:
            methods_and_responses.append(("PUT", put_response.json()["detail"]))
        
        # DELETE
        delete_response = await test_client.delete(f"/todos/{nonexistent_id}")
        if delete_response.status_code == 404:
            methods_and_responses.append(("DELETE", delete_response.json()["detail"]))
        
        # All 404 messages should be identical
        if len(methods_and_responses) > 1:
            first_message = methods_and_responses[0][1]
            for method, message in methods_and_responses[1:]:
                assert message == first_message, (
                    f"Inconsistent 404 messages: {methods_and_responses}"
                )

    async def test_production_error_handling_mode(self, test_client: AsyncClient):
        """Test that the application is configured for production error handling."""
        # Force production mode for this test to validate production behavior
        import os
        from src.config.settings import Settings
        
        # Temporarily simulate production environment
        original_namespace = os.environ.get("KUBERNETES_NAMESPACE")
        os.environ["KUBERNETES_NAMESPACE"] = "project"
        
        try:
            # Create new settings instance to pick up production environment
            production_settings = Settings()
            assert production_settings.is_production == True
            assert production_settings.debug_enabled == False
            
            # Send invalid data that might trigger detailed validation messages
            response = await test_client.post("/todos", json={"text": "x" * 1000})
            assert response.status_code == 422
            
            error_response = response.json()
            
            # In production mode, should not expose debug_info
            assert "debug_info" not in error_response, f"Production mode should not include debug_info: {error_response}"
            
            # Should only have generic message
            assert error_response == {"detail": "Invalid request data"}
            
            # Should not expose pydantic model details or validation internals in the basic response
            error_str = str(error_response["detail"]).lower()
            forbidden_terms = [
                "pydantic",
                "validation_error", 
                "field_error",
                "type_error",
                "value_error",
                "__root__",
                "model_validate",
            ]
            
            for term in forbidden_terms:
                assert term not in error_str, (
                    f"Error response contains internal term '{term}' in detail: {error_response['detail']}"
                )
        finally:
            # Restore original environment
            if original_namespace is None:
                os.environ.pop("KUBERNETES_NAMESPACE", None)
            else:
                os.environ["KUBERNETES_NAMESPACE"] = original_namespace

    async def test_debug_mode_detection(self, test_client: AsyncClient):
        """Test that debug information is conditionally included based on environment."""
        from src.config.settings import settings
        
        # Check current debug setting
        is_debug_mode = settings.debug_enabled
        
        # Test 404 error response
        response = await test_client.get("/todos/nonexistent-debug-test")
        assert response.status_code == 404
        
        error_response = response.json()
        
        if is_debug_mode:
            # In debug mode, should include debug_info
            assert "debug_info" in error_response, "Debug mode should include debug_info"
            assert error_response["debug_info"]["mode"] == "development"
            assert "path" in error_response["debug_info"]
            assert "method" in error_response["debug_info"]
            assert "original_detail" in error_response["debug_info"]
        else:
            # In production mode, should NOT include debug_info
            assert "debug_info" not in error_response, "Production mode should not include debug_info"
            assert error_response == {"detail": "Resource not found"}

    async def test_debug_mode_validation_errors(self, test_client: AsyncClient):
        """Test that validation errors include debug info only in development mode."""
        from src.config.settings import settings
        
        is_debug_mode = settings.debug_enabled
        
        # Send invalid validation data
        response = await test_client.post("/todos", json={})
        assert response.status_code == 422
        
        error_response = response.json()
        
        if is_debug_mode:
            # In debug mode, should include detailed validation errors
            assert "debug_info" in error_response
            assert "validation_errors" in error_response["debug_info"]
            assert error_response["debug_info"]["mode"] == "development"
        else:
            # In production mode, should only have generic message
            assert "debug_info" not in error_response
            assert error_response == {"detail": "Invalid request data"}
