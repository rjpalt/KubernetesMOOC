"""NATS client for publishing todo events."""

import asyncio
import json
import logging
from typing import Any

import nats
from nats.aio.client import Client as NATS

from ..config.settings import settings

logger = logging.getLogger(__name__)


class NATSClient:
    """NATS client for publishing todo events with graceful degradation."""

    def __init__(self):
        """Initialize NATS client."""
        self.nc: NATS | None = None
        self.is_connected = False
        self.settings = settings
        logger.debug("NATSClient initialized")

    async def connect(self) -> bool:
        """Connect to NATS server with graceful failure handling."""
        if not self.settings.nats_enabled:
            logger.info("NATS publishing disabled by configuration")
            return False

        try:
            nats_url = self.settings.effective_nats_url
            logger.debug(f"Attempting to connect to NATS at {nats_url}")

            self.nc = await nats.connect(
                servers=[nats_url],
                connect_timeout=5,  # Quick timeout for non-blocking behavior
                max_reconnect_attempts=1,  # Don't retry aggressively
            )

            self.is_connected = True
            logger.info(f"Successfully connected to NATS at {nats_url}")
            return True

        except Exception as e:
            logger.warning(f"Failed to connect to NATS: {e} (continuing without NATS)")
            self.is_connected = False
            return False

    async def disconnect(self) -> None:
        """Disconnect from NATS server."""
        if self.nc and self.is_connected:
            try:
                await self.nc.close()
                logger.debug("Disconnected from NATS")
            except Exception as e:
                logger.warning(f"Error disconnecting from NATS: {e}")
            finally:
                self.is_connected = False
                self.nc = None

    async def publish_todo_event(self, event_type: str, todo_data: dict[str, Any]) -> bool:
        """Publish a todo event to NATS with fire-and-forget semantics.
        
        Args:
            event_type: Type of event (e.g., 'created', 'updated', 'deleted')
            todo_data: Todo data to include in the event
            
        Returns:
            True if message was published successfully, False otherwise
        """
        if not self.settings.nats_enabled:
            logger.debug("NATS publishing disabled, skipping event")
            return False

        if not self.is_connected:
            # Try to reconnect once
            await self.connect()
            if not self.is_connected:
                logger.debug("NATS not connected, skipping event publication")
                return False

        try:
            # Create event message
            event_message = {
                "event_type": event_type,
                "timestamp": todo_data.get("created_at") or todo_data.get("updated_at"),
                "todo": todo_data,
            }

            # Serialize to JSON
            message_data = json.dumps(event_message).encode()

            # Publish message (fire-and-forget)
            await self.nc.publish(self.settings.nats_topic, message_data)

            logger.debug(f"Published {event_type} event for todo {todo_data.get('id', 'unknown')}")
            return True

        except Exception as e:
            logger.warning(f"Failed to publish todo event: {e} (continuing without NATS)")
            return False


# Global NATS client instance
_nats_client_instance: NATSClient | None = None


def get_nats_client() -> NATSClient:
    """Get the global NATS client instance."""
    global _nats_client_instance
    if _nats_client_instance is None:
        _nats_client_instance = NATSClient()
    return _nats_client_instance