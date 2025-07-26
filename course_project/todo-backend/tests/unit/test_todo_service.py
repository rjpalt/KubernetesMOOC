"""Unit tests for TodoService - Backend business logic testing.

These tests focus on the core business logic of the backend service,
testing the TodoService in isolation without HTTP concerns.

This demonstrates microservice testing principle:
- Test business logic separately from API layer
- Fast, focused tests for core functionality
- No external dependencies (no HTTP, no database)
"""

from datetime import datetime

from src.models.todo import Todo, TodoCreate, TodoStatus
from src.services.todo_service import TodoService


class TestTodoService:
    """Test the backend TodoService business logic."""

    def test_service_initializes_with_sample_todos(self):
        """Test that service starts with predefined sample todos.

        This test verifies the backend initializes correctly,
        which is important for microservice health checks.
        """
        service = TodoService()
        todos = service.get_all_todos()

        # Should have the hardcoded sample todos from __init__
        assert len(todos) == 3
        assert all(isinstance(todo, Todo) for todo in todos)

    def test_get_all_todos_returns_copy(self):
        """Test that get_all_todos returns a copy, not direct reference.

        This ensures service encapsulation - external code can't
        accidentally modify the internal todo list.
        """
        service = TodoService()
        todos1 = service.get_all_todos()
        todos2 = service.get_all_todos()

        # Should be equal content but different objects
        assert todos1 == todos2
        assert todos1 is not todos2

    def test_create_todo_adds_new_todo(self):
        """Test creating a new todo through the service.

        This tests the core CRUD operation that the backend API exposes.
        """
        service = TodoService()
        initial_count = len(service.get_all_todos())

        # Create new todo
        todo_data = TodoCreate(text="New backend todo")
        new_todo = service.create_todo(todo_data)

        # Verify todo was created correctly
        assert isinstance(new_todo, Todo)
        assert new_todo.text == "New backend todo"
        assert new_todo.status == TodoStatus.NOT_DONE
        assert new_todo.id is not None
        assert isinstance(new_todo.created_at, datetime)

        # Verify it was added to the service
        todos = service.get_all_todos()
        assert len(todos) == initial_count + 1
        assert new_todo in todos

    def test_get_todo_by_id_finds_existing_todo(self):
        """Test retrieving a specific todo by ID."""
        service = TodoService()

        # Create a todo first
        todo_data = TodoCreate(text="Findable todo")
        created_todo = service.create_todo(todo_data)

        # Find it by ID
        found_todo = service.get_todo_by_id(created_todo.id)

        assert found_todo is not None
        assert found_todo.id == created_todo.id
        assert found_todo.text == "Findable todo"

    def test_get_todo_by_id_returns_none_for_nonexistent(self):
        """Test that looking for non-existent todo returns None."""
        service = TodoService()

        found_todo = service.get_todo_by_id("nonexistent-id")

        assert found_todo is None

    def test_update_todo_text(self):
        """Test updating todo text."""
        service = TodoService()

        # Create and then update
        todo_data = TodoCreate(text="Original text")
        created_todo = service.create_todo(todo_data)

        updated_todo = service.update_todo(created_todo.id, text="Updated text")

        assert updated_todo is not None
        assert updated_todo.text == "Updated text"
        assert updated_todo.id == created_todo.id  # Same todo

    def test_update_todo_status(self):
        """Test updating todo status."""
        service = TodoService()

        # Create todo (starts as NOT_DONE)
        todo_data = TodoCreate(text="Status test todo")
        created_todo = service.create_todo(todo_data)
        assert created_todo.status == TodoStatus.NOT_DONE

        # Mark as done
        updated_todo = service.update_todo(created_todo.id, status=TodoStatus.DONE)

        assert updated_todo is not None
        assert updated_todo.status == TodoStatus.DONE
        assert updated_todo.id == created_todo.id

    def test_update_nonexistent_todo_returns_none(self):
        """Test that updating non-existent todo returns None."""
        service = TodoService()

        result = service.update_todo("nonexistent-id", text="New text")

        assert result is None

    def test_delete_todo_removes_from_service(self):
        """Test deleting a todo removes it from the service."""
        service = TodoService()

        # Create todo to delete
        todo_data = TodoCreate(text="To be deleted")
        created_todo = service.create_todo(todo_data)
        initial_count = len(service.get_all_todos())

        # Delete it
        success = service.delete_todo(created_todo.id)

        assert success is True
        assert len(service.get_all_todos()) == initial_count - 1
        assert service.get_todo_by_id(created_todo.id) is None

    def test_delete_nonexistent_todo_returns_false(self):
        """Test that deleting non-existent todo returns False."""
        service = TodoService()

        success = service.delete_todo("nonexistent-id")

        assert success is False

    def test_get_todo_count(self):
        """Test the todo count method."""
        service = TodoService()
        initial_count = service.get_todo_count()

        # Add a todo
        todo_data = TodoCreate(text="Count test")
        service.create_todo(todo_data)

        assert service.get_todo_count() == initial_count + 1
