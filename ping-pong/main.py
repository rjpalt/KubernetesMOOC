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

@app.get("/pingpong")
async def ping_pong():
    """Endpoint that responds with pong and increments counter"""
    global counter
    response = f"pong {counter}"
    counter += 1
    logger.info(f"Ping-pong request #{counter-1}, responded: {response}")
    return {"message": response}

@app.get("/pings")
async def get_pings():
    """Endpoint that returns the current ping count"""
    global counter
    logger.info(f"Pings count requested: {counter}")
    return {"pings": counter}

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "ok"}

def main():
    # Start the FastAPI server
    uvicorn.run(app, host=settings.host, port=settings.app_port, log_level=settings.log_level.lower())

if __name__ == "__main__":
    main()
