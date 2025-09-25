"""NATS consumer service for subscribing to messages and forwarding via webhooks."""

import asyncio
import json
import logging

import nats
from nats.aio.client import Client as NATS
from nats.aio.msg import Msg

from ..config.settings import settings
from ..metrics.prometheus import messages_processed_total, nats_connection_status
from .webhook_client import WebhookClient

logger = logging.getLogger(__name__)


class BroadcasterService:
    """NATS consumer service that forwards messages to HTTP webhooks."""

    def __init__(self):
        """Initialize broadcaster service."""
        self.nc: NATS | None = None
        self.webhook_client = WebhookClient()
        self.is_running = False
        self.subscription = None
        self.settings = settings
        self._stop_event = asyncio.Event()
        logger.info("BroadcasterService initialized")

    async def start(self) -> None:
        """Start the NATS consumer with retry logic."""
        self.is_running = True
        logger.info("Starting broadcaster service...")

        while self.is_running:
            try:
                connected = await self._connect_to_nats()
                if connected:
                    await self._subscribe_to_topic()

                # Keep the connection alive
                await self._stop_event.wait()

            except Exception as e:
                logger.error(f"NATS connection error: {e}")
                nats_connection_status.set(0)

                if self.is_running:
                    logger.info("Retrying NATS connection in 5 seconds...")
                    await asyncio.sleep(5)
                else:
                    break

    async def stop(self) -> None:
        """Stop the broadcaster service gracefully."""
        logger.info("Stopping broadcaster service...")
        self.is_running = False
        self._stop_event.set()

        if self.subscription:
            await self.subscription.unsubscribe()

        if self.nc:
            await self.nc.close()

        nats_connection_status.set(0)
        logger.info("Broadcaster service stopped")

    async def _connect_to_nats(self) -> bool:
        """Establish connection to NATS server with retry logic."""
        # Use environment-aware NATS URL
        nats_url = self.settings.effective_nats_url
        logger.info(f"Connecting to NATS at {nats_url} (environment: {self.settings.deployment_environment})")
        max_attempts = 3
        for attempt in range(1, max_attempts + 1):
            try:
                self.nc = await nats.connect(
                    servers=[nats_url],
                    connect_timeout=self.settings.nats_connect_timeout,
                    max_reconnect_attempts=self.settings.nats_max_reconnect_attempts,
                    error_cb=self._error_callback,
                    disconnected_cb=self._disconnected_callback,
                    reconnected_cb=self._reconnected_callback,
                )

                logger.info("Successfully connected to NATS")
                nats_connection_status.set(1)
                return True

            except Exception as e:
                logger.error(f"Failed to connect to NATS (attempt {attempt}/{max_attempts}): {e}")
                nats_connection_status.set(0)

                if attempt < max_attempts:
                    await asyncio.sleep(0.1)
                    continue

        # All attempts failed
        return False

    async def _subscribe_to_topic(self) -> None:
        """Subscribe to NATS topic with queue group for load balancing."""
        if not self.nc:
            raise RuntimeError("NATS connection not established")

        self.subscription = await self.nc.subscribe(
            subject=self.settings.nats_topic, queue=self.settings.nats_queue_group, cb=self._message_handler
        )

        logger.info(
            f"Subscribed to topic '{self.settings.nats_topic}' with queue group '{self.settings.nats_queue_group}'"
        )

    async def _message_handler(self, msg: Msg) -> None:
        """Handle incoming NATS messages."""
        try:
            # Parse message data
            message_data = json.loads(msg.data.decode())
            logger.info(f"Received message: {message_data}")

            # Forward to webhook
            success = await self.webhook_client.send_webhook(message_data)

            if success:
                messages_processed_total.labels(status="success").inc()
                logger.debug("Message successfully forwarded to webhook")
            else:
                messages_processed_total.labels(status="error").inc()
                logger.warning("Failed to forward message to webhook")

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse message JSON: {e}")
            messages_processed_total.labels(status="error").inc()

        except Exception as e:
            logger.error(f"Error processing message: {e}")
            messages_processed_total.labels(status="error").inc()

    async def _error_callback(self, error: Exception) -> None:
        """Handle NATS connection errors."""
        logger.error(f"NATS error: {error}")
        nats_connection_status.set(0)

    async def _disconnected_callback(self) -> None:
        """Handle NATS disconnection."""
        logger.warning("NATS disconnected")
        nats_connection_status.set(0)

    async def _reconnected_callback(self) -> None:
        """Handle NATS reconnection."""
        logger.info("NATS reconnected")
        nats_connection_status.set(1)
