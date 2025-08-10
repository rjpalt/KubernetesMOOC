"""Health check endpoints."""

import logging

from fastapi import APIRouter

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
