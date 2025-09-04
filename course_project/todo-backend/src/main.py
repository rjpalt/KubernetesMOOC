"""Todo Backend API - Main application."""

# Trigger CI/CD pipeline test - Azure Files ReadWriteMany backend update
import logging
import sys
from contextlib import asynccontextmanager
from pathlib import Path

import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.api.dependencies import get_todo_service, initialize_dependencies
from src.api.error_handlers import (
    custom_404_handler,
    custom_http_exception_handler,
    custom_server_error_handler,
    custom_validation_error_handler,
)
from src.api.routes import health, todos
from src.config.settings import settings
from src.database.connection import db_manager
from src.middleware.request_logging import RequestLoggingMiddleware
from src.middleware.security import SecurityHeadersMiddleware, XSSProtectionMiddleware

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

        # Check database health with graceful degradation
        try:
            is_db_healthy = await db_manager.health_check(max_retries=3)
            if not is_db_healthy:
                logger.warning("Database not immediately available - starting in degraded mode")
                logger.warning("Application will continue startup, database connectivity will be verified by health probes")
            else:
                logger.info("Database initialized and health check passed")
                
                # Only initialize sample data if database is available
                todo_service = get_todo_service()
                await todo_service.initialize_with_sample_data()
                logger.info("Sample data initialized")
                
        except Exception as e:
            logger.warning(f"Database initialization had issues: {e}")
            logger.warning("Application starting in degraded mode - health probes will handle database connectivity")

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

    # Add custom error handlers for information disclosure prevention
    app.add_exception_handler(HTTPException, custom_http_exception_handler)
    app.add_exception_handler(RequestValidationError, custom_validation_error_handler)
    app.add_exception_handler(404, custom_404_handler)
    app.add_exception_handler(Exception, custom_server_error_handler)

    # Add security middleware (should be first for security headers)
    app.add_middleware(SecurityHeadersMiddleware)
    app.add_middleware(XSSProtectionMiddleware)

    # Add request logging middleware
    app.add_middleware(RequestLoggingMiddleware)

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
