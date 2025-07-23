"""Integration tests for Todo API endpoints.

These tests verify the HTTP API layer of the backend service,
testing the actual REST endpoints that the frontend will call.

This demonstrates microservice API testing:
- Test HTTP endpoints directly
- Test request/response formats
- Test status codes and error handling
- Test the integration between routes and services
"""

import pytest
from fastapi.testclient import TestClient


class TestTodoEndpoints:
    """Test the REST API endpoints for todos."""

    def test_get_todos_returns_list(self, test_client: TestClient):
        """Test GET /todos returns a list of todos.

        This tests the main endpoint the frontend will call
        to fetch todos for display.
        """
        response = test_client.get("/todos")

        assert response.status_code == 200
        todos = response.json()
        assert isinstance(todos, list)

        # Should have the sample todos from service initialization
        assert len(todos) >= 3

        # Verify todo structure matches what frontend expects
        for todo in todos:
            assert "id" in todo
            assert "text" in todo
            assert "status" in todo
            assert "created_at" in todo

    def test_create_todo_returns_created_todo(self, test_client: TestClient):
        """Test POST /todos creates and returns new todo.

        This tests the endpoint the frontend uses to add new todos.
        """
        new_todo_data = {"text": "Test todo from API"}

        response = test_client.post("/todos", json=new_todo_data)

        assert response.status_code == 201
        created_todo = response.json()

        # Verify response structure
        assert created_todo["text"] == "Test todo from API"
        assert created_todo["status"] == "not-done"  # Default status (note: hyphen, not underscore!)
        assert "id" in created_todo
        assert "created_at" in created_todo

    def test_create_todo_validation_errors(self, test_client: TestClient):
        """Test POST /todos with invalid data returns validation errors."""
        invalid_data_cases = [
            {},  # Missing required field
            {"text": ""},  # Empty text
            {"text": "a" * 141},  # Text too long
        ]

        for invalid_data in invalid_data_cases:
            response = test_client.post("/todos", json=invalid_data)
            assert response.status_code == 422  # Validation error

    def test_get_todo_by_id_returns_todo(self, test_client: TestClient):
        """Test GET /todos/{id} returns specific todo."""
        # First create a todo
        create_response = test_client.post("/todos", json={"text": "Findable todo"})
        created_todo = create_response.json()
        todo_id = created_todo["id"]

        # Then get it by ID
        response = test_client.get(f"/todos/{todo_id}")

        assert response.status_code == 200
        todo = response.json()
        assert todo["id"] == todo_id
        assert todo["text"] == "Findable todo"

    def test_get_nonexistent_todo_returns_404(self, test_client: TestClient):
        """Test GET /todos/{id} with non-existent ID returns 404."""
        response = test_client.get("/todos/nonexistent-id")

        assert response.status_code == 404
        error = response.json()
        assert "detail" in error

    def test_update_todo_returns_updated_todo(self, test_client: TestClient):
        """Test PUT /todos/{id} updates and returns todo."""
        # Create todo first
        create_response = test_client.post("/todos", json={"text": "Original text"})
        created_todo = create_response.json()
        todo_id = created_todo["id"]

        # Update it
        update_data = {"text": "Updated text", "status": "done"}
        response = test_client.put(f"/todos/{todo_id}", json=update_data)

        assert response.status_code == 200
        updated_todo = response.json()
        assert updated_todo["text"] == "Updated text"
        assert updated_todo["status"] == "done"
        assert updated_todo["id"] == todo_id

    def test_update_nonexistent_todo_returns_404(self, test_client: TestClient):
        """Test PUT /todos/{id} with non-existent ID returns 404."""
        update_data = {"text": "Updated text"}
        response = test_client.put("/todos/nonexistent-id", json=update_data)

        assert response.status_code == 404

    def test_delete_todo_returns_success(self, test_client: TestClient):
        """Test DELETE /todos/{id} removes todo."""
        # Create todo first
        create_response = test_client.post("/todos", json={"text": "To be deleted"})
        created_todo = create_response.json()
        todo_id = created_todo["id"]

        # Delete it
        response = test_client.delete(f"/todos/{todo_id}")

        assert response.status_code == 204  # No content

        # Verify it's gone
        get_response = test_client.get(f"/todos/{todo_id}")
        assert get_response.status_code == 404

    def test_delete_nonexistent_todo_returns_404(self, test_client: TestClient):
        """Test DELETE /todos/{id} with non-existent ID returns 404."""
        response = test_client.delete("/todos/nonexistent-id")

        assert response.status_code == 404

    def test_todos_endpoint_integration_workflow(self, test_client: TestClient):
        """Test complete CRUD workflow through API.

        This integration test verifies the entire todo lifecycle
        through the REST API, simulating what the frontend would do.
        """
        # 1. Get initial todos count
        initial_response = test_client.get("/todos")
        initial_count = len(initial_response.json())

        # 2. Create a new todo
        create_response = test_client.post("/todos", json={"text": "Workflow test todo"})
        assert create_response.status_code == 201
        new_todo = create_response.json()

        # 3. Verify todos count increased
        after_create_response = test_client.get("/todos")
        assert len(after_create_response.json()) == initial_count + 1

        # 4. Update the todo
        update_response = test_client.put(
            f"/todos/{new_todo['id']}", json={"text": "Updated workflow todo", "status": "done"}
        )
        assert update_response.status_code == 200
        updated_todo = update_response.json()
        assert updated_todo["status"] == "done"

        # 5. Delete the todo
        delete_response = test_client.delete(f"/todos/{new_todo['id']}")
        assert delete_response.status_code == 204

        # 6. Verify todos count back to original
        final_response = test_client.get("/todos")
        assert len(final_response.json()) == initial_count
