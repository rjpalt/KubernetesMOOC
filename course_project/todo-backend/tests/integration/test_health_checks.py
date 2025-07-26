"""Integration tests for backend health check endpoints.

These tests verify the backend's health endpoint, which is crucial
for Kubernetes health checks and service discovery.

Moved from frontend because: Each service should test its own health endpoints.
In Kubernetes, each service needs its own health checks for proper orchestration.
"""

from fastapi.testclient import TestClient


class TestBackendHealthEndpoint:
    """Test backend health check endpoint for Kubernetes readiness."""

    def test_health_endpoint_exists(self, test_client: TestClient):
        """Test that /be-health endpoint exists and responds.

        This test verifies that the health check endpoint is available
        and returns the expected response structure.
        """
        response = test_client.get("/be-health")

        assert response.status_code == 200

    def test_health_endpoint_returns_json(self, test_client: TestClient):
        """Test that health endpoint returns valid JSON."""
        response = test_client.get("/be-health")

        assert response.headers["content-type"] == "application/json"
        data = response.json()
        assert isinstance(data, dict)

    def test_health_endpoint_with_todos(self, test_client: TestClient):
        """Test health endpoint with todos present."""
        test_client.get("/be-health")

    def test_health_endpoint_todos_count_accurate(self, test_client: TestClient):
        """Test that health endpoint reports accurate todo count."""
        # Get current count via health endpoint
        health_response = test_client.get("/be-health")
        health_count = health_response.json()["todos_count"]

        # Get actual count via todos endpoint
        todos_response = test_client.get("/todos")
        actual_count = len(todos_response.json())

        # Should match
        assert health_count == actual_count

    def test_health_endpoint_after_todo_operations(self, test_client: TestClient):
        """Test health endpoint reflects changes after todo operations."""
        # Get initial count
        initial_health = test_client.get("/be-health")
        initial_count = initial_health.json()["todos_count"]

        # Add a todo
        test_client.post("/todos", json={"text": "Health test todo"})

        # Health should reflect the change
        updated_health = test_client.get("/be-health")
        updated_count = updated_health.json()["todos_count"]

        assert updated_count == initial_count + 1

    def test_health_endpoint_performance(self, test_client: TestClient):
        """Test that health endpoint responds quickly (important for K8s probes)."""
        import time

        start_time = time.time()
        response = test_client.get("/be-health")
        end_time = time.time()

        # Health check should be fast (< 1 second for K8s)
        response_time = end_time - start_time
        assert response_time < 1.0
        assert response.status_code == 200
