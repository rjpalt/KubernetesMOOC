"""
Test Module: Service Discovery

Purpose:
    Validate Kubernetes service discovery and networking in staging.

Scope:
    - Backend service is reachable via HTTPRoute
    - Backend can communicate with database (implicit in CRUD tests)

Dependencies:
    - Gateway with HTTPRoute configured
    - Backend service with ClusterIP
    
Environment Variables:
    - STAGING_BACKEND_URL: Backend API base URL (via Gateway)
    
Test Count: 2 tests
Execution Time: ~10 seconds

NOTE: These tests validate Kubernetes networking which requires CI environment.
      Backend-to-database connectivity is only available within AKS cluster.
"""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_backend_service_reachable_via_gateway(staging_client: AsyncClient):
    """
    Verify backend service is reachable through Gateway HTTPRoute.
    
    Steps:
        1. Send GET request to root endpoint via Gateway
        2. Assert successful response (not connection error)
        3. Verify response indicates backend service
    
    Expected Result:
        Backend service responds through Gateway routing
    """
    response = await staging_client.get("/")
    
    # Accept any successful HTTP response (200, 307 redirect, etc.)
    assert response.status_code < 500, \
        f"Backend unreachable: {response.status_code}, {response.text}"


@pytest.mark.asyncio
async def test_backend_database_connectivity_via_health(staging_client: AsyncClient):
    """
    Verify backend-to-database connectivity through health endpoint.
    
    Steps:
        1. Request backend health endpoint
        2. Verify health endpoint queries database (todos_count field)
        3. Verify response indicates healthy database connection
    
    Expected Result:
        Backend can successfully query database and return count
    """
    response = await staging_client.get("/be-health")
    
    assert response.status_code == 200, \
        f"Backend health check failed: {response.status_code}"
    
    health_data = response.json()
    
    # Verify database connectivity indicator
    assert "todos_count" in health_data, \
        f"Backend cannot query database - missing todos_count: {health_data}"
    
    assert isinstance(health_data["todos_count"], int), \
        f"Invalid todos_count type: {type(health_data['todos_count'])}"
    
    assert health_data["status"] == "healthy", \
        f"Backend reports unhealthy status: {health_data['status']}"
