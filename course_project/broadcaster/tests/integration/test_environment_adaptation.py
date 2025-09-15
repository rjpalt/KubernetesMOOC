"""Test service behavior across different environments."""

from unittest.mock import AsyncMock, mock_open, patch

import pytest

from src.config.settings import Settings
from src.services.broadcaster_service import BroadcasterService


class TestEnvironmentAdaptation:
    """Test broadcaster service adaptation to environments."""

    @pytest.mark.asyncio
    async def test_local_environment_nats_connection(self):
        """Test service uses localhost NATS in local environment."""
        with patch("os.path.exists", return_value=False):
            settings = Settings(webhook_url="https://httpbin.org/post")
            service = BroadcasterService()
            service.settings = settings

            with patch("nats.connect") as mock_connect:
                mock_connect.return_value = AsyncMock()
                await service._connect_to_nats()

                # Verify localhost NATS URL used
                args = mock_connect.call_args[1]
                assert "nats://localhost:4222" in args["servers"]

    @pytest.mark.asyncio
    async def test_kubernetes_environment_nats_connection(self):
        """Test service uses Kubernetes service DNS in cluster."""
        namespace_content = "feature-ex-c4-e6"

        with patch("os.path.exists", return_value=True), patch("builtins.open", mock_open(read_data=namespace_content)):
            settings = Settings(webhook_url="https://httpbin.org/post")
            service = BroadcasterService()
            service.settings = settings

            with patch("nats.connect") as mock_connect:
                mock_connect.return_value = AsyncMock()
                await service._connect_to_nats()

                # Verify Kubernetes service DNS used
                args = mock_connect.call_args[1]
                assert "nats://nats:4222" in args["servers"]
