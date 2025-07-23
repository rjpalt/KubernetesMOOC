"""Global test configuration and fixtures.

Because apparently you need someone to set up proper testing infrastructure.
"""

from unittest.mock import Mock

import pytest
from fastapi.testclient import TestClient
from src.api import dependencies
from src.core.cache import ImageCacheManager
from src.main import create_app
from src.services.image_service import ImageService
from src.services.todo_backend_client import TodoBackendClient
from src.services.todo_service import TodoService


@pytest.fixture
def mock_todo_service():
    """Mock todo service for testing without side effects."""
    return Mock(spec=TodoService)


@pytest.fixture
def mock_image_service():
    """Mock image service for testing without HTTP calls."""
    return Mock(spec=ImageService)


@pytest.fixture
def mock_image_cache_manager():
    """Mock image cache manager for testing without file I/O."""
    return Mock(spec=ImageCacheManager)


@pytest.fixture
def test_client(mock_todo_service, mock_image_service, mock_image_cache_manager):
    """Test client with mocked dependencies.

    This overrides the global dependencies with mocks so we can test
    without hitting real services or making HTTP calls.
    """

    # Override dependencies with mocks
    app = create_app()

    # Import the actual dependency functions from the routes modules
    from src.api.routes.images import get_image_service, get_templates, get_todo_backend_client

    def override_get_todo_service():
        return mock_todo_service

    def override_get_image_service():
        return mock_image_service

    def override_get_todo_backend_client():
        # For the backend client, we can return a mock
        return Mock(spec=TodoBackendClient)

    def override_get_templates():
        # For templates, we can use the real one since it's just Jinja2
        from src.api import dependencies

        return dependencies.get_templates_instance()

    # Apply dependency overrides
    app.dependency_overrides[get_image_service] = override_get_image_service
    app.dependency_overrides[get_templates] = override_get_templates
    app.dependency_overrides[get_todo_backend_client] = override_get_todo_backend_client

    with TestClient(app) as client:
        yield client

    # Clean up overrides
    app.dependency_overrides.clear()


@pytest.fixture
def real_todo_service():
    """Real todo service for integration tests."""
    return TodoService()


@pytest.fixture
def sample_todos():
    """Sample todo data for testing."""
    from tests.fixtures.todo_fixtures import get_sample_todos

    return get_sample_todos()
