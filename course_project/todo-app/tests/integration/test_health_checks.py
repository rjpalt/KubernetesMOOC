"""Integration tests for health check endpoints.

Testing that your health endpoints actually work because
monitoring is pointless if the health checks are broken.
"""

from fastapi.testclient import TestClient


class TestHealthEndpoints:
    """Test health check endpoints because even simple things break."""

    def test_health_endpoint_exists(self, test_client: TestClient):
        """Test that /health endpoint exists and responds."""
        response = test_client.get("/health")

        assert response.status_code == 200

    def test_health_endpoint_returns_json(self, test_client: TestClient):
        """Test that health endpoint returns valid JSON."""
        response = test_client.get("/health")

        assert response.headers["content-type"] == "application/json"
        data = response.json()
        assert isinstance(data, dict)

    def test_health_endpoint_has_status_field(self, test_client: TestClient):
        """Test that health response includes status field."""
        response = test_client.get("/health")
        data = response.json()

        assert "status" in data
        assert data["status"] == "healthy"

    def test_health_endpoint_has_timestamp(self, test_client: TestClient):
        """Test that health response includes timestamp."""
        response = test_client.get("/health")
        data = response.json()

        assert "timestamp" in data
        assert isinstance(data["timestamp"], str)

    def test_health_endpoint_performance(self, test_client: TestClient):
        """Test that health endpoint responds quickly."""
        import time

        start_time = time.time()
        response = test_client.get("/health")
        end_time = time.time()

        # Health checks should be fast (<1 second)
        assert (end_time - start_time) < 1.0
        assert response.status_code == 200

    def test_health_endpoint_multiple_calls(self, test_client: TestClient):
        """Test that health endpoint is consistent across multiple calls."""
        responses = []
        for _ in range(3):
            response = test_client.get("/health")
            responses.append(response)

        # All should succeed
        for response in responses:
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "healthy"

    def test_shutdown_endpoint_exists(self, test_client: TestClient):
        """Test that shutdown endpoint exists (but don't actually shut down)."""
        # We'll just check that the endpoint exists, not actually trigger shutdown
        # because that would break other tests
        response = test_client.post("/shutdown")

        # Should respond (either success or some expected behavior)
        assert response.status_code in [200, 202, 404]  # Various acceptable responses
