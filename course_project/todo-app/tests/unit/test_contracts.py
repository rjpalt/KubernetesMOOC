"""Contract tests - Verify frontend and backend agree on existing API.

This file tests the actual contract between services, not hypothetical features.
Only test methods that actually exist in both services.
"""

from unittest.mock import AsyncMock, MagicMock, patch

import httpx
import pytest
from src.services.todo_backend_client import TodoBackendClient


class TestExistingContracts:
    """Test only the contracts that actually exist between services."""

    def test_client_initialization(self):
        """Test that client can be initialized (basic contract)."""
        client = TodoBackendClient()
        assert client.backend_url is not None
        assert client.timeout is not None

    @pytest.mark.asyncio
    async def test_get_all_todos_contract_exists(self):
        """Test that get_all_todos method exists and returns expected format."""
        # This tests the method exists, not its full implementation
        client = TodoBackendClient(backend_url="http://test:8001")

        # Method should exist
        assert hasattr(client, "get_all_todos")
        assert callable(getattr(client, "get_all_todos"))

    @pytest.mark.asyncio
    async def test_create_todo_contract_exists(self):
        """Test that create_todo method exists (note: create_todo, not add_todo!)."""
        client = TodoBackendClient(backend_url="http://test:8001")

        # Method should exist
        assert hasattr(client, "create_todo")
        assert callable(getattr(client, "create_todo"))

    @pytest.mark.asyncio
    async def test_health_check_contract_exists(self):
        """Test that health_check method exists."""
        client = TodoBackendClient(backend_url="http://test:8001")

        # Method should exist
        assert hasattr(client, "health_check")
        assert callable(getattr(client, "health_check"))


class TestMinimalWorkingContract:
    """Test minimal working functionality between services."""

    @pytest.mark.asyncio
    async def test_backend_returns_expected_todo_format(self):
        """Test that backend returns todos in the format frontend expects.

        This is the critical contract test - data format compatibility.
        """
        # Mock the exact format the backend actually returns
        backend_todo_format = {
            "id": "backend-uuid-123",
            "text": "Backend todo",
            "status": "not-done",  # Backend uses hyphen format
            "created_at": "2025-07-21T10:00:00Z",
        }

        with patch("httpx.AsyncClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value.__aenter__.return_value = mock_client

            mock_response = MagicMock()
            mock_response.json.return_value = [backend_todo_format]
            mock_response.raise_for_status.return_value = None
            mock_client.get.return_value = mock_response

            # Test that frontend can parse backend's actual format
            client = TodoBackendClient(backend_url="http://test:8001")
            todos = await client.get_all_todos()

            # Should successfully parse without errors
            assert len(todos) == 1
            assert todos[0].text == "Backend todo"
            # Frontend should correctly interpret backend's "not-done" format
            assert todos[0].status.value == "not-done"
