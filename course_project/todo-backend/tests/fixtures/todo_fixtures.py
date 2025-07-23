"""Todo fixtures for backend testing.

These fixtures provide test data that matches the backend's
Todo model schema, ensuring consistency between tests and
the actual API responses.
"""

from datetime import datetime
from typing import Dict, List

import pytest
from src.models.todo import Todo, TodoStatus


@pytest.fixture
def valid_todo_dict():
    """Valid todo data as dictionary (for API testing)."""
    return {"text": "Test todo from backend fixture", "status": "not_done"}


@pytest.fixture
def valid_todo_object():
    """Valid Todo object (for service testing)."""
    return Todo(
        id="test-id-123",
        text="Test todo object",
        status=TodoStatus.NOT_DONE,
        created_at=datetime(2025, 7, 21, 10, 0, 0),
    )


@pytest.fixture
def multiple_todos():
    """Multiple Todo objects for list testing."""
    return [
        Todo(
            id="todo-1",
            text="First backend todo",
            status=TodoStatus.NOT_DONE,
            created_at=datetime(2025, 7, 21, 10, 0, 0),
        ),
        Todo(
            id="todo-2", text="Second backend todo", status=TodoStatus.DONE, created_at=datetime(2025, 7, 21, 11, 0, 0)
        ),
    ]


@pytest.fixture
def invalid_todo_data():
    """Invalid todo data for validation testing."""
    return [
        {"text": ""},  # Empty text
        {"text": "a" * 141},  # Too long
        {"text": "Valid text", "status": "invalid_status"},  # Invalid status
        {},  # Missing required fields
    ]


@pytest.fixture
def todo_update_data():
    """Data for testing todo updates."""
    return {"text": "Updated todo text", "status": "done"}
