"""Backend test configuration and shared fixtures.

This conftest.py provides:
- FastAPI test client for backend API testing
- Shared fixtures for backend testing
- Test configuration for the modular backend architecture
"""

import pytest
from fastapi.testclient import TestClient

from src.main import create_app


@pytest.fixture
def test_client():
    """Create a FastAPI test client for backend API testing.
    
    This fixture provides a test client that:
    - Uses the backend's FastAPI app
    - Doesn't require running the actual server
    - Handles async endpoints automatically
    - Provides HTTP interface testing
    """
    app = create_app()
    return TestClient(app)


@pytest.fixture
def sample_todo_data():
    """Sample todo data matching backend's Todo model format.
    
    This ensures test data matches what the backend actually returns,
    which is crucial for microservice contract consistency.
    """
    return {
        "id": "550e8400-e29b-41d4-a716-446655440000",
        "text": "Learn Kubernetes testing patterns",
        "status": "not-done",  # Note: hyphen, not underscore!
        "created_at": "2025-07-21T10:00:00Z"
    }


@pytest.fixture
def sample_todos_list(sample_todo_data):
    """Sample list of todos for testing list endpoints."""
    return [
        sample_todo_data,
        {
            "id": "550e8400-e29b-41d4-a716-446655440001", 
            "text": "Understand microservice testing",
            "status": "done",
            "created_at": "2025-07-21T09:00:00Z"
        }
    ]
