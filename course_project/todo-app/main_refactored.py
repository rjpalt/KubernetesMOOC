"""Main application entry point - clean and modular."""
import logging
import uvicorn
from fastapi import FastAPI

from src.config.settings import settings
from src.api.dependencies import initialize_dependencies, get_background_task_manager_instance
from src.api.routes import images, health
from src.core.lifespan import create_lifespan_manager

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
    app = FastAPI(
        title="Todo App with Hourly Images",
        version="0.2.0",
        lifespan=lifespan
    )
    
    # Include routers
    app.include_router(images.router)
    app.include_router(health.router)
    
    return app


# Create app instance
app = create_app()


def main():
    """Run the server."""
    logger.info(f"Starting Todo App with Image Caching on port {settings.port}")
    logger.info(f"Image cache path: {settings.image_cache_path}")
    logger.info(f"Update interval: {settings.image_update_interval_minutes} minutes")

    uvicorn.run(
        "main_refactored:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
    )


if __name__ == "__main__":
    main()
