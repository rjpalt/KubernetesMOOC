#!/usr/bin/env python3

import logging
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI, HTTPException

from settings import get_settings
from database import init_database, close_database, get_ping_counter, increment_ping_counter

# Load settings
settings = get_settings()

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.log_level),
    format="%(message)s",
    handlers=[logging.StreamHandler()],
)

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan management"""
    # Startup
    logger.info("Starting ping-pong application")
    try:
        await init_database()
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        raise
    
    yield
    
    # Shutdown
    logger.info("Shutting down ping-pong application")
    await close_database()


app = FastAPI(
    title="Ping Pong App", 
    description="A simple ping-pong counter service with PostgreSQL storage",
    lifespan=lifespan
)


@app.get("/")
async def ping_pong():
    """Root endpoint that responds with pong and increments counter"""
    try:
        new_counter = await increment_ping_counter()
        response = f"pong {new_counter - 1}"  # Show the value before increment
        logger.info(f"Ping-pong request #{new_counter - 1}, responded: {response}")
        return {"message": response}
    except Exception as e:
        logger.error(f"Failed to increment counter: {e}")
        raise HTTPException(status_code=500, detail="Database error")


@app.get("/pings")
async def get_pings():
    """Endpoint that returns the current ping count"""
    try:
        counter = await get_ping_counter()
        logger.info(f"Pings count requested: {counter}")
        return {"pings": counter}
    except Exception as e:
        logger.error(f"Failed to get counter: {e}")
        raise HTTPException(status_code=500, detail="Database error")


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "ok"}


@app.get("/health/ready")
async def readiness_check():
    """Readiness check endpoint - checks database connectivity"""
    try:
        # Try to get counter to verify database is accessible
        await get_ping_counter()
        return {"status": "ready", "database": "connected"}
    except Exception as e:
        logger.error(f"Readiness check failed: {e}")
        raise HTTPException(status_code=503, detail="Database not ready")


def main():
    # Start the FastAPI server
    uvicorn.run(
        app,
        host=settings.host,
        port=settings.app_port,
        log_level=settings.log_level.lower(),
    )


if __name__ == "__main__":
    main()
