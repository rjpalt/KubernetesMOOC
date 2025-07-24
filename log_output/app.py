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

# Initialize configuration at startup - this will fail fast if required config is missing
try:
    settings.initialize_config()
    logger.info("Configuration initialized successfully")
except RuntimeError as e:
    logger.error(f"Configuration initialization failed: {e}")
    exit(1)

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
    
    # Get ConfigMap information once at startup
    file_content, env_message = settings.get_config_info()
    
    # Log ConfigMap detection at startup
    config_status = []
    if file_content:
        config_status.append(f"ConfigMap file detected: {file_content}")
    else:
        config_status.append(f"ConfigMap file not found at: {settings.config_file_path}")
    
    if env_message:
        config_status.append(f"MESSAGE env var detected: {env_message}")
    else:
        config_status.append("MESSAGE env var not set")
    
    logger.info("ConfigMap status:\n" + "\n".join(config_status))
    
    async def log_with_ping_count():
        timestamp = get_current_timestamp()
        ping_pong_count = await get_ping_pong_counter()
        
        # Build log message with ConfigMap info if available
        log_lines = []
        
        # Add ConfigMap file content if available (read once at startup)
        if file_content:
            log_lines.append(f"file content: {file_content}")
        
        # Add ConfigMap environment variable if available  
        if env_message:
            log_lines.append(f"env variable: MESSAGE={env_message}")
        
        # Add timestamp and random string
        log_lines.append(f"{timestamp}: {random_string}")
        
        # Add ping-pong count if available
        if ping_pong_count > 0:
            log_lines.append(f"Ping / Pongs: {ping_pong_count}")
        
        # Join all lines and log
        log_message = "\n".join(log_lines)
        logger.info(log_message)
    
    while True:
        # Run the async function in the current thread
        asyncio.run(log_with_ping_count())
        time.sleep(settings.log_interval_seconds)

@app.get("/")
async def get_status():
    """Endpoint to get current status with timestamp, random string, and ping-pong count"""
    ping_pong_count = await get_ping_pong_counter()
    
    # Get ConfigMap information
    file_content, env_message = settings.get_config_info()
    
    response = {
        "timestamp": get_current_timestamp(),
        "string": random_string,
        "status": "healthy"
    }
    
    # Add ConfigMap info if available
    if file_content:
        response["config_file_content"] = file_content
    
    if env_message:
        response["config_env_message"] = env_message
    
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
