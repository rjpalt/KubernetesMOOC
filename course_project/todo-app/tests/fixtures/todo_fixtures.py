"""Frontend test fixtures for mocking backend responses.

After microservice separation:
- Todo business logic moved to backend
- Frontend tests mock backend HTTP responses
- These fixtures provide consistent mock data that matches backend format

This ensures frontend tests use the same data format the backend actually returns.
"""

from datetime import datetime
from typing import Dict, List


def get_mock_backend_todo_response() -> Dict:
    """Get a single todo in the format the backend returns.

    Critical: This must match the exact format todo-backend returns!
    """
    return {
        "id": "mock-backend-todo-1",
        "text": "Mock todo from backend",
        "status": "not-done",  # Note: hyphen format from backend!
        "created_at": "2025-07-21T10:00:00Z",
    }


def get_mock_backend_todos_list() -> List[Dict]:
    """Get multiple todos in backend response format."""
    return [
        {"id": "mock-todo-1", "text": "First mock todo", "status": "not-done", "created_at": "2025-07-21T10:00:00Z"},
        {"id": "mock-todo-2", "text": "Second mock todo", "status": "done", "created_at": "2025-07-21T11:00:00Z"},
        {"id": "mock-todo-3", "text": "Third mock todo", "status": "not-done", "created_at": "2025-07-21T12:00:00Z"},
    ]


def get_sample_todos() -> List[Dict]:
    """Alias for get_mock_backend_todos_list for backward compatibility."""
    return get_mock_backend_todos_list()


def get_mock_backend_created_todo_response() -> Dict:
    """Get response format for newly created todo from backend."""
    return {
        "id": "newly-created-mock-id",
        "text": "Newly created mock todo",
        "status": "not-done",
        "created_at": "2025-07-21T13:00:00Z",
    }


def get_mock_backend_error_response() -> Dict:
    """Get error response format from backend."""
    return {"detail": "Mock backend error for testing"}


# TODO: Add Image fixtures here when Image functionality is implemented
# Example:
# def get_mock_image_info() -> Dict:
#     """Mock image information for frontend testing."""
#     return {
#         "filename": "mock-image.jpg",
#         "last_updated": "2025-07-21T10:00:00Z",
#         "size": 1024
#     }
