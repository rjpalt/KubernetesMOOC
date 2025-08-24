import asyncio
import logging
import os

from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker, create_async_engine

from src.config.settings import settings

from .models import Base

"""Database connection management with async SQLAlchemy. Handles local and Azure Cloud, yeah baby."""
"""
Database connection management using asynchronous SQLAlchemy.

This module provides the `DatabaseManager` class, which encapsulates the logic for initializing,
managing, and closing asynchronous database connections and sessions. It is designed to work with
both local and Azure Cloud environments, supporting connection pooling and robust health checks.

Key Features:
- Asynchronous database engine creation with configurable connection pooling.
- Session factory management for generating async database sessions.
- Automatic creation of database tables based on SQLAlchemy models.
- Health check functionality with retry logic and exponential backoff to ensure database connectivity.
- Graceful shutdown and disposal of database connections.

Classes:
    DatabaseManager:
        Handles the lifecycle of the database engine and session factory, provides methods for
        initialization, health checking, session retrieval, and cleanup.

Global Variables:
    db_manager:
        A singleton instance of `DatabaseManager` for use throughout the application.

Usage:
    1. Call `await db_manager.initialize()` during application startup to set up the database.
    2. Use `db_manager.get_session()` to obtain an async session for database operations.
    3. Optionally, use `await db_manager.health_check()` to verify connectivity.
    4. Call `await db_manager.close()` during application shutdown to release resources.

Configuration:
    The database connection URL and other settings are sourced from the application's configuration
    (see `src.config.settings`). Connection pool parameters can be adjusted as needed.

Logging:
    All major operations and errors are logged using the standard Python logging module.
"""

logger = logging.getLogger(__name__)


class DatabaseManager:
    """Manages database connections and sessions."""

    def __init__(self):
        self.engine: AsyncEngine | None = None
        self.session_factory: async_sessionmaker[AsyncSession] | None = None

    @property
    def database_url(self) -> str:
        """Get database URL from enhanced settings."""
        return settings.database_url

    async def initialize(self) -> None:
        """Initialize database connection with connection pooling."""
        try:
            # Create async engine with connection pooling
            self.engine = create_async_engine(
                self.database_url,
                # Connection pool settings
                pool_size=5,  # Number of connections to maintain
                max_overflow=10,  # Additional connections when pool is full
                pool_timeout=30,  # Seconds to wait for connection
                pool_recycle=3600,  # Recycle connections after 1 hour
                # Async settings
                echo=os.getenv("SQL_DEBUG", "false").lower() == "true",
            )

            # Create session factory
            self.session_factory = async_sessionmaker(bind=self.engine, class_=AsyncSession, expire_on_commit=False)

            # Create tables if they don't exist
            await self._create_tables()

            logger.info("Database initialized successfully")

        except Exception as e:
            logger.error(f"Failed to initialize database: {e}")
            raise

    async def _create_tables(self) -> None:
        """Create database tables."""
        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    async def health_check(self, max_retries: int = 3) -> bool:
        """Check database connectivity with retries."""
        for attempt in range(max_retries):
            try:
                session = self.get_session()
                async with session as s:
                    await s.execute(text("SELECT 1"))
                    return True
            except SQLAlchemyError as e:
                logger.warning(f"Database health check failed (attempt {attempt + 1}): {e}")
                if attempt < max_retries - 1:
                    await asyncio.sleep(2**attempt)  # Exponential backoff

        return False

    def get_session(self) -> AsyncSession:
        """Get database session."""
        if not self.session_factory:
            raise RuntimeError("Database not initialized")

        return self.session_factory()

    async def close(self) -> None:
        """Close database connections."""
        if self.engine:
            await self.engine.dispose()
            logger.info("Database connections closed")


# Global database manager instance
db_manager = DatabaseManager()
