"""Integration tests for image endpoints and caching behavior."""

from pathlib import Path
from unittest.mock import Mock, patch

import pytest
from fastapi.testclient import TestClient
from src.models.image import ImageInfo, ImageMetadata


class TestImageEndpoints:
    """Test image-related endpoints and caching behavior."""

    def test_image_endpoint_returns_cache_headers(self, test_client: TestClient, mock_image_service):
        """Test that /image endpoint returns proper cache-control headers."""
        # Setup: Mock image service to return an existing image
        import os
        import tempfile
        from pathlib import Path

        # Create a real temporary file for FileResponse to serve
        with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as temp_file:
            temp_file.write(b"fake_image_data")
            temp_file.flush()

            # Update the mock to return the real temp file path
            mock_image_service.get_image_path.return_value = Path(temp_file.name)

            response = test_client.get("/image")

            # Verify cache headers are present
            assert response.status_code == 200
            assert response.headers.get("Cache-Control") == "no-cache, no-store, must-revalidate"
            assert response.headers.get("Pragma") == "no-cache"
            assert response.headers.get("Expires") == "0"

            # Clean up
            os.unlink(temp_file.name)

    def test_image_endpoint_404_when_no_image(self, test_client: TestClient, mock_image_service):
        """Test that /image endpoint returns 404 when no image exists."""
        # Setup: Mock image service to return non-existing image
        mock_image_path = Mock(spec=Path)
        mock_image_path.exists.return_value = False
        mock_image_service.get_image_path.return_value = mock_image_path

        response = test_client.get("/image")

        assert response.status_code == 404
        assert "No image available" in response.json()["detail"]

    def test_image_info_endpoint(self, test_client: TestClient, mock_image_service):
        """Test that /image/info endpoint returns image information."""
        # Setup: Mock image service to return image info
        mock_image_info = ImageInfo(
            status="available",
            file_size=12345,
            modified_time="2025-07-21T10:00:00Z",
            metadata=ImageMetadata(
                timestamp="2025-07-21T10:00:00Z",
                size_bytes=12345,
                url="https://picsum.photos/400/600",
                status="success",
            ),
        )
        mock_image_service.get_image_info.return_value = mock_image_info

        response = test_client.get("/image/info")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "available"
        assert data["file_size"] == 12345

    def test_fetch_image_endpoint(self, test_client: TestClient, mock_image_service):
        """Test that POST /fetch-image endpoint works."""
        from src.models.image import FetchResult

        # Setup: Mock image service fetch result
        mock_fetch_result = FetchResult(
            status="success", timestamp="2025-07-21T10:00:00Z", size_bytes=12345, url="https://picsum.photos/400/600"
        )
        mock_image_service.fetch_new_image.return_value = mock_fetch_result

        response = test_client.post("/fetch-image")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"

        # Verify the service method was called
        mock_image_service.fetch_new_image.assert_called_once_with(force=False)

    def test_fetch_image_endpoint_with_force(self, test_client: TestClient, mock_image_service):
        """Test that POST /fetch-image endpoint works with force parameter."""
        from src.models.image import FetchResult

        # Setup: Mock image service fetch result
        mock_fetch_result = FetchResult(
            status="success", timestamp="2025-07-21T10:00:00Z", size_bytes=12345, url="https://picsum.photos/400/600"
        )
        mock_image_service.fetch_new_image.return_value = mock_fetch_result

        response = test_client.post("/fetch-image?force=true")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"

        # Verify the service method was called with force=True
        mock_image_service.fetch_new_image.assert_called_once_with(force=True)

    def test_image_caching_behavior_integration(self, test_client: TestClient, mock_image_service):
        """Test the complete image caching flow: fetch -> serve -> cache headers."""
        from src.models.image import FetchResult

        # Step 1: Fetch a new image
        mock_fetch_result = FetchResult(
            status="success", timestamp="2025-07-21T10:00:00Z", size_bytes=12345, url="https://picsum.photos/400/600"
        )
        mock_image_service.fetch_new_image.return_value = mock_fetch_result

        fetch_response = test_client.post("/fetch-image")
        assert fetch_response.status_code == 200

        # Step 2: Verify image is now available with proper cache headers
        import tempfile

        with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as temp_file:
            temp_file.write(b"fake_image_data")
            temp_file.flush()

            # Update the mock to return the real temp file path
            from pathlib import Path

            mock_image_service.get_image_path.return_value = Path(temp_file.name)

            image_response = test_client.get("/image")

            # Verify cache headers were set
            assert image_response.status_code == 200
            assert image_response.headers.get("Cache-Control") == "no-cache, no-store, must-revalidate"

            # Clean up
            import os

            os.unlink(temp_file.name)
