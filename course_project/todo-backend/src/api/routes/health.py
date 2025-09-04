"""Health check endpoints."""

import logging
from datetime import datetime, UTC
from fastapi import APIRouter, HTTPException

from ...api.dependencies import get_todo_service
from ...config.settings import settings

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/be-health")
async def health_check():
    """Backend health check endpoint."""
    response = {
        "status": "healthy",
        "service": "todo-backend",
        "environment": {
            "is_production": settings.is_production,
            "debug_enabled": settings.debug_enabled,
            "mode": "production" if settings.is_production else "development",
        },
    }

    # Try to get todo count, but don't fail if database is unavailable
    try:
        todo_service = get_todo_service()
        response["todos_count"] = await todo_service.get_todo_count()
    except Exception as e:
        response["todos_count"] = "unavailable"
        response["database_status"] = f"error: {str(e)}"

    return response


@router.get("/health")
async def comprehensive_health_check():
    """Comprehensive health check endpoint with database connectivity."""
    from ...database.connection import db_manager
    
    response = {
        "status": "healthy",
        "service": "todo-backend", 
        "timestamp": datetime.now(UTC).isoformat(),
        "database": "connected"
    }
    
    # Check database connectivity - this is critical for readiness
    try:
        is_db_healthy = await db_manager.health_check(max_retries=1)
        if not is_db_healthy:
            response["status"] = "unhealthy"
            response["database"] = "unavailable"
            raise HTTPException(status_code=503, detail=response)
            
        # If database is healthy, include todo count
        todo_service = get_todo_service()
        response["todos_count"] = await todo_service.get_todo_count()
        
    except HTTPException:
        # Re-raise 503 errors
        raise
    except Exception as e:
        # Any other error also means unhealthy
        logger.error(f"Health check failed: {e}")
        response["status"] = "unhealthy" 
        response["database"] = "error"
        response["error"] = "Database connectivity check failed"
        raise HTTPException(status_code=503, detail=response)
    
    return response


@router.get("/healthz")
async def liveness_check():
    """Lightweight liveness check endpoint - no dependencies."""
    return {"status": "ok"}
