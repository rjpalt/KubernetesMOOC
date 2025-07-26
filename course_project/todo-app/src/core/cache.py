"""Image cache management with atomic operations and metadata tracking."""

import logging
import uuid
from datetime import UTC, datetime, timedelta

import aiofiles
import httpx

from ..config.settings import settings
from ..models.image import FetchResult, ImageInfo, ImageMetadata

logger = logging.getLogger(__name__)


class ImageCacheManager:
    """Manages image caching with atomic operations and metadata tracking."""

    def __init__(self):
        self.cache_path = settings.image_cache_path
        self.current_image_file = settings.image_current_file
        self.metadata_file = settings.image_metadata_file
        self._last_fetch_time: datetime | None = None

    @property
    def last_fetch_time(self) -> datetime | None:
        """Get the last fetch time."""
        return self._last_fetch_time

    async def fetch_new_image(self, force: bool = False) -> FetchResult:
        """Fetch a new image from Lorem Picsum and cache it."""
        # Check if we need to fetch (unless forced)
        if not force and self._last_fetch_time:
            time_since_last = datetime.now(UTC) - self._last_fetch_time
            if time_since_last < timedelta(minutes=settings.image_update_interval_minutes):
                return FetchResult(
                    status="skipped",
                    reason=f"Last fetch was {time_since_last.total_seconds():.0f}s ago, "
                    f"interval is {settings.image_update_interval_minutes * 60}s",
                    last_fetch=self._last_fetch_time.isoformat(),
                    timestamp=datetime.now(UTC).isoformat(),
                )

        logger.info(f"Fetching new image from {settings.picsum_url}...")

        try:
            # Add random parameter to bypass Picsum caching
            url = f"{settings.picsum_url}?random={uuid.uuid4().hex[:8]}"

            async with httpx.AsyncClient(timeout=settings.http_timeout, follow_redirects=True) as client:
                response = await client.get(url)
                response.raise_for_status()

                # Write to temporary file first (atomic operation)
                temp_file = self.cache_path / f"temp_{uuid.uuid4().hex[:8]}.jpg"

                async with aiofiles.open(temp_file, "wb") as f:
                    await f.write(response.content)

                # Verify it's a valid image (basic check)
                if len(response.content) < 1000:  # Too small to be a real image
                    temp_file.unlink()
                    raise ValueError("Downloaded file is too small to be a valid image")

                # Atomic move to final location
                temp_file.rename(self.current_image_file)

                # Update metadata
                now = datetime.now(UTC)
                self._last_fetch_time = now

                metadata = ImageMetadata(
                    timestamp=now.isoformat(),
                    size_bytes=len(response.content),
                    url=url,
                    status="success",
                )

                async with aiofiles.open(self.metadata_file, "w") as f:
                    await f.write(f"{metadata.timestamp}\n{metadata.size_bytes}\n{metadata.url}")

                logger.info(f"Successfully cached new image: {len(response.content)} bytes")

                return FetchResult(
                    status="success",
                    timestamp=metadata.timestamp,
                    size_bytes=metadata.size_bytes,
                    url=metadata.url,
                )

        except Exception as e:
            logger.error(f"Failed to fetch image: {e}")
            return FetchResult(
                status="error",
                error=str(e),
                timestamp=datetime.now(UTC).isoformat(),
            )

    async def get_current_image_info(self) -> ImageInfo:
        """Get information about the current cached image."""
        if not self.current_image_file.exists():
            return ImageInfo(status="no_image", message="No image has been cached yet")

        stat = self.current_image_file.stat()

        # Try to read metadata
        metadata = None
        if self.metadata_file.exists():
            try:
                async with aiofiles.open(self.metadata_file) as f:
                    lines = (await f.read()).strip().split("\n")
                    if len(lines) >= 3:
                        metadata = ImageMetadata(
                            timestamp=lines[0],
                            size_bytes=int(lines[1]),
                            url=lines[2],
                        )
            except Exception as e:
                logger.warning(f"Failed to read metadata: {e}")

        next_auto_fetch = None
        if self._last_fetch_time:
            next_auto_fetch = (
                self._last_fetch_time + timedelta(minutes=settings.image_update_interval_minutes)
            ).isoformat()

        return ImageInfo(
            status="available",
            file_size=stat.st_size,
            modified_time=datetime.fromtimestamp(stat.st_mtime, UTC).isoformat(),
            metadata=metadata,
            last_fetch_time=self._last_fetch_time.isoformat() if self._last_fetch_time else None,
            next_auto_fetch=next_auto_fetch,
        )
