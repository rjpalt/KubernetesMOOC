"""Integration tests for health probe endpoints."""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, patch

from src.main import create_app


@pytest.fixture
def client():
    """Create test client."""
    app = create_app()
    return TestClient(app)


@pytest.fixture  
def mock_db_manager():
    """Mock database manager for testing."""
    with patch("src.database.connection.db_manager") as mock:
        yield mock


@pytest.fixture
def mock_todo_service():
    """Mock todo service for testing."""
    with patch("src.api.routes.health.get_todo_service") as mock:
        yield mock


class TestHealthzEndpoint:
    """Test lightweight /healthz endpoint."""

    def test_healthz_returns_ok(self, client):
        """Test /healthz returns 200 OK."""
        response = client.get("/healthz")
        assert response.status_code == 200
        assert response.json() == {"status": "ok"}

    def test_healthz_no_database_dependency(self, client, mock_db_manager):
        """Test /healthz works even when database is unavailable."""
        # Make database health check fail
        mock_db_manager.health_check = AsyncMock(return_value=False)
        
        response = client.get("/healthz")
        assert response.status_code == 200
        assert response.json() == {"status": "ok"}
        
        # Verify database was not called
        mock_db_manager.health_check.assert_not_called()

    def test_healthz_fast_response(self, client):
        """Test /healthz has fast response time."""
        import time
        start_time = time.time()
        
        response = client.get("/healthz")
        
        end_time = time.time()
        response_time = end_time - start_time
        
        assert response.status_code == 200
        assert response_time < 0.1  # Should be very fast


class TestHealthEndpoint:
    """Test comprehensive /health endpoint."""

    def test_health_database_available(self, client, mock_db_manager, mock_todo_service):
        """Test /health returns 200 when database is available."""
        # Mock successful database connection
        mock_db_manager.health_check = AsyncMock(return_value=True)
        
        # Mock todo service
        mock_service_instance = AsyncMock()
        mock_service_instance.get_todo_count = AsyncMock(return_value=5)
        mock_todo_service.return_value = mock_service_instance
        
        response = client.get("/health")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["service"] == "todo-backend"
        assert data["database"] == "connected"
        assert data["todos_count"] == 5
        assert "timestamp" in data

    def test_health_database_unavailable(self, client, mock_db_manager):
        """Test /health returns 503 when database is unavailable."""
        # Mock failed database connection
        mock_db_manager.health_check = AsyncMock(return_value=False)
        
        response = client.get("/health")
        
        assert response.status_code == 503
        # In the actual app, the error is wrapped by error handlers
        data = response.json()
        assert "detail" in data
        # The actual error detail is in debug_info in development mode
        assert "debug_info" in data
        assert "HTTPException" in data["debug_info"]["error_type"]

    def test_health_database_error(self, client, mock_db_manager):
        """Test /health returns 503 when database check raises exception."""
        # Mock database exception
        mock_db_manager.health_check = AsyncMock(side_effect=Exception("DB Connection failed"))
        
        response = client.get("/health")
        
        assert response.status_code == 503
        data = response.json()
        assert "detail" in data
        # Verify the error was processed correctly
        assert "debug_info" in data
        assert "HTTPException" in data["debug_info"]["error_type"]

    def test_health_todo_service_error(self, client, mock_db_manager, mock_todo_service):
        """Test /health handles todo service errors gracefully."""
        # Mock successful database but failing todo service
        mock_db_manager.health_check = AsyncMock(return_value=True)
        mock_service_instance = AsyncMock()
        mock_service_instance.get_todo_count = AsyncMock(side_effect=Exception("Service error"))
        mock_todo_service.return_value = mock_service_instance
        
        response = client.get("/health")
        
        assert response.status_code == 503
        data = response.json()
        assert "detail" in data
        # Verify the error was processed correctly
        assert "debug_info" in data
        assert "HTTPException" in data["debug_info"]["error_type"]


class TestDatabaseResilience:
    """Test database connection resilience during startup."""

    def test_app_startup_with_database_unavailable(self, mock_db_manager):
        """Test application can start even when database is unavailable.""" 
        # Mock database as unavailable during startup
        mock_db_manager.health_check = AsyncMock(return_value=False)
        mock_db_manager.initialize = AsyncMock()
        
        # This should not raise an exception
        app = create_app()
        client = TestClient(app)
        
        # App should still respond to healthz
        response = client.get("/healthz") 
        assert response.status_code == 200

    @patch("src.main.get_todo_service")
    def test_startup_graceful_degradation(self, mock_get_todo_service, mock_db_manager):
        """Test startup continues with graceful degradation."""
        # Mock database health check failure
        mock_db_manager.health_check = AsyncMock(return_value=False)
        mock_db_manager.initialize = AsyncMock()
        
        # Mock todo service 
        mock_service = AsyncMock()
        mock_get_todo_service.return_value = mock_service
        
        # Create app (this triggers lifespan startup)
        app = create_app()
        client = TestClient(app)
        
        # Verify todo service initialization was skipped
        mock_service.initialize_with_sample_data.assert_not_called()
        
        # But healthz should still work
        response = client.get("/healthz")
        assert response.status_code == 200


class TestEndpointSecurity:
    """Test health endpoints follow security guidelines."""

    def test_health_no_sensitive_info_in_error(self, client, mock_db_manager):
        """Test error responses don't expose sensitive information."""
        mock_db_manager.health_check = AsyncMock(side_effect=Exception("Connection to db-server-internal-host:5432 failed"))
        
        response = client.get("/health")
        
        assert response.status_code == 503
        data = response.json()
        
        # Should not contain internal server details in the main detail
        assert "db-server-internal-host" not in data["detail"]
        assert "5432" not in data["detail"]
        
        # Verify error is sanitized
        assert data["detail"] == "Internal server error"

    def test_healthz_no_error_leakage(self, client):
        """Test /healthz never leaks error information."""
        # Even if something goes wrong internally, healthz should be stable
        response = client.get("/healthz")
        assert response.status_code == 200
        assert response.json() == {"status": "ok"}


@pytest.mark.asyncio
async def test_health_endpoint_compatibility():
    """Test both health endpoints coexist properly."""
    # This is a documentation test to verify the endpoint coexistence
    app = create_app()
    client = TestClient(app)
    
    # Old endpoint should still exist for backwards compatibility
    response = client.get("/be-health")
    assert response.status_code == 200
    
    # New endpoint should exist
    response = client.get("/health")
    assert response.status_code in [200, 503]  # Either healthy or unhealthy
    
    # Both should be functional
    healthz_response = client.get("/healthz")
    assert healthz_response.status_code == 200
