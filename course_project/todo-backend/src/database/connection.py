"""Database connection management with async SQLAlchemy."""

import asyncio
import logging
import os

from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker, create_async_engine

from config.settings import settings

from .models import Base

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
