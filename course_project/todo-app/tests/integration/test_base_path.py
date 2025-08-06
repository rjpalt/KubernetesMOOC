"""Tests for API base path functionality.

Tests that the base path configuration works correctly in different deployment scenarios:
- Local development: empty base path (default)
- Kubernetes/Gateway API: /project base path
"""

import os
from unittest.mock import AsyncMock, Mock, patch

from fastapi.testclient import TestClient

from src.models.image import ImageInfo
from src.models.todo import Todo, TodoStatus


def get_sample_todos():
    """Return sample Todo objects for testing."""
    from datetime import datetime

    return [
        Todo(
            id="mock-todo-1",
            text="Test todo",
            status=TodoStatus.NOT_DONE,
            created_at=datetime.fromisoformat("2025-07-21T10:00:00+00:00"),
        )
    ]


class TestBasePath:
    """Test base path configuration and template rendering."""

    def test_default_base_path_empty_urls(self, test_client: TestClient, mock_todo_service, mock_image_service):
        """Test that default base_path results in URLs without prefix."""
        # Setup mocks
        mock_todo_service.get_all_todos.return_value = get_sample_todos()

        # Mock image service to return "available" status so image tag appears
        mock_image_info = Mock(spec=ImageInfo)
        mock_image_info.status = "available"
        mock_image_info.model_dump.return_value = {"status": "available"}
        mock_image_service.get_image_info.return_value = mock_image_info
        mock_image_service.format_image_status.return_value = "Status: Available"
        mock_image_service.get_config_for_template.return_value = {"update_interval": 10}

        # Mock the backend client
        with patch("src.api.routes.images.TodoBackendClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value = mock_client
            mock_client.get_all_todos.return_value = get_sample_todos()

            response = test_client.get("/")

            assert response.status_code == 200
            html_content = response.text

            # Default base_path should be empty, so URLs should start with /
            assert 'hx-post="/todos"' in html_content
            assert 'src="/image"' in html_content  # This is in the <img> tag
            assert "/fetch-image" in html_content  # This is in JavaScript

    def test_configured_base_path_with_prefix_subprocess(self):
        """Test that configured base_path adds prefix to URLs using subprocess."""
        import subprocess
        import sys

        # Create a script to test with environment variable set
        test_script = """
from src.main import create_app
from fastapi.testclient import TestClient
from unittest.mock import Mock, AsyncMock, patch

app = create_app()
client = TestClient(app)

# Mock the image service dependency
from src.api.routes.images import get_image_service
from src.services.image_service import ImageService
from src.models.image import ImageInfo

def mock_image_service():
    mock_service = Mock(spec=ImageService)
    mock_image_info = Mock(spec=ImageInfo)
    mock_image_info.status = "available"
    mock_image_info.model_dump.return_value = {"status": "available"}
    mock_service.get_image_info.return_value = mock_image_info
    mock_service.format_image_status.return_value = "Status: Available"
    mock_service.get_config_for_template.return_value = {"update_interval": 10}
    return mock_service

app.dependency_overrides[get_image_service] = mock_image_service

# Mock the backend client
with patch("src.api.routes.images.TodoBackendClient") as mock_client_class:
    mock_client = AsyncMock()
    mock_client_class.return_value = mock_client
    mock_client.get_all_todos.return_value = []

    response = client.get("/")

    if response.status_code != 200:
        print(f"FAIL: Status code {response.status_code}")
        exit(1)

    html_content = response.text

    # Check for /project prefix in URLs
    checks = [
        ('hx-post="/project/todos"', "HTMX todos form"),
        ('src="/project/image"', "Image source"),
        ('/project/fetch-image', "Fetch image JavaScript")
    ]

    for check, description in checks:
        if check not in html_content:
            print(f"FAIL: {description} - expected {check} not found")
            exit(1)
        else:
            print(f"PASS: {description}")

print("All base path prefix checks passed!")
"""

        # Run the test script with API_BASE_PATH="/project"
        result = subprocess.run(
            [sys.executable, "-c", test_script],
            env={**os.environ, "API_BASE_PATH": "/project"},
            cwd="/Users/rasmuspaltschik/Projects/HY/KubernetesMOOC/course_project/todo-app",
            capture_output=True,
            text=True,
        )

        # Check the result
        assert result.returncode == 0, f"Subprocess failed: {result.stdout}\n{result.stderr}"
        assert "All base path prefix checks passed!" in result.stdout

    def test_settings_api_base_path_default(self):
        """Test that settings default api_base_path is empty."""
        from src.config.settings import Settings

        settings = Settings()
        assert settings.api_base_path == ""

    @patch.dict(os.environ, {"API_BASE_PATH": "/test-prefix"})
    def test_settings_api_base_path_from_env(self):
        """Test that settings picks up API_BASE_PATH from environment."""
        from src.config.settings import Settings

        settings = Settings()
        assert settings.api_base_path == "/test-prefix"

    def test_base_path_available_in_routes(self, test_client: TestClient, mock_todo_service, mock_image_service):
        """Test that routes have access to base_path in context via settings."""
        from src.config.settings import settings

        # Verify settings is accessible and has correct default
        assert hasattr(settings, "api_base_path")
        assert settings.api_base_path == ""  # Default value
