"""Unit tests for Todo models - Backend data validation testing.

These tests focus on Pydantic model validation for the backend's
Todo data structures. This ensures the backend properly validates
data it receives and returns.

Moved from frontend because: Data models belong to the service that owns them.
In microservices, each service owns its data models and should test them.
"""

import pytest
from datetime import datetime
from pydantic import ValidationError
from uuid import UUID

from src.models.todo import Todo, TodoCreate, TodoUpdate, TodoStatus


class TestTodoStatus:
    """Test TodoStatus enum - Backend data validation."""
    
    def test_todo_status_values(self):
        """Test that enum values match backend's expected format."""
        # Critical: This ensures frontend and backend agree on status values
        assert TodoStatus.NOT_DONE == "not-done"  # Note: hyphen!
        assert TodoStatus.DONE == "done"
    
    def test_todo_status_string_representation(self):
        """Test string representation matches API responses."""
        assert TodoStatus.NOT_DONE.value == "not-done"
        assert TodoStatus.DONE.value == "done"
        
    def test_todo_status_serialization(self):
        """Test that status serializes correctly for API responses."""
        # This is what gets sent to frontend (the .value, not str())
        assert TodoStatus.NOT_DONE.value == "not-done"
        assert TodoStatus.DONE.value == "done"


class TestTodoCreate:
    """Test TodoCreate model - Input validation for API."""
    
    def test_valid_todo_create(self):
        """Test creating TodoCreate with valid data."""
        todo_data = TodoCreate(text="Valid todo text")
        
        assert todo_data.text == "Valid todo text"
        
    def test_todo_create_text_validation(self):
        """Test text field validation constraints."""
        # Text cannot be empty
        with pytest.raises(ValidationError) as exc_info:
            TodoCreate(text="")
        assert "at least 1 character" in str(exc_info.value)
        
        # Text cannot be too long (140 char limit)
        with pytest.raises(ValidationError) as exc_info:
            TodoCreate(text="a" * 141)
        assert "at most 140 characters" in str(exc_info.value)
        
    def test_todo_create_missing_text(self):
        """Test that text field is required."""
        with pytest.raises(ValidationError) as exc_info:
            TodoCreate()
        assert "Field required" in str(exc_info.value)
        
    def test_todo_create_boundary_values(self):
        """Test boundary conditions for text length."""
        # Exactly at limit should work
        TodoCreate(text="a" * 140)  # Should not raise
        
        # Minimum length should work
        TodoCreate(text="a")  # Should not raise


class TestTodoUpdate:
    """Test TodoUpdate model - Update validation for API."""
    
    def test_valid_todo_update_text_only(self):
        """Test updating only text."""
        update_data = TodoUpdate(text="Updated text")
        
        assert update_data.text == "Updated text"
        assert update_data.status is None
        
    def test_valid_todo_update_status_only(self):
        """Test updating only status."""
        update_data = TodoUpdate(status=TodoStatus.DONE)
        
        assert update_data.status == TodoStatus.DONE
        assert update_data.text is None
        
    def test_valid_todo_update_both_fields(self):
        """Test updating both text and status."""
        update_data = TodoUpdate(
            text="Updated text",
            status=TodoStatus.DONE
        )
        
        assert update_data.text == "Updated text"
        assert update_data.status == TodoStatus.DONE
        
    def test_todo_update_empty_is_valid(self):
        """Test that TodoUpdate with no fields is valid (partial update)."""
        update_data = TodoUpdate()
        
        assert update_data.text is None
        assert update_data.status is None
        
    def test_todo_update_text_validation(self):
        """Test text validation in updates."""
        # Empty text should fail
        with pytest.raises(ValidationError):
            TodoUpdate(text="")
            
        # Too long text should fail
        with pytest.raises(ValidationError):
            TodoUpdate(text="a" * 141)


class TestTodo:
    """Test Todo model - Complete Todo object validation."""
    
    def test_todo_creation_with_all_fields(self):
        """Test creating Todo with all required fields."""
        todo = Todo(
            id="test-uuid-123",
            text="Test todo text",
            status=TodoStatus.NOT_DONE,
            created_at=datetime(2025, 7, 21, 10, 0, 0)
        )
        
        assert todo.id == "test-uuid-123"
        assert todo.text == "Test todo text"
        assert todo.status == TodoStatus.NOT_DONE
        assert todo.created_at == datetime(2025, 7, 21, 10, 0, 0)
    
    def test_todo_default_status(self):
        """Test that default status is NOT_DONE."""
        todo = Todo(
            id="test-id",
            text="Test todo",
            created_at=datetime.now()
        )
        
        assert todo.status == TodoStatus.NOT_DONE
    
    def test_todo_serialization_for_api(self):
        """Test that Todo serializes correctly for API responses."""
        todo = Todo(
            id="test-id",
            text="Test todo",
            status=TodoStatus.NOT_DONE,
            created_at=datetime(2025, 7, 21, 10, 0, 0)
        )
        
        # This is what gets sent to frontend
        todo_dict = todo.model_dump()
        
        assert todo_dict["id"] == "test-id"
        assert todo_dict["text"] == "Test todo"
        assert todo_dict["status"] == "not-done"  # Critical: hyphen format
        assert "created_at" in todo_dict
        
    def test_todo_create_new_class_method(self):
        """Test the create_new class method from backend."""
        # This tests the backend's Todo.create_new() method
        todo = Todo.create_new("New todo text")
        
        assert todo.text == "New todo text"
        assert todo.status == TodoStatus.NOT_DONE
        assert todo.id is not None  # Should have generated UUID
        assert isinstance(todo.created_at, datetime)
        
        # ID should be a valid UUID format
        UUID(todo.id)  # This will raise if not valid UUID
        
    def test_todo_mark_done_method(self):
        """Test the mark_done method from backend."""
        todo = Todo.create_new("Test todo")
        assert todo.status == TodoStatus.NOT_DONE
        
        todo.mark_done()
        assert todo.status == TodoStatus.DONE
        
    def test_todo_mark_not_done_method(self):
        """Test the mark_not_done method from backend."""
        todo = Todo.create_new("Test todo")
        todo.mark_done()  # First mark as done
        assert todo.status == TodoStatus.DONE
        
        todo.mark_not_done()
        assert todo.status == TodoStatus.NOT_DONE
        
    def test_todo_update_text_method(self):
        """Test the update_text method from backend."""
        todo = Todo.create_new("Original text")
        
        todo.update_text("Updated text")
        assert todo.text == "Updated text"
        
    def test_todo_text_validation_in_creation(self):
        """Test text validation during Todo creation."""
        # Empty text should fail
        with pytest.raises(ValidationError):
            Todo(
                id="test-id",
                text="",
                created_at=datetime.now()
            )
            
        # Too long text should fail  
        with pytest.raises(ValidationError):
            Todo(
                id="test-id",
                text="a" * 141,
                created_at=datetime.now()
            )
