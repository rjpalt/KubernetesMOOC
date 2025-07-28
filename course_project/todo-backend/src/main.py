"""Todo Backend API - Main application."""

import logging
import sys
from contextlib import asynccontextmanager
from pathlib import Path

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.api.dependencies import get_todo_service, initialize_dependencies
from src.api.routes import health, todos
from src.config.settings import settings
from src.database.connection import db_manager

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
    logger.info("Starting up todo backend...")

    try:
        # Initialize database
        await db_manager.initialize()

        # Check database health
        if not await db_manager.health_check():
            logger.error("Database health check failed")
            raise RuntimeError("Database connection failed")

        logger.info("Database initialized and health check passed")

        # Initialize sample data
        todo_service = get_todo_service()
        await todo_service.initialize_with_sample_data()
        logger.info("Sample data initialized")

    except Exception as e:
        logger.error(f"Startup failed: {e}")
        raise

    yield

    # Shutdown
    logger.info("Shutting down todo backend...")
    await db_manager.close()
    logger.info("Database connections closed")


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    # Initialize dependencies
    initialize_dependencies()

    # Create FastAPI app with lifespan
    app = FastAPI(
        title=settings.api_title,
        description=settings.api_description,
        version=settings.api_version,
        lifespan=lifespan,
    )

    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins_list,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Include routers
    app.include_router(health.router)
    app.include_router(todos.router)

    return app


# Create app instance
app = create_app()


def main():
    """Run the server."""
    uvicorn.run(app, host=settings.host, port=settings.port)


if __name__ == "__main__":
    main()
