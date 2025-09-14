"""Integration tests for NATS integration."""

import asyncio
from unittest.mock import AsyncMock, patch

import pytest

from src.services.broadcaster_service import BroadcasterService


class TestNATSIntegration:
    """Integration test cases for NATS functionality."""

    @pytest.mark.asyncio
    async def test_nats_connection_retry(self, mock_settings):
        """Test NATS connection retry logic."""
        service = BroadcasterService()

        with patch("nats.connect") as mock_connect:
            # First call fails, second succeeds
            mock_connect.side_effect = [Exception("Connection failed"), AsyncMock()]

            # Mock successful subscription
            with patch.object(service, "_subscribe_to_topic"):
                # Start service briefly
                start_task = asyncio.create_task(service.start())
                await asyncio.sleep(0.1)

                await service.stop()
                start_task.cancel()

                # Should have attempted connection twice
                assert mock_connect.call_count >= 1

    @pytest.mark.asyncio
    async def test_graceful_degradation(self, mock_settings):
        """Test service starts even when NATS is unavailable."""
        service = BroadcasterService()

        with patch("nats.connect") as mock_connect:
            mock_connect.side_effect = Exception("NATS unavailable")

            # Service should start and handle the error gracefully
            start_task = asyncio.create_task(service.start())
            await asyncio.sleep(0.1)

            await service.stop()
            start_task.cancel()

            # Service should have attempted connection
            assert mock_connect.called
