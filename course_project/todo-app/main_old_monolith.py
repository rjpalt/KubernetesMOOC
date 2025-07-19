import logging
import os
import asyncio
import uuid
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Optional
from contextlib import asynccontextmanager

import aiofiles
import httpx
import uvicorn
from fastapi import FastAPI, HTTPException, BackgroundTasks, Request
from fastapi.responses import FileResponse
from fastapi.templating import Jinja2Templates

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()],
)

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup and shutdown events."""
    # Startup: Start background tasks
    global image_fetch_task
    image_fetch_task = asyncio.create_task(background_image_fetcher())
    logger.info("Application startup complete - background image fetcher started")

    yield  # Application runs here

    # Shutdown: Clean up background tasks
    if image_fetch_task:
        image_fetch_task.cancel()
        try:
            await image_fetch_task
        except asyncio.CancelledError:
            pass
    logger.info("Application shutdown complete - background tasks cleaned up")


app = FastAPI(title="Todo App with Hourly Images", version="0.2.0", lifespan=lifespan)

# Setup Jinja2 templates
templates = Jinja2Templates(directory="templates")

# Configuration
IMAGE_CACHE_PATH = Path(os.environ.get("IMAGE_CACHE_PATH", "./images"))
IMAGE_UPDATE_INTERVAL_MINUTES = int(os.environ.get("IMAGE_UPDATE_INTERVAL_MINUTES", "10"))
PICSUM_URL = "https://picsum.photos/1200"

# Ensure image cache directory exists
IMAGE_CACHE_PATH.mkdir(exist_ok=True)

# Global state
image_fetch_task: Optional[asyncio.Task] = None
last_fetch_time: Optional[datetime] = None
current_image_path: Optional[Path] = None


class ImageCacheManager:
    """Manages image caching with atomic operations and metadata tracking."""

    def __init__(self, cache_path: Path):
        self.cache_path = cache_path
        self.current_image_file = cache_path / "current.jpg"
        self.metadata_file = cache_path / "metadata.txt"

    async def fetch_new_image(self, force: bool = False) -> dict:
        """Fetch a new image from Lorem Picsum and cache it."""
        global last_fetch_time, current_image_path

        # Check if we need to fetch (unless forced)
        if not force and last_fetch_time:
            time_since_last = datetime.now(timezone.utc) - last_fetch_time
            if time_since_last < timedelta(minutes=IMAGE_UPDATE_INTERVAL_MINUTES):
                return {
                    "status": "skipped",
                    "reason": f"Last fetch was {time_since_last.total_seconds():.0f}s ago, "
                    f"interval is {IMAGE_UPDATE_INTERVAL_MINUTES*60}s",
                    "last_fetch": last_fetch_time.isoformat(),
                }

        logger.info(f"Fetching new image from {PICSUM_URL}...")

        try:
            # Add random parameter to bypass Picsum caching
            url = f"{PICSUM_URL}?random={uuid.uuid4().hex[:8]}"

            async with httpx.AsyncClient(timeout=30.0, follow_redirects=True) as client:
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
                current_image_path = self.current_image_file

                # Update metadata
                now = datetime.now(timezone.utc)
                last_fetch_time = now

                metadata = {
                    "timestamp": now.isoformat(),
                    "size_bytes": len(response.content),
                    "url": url,
                    "status": "success",
                }

                async with aiofiles.open(self.metadata_file, "w") as f:
                    await f.write(f"{metadata['timestamp']}\n{metadata['size_bytes']}\n{metadata['url']}")

                logger.info(f"Successfully cached new image: {len(response.content)} bytes")
                return metadata

        except Exception as e:
            logger.error(f"Failed to fetch image: {e}")
            return {
                "status": "error",
                "error": str(e),
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }

    async def get_current_image_info(self) -> dict:
        """Get information about the current cached image."""
        if not self.current_image_file.exists():
            return {"status": "no_image", "message": "No image has been cached yet"}

        stat = self.current_image_file.stat()

        # Try to read metadata
        metadata = {"timestamp": None, "size_bytes": stat.st_size, "url": "unknown"}
        if self.metadata_file.exists():
            try:
                async with aiofiles.open(self.metadata_file, "r") as f:
                    lines = (await f.read()).strip().split("\n")
                    if len(lines) >= 3:
                        metadata.update(
                            {
                                "timestamp": lines[0],
                                "size_bytes": int(lines[1]),
                                "url": lines[2],
                            }
                        )
            except Exception as e:
                logger.warning(f"Failed to read metadata: {e}")

        return {
            "status": "available",
            "file_size": stat.st_size,
            "modified_time": datetime.fromtimestamp(stat.st_mtime, timezone.utc).isoformat(),
            "metadata": metadata,
            "last_fetch_time": last_fetch_time.isoformat() if last_fetch_time else None,
            "next_auto_fetch": (
                (last_fetch_time + timedelta(minutes=IMAGE_UPDATE_INTERVAL_MINUTES)).isoformat()
                if last_fetch_time
                else None
            ),
        }


# Initialize image cache manager
image_cache = ImageCacheManager(IMAGE_CACHE_PATH)


async def background_image_fetcher():
    """Background task that periodically fetches new images."""
    logger.info(f"Starting background image fetcher (interval: {IMAGE_UPDATE_INTERVAL_MINUTES} minutes)")

    # Fetch initial image if none exists
    if not image_cache.current_image_file.exists():
        logger.info("No cached image found, fetching initial image...")
        await image_cache.fetch_new_image(force=True)

    while True:
        try:
            await asyncio.sleep(60)  # Check every minute
            await image_cache.fetch_new_image(force=False)
        except asyncio.CancelledError:
            logger.info("Background image fetcher cancelled")
            break
        except Exception as e:
            logger.error(f"Error in background image fetcher: {e}")
            await asyncio.sleep(60)  # Wait a minute before retrying


@app.get("/")
async def read_root(request: Request):
    """Root endpoint - returns HTML page with current image and controls."""
    image_info = await image_cache.get_current_image_info()

    # Determine image status for display
    image_status = "No image available"
    if image_info["status"] == "available":
        image_status = f"Image loaded ({image_info['file_size']} bytes)"
        if image_info.get("last_fetch_time"):
            fetch_time = datetime.fromisoformat(image_info["last_fetch_time"].replace("Z", "+00:00"))
            image_status += f" - Last updated: {fetch_time.strftime('%H:%M:%S UTC')}"

    # Configuration data for template
    config = {
        "cache_path": str(IMAGE_CACHE_PATH),
        "update_interval": IMAGE_UPDATE_INTERVAL_MINUTES,
        "picsum_url": PICSUM_URL,
    }

    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "image_info": image_info,
            "image_status": image_status,
            "config": config,
        },
    )


@app.get("/image")
async def get_current_image():
    """Serve the current cached image."""
    if not image_cache.current_image_file.exists():
        raise HTTPException(status_code=404, detail="No image available. Fetch one first.")

    return FileResponse(image_cache.current_image_file, media_type="image/jpeg")


@app.get("/image/info")
async def get_image_info():
    """Get detailed information about the current cached image."""
    return await image_cache.get_current_image_info()


@app.post("/fetch-image")
async def fetch_new_image_endpoint(force: bool = False, background_tasks: BackgroundTasks = None):
    """Manually trigger a new image fetch."""
    logger.info(f"Manual image fetch requested (force={force})")
    result = await image_cache.fetch_new_image(force=force)
    return result


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    image_info = await image_cache.get_current_image_info()
    return {
        "status": "healthy",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "image_cache_status": image_info["status"],
        "cache_path": str(IMAGE_CACHE_PATH),
        "update_interval_minutes": IMAGE_UPDATE_INTERVAL_MINUTES,
    }


@app.post("/shutdown")
async def shutdown_container():
    """Shutdown endpoint for testing container resilience."""
    logger.warning("Shutdown endpoint called - stopping application for testing")

    # Cancel background task
    if image_fetch_task:
        image_fetch_task.cancel()

    # Give a brief response before shutting down
    import asyncio

    asyncio.create_task(delayed_shutdown())

    return {"message": "Shutdown initiated for testing purposes"}


async def delayed_shutdown():
    """Shutdown the application after a brief delay."""
    await asyncio.sleep(1)  # Give time for the response to be sent
    import os

    os._exit(0)  # Force exit (for testing purposes)


def main():
    """Run the server."""
    port = int(os.environ.get("PORT", 8000))
    logger.info(f"Starting Todo App with Image Caching on port {port}")
    logger.info(f"Image cache path: {IMAGE_CACHE_PATH}")
    logger.info(f"Update interval: {IMAGE_UPDATE_INTERVAL_MINUTES} minutes")

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=port,
        reload=False,
    )


if __name__ == "__main__":
    main()
