"""Unit tests for todo service.

Testing the todo service because in-memory storage 
can still be screwed up somehow.
"""

import pytest
from datetime import datetime

from src.services.todo_service import TodoService
from src.models.todo import Todo, TodoStatus
from tests.fixtures.todo_fixtures import get_sample_todos


class TestTodoService:
    """Test the TodoService because even simple things can break."""
    
    def test_todo_service_initialization(self):
        """Test that service initializes with sample todos."""
        service = TodoService()
        todos = service.get_all_todos()
        
        # Should have the hardcoded sample todos
        assert len(todos) == 5
        assert all(isinstance(todo, Todo) for todo in todos)
    
    def test_get_all_todos_returns_list(self):
        """Test that get_all_todos returns a list."""
        service = TodoService()
        todos = service.get_all_todos()
        
        assert isinstance(todos, list)
    
    def test_get_all_todos_returns_todo_objects(self):
        """Test that all returned items are Todo objects."""
        service = TodoService()
        todos = service.get_all_todos()
        
        for todo in todos:
            assert isinstance(todo, Todo)
            assert hasattr(todo, 'id')
            assert hasattr(todo, 'text')
            assert hasattr(todo, 'status')
            assert hasattr(todo, 'created_at')
    
    def test_sample_todos_have_valid_status(self):
        """Test that sample todos have valid status values."""
        service = TodoService()
        todos = service.get_all_todos()
        
        valid_statuses = [TodoStatus.DONE, TodoStatus.NOT_DONE]
        for todo in todos:
            assert todo.status in valid_statuses
    
    def test_sample_todos_have_text_within_limits(self):
        """Test that sample todos respect character limits."""
        service = TodoService()
        todos = service.get_all_todos()
        
        for todo in todos:
            assert len(todo.text) <= 140
            assert len(todo.text) > 0
    
    def test_sample_todos_have_unique_ids(self):
        """Test that sample todos have unique IDs."""
        service = TodoService()
        todos = service.get_all_todos()
        
        ids = [todo.id for todo in todos]
        assert len(ids) == len(set(ids))  # All IDs should be unique
    
    def test_sample_todos_have_valid_datetime(self):
        """Test that sample todos have valid datetime objects."""
        service = TodoService()
        todos = service.get_all_todos()
        
        for todo in todos:
            assert isinstance(todo.created_at, datetime)
    
    def test_service_contains_expected_sample_text(self):
        """Test that service contains the expected hardcoded sample todos."""
        service = TodoService()
        todos = service.get_all_todos()
        todo_texts = [todo.text for todo in todos]
        
        # Check for some expected sample texts from the service
        assert any("Kubernetes" in text for text in todo_texts)
        assert any("FastAPI" in text for text in todo_texts)
    
    def test_service_has_both_done_and_not_done_todos(self):
        """Test that service has examples of both status types."""
        service = TodoService()
        todos = service.get_all_todos()
        
        statuses = [todo.status for todo in todos]
        assert TodoStatus.DONE in statuses
        assert TodoStatus.NOT_DONE in statuses
    
    def test_multiple_service_instances_independent(self):
        """Test that multiple service instances don't share state."""
        service1 = TodoService()
        service2 = TodoService()
        
        todos1 = service1.get_all_todos()
        todos2 = service2.get_all_todos()
        
        # Should have same number and content but be different objects
        assert len(todos1) == len(todos2)
        assert todos1 is not todos2  # Different list objects
        
        # But the content should be equivalent
        for todo1, todo2 in zip(todos1, todos2):
            assert todo1.text == todo2.text
            assert todo1.status == todo2.status
