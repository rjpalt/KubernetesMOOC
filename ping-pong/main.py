#!/usr/bin/env python3

import logging
from fastapi import FastAPI
import uvicorn

# Configure logging
logging.basicConfig(
    level=logging.INFO,
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

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "ok"}

def main():
    # Start the FastAPI server
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")

if __name__ == "__main__":
    main()
