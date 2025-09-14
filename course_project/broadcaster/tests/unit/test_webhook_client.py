"""Unit tests for webhook client."""

from unittest.mock import AsyncMock, MagicMock, patch

import httpx
import pytest

from src.services.webhook_client import WebhookClient


class TestWebhookClient:
    """Test cases for WebhookClient."""

    @pytest.mark.asyncio
    async def test_send_webhook_success(self, mock_settings):
        """Test successful webhook sending."""
        client = WebhookClient(webhook_url="http://test.example.com/webhook")

        with patch("httpx.AsyncClient") as mock_client:
            mock_response = AsyncMock()
            mock_response.status_code = 200
            mock_response.raise_for_status.return_value = None

            mock_client.return_value.__aenter__.return_value.post.return_value = mock_response

            result = await client.send_webhook({"test": "data"})

            assert result is True
            mock_client.return_value.__aenter__.return_value.post.assert_called_once_with(
                "http://test.example.com/webhook", json={"test": "data"}
            )

    @pytest.mark.asyncio
    async def test_send_webhook_http_error(self, mock_settings):
        """Test webhook HTTP error handling."""
        client = WebhookClient(webhook_url="http://test.example.com/webhook")

        with patch("httpx.AsyncClient") as mock_client:
            mock_response = MagicMock()
            mock_response.status_code = 500
            mock_response.raise_for_status.side_effect = httpx.HTTPStatusError(
                "Server Error", request=MagicMock(), response=mock_response
            )

            mock_client.return_value.__aenter__.return_value.post.return_value = mock_response

            result = await client.send_webhook({"test": "data"})

            assert result is False

    @pytest.mark.asyncio
    async def test_send_webhook_request_error(self, mock_settings):
        """Test webhook request error handling."""
        client = WebhookClient(webhook_url="http://test.example.com/webhook")

        with patch("httpx.AsyncClient") as mock_client:
            mock_client.return_value.__aenter__.return_value.post.side_effect = httpx.RequestError("Connection failed")

            result = await client.send_webhook({"test": "data"})

            assert result is False
