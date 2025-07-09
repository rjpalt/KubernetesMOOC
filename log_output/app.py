#!/usr/bin/env python3

import time
import uuid
import logging
import asyncio
import threading
from datetime import datetime, timezone
from fastapi import FastAPI
import uvicorn

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(message)s',
    handlers=[logging.StreamHandler()]
)

logger = logging.getLogger(__name__)

# Global variables to store the random string and app state
random_string = str(uuid.uuid4())
app = FastAPI(title="Log Output App", description="A simple app that logs timestamps and serves status")

def get_current_timestamp():
    """Get current timestamp in ISO format"""
    return datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z'

def logging_worker():
    """Background worker that logs the timestamp and random string every 5 seconds"""
    logger.info(f"Application started. Generated string: {random_string}")
    
    while True:
        timestamp = get_current_timestamp()
        logger.info(f"{timestamp}: {random_string}")
        time.sleep(5)

@app.get("/")
async def get_status():
    """Endpoint to get current status with timestamp and random string"""
    return {
        "timestamp": get_current_timestamp(),
        "string": random_string,
        "status": "healthy"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "ok"}

def main():
    # Start the logging worker in a separate thread
    logging_thread = threading.Thread(target=logging_worker, daemon=True)
    logging_thread.start()
    
    # Start the FastAPI server
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")

if __name__ == "__main__":
    main()
