"""
Test Module: Backend Health Checks

Purpose:
    Validate backend health endpoints return correct status and data.

Scope:
    - GET /be-health returns 200 with service name and todo count
    - Health endpoint structure matches expected schema

Dependencies:
    - Backend service deployed to staging
    - Database accessible from backend
    
Environment Variables:
    - STAGING_BACKEND_URL: Backend API base URL
    
Test Count: 2 tests
Execution Time: ~10 seconds
"""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_health_endpoint_returns_200_with_service_name(staging_client: AsyncClient):
    """
    Verify health endpoint returns 200 status with correct service name.
    
    Steps:
        1. Send GET request to /be-health
        2. Assert status code is 200
        3. Assert response contains "service" field
        4. Assert service name is "todo-backend"
    
    Expected Result:
        Health endpoint returns 200 with service name "todo-backend"
    """
    response = await staging_client.get("/be-health")
    
    assert response.status_code == 200, \
        f"Health check failed: {response.status_code}, body: {response.text}"
    
    health_data = response.json()
    assert "service" in health_data, \
        f"Missing 'service' field in health response: {health_data}"
    
    assert health_data["service"] == "todo-backend", \
        f"Expected service='todo-backend', got: {health_data['service']}"


@pytest.mark.asyncio
async def test_health_endpoint_includes_todo_count(staging_client: AsyncClient):
    """
    Verify health endpoint includes todo count field with valid value.
    
    Steps:
        1. Send GET request to /be-health
        2. Assert status code is 200
        3. Assert response contains "todo_count" field
        4. Assert todo_count is a non-negative integer
    
    Expected Result:
        Health endpoint returns todo_count >= 0
    """
    response = await staging_client.get("/be-health")
    
    assert response.status_code == 200, \
        f"Health check failed: {response.status_code}"
    
    health_data = response.json()
    assert "todo_count" in health_data, \
        f"Missing 'todo_count' field in health response: {health_data}"
    
    assert isinstance(health_data["todo_count"], int), \
        f"todo_count must be integer, got: {type(health_data['todo_count'])}"
    
    assert health_data["todo_count"] >= 0, \
        f"todo_count must be non-negative, got: {health_data['todo_count']}"
