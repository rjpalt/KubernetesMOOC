"""Broadcaster Service - Main application."""

import asyncio
import logging
import sys
from contextlib import asynccontextmanager
from pathlib import Path

import uvicorn
from fastapi import FastAPI
from prometheus_client import start_http_server

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.api.routes import health
from src.config.settings import settings
from src.services.broadcaster_service import BroadcasterService

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.log_level),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()],
)

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler for startup and shutdown."""
    # Startup
    logger.info("Starting up broadcaster service...")

    # Start Prometheus metrics server
    try:
        start_http_server(settings.metrics_port)
        logger.info(f"Prometheus metrics server started on port {settings.metrics_port}")
    except Exception as e:
        logger.warning(f"Failed to start metrics server: {e}")

    # Start NATS consumer as background task
    broadcaster = BroadcasterService()
    task = asyncio.create_task(broadcaster.start())

    # Store broadcaster in app state for access during shutdown
    app.state.broadcaster = broadcaster
    app.state.broadcaster_task = task

    logger.info("Broadcaster service startup complete")

    yield

    # Shutdown
    logger.info("Shutting down broadcaster service...")

    # Stop broadcaster service
    await broadcaster.stop()

    # Cancel the background task
    if not task.done():
        task.cancel()
        try:
            await task
        except asyncio.CancelledError:
            pass

    logger.info("Broadcaster service shutdown complete")


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""

    # Create FastAPI app with lifespan
    app = FastAPI(
        title="Broadcaster Service",
        description="NATS to HTTP webhook broadcaster",
        version="0.1.0",
        lifespan=lifespan,
    )

    # Include health check routes
    app.include_router(health.router)

    return app


# Create app instance
app = create_app()


def main():
    """Run the server."""
    try:
        logger.info(f"Starting broadcaster service on {settings.host}:{settings.port}")
        logger.info(f"NATS URL: {settings.nats_url}")
        logger.info(f"NATS Topic: {settings.nats_topic}")
        logger.info(f"Webhook URL: {settings.webhook_url}")
        logger.info(f"Metrics port: {settings.metrics_port}")

        uvicorn.run(app, host=settings.host, port=settings.port)
    except Exception as e:
        logger.error(f"Failed to start broadcaster service: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
