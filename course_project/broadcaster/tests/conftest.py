"""Test configuration and fixtures."""

import os

import pytest

# Ensure required settings are available during import-time of application modules
# The Settings model requires WEBHOOK_URL; set a default for tests.
os.environ.setdefault("WEBHOOK_URL", "http://test-webhook.example.com/webhook")


@pytest.fixture
def mock_settings():
    """Mock settings for testing."""
    from src.config.settings import Settings

    return Settings(
        webhook_url="http://test-webhook.example.com/webhook",
        nats_url="nats://test-nats:4222",
        nats_topic="test.events",
        webhook_timeout=5,
        webhook_retry_attempts=2,
    )


@pytest.fixture
def test_registry():
    """Isolated Prometheus metrics registry."""
    from prometheus_client import CollectorRegistry

    return CollectorRegistry()


@pytest.fixture
def mock_nats_client():
    """Mock NATS client for unit tests."""
    from unittest.mock import AsyncMock

    import nats

    mock_client = AsyncMock(spec=nats.NATS)
    mock_client.is_connected = True
    mock_client.subscribe = AsyncMock()
    mock_client.publish = AsyncMock()
    mock_client.close = AsyncMock()
    return mock_client


@pytest.fixture
def mock_httpx_client():
    """Mock HTTPX client for webhook tests."""
    from unittest.mock import AsyncMock, Mock

    import httpx

    mock_client = AsyncMock(spec=httpx.AsyncClient)
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.raise_for_status = Mock()
    mock_client.post.return_value.__aenter__.return_value = mock_response
    return mock_client


@pytest.fixture
def test_client():
    """FastAPI test client for endpoint tests."""
    from fastapi.testclient import TestClient

    # Import app lazily to ensure fixtures/env are set
    from src.main import app

    client = TestClient(app)
    return client
