"""Unit tests for TodoService - Backend business logic testing.

These tests focus on the core business logic of the backend service,
testing the TodoService in isolation with a real database.

This demonstrates microservice testing principles:
- Test business logic with real database (container-based)
- Fast, focused tests for core functionality
- Database isolation between tests
- Async testing patterns for modern applications
"""

from datetime import datetime

from src.models.todo import Todo, TodoCreate, TodoStatus
from src.services.todo_service import TodoService


class TestTodoService:
    """Test the backend TodoService business logic with async database."""

    async def test_service_initializes_empty(self, test_db_manager):
        """Test that service starts with empty database.

        This test verifies the backend initializes correctly with a clean database,
        which is important for microservice health checks and container restarts.
        """
        service = TodoService()
        todos = await service.get_all_todos()

        # Should start empty (sample data is only added via initialize_with_sample_data)
        assert len(todos) == 0

    async def test_initialize_with_sample_data(self, test_db_manager):
        """Test that service can initialize with sample data."""
        service = TodoService()

        # Should be empty initially
        count = await service.get_todo_count()
        assert count == 0

        # Initialize with sample data
        await service.initialize_with_sample_data()

        # Should now have sample todos
        todos = await service.get_all_todos()
        assert len(todos) == 3
        assert all(isinstance(todo, Todo) for todo in todos)

    async def test_get_all_todos_returns_list(self, test_db_manager):
        """Test that get_all_todos returns a list.

        This ensures the async database operations return proper types.
        """
        service = TodoService()
        todos = await service.get_all_todos()

        assert isinstance(todos, list)

    async def test_create_todo_adds_new_todo(self, test_db_manager):
        """Test creating a new todo through the service.

        This tests the core CRUD operation that the backend API exposes.
        """
        service = TodoService()
        initial_count = await service.get_todo_count()

        # Create new todo
        todo_data = TodoCreate(text="New backend todo")
        new_todo = await service.create_todo(todo_data)

        # Verify todo was created correctly
        assert isinstance(new_todo, Todo)
        assert new_todo.text == "New backend todo"
        assert new_todo.status == TodoStatus.NOT_DONE
        assert new_todo.id is not None
        assert isinstance(new_todo.created_at, datetime)

        # Verify it was added to the service
        todos = await service.get_all_todos()
        assert len(todos) == initial_count + 1

        # Verify it's actually in the database
        found_todo = await service.get_todo_by_id(new_todo.id)
        assert found_todo is not None
        assert found_todo.text == "New backend todo"

    async def test_get_todo_by_id_finds_existing_todo(self, test_db_manager):
        """Test retrieving a specific todo by ID."""
        service = TodoService()

        # Create a todo first
        todo_data = TodoCreate(text="Findable todo")
        created_todo = await service.create_todo(todo_data)

        # Find it by ID
        found_todo = await service.get_todo_by_id(created_todo.id)

        assert found_todo is not None
        assert found_todo.id == created_todo.id
        assert found_todo.text == "Findable todo"

    async def test_get_todo_by_id_returns_none_for_nonexistent(self, test_db_manager):
        """Test that looking for non-existent todo returns None."""
        service = TodoService()

        found_todo = await service.get_todo_by_id("nonexistent-id")

        assert found_todo is None

    async def test_update_todo_text(self, test_db_manager):
        """Test updating todo text."""
        service = TodoService()

        # Create and then update
        todo_data = TodoCreate(text="Original text")
        created_todo = await service.create_todo(todo_data)

        updated_todo = await service.update_todo(created_todo.id, text="Updated text")

        assert updated_todo is not None
        assert updated_todo.text == "Updated text"
        assert updated_todo.id == created_todo.id  # Same todo

    async def test_update_todo_status(self, test_db_manager):
        """Test updating todo status."""
        service = TodoService()

        # Create todo (starts as NOT_DONE)
        todo_data = TodoCreate(text="Status test todo")
        created_todo = await service.create_todo(todo_data)
        assert created_todo.status == TodoStatus.NOT_DONE

        # Mark as done
        updated_todo = await service.update_todo(created_todo.id, status=TodoStatus.DONE)

        assert updated_todo is not None
        assert updated_todo.status == TodoStatus.DONE
        assert updated_todo.id == created_todo.id

    async def test_update_nonexistent_todo_returns_none(self, test_db_manager):
        """Test that updating non-existent todo returns None."""
        service = TodoService()

        result = await service.update_todo("nonexistent-id", text="New text")

        assert result is None

    async def test_delete_todo_removes_from_service(self, test_db_manager):
        """Test deleting a todo removes it from the service."""
        service = TodoService()

        # Create todo to delete
        todo_data = TodoCreate(text="To be deleted")
        created_todo = await service.create_todo(todo_data)
        initial_count = await service.get_todo_count()

        # Delete it
        success = await service.delete_todo(created_todo.id)

        assert success is True
        assert await service.get_todo_count() == initial_count - 1
        assert await service.get_todo_by_id(created_todo.id) is None

    async def test_delete_nonexistent_todo_returns_false(self, test_db_manager):
        """Test that deleting non-existent todo returns False."""
        service = TodoService()

        success = await service.delete_todo("nonexistent-id")

        assert success is False

    async def test_get_todo_count(self, test_db_manager):
        """Test the todo count method."""
        service = TodoService()
        initial_count = await service.get_todo_count()

        # Add a todo
        todo_data = TodoCreate(text="Count test")
        await service.create_todo(todo_data)

        assert await service.get_todo_count() == initial_count + 1
