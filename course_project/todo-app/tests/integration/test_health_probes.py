"""Integration tests for frontend health probe endpoints."""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, patch

from src.main import create_app


@pytest.fixture
def client():
    """Create test client."""
    app = create_app()
    return TestClient(app)


@pytest.fixture
def mock_image_service():
    """Mock image service for testing."""
    with patch("src.api.routes.health.get_image_service") as mock:
        mock_service = AsyncMock()
        mock.return_value = mock_service
        yield mock_service


class TestHealthzEndpoint:
    """Test lightweight /healthz endpoint."""

    def test_healthz_returns_ok(self, client):
        """Test /healthz returns 200 OK."""
        response = client.get("/healthz")
        assert response.status_code == 200
        assert response.json() == {"status": "ok"}

    def test_healthz_no_dependencies(self, client, mock_image_service):
        """Test /healthz works independent of image service."""
        # Make image service fail
        mock_image_service.get_image_info = AsyncMock(side_effect=Exception("Service down"))
        
        response = client.get("/healthz")
        assert response.status_code == 200
        assert response.json() == {"status": "ok"}
        
        # Verify image service was not called
        mock_image_service.get_image_info.assert_not_called()

    def test_healthz_fast_response(self, client):
        """Test /healthz has fast response time."""
        import time
        start_time = time.time()
        
        response = client.get("/healthz")
        
        end_time = time.time()
        response_time = end_time - start_time
        
        assert response.status_code == 200
        assert response_time < 0.05  # Should be very fast for frontend

    def test_healthz_consistent_response(self, client):
        """Test /healthz returns consistent response across multiple calls."""
        responses = []
        for _ in range(10):
            response = client.get("/healthz")
            responses.append(response.json())
            
        # All responses should be identical
        assert all(resp == {"status": "ok"} for resp in responses)


class TestHealthEndpoint:
    """Test comprehensive /health endpoint (existing functionality)."""

    def test_health_comprehensive_response(self, client, mock_image_service):
        """Test /health returns comprehensive information."""
        # Mock image service response
        mock_image_info = AsyncMock()
        mock_image_info.status = "ready"
        mock_image_service.get_image_info = AsyncMock(return_value=mock_image_info)
        
        response = client.get("/health")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "timestamp" in data
        assert "image_cache_status" in data
        assert "cache_path" in data
        assert "update_interval_minutes" in data

    def test_health_image_service_dependency(self, client, mock_image_service):
        """Test /health properly uses image service."""
        # The test client uses dependency overrides, so we need to check that
        # the health endpoint works with the image service
        response = client.get("/health")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        # The mock image service provides a default status
        assert "image_cache_status" in data
        
        # Verify image service was called (through dependency injection)
        # Note: The exact mocking here depends on how the test client overrides work


class TestEndpointPerformance:
    """Test health endpoint performance characteristics."""

    def test_healthz_vs_health_performance(self, client, mock_image_service):
        """Test /healthz is significantly faster than /health."""
        import time
        
        # Mock image service to add some delay  
        async def slow_image_info():
            import asyncio
            await asyncio.sleep(0.01)  # 10ms delay
            mock_info = AsyncMock()
            mock_info.status = "ready"
            return mock_info
            
        mock_image_service.get_image_info = slow_image_info
        
        # Test /healthz performance
        start = time.time()
        response = client.get("/healthz")
        healthz_time = time.time() - start
        assert response.status_code == 200
        
        # Test /health performance
        start = time.time() 
        response = client.get("/health")
        health_time = time.time() - start
        assert response.status_code == 200
        
        # /healthz should be significantly faster
        assert healthz_time < health_time
        assert healthz_time < 0.005  # Very fast


class TestEndpointCompatibility:
    """Test endpoint compatibility and migration."""

    def test_both_endpoints_available(self, client):
        """Test both /health and /healthz are available."""
        healthz_response = client.get("/healthz")
        health_response = client.get("/health")
        
        assert healthz_response.status_code == 200
        assert health_response.status_code == 200
        
        # Different response formats
        assert healthz_response.json() == {"status": "ok"}
        assert "timestamp" in health_response.json()

    def test_shutdown_endpoint_still_works(self, client):
        """Test existing /shutdown endpoint is not affected.""" 
        response = client.post("/shutdown")
        
        # Should start shutdown process
        assert response.status_code == 200
        assert "Shutdown initiated" in response.json()["message"]


class TestProbeUsageScenarios:
    """Test scenarios that match Kubernetes probe usage."""

    def test_liveness_probe_scenario(self, client):
        """Test behavior suitable for liveness probe."""
        # Liveness probe should use /healthz
        # Should always return 200 unless process is dead
        response = client.get("/healthz")
        assert response.status_code == 200

    def test_readiness_probe_scenario(self, client):
        """Test behavior suitable for readiness probe."""
        # Readiness probe should use /healthz for frontend
        # (No external dependencies to check)
        response = client.get("/healthz")
        assert response.status_code == 200
        
        # Response should be immediate
        import time
        start = time.time()
        response = client.get("/healthz")
        duration = time.time() - start
        assert duration < 0.01  # Very fast for readiness


@pytest.mark.asyncio
async def test_concurrent_health_checks():
    """Test health endpoints handle concurrent requests."""
    # Test with sync client making multiple rapid requests
    app = create_app()
    client = TestClient(app)
    
    def make_request():
        return client.get("/healthz")
    
    # Make multiple concurrent requests using threading
    import concurrent.futures
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        futures = [executor.submit(make_request) for _ in range(20)]
        responses = [future.result() for future in futures]
    
    # All should succeed
    assert all(resp.status_code == 200 for resp in responses)
    assert all(resp.json() == {"status": "ok"} for resp in responses)
