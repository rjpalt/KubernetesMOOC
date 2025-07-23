"""Health check endpoints."""

import logging

from fastapi import APIRouter

from ...api.dependencies import get_todo_service

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/health")
async def health_check():
    """Health check endpoint."""
    todo_service = get_todo_service()
    return {
        "status": "healthy",
        "service": "todo-backend",
        "todos_count": todo_service.get_todo_count(),
    }
