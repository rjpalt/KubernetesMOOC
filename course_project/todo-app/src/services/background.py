"""Background task management."""

import asyncio
import logging
from typing import Optional

from ..services.image_service import ImageService

logger = logging.getLogger(__name__)


class BackgroundTaskManager:
    """Manages background tasks for the application."""

    def __init__(self, image_service: ImageService):
        self.image_service = image_service
        self._image_fetch_task: Optional[asyncio.Task] = None

    async def start_background_tasks(self):
        """Start all background tasks."""
        self._image_fetch_task = asyncio.create_task(self._background_image_fetcher())
        logger.info("Background tasks started")

    async def stop_background_tasks(self):
        """Stop all background tasks."""
        if self._image_fetch_task:
            self._image_fetch_task.cancel()
            try:
                await self._image_fetch_task
            except asyncio.CancelledError:
                pass
        logger.info("Background tasks stopped")

    async def _background_image_fetcher(self):
        """Background task that periodically fetches new images."""
        from ..config.settings import settings

        logger.info(f"Starting background image fetcher (interval: {settings.image_update_interval_minutes} minutes)")

        # Fetch initial image if none exists
        if not settings.image_current_file.exists():
            logger.info("No cached image found, fetching initial image...")
            await self.image_service.fetch_new_image(force=True)

        while True:
            try:
                await asyncio.sleep(60)  # Check every minute
                await self.image_service.fetch_new_image(force=False)
            except asyncio.CancelledError:
                logger.info("Background image fetcher cancelled")
                break
            except Exception as e:
                logger.error(f"Error in background image fetcher: {e}")
                await asyncio.sleep(60)  # Wait a minute before retrying
