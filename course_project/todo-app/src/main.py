"""Main application entry point - clean and modular."""

# Trigger CI/CD pipeline test - Azure Files storage update
import logging

import uvicorn
from fastapi import FastAPI

from .api.dependencies import get_background_task_manager_instance, initialize_dependencies
from .api.routes import health, images, todos
from .config.settings import settings
from .core.lifespan import create_lifespan_manager
from .middleware.security import FrontendSecurityHeadersMiddleware

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.log_level),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()],
)

logger = logging.getLogger(__name__)


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    # Initialize dependencies
    initialize_dependencies()

    # Get background task manager for lifespan
    background_task_manager = get_background_task_manager_instance()

    # Create lifespan manager
    lifespan = create_lifespan_manager(background_task_manager)

    # Create FastAPI app
    app = FastAPI(title="Todo App with Hourly Images", version="0.2.0", lifespan=lifespan)

    # Add security middleware (should be first)
    app.add_middleware(FrontendSecurityHeadersMiddleware)

    # Include routers
    app.include_router(images.router)
    app.include_router(health.router)
    app.include_router(todos.router)

    return app


# Create app instance
app = create_app()


def main():
    """Run the server."""
    logger.info(f"Starting Todo App with Image Caching on port {settings.port}")
    logger.info(f"Image cache path: {settings.image_cache_path}")
    logger.info(f"Update interval: {settings.image_update_interval_minutes} minutes")

    uvicorn.run(
        "src.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
    )


if __name__ == "__main__":
    main()
