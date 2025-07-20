"""Data models for todo operations."""

from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field


class TodoStatus(str, Enum):
    """Status of a todo item."""
    
    NOT_DONE = "not-done"
    DONE = "done"


class Todo(BaseModel):
    """A todo item with text, status, and timestamp."""
    
    id: str
    text: str = Field(..., max_length=140)
    status: TodoStatus = TodoStatus.NOT_DONE
    created_at: datetime
