#!/usr/bin/env python3

import os
import logging
from fastapi import FastAPI
import uvicorn
from settings import get_settings

# Load settings
settings = get_settings()

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.log_level),
    format='%(message)s',
    handlers=[logging.StreamHandler()]
)

logger = logging.getLogger(__name__)

# Global counter - yes, it's in memory, yes it will reset
counter = 0
app = FastAPI(title="Ping Pong App", description="A simple ping-pong counter service")

def write_counter_to_file():
    """Write the current counter value to the shared file"""
    try:
        os.makedirs(settings.shared_volume_path, exist_ok=True)
        with open(settings.counter_file_path, 'w') as f:
            f.write(str(counter))
    except Exception as e:
        logger.error(f"Failed to write counter to file: {e}")

def read_counter_from_file():
    """Read the counter value from the shared file on startup"""
    global counter
    try:
        if os.path.exists(settings.counter_file_path):
            with open(settings.counter_file_path, 'r') as f:
                counter = int(f.read().strip())
                logger.info(f"Restored counter from file: {counter}")
    except Exception as e:
        logger.error(f"Failed to read counter from file: {e}")
        counter = 0

@app.get("/pingpong")
async def ping_pong():
    """Endpoint that responds with pong and increments counter"""
    global counter
    response = f"pong {counter}"
    counter += 1
    write_counter_to_file()  # Persist counter to shared volume
    logger.info(f"Ping-pong request #{counter-1}, responded: {response}")
    return {"message": response}

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "ok"}

def main():
    # Read counter from shared file on startup
    read_counter_from_file()
    
    # Start the FastAPI server
    uvicorn.run(app, host=settings.host, port=settings.app_port, log_level=settings.log_level.lower())

if __name__ == "__main__":
    main()
