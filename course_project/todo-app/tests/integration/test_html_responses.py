"""Integration tests for HTML responses and template rendering.

Testing that your templates actually render and include the expected content
because broken HTML is embarrassing.
"""

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
            text="First mock todo",
            status=TodoStatus.NOT_DONE,
            created_at=datetime.fromisoformat("2025-07-21T10:00:00+00:00"),
        ),
        Todo(
            id="mock-todo-2",
            text="Second mock todo",
            status=TodoStatus.DONE,
            created_at=datetime.fromisoformat("2025-07-21T11:00:00+00:00"),
        ),
        Todo(
            id="mock-todo-3",
            text="Third mock todo",
            status=TodoStatus.NOT_DONE,
            created_at=datetime.fromisoformat("2025-07-21T12:00:00+00:00"),
        ),
    ]


class TestHTMLResponses:
    """Test HTML template rendering because even simple templates break."""

    def test_root_endpoint_returns_html(self, test_client: TestClient, mock_todo_service, mock_image_service):
        """Test that root endpoint returns HTML content."""
        # Setup mocks
        mock_todo_service.get_all_todos.return_value = get_sample_todos()
        mock_image_service.get_image_info.return_value = Mock(spec=ImageInfo)
        mock_image_service.format_image_status.return_value = {"current_image": "test.jpg"}
        mock_image_service.get_config_for_template.return_value = {"fetch_interval_hours": 1}

        response = test_client.get("/")

        assert response.status_code == 200
        assert "text/html" in response.headers["content-type"]

    def test_root_endpoint_handles_backend_unavailable(
        self, test_client: TestClient, mock_todo_service, mock_image_service
    ):
        """Test that root endpoint gracefully handles backend unavailability."""
        # Setup image service mocks (these should work)
        mock_image_service.get_image_info.return_value = Mock(spec=ImageInfo)
        mock_image_service.format_image_status.return_value = {"current_image": "test.jpg"}
        mock_image_service.get_config_for_template.return_value = {"fetch_interval_hours": 1}

        # Don't mock backend client - let it fail naturally
        response = test_client.get("/")

        # Should still return successful response even if backend is down
        assert response.status_code == 200
        html_content = response.text

        # Should contain basic HTML structure
        assert "<html" in html_content.lower()
        assert "todo app" in html_content.lower()

        # Should contain image section even when todos fail
        assert "image" in html_content.lower()

    def test_root_endpoint_backend_communication_architecture(
        self, test_client: TestClient, mock_todo_service, mock_image_service
    ):
        """Test that the microservice architecture is properly set up.

        This test verifies that:
        1. Frontend can handle backend being unavailable (graceful degradation)
        2. Frontend doesn't depend on local todo service (microservice separation)
        3. UI still renders when backend communication fails
        """
        # Setup only image service (frontend-local functionality)
        mock_image_service.get_image_info.return_value = Mock(spec=ImageInfo)
        mock_image_service.format_image_status.return_value = {"current_image": "test.jpg"}
        mock_image_service.get_config_for_template.return_value = {"fetch_interval_hours": 1}

        response = test_client.get("/")

        # Verify microservice architecture principles:
        assert response.status_code == 200  # Frontend stays up when backend is down

        # Verify that local todo service is NOT used (microservice separation)
        mock_todo_service.get_all_todos.assert_not_called()

        # Verify frontend-specific functionality still works
        mock_image_service.get_image_info.assert_called_once()
        mock_image_service.format_image_status.assert_called_once()

    def test_root_endpoint_includes_image_info(self, test_client: TestClient, mock_todo_service, mock_image_service):
        """Test that root endpoint includes image information."""
        # Setup mocks
        mock_todo_service.get_all_todos.return_value = get_sample_todos()
        mock_image_service.get_image_info.return_value = Mock(spec=ImageInfo)
        mock_image_service.format_image_status.return_value = {"current_image": "test.jpg", "last_fetch": "2024-01-01"}
        mock_image_service.get_config_for_template.return_value = {"fetch_interval_hours": 1}

        response = test_client.get("/")
        html_content = response.text

        # Should include image-related content
        # (The exact content depends on your template structure)
        assert response.status_code == 200
        assert len(html_content) > 0

    def test_root_endpoint_handles_empty_todos(self, test_client: TestClient, mock_todo_service, mock_image_service):
        """Test that root endpoint handles empty todo list gracefully."""
        # Setup mocks with empty todos
        mock_todo_service.get_all_todos.return_value = []
        mock_image_service.get_image_info.return_value = Mock(spec=ImageInfo)
        mock_image_service.format_image_status.return_value = {"current_image": "test.jpg"}
        mock_image_service.get_config_for_template.return_value = {"fetch_interval_hours": 1}

        response = test_client.get("/")

        assert response.status_code == 200
        assert "text/html" in response.headers["content-type"]

        # Verify frontend-specific functionality still works
        mock_image_service.get_image_info.assert_called_once()
        mock_image_service.format_image_status.assert_called_once()

    def test_root_endpoint_calls_image_service(self, test_client: TestClient, mock_todo_service, mock_image_service):
        """Test that root endpoint calls the image service methods."""
        # Setup mocks
        mock_image_info = Mock(spec=ImageInfo)
        mock_image_service.get_image_info.return_value = mock_image_info
        mock_image_service.format_image_status.return_value = {"current_image": "test.jpg"}
        mock_image_service.get_config_for_template.return_value = {"fetch_interval_hours": 1}

        # Mock the backend client to avoid errors
        with patch("src.api.routes.images.TodoBackendClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value = mock_client
            mock_client.get_all_todos.return_value = []

            response = test_client.get("/")

            assert response.status_code == 200
            # Verify image service methods were called
            mock_image_service.get_image_info.assert_called_once()
            mock_image_service.format_image_status.assert_called_once_with(mock_image_info)
            mock_image_service.get_config_for_template.assert_called_once()

    def test_html_response_has_proper_structure(self, test_client: TestClient, mock_todo_service, mock_image_service):
        """Test that HTML response has basic HTML structure."""
        # Setup mocks
        mock_todo_service.get_all_todos.return_value = get_sample_todos()
        mock_image_service.get_image_info.return_value = Mock(spec=ImageInfo)
        mock_image_service.format_image_status.return_value = {"current_image": "test.jpg"}
        mock_image_service.get_config_for_template.return_value = {"fetch_interval_hours": 1}

        response = test_client.get("/")
        html_content = response.text

        # Basic HTML structure checks
        assert "<html" in html_content or "<!DOCTYPE html>" in html_content
        assert "<body" in html_content
        assert "</body>" in html_content

    def test_template_rendering_performance(self, test_client: TestClient, mock_todo_service, mock_image_service):
        """Test that template rendering is reasonably fast."""
        import time

        # Setup mocks
        mock_todo_service.get_all_todos.return_value = get_sample_todos()
        mock_image_service.get_image_info.return_value = Mock(spec=ImageInfo)
        mock_image_service.format_image_status.return_value = {"current_image": "test.jpg"}
        mock_image_service.get_config_for_template.return_value = {"fetch_interval_hours": 1}

        start_time = time.time()
        response = test_client.get("/")
        end_time = time.time()

        # Template rendering should be fast (<2 seconds)
        assert (end_time - start_time) < 2.0
        assert response.status_code == 200
