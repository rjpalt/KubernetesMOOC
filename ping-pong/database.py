#!/usr/bin/env python3

import asyncio
import logging
from typing import Optional
import asyncpg
from settings import get_settings

logger = logging.getLogger(__name__)

class DatabaseManager:
    """Database connection and management for ping-pong counter"""
    
    def __init__(self):
        self.settings = get_settings()
        self.pool: Optional[asyncpg.Pool] = None
    
    async def initialize(self):
        """Initialize database connection pool and create tables"""
        try:
            logger.info(f"Connecting to database at {self.settings.db_host}:{self.settings.db_port}")
            
            # Create connection pool
            self.pool = await asyncpg.create_pool(
                self.settings.database_url,
                min_size=self.settings.db_pool_min_size,
                max_size=self.settings.db_pool_max_size,
                command_timeout=60
            )
            
            # Create tables if they don't exist
            await self._create_tables()
            
            # Initialize counter if it doesn't exist
            await self._initialize_counter()
            
            logger.info("Database connection and initialization successful")
            
        except Exception as e:
            logger.error(f"Failed to initialize database: {e}")
            raise
    
    async def _create_tables(self):
        """Create the ping_counter table if it doesn't exist"""
        async with self.pool.acquire() as conn:
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS ping_counter (
                    id SERIAL PRIMARY KEY,
                    counter_value INTEGER NOT NULL DEFAULT 0,
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
                )
            """)
            logger.info("Table ping_counter created or already exists")
    
    async def _initialize_counter(self):
        """Initialize counter to 0 if no record exists"""
        async with self.pool.acquire() as conn:
            # Check if counter exists
            result = await conn.fetchval("SELECT COUNT(*) FROM ping_counter")
            
            if result == 0:
                # Insert initial counter
                await conn.execute(
                    "INSERT INTO ping_counter (counter_value) VALUES ($1)",
                    0
                )
                logger.info("Initialized ping counter to 0")
            else:
                current_value = await conn.fetchval("SELECT counter_value FROM ping_counter ORDER BY id LIMIT 1")
                logger.info(f"Found existing counter with value: {current_value}")
    
    async def get_counter(self) -> int:
        """Get the current counter value"""
        # Try to reconnect if pool is not available
        if not self.pool:
            try:
                logger.info("Database not initialized, attempting to connect...")
                await self.initialize()
            except Exception as e:
                logger.warning(f"Failed to connect to database: {e}")
                raise RuntimeError("Database not initialized")
        
        # At this point, pool should be initialized
        if not self.pool:
            raise RuntimeError("Database not initialized")
            
        try:
            async with self.pool.acquire() as conn:
                result = await conn.fetchval(
                    "SELECT counter_value FROM ping_counter ORDER BY id LIMIT 1"
                )
                return result if result is not None else 0
        except Exception as e:
            logger.error(f"Database query failed: {e}")
            # Reset pool to force reconnection on next attempt
            self.pool = None
            raise RuntimeError("Database not initialized")
    
    async def increment_counter(self) -> int:
        """Increment the counter and return the new value"""
        # Try to reconnect if pool is not available
        if not self.pool:
            try:
                logger.info("Database not initialized, attempting to connect...")
                await self.initialize()
            except Exception as e:
                logger.warning(f"Failed to connect to database: {e}")
                raise RuntimeError("Database not initialized")
        
        # At this point, pool should be initialized
        if not self.pool:
            raise RuntimeError("Database not initialized")
            
        try:
            async with self.pool.acquire() as conn:
                # Use a transaction to ensure atomicity
                async with conn.transaction():
                    # Get current value and increment
                    new_value = await conn.fetchval("""
                        UPDATE ping_counter 
                        SET counter_value = counter_value + 1, 
                            updated_at = NOW() 
                        WHERE id = (SELECT id FROM ping_counter ORDER BY id LIMIT 1)
                        RETURNING counter_value
                    """)
                    
                    if new_value is None:
                        # This should not happen if initialization worked correctly
                        logger.warning("No counter found, creating new one")
                        await conn.execute(
                            "INSERT INTO ping_counter (counter_value) VALUES ($1)",
                            1
                        )
                        new_value = 1
                    
                    return new_value
        except Exception as e:
            logger.error(f"Database query failed: {e}")
            # Reset pool to force reconnection on next attempt
            self.pool = None
            raise RuntimeError("Database not initialized")
    
    async def close(self):
        """Close database connection pool"""
        if self.pool:
            await self.pool.close()
            logger.info("Database connection pool closed")
        else:
            logger.info("Database connection pool was not initialized, nothing to close")

# Global database manager instance
db_manager = DatabaseManager()

async def init_database():
    """Initialize the database connection"""
    await db_manager.initialize()

async def close_database():
    """Close the database connection"""
    await db_manager.close()

async def get_ping_counter() -> int:
    """Get current ping counter value"""
    return await db_manager.get_counter()

async def increment_ping_counter() -> int:
    """Increment and return new ping counter value"""
    return await db_manager.increment_counter()
