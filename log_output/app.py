#!/usr/bin/env python3

import time
import uuid
import logging
import asyncio
import threading
import httpx
from datetime import datetime, timezone
from fastapi import FastAPI
import uvicorn
from settings import get_settings

# Load settings
settings = get_settings()

def setup_logging():
    logger = logging.getLogger(__name__)
    logger.setLevel(getattr(logging, settings.log_level))
    
    # Clear any existing handlers
    logger.handlers.clear()
    
    # Console handler for kubectl logs
    console_handler = logging.StreamHandler()
    console_handler.setLevel(getattr(logging, settings.log_level))
    
    # Simple format without metadata cruft
    formatter = logging.Formatter('%(message)s')
    console_handler.setFormatter(formatter)
    
    logger.addHandler(console_handler)
    
    return logger

logger = setup_logging()

# Global variables to store the random string and app state
random_string = str(uuid.uuid4())
app = FastAPI(title="Log Output App", description="A simple app that logs timestamps and serves status")

async def get_ping_pong_counter():
    """Get the current ping-pong counter via HTTP request"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"http://{settings.ping_pong_service_host}:{settings.ping_pong_service_port}/pings", timeout=5.0)
            response.raise_for_status()
            data = response.json()
            return data.get("pings", 0)
    except Exception as e:
        logger.error(f"Failed to get ping-pong counter via HTTP: {e}")
        return 0

def get_current_timestamp():
    """Get current timestamp in ISO format"""
    return datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z'

def logging_worker():
    """Background worker that logs the timestamp, random string, and ping-pong counter every 5 seconds"""
    logger.info(f"Application started. Generated string: {random_string}")
    
    async def log_with_ping_count():
        timestamp = get_current_timestamp()
        ping_pong_count = await get_ping_pong_counter()
        log_message = f"{timestamp}: {random_string}"
        if ping_pong_count > 0:
            log_message += f"\nPing / Pongs: {ping_pong_count}"
        logger.info(log_message)
    
    while True:
        # Run the async function in the current thread
        asyncio.run(log_with_ping_count())
        time.sleep(settings.log_interval_seconds)

@app.get("/")
async def get_status():
    """Endpoint to get current status with timestamp, random string, and ping-pong count"""
    ping_pong_count = await get_ping_pong_counter()
    response = {
        "timestamp": get_current_timestamp(),
        "string": random_string,
        "status": "healthy"
    }
    if ping_pong_count > 0:
        response["ping_pong_count"] = ping_pong_count
    return response

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "ok"}

def main():
    # Start the logging worker in a separate thread
    logging_thread = threading.Thread(target=logging_worker, daemon=True)
    logging_thread.start()
    
    # Start the FastAPI server
    uvicorn.run(app, host=settings.host, port=settings.app_port, log_level=settings.log_level.lower())

if __name__ == "__main__":
    main()
