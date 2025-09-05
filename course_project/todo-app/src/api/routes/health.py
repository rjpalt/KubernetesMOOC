"""Health and system-related API routes."""

import asyncio
import os
from datetime import UTC, datetime

from fastapi import APIRouter, Depends

from ...config.settings import settings
from ...services.image_service import ImageService

router = APIRouter()


def get_image_service() -> ImageService:
    """Dependency to get image service instance."""
    from ...api.dependencies import get_image_service_instance

    return get_image_service_instance()


@router.get("/health")
async def health_check(image_service: ImageService = Depends(get_image_service)):
    """Health check endpoint."""
    image_info = await image_service.get_image_info()
    return {
        "status": "healthy",
        "timestamp": datetime.now(UTC).isoformat(),
        "image_cache_status": image_info.status,
        "cache_path": str(settings.image_cache_path),
        "update_interval_minutes": settings.image_update_interval_minutes,
    }


@router.get("/healthz")
async def liveness_check():
    """Lightweight liveness check endpoint - no dependencies."""
    return {"status": "ok"}


@router.post("/shutdown")
async def shutdown_container():
    """Shutdown endpoint for testing container resilience."""
    import logging

    logger = logging.getLogger(__name__)
    logger.warning("Shutdown endpoint called - stopping application for testing")

    # Give a brief response before shutting down
    asyncio.create_task(_delayed_shutdown())
    return {"message": "Shutdown initiated for testing purposes"}


async def _delayed_shutdown():
    """Shutdown the application after a brief delay."""
    await asyncio.sleep(1)  # Give time for the response to be sent
    os._exit(0)  # Force exit (for testing purposes)
