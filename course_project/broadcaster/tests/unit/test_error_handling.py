"""Test error handling and retry logic."""

from unittest.mock import AsyncMock, Mock, patch

import httpx
import pytest

from src.services.broadcaster_service import BroadcasterService


class TestErrorHandling:
    """Test error handling scenarios."""

    @pytest.mark.asyncio
    async def test_nats_connection_failure_recovery(self, mock_settings):
        """Test NATS connection failure and recovery."""
        service = BroadcasterService()
        service.settings = mock_settings

        # Mock NATS connection failure then success
        with patch(
            "nats.connect",
            side_effect=[
                Exception("Connection failed"),
                Exception("Still failing"),
                AsyncMock(),  # Third attempt succeeds
            ],
        ) as mock_connect:
            result = await service._connect_to_nats()
            assert mock_connect.call_count == 3
            assert result is not None  # Should eventually succeed

    @pytest.mark.asyncio
    async def test_webhook_timeout_handling(self):
        """Test webhook timeout and retry logic."""
        from src.services.webhook_client import WebhookClient

        # Mock timeout then success
        mock_client = AsyncMock()
        mock_client.post.side_effect = [httpx.TimeoutException("Request timeout"), Mock(status_code=200)]

        webhook_client = WebhookClient("https://test.example.com", timeout=5)
        webhook_client.client = mock_client

        # Should retry and succeed
        result = await webhook_client.send_message({"test": "data"})
        assert result is True
        assert mock_client.post.call_count == 2

    @pytest.mark.asyncio
    async def test_webhook_5xx_retry_logic(self):
        """Test webhook 5xx error retry logic."""
        from src.services.webhook_client import WebhookClient

        mock_client = AsyncMock()
        # First call returns 500, second succeeds
        mock_response_500 = Mock()
        mock_response_500.status_code = 500
        mock_response_500.raise_for_status.side_effect = httpx.HTTPStatusError(
            "Server Error", request=Mock(), response=mock_response_500
        )

        mock_response_200 = Mock()
        mock_response_200.status_code = 200
        mock_response_200.raise_for_status.return_value = None

        mock_client.post.return_value.__aenter__.side_effect = [mock_response_500, mock_response_200]

        webhook_client = WebhookClient("https://test.example.com", timeout=5)
        webhook_client.client = mock_client

        result = await webhook_client.send_message({"test": "data"})
        assert result is True
