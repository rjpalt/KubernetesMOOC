"""Unit tests for TodoBackendClient - Frontend HTTP client testing.

These tests verify the frontend's HTTP client for communicating with
the todo-backend service. This is pure frontend responsibility.

Testing approach:
- Mock httpx responses (no real HTTP calls)
- Test error handling when backend is unavailable
- Test data format conversions
- Test timeout handling
"""

from unittest.mock import AsyncMock, MagicMock, patch

import httpx
import pytest
from fastapi import HTTPException

from src.models.todo import Todo, TodoStatus
from src.services.todo_backend_client import TodoBackendClient


class TestTodoBackendClient:
    """Test the HTTP client for backend communication."""

    def test_client_initialization_with_default_url(self):
        """Test client initializes with default backend URL from settings."""
        client = TodoBackendClient()

        # Should use settings.todo_backend_url
        assert client.backend_url is not None
        assert client.timeout is not None

    def test_client_initialization_with_custom_url(self):
        """Test client initializes with custom backend URL."""
        custom_url = "http://custom-backend:8001"
        client = TodoBackendClient(backend_url=custom_url)

        assert client.backend_url == custom_url

    def test_client_strips_trailing_slash(self):
        """Test that trailing slash is removed from backend URL."""
        client = TodoBackendClient(backend_url="http://backend:8001/")

        assert client.backend_url == "http://backend:8001"

    @pytest.mark.asyncio
    async def test_get_all_todos_success(self):
        """Test successful retrieval of todos from backend."""
        # Mock httpx response
        mock_response_data = [
            {"id": "1", "text": "Backend todo 1", "status": "not-done", "created_at": "2025-07-21T10:00:00Z"},
            {"id": "2", "text": "Backend todo 2", "status": "done", "created_at": "2025-07-21T11:00:00Z"},
        ]

        with patch("httpx.AsyncClient") as mock_client_class:
            # Setup mock
            mock_client = AsyncMock()
            mock_client_class.return_value.__aenter__.return_value = mock_client

            mock_response = MagicMock()
            mock_response.json.return_value = mock_response_data
            mock_response.raise_for_status.return_value = None
            mock_client.get.return_value = mock_response

            # Test
            client = TodoBackendClient(backend_url="http://test-backend:8001")
            todos = await client.get_all_todos()

            # Verify
            assert len(todos) == 2
            assert all(isinstance(todo, Todo) for todo in todos)
            assert todos[0].text == "Backend todo 1"
            assert todos[0].status == TodoStatus.NOT_DONE
            assert todos[1].text == "Backend todo 2"
            assert todos[1].status == TodoStatus.DONE

            # Verify HTTP call was made correctly
            mock_client.get.assert_called_once_with("http://test-backend:8001/api/todos")

    @pytest.mark.asyncio
    async def test_get_all_todos_http_error(self):
        """Test handling of HTTP errors from backend."""
        with patch("httpx.AsyncClient") as mock_client_class:
            # Setup mock to raise HTTP error
            mock_client = AsyncMock()
            mock_client_class.return_value.__aenter__.return_value = mock_client

            mock_response = MagicMock()
            mock_response.raise_for_status.side_effect = httpx.HTTPStatusError(
                "404 Not Found", request=None, response=mock_response
            )
            mock_client.get.return_value = mock_response

            # Test
            client = TodoBackendClient(backend_url="http://test-backend:8001")

            with pytest.raises(HTTPException) as exc_info:
                await client.get_all_todos()

            # Should convert httpx error to FastAPI HTTPException
            assert exc_info.value.status_code == mock_response.status_code  # Use actual status code
            assert "Error fetching todos from backend" in str(exc_info.value.detail)

    @pytest.mark.asyncio
    async def test_get_all_todos_connection_error(self):
        """Test handling of connection errors to backend."""
        with patch("httpx.AsyncClient") as mock_client_class:
            # Setup mock to raise connection error
            mock_client = AsyncMock()
            mock_client_class.return_value.__aenter__.return_value = mock_client
            mock_client.get.side_effect = httpx.RequestError("Connection failed")

            # Test
            client = TodoBackendClient(backend_url="http://test-backend:8001")

            with pytest.raises(HTTPException) as exc_info:
                await client.get_all_todos()

            # Should handle connection error gracefully
            assert exc_info.value.status_code == 503
            assert "Todo backend service unavailable" in str(exc_info.value.detail)

    @pytest.mark.asyncio
    async def test_get_all_todos_timeout(self):
        """Test handling of timeout when calling backend."""
        with patch("httpx.AsyncClient") as mock_client_class:
            # Setup mock to raise timeout
            mock_client = AsyncMock()
            mock_client_class.return_value.__aenter__.return_value = mock_client
            mock_client.get.side_effect = httpx.TimeoutException("Request timeout")

            # Test
            client = TodoBackendClient(backend_url="http://test-backend:8001")

            with pytest.raises(HTTPException) as exc_info:
                await client.get_all_todos()

            # Should handle timeout gracefully
            assert exc_info.value.status_code == 503
            assert "Todo backend service unavailable" in str(exc_info.value.detail)

    @pytest.mark.asyncio
    async def test_create_todo_success(self):
        """Test successful creation of todo via backend."""
        # Mock backend response for created todo
        mock_response_data = {
            "id": "new-todo-id",
            "text": "New todo from frontend",
            "status": "not-done",
            "created_at": "2025-07-21T12:00:00Z",
        }

        with patch("httpx.AsyncClient") as mock_client_class:
            # Setup mock
            mock_client = AsyncMock()
            mock_client_class.return_value.__aenter__.return_value = mock_client

            mock_response = MagicMock()
            mock_response.json.return_value = mock_response_data
            mock_response.raise_for_status.return_value = None
            mock_client.post.return_value = mock_response

            # Test
            client = TodoBackendClient(backend_url="http://test-backend:8001")
            todo = await client.create_todo("New todo from frontend")

            # Verify
            assert isinstance(todo, Todo)
            assert todo.text == "New todo from frontend"
            assert todo.status == TodoStatus.NOT_DONE
            assert todo.id == "new-todo-id"

            # Verify HTTP call
            mock_client.post.assert_called_once_with(
                "http://test-backend:8001/api/todos", json={"text": "New todo from frontend"}
            )

    @pytest.mark.asyncio
    async def test_schema_consistency_with_backend(self):
        """Test that frontend expects the exact format backend provides.

        This is a contract test ensuring frontend and backend agree on data format.
        """
        # This is the exact format the backend returns (with hyphens!)
        backend_format_response = [
            {
                "id": "backend-uuid-123",
                "text": "Backend formatted todo",
                "status": "not-done",  # Hyphen format!
                "created_at": "2025-07-21T10:00:00Z",
            }
        ]

        with patch("httpx.AsyncClient") as mock_client_class:
            # Setup mock with backend's actual format
            mock_client = AsyncMock()
            mock_client_class.return_value.__aenter__.return_value = mock_client

            mock_response = MagicMock()
            mock_response.json.return_value = backend_format_response
            mock_response.raise_for_status.return_value = None
            mock_client.get.return_value = mock_response

            # Test that frontend can parse backend's format
            client = TodoBackendClient(backend_url="http://test-backend:8001")
            todos = await client.get_all_todos()

            # Frontend should correctly parse backend's format
            assert len(todos) == 1
            assert todos[0].status == TodoStatus.NOT_DONE  # Should parse "not-done" correctly
            assert todos[0].text == "Backend formatted todo"
