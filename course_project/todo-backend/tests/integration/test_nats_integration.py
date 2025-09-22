"""Integration tests for NATS message publishing."""

from unittest.mock import AsyncMock, patch

from httpx import AsyncClient


class TestNATSIntegration:
    """Test NATS integration with todo operations."""

    async def test_create_todo_publishes_nats_message(self, test_client: AsyncClient):
        """Test that creating a todo publishes a NATS message."""
        # Mock NATS service
        mock_nats_service = AsyncMock()
        mock_nats_service.is_connected = True

        # Replace the app state NATS service with our mock
        test_client._test_app.state.nats_service = mock_nats_service

        # Reset the todo service singleton to pick up fresh dependencies
        with patch("src.api.dependencies._todo_service_instance", None):
            # Create todo via API
            response = await test_client.post("/todos", json={"text": "Test NATS integration"})
            assert response.status_code == 201

            todo_data = response.json()

            # Verify NATS publish was called with correct payload
            mock_nats_service.publish_todo_event.assert_called_once()
            call_args = mock_nats_service.publish_todo_event.call_args

            # Check the payload structure
            todo_data_arg = call_args[1]["todo_data"]
            action_arg = call_args[1]["action"]

            assert action_arg == "created"
            assert todo_data_arg["id"] == todo_data["id"]
            assert todo_data_arg["text"] == "Test NATS integration"
            assert todo_data_arg["status"] == "not-done"
            assert "created_at" in todo_data_arg
            assert "updated_at" in todo_data_arg

    async def test_update_todo_publishes_nats_message(self, test_client: AsyncClient):
        """Test that updating a todo publishes a NATS message."""
        # Mock NATS service
        mock_nats_service = AsyncMock()
        mock_nats_service.is_connected = True

        # Replace the app state NATS service with our mock
        test_client._test_app.state.nats_service = mock_nats_service

        # Reset the todo service singleton to pick up fresh dependencies
        with patch("src.api.dependencies._todo_service_instance", None):
            # Create todo first
            create_response = await test_client.post("/todos", json={"text": "Test update"})
            todo_id = create_response.json()["id"]

            # Reset mock to track update call
            mock_nats_service.publish_todo_event.reset_mock()

            # Update todo
            update_response = await test_client.put(
                f"/todos/{todo_id}", json={"text": "Updated text", "status": "done"}
            )
            assert update_response.status_code == 200

            # Verify update message was published
            mock_nats_service.publish_todo_event.assert_called_once()
            call_args = mock_nats_service.publish_todo_event.call_args

            # Check the payload structure
            todo_data_arg = call_args[1]["todo_data"]
            action_arg = call_args[1]["action"]

            assert action_arg == "updated"
            assert todo_data_arg["text"] == "Updated text"
            assert todo_data_arg["status"] == "done"

    async def test_nats_failure_does_not_break_todo_operations(self, test_client: AsyncClient):
        """Test that NATS publishing failures don't affect todo operations."""
        # Mock NATS service to raise exception on publish
        mock_nats_service = AsyncMock()
        mock_nats_service.is_connected = True
        mock_nats_service.publish_todo_event.side_effect = Exception("NATS connection failed")

        # Replace the app state NATS service with our mock
        test_client._test_app.state.nats_service = mock_nats_service

        # Reset the todo service singleton to pick up fresh dependencies
        with patch("src.api.dependencies._todo_service_instance", None):
            # Create todo (should succeed despite NATS failure)
            response = await test_client.post("/todos", json={"text": "Test error handling"})
            assert response.status_code == 201

            todo_data = response.json()
            assert todo_data["text"] == "Test error handling"

            # Verify NATS publish was attempted but failed gracefully
            mock_nats_service.publish_todo_event.assert_called_once()

    @patch("src.services.nats_service.nats.connect")
    async def test_nats_not_connected_skips_publishing(self, mock_connect, test_client: AsyncClient):
        """Test that when NATS is not connected, publishing is skipped gracefully."""
        # Mock connection failure
        mock_connect.side_effect = Exception("Connection failed")

        # Create todo (should succeed without NATS)
        response = await test_client.post("/todos", json={"text": "Test no connection"})
        assert response.status_code == 201

        todo_data = response.json()
        assert todo_data["text"] == "Test no connection"

    async def test_message_format_specification(self, test_client: AsyncClient):
        """Test that published messages match exact specification."""
        # Mock NATS service to capture the message
        mock_nats_service = AsyncMock()
        mock_nats_service.is_connected = True

        # Replace the app state NATS service with our mock
        test_client._test_app.state.nats_service = mock_nats_service

        # Reset the todo service singleton to pick up fresh dependencies
        with patch("src.api.dependencies._todo_service_instance", None):
            # Create todo
            response = await test_client.post("/todos", json={"text": "Format test"})
            assert response.status_code == 201

            # Extract published message
            mock_nats_service.publish_todo_event.assert_called_once()
            call_args = mock_nats_service.publish_todo_event.call_args

            # Check the payload structure
            todo_data_arg = call_args[1]["todo_data"]
            action_arg = call_args[1]["action"]

            # Validate exact message structure
            required_fields = ["id", "text", "status", "created_at", "updated_at"]
            for field in required_fields:
                assert field in todo_data_arg, f"Missing required field: {field}"

            # Validate field types and values
            assert isinstance(todo_data_arg["id"], str)
            assert isinstance(todo_data_arg["text"], str)
            assert todo_data_arg["status"] in ["not-done", "done"]
            assert action_arg in ["created", "updated"]

            # Validate ISO timestamp format
            from datetime import datetime

            datetime.fromisoformat(todo_data_arg["created_at"])
            datetime.fromisoformat(todo_data_arg["updated_at"])
