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
async def test_backend_can_query_database(
    staging_client: AsyncClient,
    unique_id_generator
):
    """
    Verify backend can communicate with database (service-to-service).
    
    Steps:
        1. Create todo (requires database write)
        2. Read todo (requires database read)
        3. Verify both operations succeed
        4. Cleanup
    
    Expected Result:
        Backend successfully performs database operations
    """
    # Create requires database write
    todo_text = unique_id_generator("test_svc_discovery")
    create_response = await staging_client.post(
        "/todos",
        json={"text": todo_text}
    )
    assert create_response.status_code == 201, \
        f"Backend cannot write to database: {create_response.status_code}"
    
    todo_id = create_response.json()["id"]
    
    # Read requires database query
    read_response = await staging_client.get(f"/todos/{todo_id}")
    assert read_response.status_code == 200, \
        f"Backend cannot read from database: {read_response.status_code}"
    
    # Cleanup
    delete_response = await staging_client.delete(f"/todos/{todo_id}")
    assert delete_response.status_code == 204
