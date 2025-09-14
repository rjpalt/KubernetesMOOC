"""Health check endpoints for Kubernetes probes."""

import logging
from typing import Any

from fastapi import APIRouter, status

from ...config.settings import settings

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/health", status_code=status.HTTP_200_OK)
async def health() -> dict[str, Any]:
    """Basic health check endpoint for liveness probe."""
    return {"status": "healthy", "service": "broadcaster", "version": "0.1.0"}


@router.get("/healthz", status_code=status.HTTP_200_OK)
async def healthz() -> dict[str, Any]:
    """Kubernetes-style health check endpoint."""
    return {
        "status": "healthy",
        "service": "broadcaster",
        "version": "0.1.0",
        "nats_url": settings.nats_url,
        "webhook_url": settings.webhook_url,
    }


@router.get("/ready", status_code=status.HTTP_200_OK)
async def ready() -> dict[str, Any]:
    """Readiness probe endpoint."""
    # For now, just return healthy - in production this could check NATS connection
    return {"status": "ready", "service": "broadcaster", "version": "0.1.0"}
