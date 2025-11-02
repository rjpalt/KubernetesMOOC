"""
Test Module: Database Integration via API

Purpose:
    Validate database connectivity and data persistence through backend API.

Scope:
    - Creating todo via API persists data in database
    - Reading todo via API retrieves persisted data

Dependencies:
    - Backend service deployed to staging
    - Database accessible from backend (Azure DBaaS)
    
Environment Variables:
    - STAGING_BACKEND_URL: Backend API base URL
    
Test Count: 2 tests
Execution Time: ~20 seconds

NOTE: These tests require CI environment execution as Azure DBaaS is not
      publicly accessible. Local execution will fail with connection errors.
"""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_create_todo_persists_in_database(
    staging_client: AsyncClient,
    unique_id_generator
):
    """
    Verify creating a todo via API persists data in database.
    
    Steps:
        1. Generate unique todo text
        2. POST /todos with todo data
        3. Assert 201 Created response
        4. Assert response contains created todo with ID
        5. GET /todos to verify todo exists
        6. DELETE created todo (cleanup)
    
    Expected Result:
        Todo created via API persists and is retrievable
    """
    # Arrange
    todo_text = unique_id_generator("test_todo")
    
    # Act - Create
    create_response = await staging_client.post(
        "/todos",
        json={"text": todo_text}
    )
    
    # Assert - Create
    assert create_response.status_code == 201, \
        f"Failed to create todo: {create_response.status_code}, {create_response.text}"
    
    created_todo = create_response.json()
    assert "id" in created_todo, \
        f"Missing 'id' in created todo: {created_todo}"
    assert created_todo["text"] == todo_text, \
        f"Todo text mismatch: expected '{todo_text}', got '{created_todo['text']}'"
    
    todo_id = created_todo["id"]
    
    # Act - Verify persistence
    list_response = await staging_client.get("/todos")
    assert list_response.status_code == 200, \
        f"Failed to list todos: {list_response.status_code}"
    
    todos = list_response.json()
    todo_texts = [todo["text"] for todo in todos]
    
    assert todo_text in todo_texts, \
        f"Created todo '{todo_text}' not found in list: {todo_texts}"
    
    # Cleanup
    delete_response = await staging_client.delete(f"/todos/{todo_id}")
    assert delete_response.status_code == 204, \
        f"Failed to cleanup todo: {delete_response.status_code}"


@pytest.mark.asyncio
async def test_read_todo_retrieves_persisted_data(
    staging_client: AsyncClient,
    unique_id_generator
):
    """
    Verify reading a specific todo retrieves correct persisted data.
    
    Steps:
        1. Create todo via API
        2. GET /todos/{id} for specific todo
        3. Assert 200 OK response
        4. Assert retrieved todo matches created data
        5. DELETE created todo (cleanup)
    
    Expected Result:
        Individual todo retrieval returns correct persisted data
    """
    # Arrange - Create todo
    todo_text = unique_id_generator("test_todo")
    create_response = await staging_client.post(
        "/todos",
        json={"text": todo_text}
    )
    assert create_response.status_code == 201
    created_todo = create_response.json()
    todo_id = created_todo["id"]
    
    # Act - Read specific todo
    read_response = await staging_client.get(f"/todos/{todo_id}")
    
    # Assert
    assert read_response.status_code == 200, \
        f"Failed to read todo {todo_id}: {read_response.status_code}"
    
    retrieved_todo = read_response.json()
    assert retrieved_todo["id"] == todo_id, \
        f"ID mismatch: expected {todo_id}, got {retrieved_todo['id']}"
    assert retrieved_todo["text"] == todo_text, \
        f"Text mismatch: expected '{todo_text}', got '{retrieved_todo['text']}'"
    
    # Cleanup
    delete_response = await staging_client.delete(f"/todos/{todo_id}")
    assert delete_response.status_code == 204
