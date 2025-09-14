"""Test configuration and fixtures."""

import pytest


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
