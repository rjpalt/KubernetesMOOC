"""Unit tests for broadcaster service."""

import json
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from src.services.broadcaster_service import BroadcasterService


class TestBroadcasterService:
    """Test cases for BroadcasterService."""

    @pytest.mark.asyncio
    async def test_start_stop_service(self, mock_settings):
        """Test starting and stopping the service."""
        service = BroadcasterService()

        with (
            patch.object(service, "_connect_to_nats") as mock_connect,
            patch.object(service, "_subscribe_to_topic") as mock_subscribe,
        ):
            # Mock NATS connection
            mock_connect.return_value = None
            mock_subscribe.return_value = None
            mock_nc = AsyncMock()
            mock_nc.is_connected = True
            service.nc = mock_nc

            # Start service in background and immediately stop
            import asyncio

            start_task = asyncio.create_task(service.start())
            await asyncio.sleep(0.1)  # Let it start

            await service.stop()
            start_task.cancel()

            assert not service.is_running

    @pytest.mark.asyncio
    async def test_message_handler_success(self, mock_settings):
        """Test successful message handling."""
        service = BroadcasterService()

        # Mock webhook client
        service.webhook_client = AsyncMock()
        service.webhook_client.send_webhook.return_value = True

        # Create mock message
        mock_msg = MagicMock()
        mock_msg.data = json.dumps({"test": "data"}).encode()

        await service._message_handler(mock_msg)

        service.webhook_client.send_webhook.assert_called_once_with({"test": "data"})

    @pytest.mark.asyncio
    async def test_message_handler_invalid_json(self, mock_settings):
        """Test message handler with invalid JSON."""
        service = BroadcasterService()

        # Mock webhook client
        service.webhook_client = AsyncMock()

        # Create mock message with invalid JSON
        mock_msg = MagicMock()
        mock_msg.data = b"invalid json"

        # Should not raise exception
        await service._message_handler(mock_msg)

        # Webhook should not be called
        service.webhook_client.send_webhook.assert_not_called()
