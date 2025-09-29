"""NATS service for publishing todo events, because we like it."""

import json
import logging
from typing import Any

import nats

from ..config.settings import settings

logger = logging.getLogger(__name__)


class NATSService:
    """Service for publishing messages to NATS."""

    def __init__(self):
        """Initialize NATS service."""
        self.nc: nats.aio.client.Client | None = None
        self.is_connected = False

    async def connect(self) -> bool:
        """Connect to NATS server."""
        try:
            self.nc = await nats.connect(
                servers=[settings.effective_nats_url],
                connect_timeout=settings.nats_connect_timeout,
                max_reconnect_attempts=settings.nats_max_reconnect_attempts,
            )
            self.is_connected = True
            logger.info(f"Successfully connected to NATS at {settings.effective_nats_url}")
            return True
        except Exception as e:
            logger.warning(f"Failed to connect to NATS: {e}")
            self.is_connected = False
            return False

    async def disconnect(self) -> None:
        """Disconnect from NATS server."""
        try:
            if self.nc and self.is_connected:
                await self.nc.close()
                logger.info("Disconnected from NATS")
        except Exception as e:
            logger.warning(f"Error during NATS disconnect: {e}")
        finally:
            self.nc = None
            self.is_connected = False

    async def publish_todo_event(self, todo_data: dict[str, Any], action: str) -> bool:
        """Publish a todo event to NATS."""
        if not self.is_connected or not self.nc:
            logger.warning("NATS not connected, skipping message publish")
            return False

        try:
            # Create message payload
            message = {**todo_data, "action": action}
            message_bytes = json.dumps(message).encode()

            # Publish to NATS topic
            await self.nc.publish(settings.nats_topic, message_bytes)
            logger.info(f"Published {action} event for todo {todo_data.get('id')}")
            return True

        except Exception as e:
            logger.warning(f"Failed to publish NATS message: {e}")
            return False
