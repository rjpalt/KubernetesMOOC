"""Application lifespan management."""
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI

logger = logging.getLogger(__name__)


def create_lifespan_manager(background_task_manager):
    """Create a lifespan context manager for the FastAPI application."""
    
    @asynccontextmanager
    async def lifespan(app: FastAPI):
        """Lifespan context manager for startup and shutdown events."""
        # Startup: Start background tasks
        await background_task_manager.start_background_tasks()
        logger.info("Application startup complete")

        yield  # Application runs here

        # Shutdown: Clean up background tasks
        await background_task_manager.stop_background_tasks()
        logger.info("Application shutdown complete")
    
    return lifespan
