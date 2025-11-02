"""
Test Module: Database Integration via Health Endpoint

Purpose:
    Validate database connectivity through backend health endpoint.

Scope:
    - Backend can query database (evidenced by todos_count in health response)
    - Database connection is stable across multiple requests

Dependencies:
    - Backend service deployed to staging
    - Database accessible from backend (Azure DBaaS)
    
Environment Variables:
    - STAGING_BACKEND_URL: Backend API base URL
    
Test Count: 2 tests
Execution Time: ~10 seconds

NOTE: These tests validate backend-to-database connectivity indirectly.
      Direct backend API endpoints (/todos) are not exposed via Gateway
      (they're only accessible to frontend service internally).
"""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_backend_can_query_database_for_count(staging_client: AsyncClient):
    """
    Verify backend can query database by checking todos_count in health endpoint.
    
    Steps:
        1. Send GET request to /be-health
        2. Assert 200 OK response
        3. Assert response contains todos_count field
        4. Assert todos_count is a valid integer
    
    Expected Result:
        Health endpoint returns todos_count, proving database connectivity
    """
    response = await staging_client.get("/be-health")
    
    assert response.status_code == 200, \
        f"Health check failed: {response.status_code}, {response.text}"
    
    health_data = response.json()
    assert "todos_count" in health_data, \
        f"Missing 'todos_count' field - backend may not be connected to database: {health_data}"
    
    todos_count = health_data["todos_count"]
    assert isinstance(todos_count, int), \
        f"todos_count should be integer, got {type(todos_count)}: {todos_count}"
    
    assert todos_count >= 0, \
        f"todos_count should be non-negative, got: {todos_count}"


@pytest.mark.asyncio
async def test_database_connection_stable_across_requests(staging_client: AsyncClient):
    """
    Verify database connection remains stable across multiple requests.
    
    Steps:
        1. Make first health check request
        2. Make second health check request
        3. Assert both succeed with 200 OK
        4. Assert both return valid todos_count
    
    Expected Result:
        Multiple consecutive database queries succeed (connection pooling works)
    """
    # First request
    response1 = await staging_client.get("/be-health")
    assert response1.status_code == 200, \
        f"First health check failed: {response1.status_code}"
    
    data1 = response1.json()
    assert "todos_count" in data1, \
        f"First request missing todos_count: {data1}"
    assert isinstance(data1["todos_count"], int), \
        f"First request todos_count invalid type: {type(data1['todos_count'])}"
    
    # Second request
    response2 = await staging_client.get("/be-health")
    assert response2.status_code == 200, \
        f"Second health check failed: {response2.status_code}"
    
    data2 = response2.json()
    assert "todos_count" in data2, \
        f"Second request missing todos_count: {data2}"
    assert isinstance(data2["todos_count"], int), \
        f"Second request todos_count invalid type: {type(data2['todos_count'])}"
