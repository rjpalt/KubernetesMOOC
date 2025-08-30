"""Todo data models. Very helpful, indeed."""

import uuid
from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field


class TodoStatus(str, Enum):
    """Todo status enumeration."""

    NOT_DONE = "not-done"
    DONE = "done"


class TodoCreate(BaseModel):
    """Model for creating a new todo."""

    text: str = Field(..., min_length=1, max_length=140, description="Todo text content")


class TodoUpdate(BaseModel):
    """Model for updating a todo."""

    text: str | None = Field(None, min_length=1, max_length=140, description="Todo text content")
    status: TodoStatus | None = Field(None, description="Todo status")


class Todo(BaseModel):
    """Todo item model."""

    id: str = Field(..., description="Unique todo identifier")
    text: str = Field(..., min_length=1, max_length=140, description="Todo text content")
    status: TodoStatus = Field(default=TodoStatus.NOT_DONE, description="Todo completion status")
    created_at: datetime = Field(default_factory=datetime.now, description="Creation timestamp")
    updated_at: datetime | None = Field(None, description="Last update timestamp")ot

    @classmethod
    def create_new(cls, text: str) -> "Todo":
        """Create a new todo with generated ID and timestamp."""
        return cls(
            id=str(uuid.uuid4()),
            text=text,
            status=TodoStatus.NOT_DONE,
            created_at=datetime.now(),
        )

    def update_text(self, text: str) -> None:
        """Update todo text and timestamp."""
        self.text = text
        self.updated_at = datetime.now()

    def toggle_status(self) -> None:
        """Toggle todo completion status and update timestamp."""
        self.status = TodoStatus.DONE if self.status == TodoStatus.NOT_DONE else TodoStatus.NOT_DONE
        self.updated_at = datetime.now()

    def mark_done(self) -> None:
        """Mark todo as done and update timestamp."""
        self.status = TodoStatus.DONE
        self.updated_at = datetime.now()

    def mark_not_done(self) -> None:
        """Mark todo as not done and update timestamp."""
        self.status = TodoStatus.NOT_DONE
        self.updated_at = datetime.now()
