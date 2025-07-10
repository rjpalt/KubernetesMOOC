#!/usr/bin/env python3

import os
import logging
from datetime import datetime, timezone
from fastapi import FastAPI, HTTPException
from fastapi.responses import PlainTextResponse
import uvicorn
from settings import get_settings

# Load settings
settings = get_settings()

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.log_level),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)

logger = logging.getLogger(__name__)

app = FastAPI(title="Log Server", description="Serves shared log file contents via HTTP")

def get_current_timestamp():
    """Get current timestamp in ISO format"""
    return datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z'

@app.get("/logs", response_class=PlainTextResponse)
async def read_logs():
    """Read and return the contents of the shared log file"""
    try:
        if not os.path.exists(settings.shared_log_path):
            return "Log file not found. Generator may not have started yet."
        
        with open(settings.shared_log_path, 'r') as f:
            content = f.read()
        
        if not content.strip():
            return "Log file is empty. Generator may not have written anything yet."
        
        return content
    
    except Exception as e:
        logger.error(f"Error reading log file: {e}")
        raise HTTPException(status_code=500, detail=f"Error reading log file: {str(e)}")

@app.get("/")
async def root():
    """Root endpoint - redirects to logs for convenience"""
    return {"message": "Log Server", "logs_endpoint": "/logs", "health_endpoint": "/health", "status_endpoint": "/status"}

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "ok",
        "timestamp": get_current_timestamp(),
        "file_exists": os.path.exists(settings.shared_log_path)
    }

@app.get("/status")
async def get_status():
    """Get status information including file stats"""
    file_exists = os.path.exists(settings.shared_log_path)
    file_size = 0
    line_count = 0
    last_modified = None
    
    if file_exists:
        try:
            file_stat = os.stat(settings.shared_log_path)
            file_size = file_stat.st_size
            last_modified = datetime.fromtimestamp(file_stat.st_mtime, timezone.utc).strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z'
            
            with open(settings.shared_log_path, 'r') as f:
                line_count = sum(1 for line in f if line.strip())
        except Exception as e:
            logger.error(f"Error getting file stats: {e}")
    
    return {
        "timestamp": get_current_timestamp(),
        "log_file_path": settings.shared_log_path,
        "file_exists": file_exists,
        "file_size_bytes": file_size,
        "line_count": line_count,
        "last_modified": last_modified,
        "server_port": settings.log_server_port
    }

def main():
    """Start the log server"""
    logger.info(f"Starting log server on {settings.host}:{settings.log_server_port}")
    logger.info(f"Reading logs from: {settings.shared_log_path}")
    uvicorn.run(app, host=settings.host, port=settings.log_server_port, log_level=settings.log_level.lower())

if __name__ == "__main__":
    main()
