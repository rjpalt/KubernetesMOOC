"""Todo test fixtures and sample data.

Sample data for testing todo functionality because you'll probably 
create garbage data if left to your own devices.
"""

import uuid
from datetime import datetime
from typing import List

from src.models.todo import Todo, TodoStatus


def get_sample_todos() -> List[Todo]:
    """Get sample todos for testing."""
    return [
        Todo(
            id="test-id-1",
            text="Test todo that's not done",
            status=TodoStatus.NOT_DONE,
            created_at=datetime(2024, 1, 1, 12, 0, 0)
        ),
        Todo(
            id="test-id-2", 
            text="Test todo that's done",
            status=TodoStatus.DONE,
            created_at=datetime(2024, 1, 1, 13, 0, 0)
        ),
        Todo(
            id="test-id-3",
            text="Another test todo",
            status=TodoStatus.NOT_DONE,
            created_at=datetime(2024, 1, 1, 14, 0, 0)
        )
    ]


def get_sample_todo() -> Todo:
    """Get a single sample todo for testing."""
    return Todo(
        id="single-test-id",
        text="Single test todo",
        status=TodoStatus.NOT_DONE,
        created_at=datetime(2024, 1, 1, 12, 0, 0)
    )


def get_long_text_todo() -> Todo:
    """Get a todo with text at the character limit for boundary testing."""
    return Todo(
        id="long-text-id",
        text="x" * 140,  # Exactly at the 140 character limit
        status=TodoStatus.NOT_DONE,
        created_at=datetime(2024, 1, 1, 12, 0, 0)
    )


def get_invalid_todo_data() -> dict:
    """Get invalid todo data for testing validation."""
    return {
        "id": "invalid-test-id",
        "text": "x" * 141,  # Over the 140 character limit
        "status": "invalid-status",
        "created_at": "not-a-datetime"
    }


def create_todo_with_id(todo_id: str) -> Todo:
    """Create a todo with a specific ID for testing."""
    return Todo(
        id=todo_id,
        text=f"Test todo with ID {todo_id}",
        status=TodoStatus.NOT_DONE,
        created_at=datetime(2024, 1, 1, 12, 0, 0)
    )
