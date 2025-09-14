"""HTTP webhook client for posting messages to external URLs."""

import logging
from typing import Any

import httpx

from ..config.settings import settings
from ..metrics.prometheus import webhook_requests_total

logger = logging.getLogger(__name__)


class WebhookClient:
    """HTTP client for sending webhook requests."""

    def __init__(self, webhook_url: str | None = None):
        """Initialize webhook client with URL and timeout settings."""
        self.webhook_url = webhook_url or settings.webhook_url
        self.timeout = settings.webhook_timeout
        self.retry_attempts = settings.webhook_retry_attempts
        logger.info(f"WebhookClient configured for: {self.webhook_url}")

    async def send_webhook(self, payload: dict[str, Any]) -> bool:
        """Send webhook with retry logic.

        Args:
            payload: JSON payload to send to webhook URL

        Returns:
            bool: True if successful, False otherwise
        """
        for attempt in range(self.retry_attempts):
            try:
                async with httpx.AsyncClient(timeout=self.timeout) as client:
                    response = await client.post(self.webhook_url, json=payload)
                    response.raise_for_status()

                    # Record successful webhook
                    webhook_requests_total.labels(status_code=response.status_code).inc()
                    logger.info(f"Webhook sent successfully: {response.status_code}")
                    return True

            except httpx.RequestError as e:
                logger.warning(f"Webhook request error (attempt {attempt + 1}/{self.retry_attempts}): {e}")
                webhook_requests_total.labels(status_code="error").inc()

            except httpx.HTTPStatusError as e:
                logger.warning(f"Webhook HTTP error (attempt {attempt + 1}/{self.retry_attempts}): {e}")
                webhook_requests_total.labels(status_code=e.response.status_code).inc()
                # Return False immediately for HTTP errors (don't retry)
                return False

            # Don't retry on last attempt
            if attempt == self.retry_attempts - 1:
                break

        logger.error(f"Webhook failed after {self.retry_attempts} attempts")
        return False
