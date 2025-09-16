"""Integration tests for NATS client functionality."""

import json
from unittest.mock import AsyncMock, Mock, patch

import pytest

from src.models.todo import Todo, TodoStatus
from src.services.nats_client import NATSClient, get_nats_client


class TestNATSClient:
    """Test NATS client functionality with proper mocking."""

    @pytest.fixture
    def nats_client(self):
        """Create a fresh NATS client instance for testing."""
        return NATSClient()

    @pytest.fixture
    def mock_nats_connection(self):
        """Mock NATS connection."""
        mock_nc = AsyncMock()
        mock_nc.publish = AsyncMock()
        mock_nc.close = AsyncMock()
        return mock_nc

    async def test_nats_client_initialization(self, nats_client):
        """Test NATS client initializes correctly."""
        assert nats_client.nc is None
        assert nats_client.is_connected is False
        assert nats_client.settings is not None

    @patch("src.services.nats_client.nats.connect")
    async def test_successful_connection(self, mock_connect, nats_client, mock_nats_connection):
        """Test successful NATS connection."""
        mock_connect.return_value = mock_nats_connection

        result = await nats_client.connect()

        assert result is True
        assert nats_client.is_connected is True
        assert nats_client.nc == mock_nats_connection
        mock_connect.assert_called_once()

    @patch("src.services.nats_client.nats.connect")
    async def test_connection_failure_graceful_degradation(self, mock_connect, nats_client):
        """Test NATS connection failure is handled gracefully."""
        mock_connect.side_effect = Exception("Connection failed")

        result = await nats_client.connect()

        assert result is False
        assert nats_client.is_connected is False
        assert nats_client.nc is None

    async def test_disconnect_with_active_connection(self, nats_client, mock_nats_connection):
        """Test disconnection with active connection."""
        nats_client.nc = mock_nats_connection
        nats_client.is_connected = True

        await nats_client.disconnect()

        mock_nats_connection.close.assert_called_once()
        assert nats_client.is_connected is False
        assert nats_client.nc is None

    async def test_disconnect_without_connection(self, nats_client):
        """Test disconnection without active connection."""
        # Should not raise exception
        await nats_client.disconnect()
        assert nats_client.is_connected is False

    async def test_publish_event_when_disabled(self, nats_client):
        """Test publishing when NATS is disabled."""
        with patch.object(nats_client.settings, "nats_enabled", False):
            todo_data = {"id": "123", "text": "test", "status": "NOT_DONE"}

            result = await nats_client.publish_todo_event("created", todo_data)

            assert result is False

    async def test_publish_event_when_not_connected(self, nats_client):
        """Test publishing when not connected to NATS."""
        todo_data = {"id": "123", "text": "test", "status": "NOT_DONE"}

        result = await nats_client.publish_todo_event("created", todo_data)

        assert result is False

    @patch("src.services.nats_client.nats.connect")
    async def test_publish_event_successful(self, mock_connect, nats_client, mock_nats_connection):
        """Test successful event publishing."""
        mock_connect.return_value = mock_nats_connection
        await nats_client.connect()

        todo_data = {
            "id": "123",
            "text": "test todo",
            "status": "NOT_DONE",
            "created_at": "2023-01-01T00:00:00",
        }

        result = await nats_client.publish_todo_event("created", todo_data)

        assert result is True
        mock_nats_connection.publish.assert_called_once()

        # Verify the message content
        call_args = mock_nats_connection.publish.call_args
        topic, message_data = call_args[0]

        assert topic == nats_client.settings.nats_topic
        message = json.loads(message_data.decode())
        assert message["event_type"] == "created"
        assert message["todo"] == todo_data
        assert "timestamp" in message

    @patch("src.services.nats_client.nats.connect")
    async def test_publish_event_connection_error_during_publish(self, mock_connect, nats_client, mock_nats_connection):
        """Test publishing error is handled gracefully."""
        mock_connect.return_value = mock_nats_connection
        mock_nats_connection.publish.side_effect = Exception("Publish failed")
        await nats_client.connect()

        todo_data = {"id": "123", "text": "test", "status": "NOT_DONE"}

        result = await nats_client.publish_todo_event("created", todo_data)

        assert result is False

    async def test_environment_specific_nats_url(self, nats_client):
        """Test environment-specific NATS URL detection."""
        # Test with explicit URL
        with patch.object(nats_client.settings, "nats_url", "nats://custom:4222"):
            assert nats_client.settings.effective_nats_url == "nats://custom:4222"

        # Test Kubernetes detection
        with patch("os.path.exists") as mock_exists:
            mock_exists.return_value = True
            with patch.object(nats_client.settings, "nats_url", ""):
                assert nats_client.settings.effective_nats_url == "nats://nats:4222"

    def test_get_nats_client_singleton(self):
        """Test that get_nats_client returns the same instance."""
        client1 = get_nats_client()
        client2 = get_nats_client()
        assert client1 is client2


class TestNATSIntegrationWithTodoService:
    """Test NATS integration with TodoService."""

    @pytest.fixture
    def mock_nats_client(self):
        """Mock NATS client for TodoService testing."""
        mock_client = Mock()
        mock_client.publish_todo_event = AsyncMock(return_value=True)
        return mock_client

    @patch("src.services.todo_service.get_nats_client")
    async def test_todo_service_uses_nats_client(self, mock_get_nats_client, mock_nats_client):
        """Test that TodoService initializes with NATS client."""
        from src.services.todo_service import TodoService

        mock_get_nats_client.return_value = mock_nats_client

        service = TodoService()
        assert service._nats_client == mock_nats_client

    async def test_publish_todo_event_creates_correct_message_format(self):
        """Test that _publish_todo_event creates the correct message format."""
        from src.services.todo_service import TodoService
        from datetime import datetime

        service = TodoService()
        service._nats_client = Mock()
        service._nats_client.publish_todo_event = AsyncMock(return_value=True)

        # Create a mock todo
        todo = Todo(
            id="test-123",
            text="Test todo",
            status=TodoStatus.NOT_DONE,
            created_at=datetime(2023, 1, 1, 12, 0, 0),
            updated_at=datetime(2023, 1, 1, 12, 0, 0),
        )

        await service._publish_todo_event("created", todo)

        # Verify the NATS client was called with correct data
        service._nats_client.publish_todo_event.assert_called_once()
        call_args = service._nats_client.publish_todo_event.call_args
        event_type, todo_data = call_args[0]

        assert event_type == "created"
        assert todo_data["id"] == "test-123"
        assert todo_data["text"] == "Test todo"
        assert todo_data["status"] == "not-done"
        assert todo_data["created_at"] == "2023-01-01T12:00:00"
        assert todo_data["updated_at"] == "2023-01-01T12:00:00"

    async def test_publish_todo_event_handles_nats_errors_gracefully(self):
        """Test that NATS publishing errors don't crash todo operations."""
        from src.services.todo_service import TodoService

        service = TodoService()
        service._nats_client = Mock()
        service._nats_client.publish_todo_event = AsyncMock(side_effect=Exception("NATS error"))

        # Create a mock todo
        todo = Todo(
            id="test-123",
            text="Test todo",
            status=TodoStatus.NOT_DONE,
        )

        # Should not raise exception
        await service._publish_todo_event("created", todo)

        # Verify NATS client was called despite the error
        service._nats_client.publish_todo_event.assert_called_once()


class TestNATSConfiguration:
    """Test NATS configuration settings."""

    def test_nats_settings_defaults(self):
        """Test that NATS settings have appropriate defaults."""
        from src.config.settings import Settings

        settings = Settings(postgres_user="test", postgres_password="test")

        assert settings.nats_topic == "todos.events"
        assert settings.nats_enabled is True
        assert settings.nats_url == ""

    def test_effective_nats_url_with_explicit_setting(self):
        """Test effective NATS URL with explicit configuration."""
        from src.config.settings import Settings

        settings = Settings(
            postgres_user="test", postgres_password="test", nats_url="nats://explicit:4222"
        )

        assert settings.effective_nats_url == "nats://explicit:4222"

    @patch("os.path.exists")
    def test_effective_nats_url_kubernetes_detection(self, mock_exists):
        """Test effective NATS URL with Kubernetes detection."""
        from src.config.settings import Settings

        mock_exists.return_value = True
        settings = Settings(postgres_user="test", postgres_password="test", nats_url="")

        assert settings.effective_nats_url == "nats://nats:4222"

    @patch("os.path.exists")
    @patch("os.environ.get")
    def test_effective_nats_url_docker_detection(self, mock_env_get, mock_exists):
        """Test effective NATS URL with Docker detection."""
        from src.config.settings import Settings

        mock_exists.return_value = False
        mock_env_get.side_effect = lambda key, default=None: "true" if key == "DOCKER_CONTAINER" else default

        settings = Settings(postgres_user="test", postgres_password="test", nats_url="")

        assert settings.effective_nats_url == "nats://nats:4222"

    @patch("os.path.exists")
    @patch("os.environ.get")
    def test_effective_nats_url_local_development(self, mock_env_get, mock_exists):
        """Test effective NATS URL for local development."""
        from src.config.settings import Settings

        mock_exists.return_value = False
        mock_env_get.return_value = None

        settings = Settings(postgres_user="test", postgres_password="test", nats_url="")

        assert settings.effective_nats_url == "nats://localhost:4222"