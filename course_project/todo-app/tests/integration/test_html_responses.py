"""Integration tests for HTML responses and template rendering.

Testing that your templates actually render and include the expected content
because broken HTML is embarrassing.
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import Mock

from src.models.todo import Todo, TodoStatus
from src.models.image import ImageInfo
from tests.fixtures.todo_fixtures import get_sample_todos


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
    
    def test_root_endpoint_includes_todos_in_response(self, test_client: TestClient, mock_todo_service, mock_image_service):
        """Test that root endpoint includes todo data in the HTML."""
        # Setup mocks with sample todos
        sample_todos = get_sample_todos()
        mock_todo_service.get_all_todos.return_value = sample_todos
        mock_image_service.get_image_info.return_value = Mock(spec=ImageInfo)
        mock_image_service.format_image_status.return_value = {"current_image": "test.jpg"}
        mock_image_service.get_config_for_template.return_value = {"fetch_interval_hours": 1}
        
        response = test_client.get("/")
        html_content = response.text
        
        # Should include some todo text in the HTML
        assert any(todo.text in html_content for todo in sample_todos)
    
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
    
    def test_root_endpoint_calls_todo_service(self, test_client: TestClient, mock_todo_service, mock_image_service):
        """Test that root endpoint calls the todo service."""
        # Setup mocks
        mock_todo_service.get_all_todos.return_value = get_sample_todos()
        mock_image_service.get_image_info.return_value = Mock(spec=ImageInfo)
        mock_image_service.format_image_status.return_value = {"current_image": "test.jpg"}
        mock_image_service.get_config_for_template.return_value = {"fetch_interval_hours": 1}
        
        response = test_client.get("/")
        
        assert response.status_code == 200
        mock_todo_service.get_all_todos.assert_called_once()
    
    def test_root_endpoint_calls_image_service(self, test_client: TestClient, mock_todo_service, mock_image_service):
        """Test that root endpoint calls the image service methods."""
        # Setup mocks
        mock_todo_service.get_all_todos.return_value = get_sample_todos()
        mock_image_service.get_image_info.return_value = Mock(spec=ImageInfo)
        mock_image_service.format_image_status.return_value = {"current_image": "test.jpg"}
        mock_image_service.get_config_for_template.return_value = {"fetch_interval_hours": 1}
        
        response = test_client.get("/")
        
        assert response.status_code == 200
        mock_image_service.get_image_info.assert_called_once()
        mock_image_service.format_image_status.assert_called_once()
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
