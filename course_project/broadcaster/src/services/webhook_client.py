"""HTTP webhook client for posting messages to external URLs."""

import asyncio
import logging
from typing import Any

import httpx

from ..config.settings import settings
from ..metrics.prometheus import webhook_requests_total

logger = logging.getLogger(__name__)


class WebhookClient:
    """HTTP client for sending webhook requests."""

    def __init__(self, webhook_url: str | None = None, timeout: int | None = None, client: Any | None = None):
        """Initialize webhook client with URL and timeout settings.

        Accepts an optional `client` for injection in tests (e.g., AsyncMock).
        """
        self.webhook_url = webhook_url or settings.webhook_url
        self.timeout = timeout if timeout is not None else settings.webhook_timeout
        self.retry_attempts = settings.webhook_retry_attempts
        self.client = client
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
                if self.client:
                    # Injected client (AsyncMock) used in tests
                    response = await self.client.post(self.webhook_url, json=payload)
                else:
                    async with httpx.AsyncClient(timeout=self.timeout) as client:
                        response = await client.post(self.webhook_url, json=payload)

                # If response is an async context manager mock, handle accordingly
                if hasattr(response, "raise_for_status"):
                    # Some tests inject AsyncMock objects where raise_for_status is async
                    # calling it may return a coroutine that must be awaited to avoid
                    # 'coroutine was never awaited' warnings. Handle both sync and async.
                    maybe = response.raise_for_status()
                    if asyncio.iscoroutine(maybe):
                        await maybe

                # Record successful webhook
                try:
                    webhook_requests_total.labels(status_code=getattr(response, "status_code", 200)).inc()
                except Exception:
                    pass
                logger.info(f"Webhook sent successfully: {getattr(response, 'status_code', 200)}")
                return True

            except httpx.RequestError as e:
                logger.warning(f"Webhook request error (attempt {attempt + 1}/{self.retry_attempts}): {e}")
                try:
                    webhook_requests_total.labels(status_code="error").inc()
                except Exception:
                    pass

            except httpx.HTTPStatusError as e:
                logger.warning(f"Webhook HTTP error (attempt {attempt + 1}/{self.retry_attempts}): {e}")
                try:
                    webhook_requests_total.labels(status_code=e.response.status_code).inc()
                except Exception:
                    pass
                # Return False immediately for HTTP errors (don't retry)
                return False

            # Don't retry on last attempt
            if attempt == self.retry_attempts - 1:
                break

        logger.error(f"Webhook failed after {self.retry_attempts} attempts")
        return False

    # Backwards-compatible alias expected by tests
    async def send_message(self, payload: dict[str, Any]) -> bool:
        return await self.send_webhook(payload)
