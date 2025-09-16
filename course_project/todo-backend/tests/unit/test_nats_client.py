"""Unit tests for NATS client service."""

import json
from unittest.mock import AsyncMock, Mock, patch

import pytest

from src.services.nats_client import NATSClient


class TestNATSClientUnit:
    """Unit tests for NATS client functionality."""

    @pytest.fixture
    def nats_client(self):
        """Create a NATS client instance."""
        return NATSClient()

    def test_nats_client_initialization(self, nats_client):
        """Test NATS client initializes with correct defaults."""
        assert nats_client.nc is None
        assert nats_client.is_connected is False
        assert nats_client.settings is not None

    async def test_disconnect_without_connection_is_safe(self, nats_client):
        """Test that disconnect is safe when no connection exists."""
        # Should not raise any exception
        await nats_client.disconnect()

    async def test_publish_when_nats_disabled(self, nats_client):
        """Test publishing returns False when NATS is disabled."""
        with patch.object(nats_client.settings, "nats_enabled", False):
            result = await nats_client.publish_todo_event("created", {"id": "test"})
            assert result is False

    async def test_publish_when_not_connected(self, nats_client):
        """Test publishing returns False when not connected."""
        # Client is not connected by default
        result = await nats_client.publish_todo_event("created", {"id": "test"})
        assert result is False

    @patch("src.services.nats_client.nats.connect")
    async def test_connection_success_updates_state(self, mock_connect, nats_client):
        """Test successful connection updates client state."""
        mock_nc = AsyncMock()
        mock_connect.return_value = mock_nc

        result = await nats_client.connect()

        assert result is True
        assert nats_client.is_connected is True
        assert nats_client.nc == mock_nc

    @patch("src.services.nats_client.nats.connect")
    async def test_connection_failure_handles_gracefully(self, mock_connect, nats_client):
        """Test connection failure is handled without raising exceptions."""
        mock_connect.side_effect = Exception("Connection error")

        result = await nats_client.connect()

        assert result is False
        assert nats_client.is_connected is False
        assert nats_client.nc is None

    @patch("src.services.nats_client.nats.connect")
    async def test_publish_message_format(self, mock_connect, nats_client):
        """Test that published messages have the correct format."""
        mock_nc = AsyncMock()
        mock_connect.return_value = mock_nc
        await nats_client.connect()

        todo_data = {
            "id": "test-123",
            "text": "Test todo",
            "status": "not-done",
            "created_at": "2023-01-01T00:00:00",
        }

        result = await nats_client.publish_todo_event("created", todo_data)

        assert result is True
        mock_nc.publish.assert_called_once()

        # Check message format
        call_args = mock_nc.publish.call_args
        topic, message_bytes = call_args[0]

        assert topic == nats_client.settings.nats_topic
        message = json.loads(message_bytes.decode())
        assert message["event_type"] == "created"
        assert message["todo"] == todo_data
        assert "timestamp" in message

    @patch("src.services.nats_client.nats.connect")
    async def test_publish_handles_serialization_errors(self, mock_connect, nats_client):
        """Test that JSON serialization errors are handled gracefully."""
        mock_nc = AsyncMock()
        mock_connect.return_value = mock_nc
        await nats_client.connect()

        # Create data that can't be JSON serialized
        class UnserializableObject:
            pass

        todo_data = {"id": "test", "object": UnserializableObject()}

        with patch("json.dumps", side_effect=TypeError("Not serializable")):
            result = await nats_client.publish_todo_event("created", todo_data)

        assert result is False

    @patch("src.services.nats_client.nats.connect")
    async def test_publish_handles_nats_publish_errors(self, mock_connect, nats_client):
        """Test that NATS publish errors are handled gracefully."""
        mock_nc = AsyncMock()
        mock_nc.publish.side_effect = Exception("Publish failed")
        mock_connect.return_value = mock_nc
        await nats_client.connect()

        todo_data = {"id": "test", "text": "Test"}

        result = await nats_client.publish_todo_event("created", todo_data)

        assert result is False

    async def test_disconnect_handles_close_errors(self, nats_client):
        """Test that disconnect handles connection close errors gracefully."""
        mock_nc = AsyncMock()
        mock_nc.close.side_effect = Exception("Close failed")
        nats_client.nc = mock_nc
        nats_client.is_connected = True

        # Should not raise exception
        await nats_client.disconnect()

        # State should still be updated
        assert nats_client.is_connected is False
        assert nats_client.nc is None

    @patch("src.services.nats_client.nats.connect")
    async def test_reconnect_attempt_during_publish(self, mock_connect, nats_client):
        """Test that publish attempts to reconnect if not connected."""
        mock_nc = AsyncMock()
        mock_connect.return_value = mock_nc

        # Initially not connected
        assert nats_client.is_connected is False

        todo_data = {"id": "test", "text": "Test"}

        result = await nats_client.publish_todo_event("created", todo_data)

        # Should attempt to connect and then publish
        mock_connect.assert_called_once()
        assert result is True

    @patch("src.services.nats_client.nats.connect")
    async def test_failed_reconnect_during_publish(self, mock_connect, nats_client):
        """Test that failed reconnect during publish is handled gracefully."""
        mock_connect.side_effect = Exception("Reconnect failed")

        todo_data = {"id": "test", "text": "Test"}

        result = await nats_client.publish_todo_event("created", todo_data)

        assert result is False
        mock_connect.assert_called_once()

    def test_different_event_types(self, nats_client):
        """Test that different event types are handled correctly."""
        # This is more of a contract test to ensure the interface supports different event types
        assert callable(nats_client.publish_todo_event)

        # The actual async testing is done in other tests, this just verifies the method exists
        # and can be called with different event types without immediate errors