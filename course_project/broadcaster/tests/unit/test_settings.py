"""Test environment-aware configuration."""

from unittest.mock import mock_open, patch

from src.config.settings import Settings


class TestEnvironmentDetection:
    """Test environment detection logic."""

    def test_local_environment_detection(self, monkeypatch):
        """Test local development environment detection."""
        # Remove Kubernetes indicators
        monkeypatch.delenv("KUBERNETES_NAMESPACE", raising=False)
        monkeypatch.delenv("POD_NAMESPACE", raising=False)

        with patch("os.path.exists", return_value=False):
            settings = Settings(webhook_url="https://test.example.com")
            assert settings.deployment_environment == "local"
            assert settings.debug_mode is True
            assert settings.effective_nats_url == "nats://localhost:4222"

    def test_feature_environment_detection(self):
        """Test feature branch environment detection."""
        namespace_content = "feature-ex-c4-e6"

        with patch("os.path.exists", return_value=True), patch("builtins.open", mock_open(read_data=namespace_content)):
            settings = Settings(webhook_url="https://test.example.com")
            assert settings.deployment_environment == "development"
            assert settings.current_namespace == "feature-ex-c4-e6"
            assert settings.effective_nats_url == "nats://nats:4222"

    def test_production_environment_detection(self):
        """Test production environment detection."""
        namespace_content = "project"

        with patch("os.path.exists", return_value=True), patch("builtins.open", mock_open(read_data=namespace_content)):
            settings = Settings(webhook_url="https://prod.webhook.com")
            assert settings.deployment_environment == "production"
            assert settings.current_namespace == "project"
            assert settings.debug_mode is False

    def test_kubernetes_downward_api(self, monkeypatch):
        """Test Kubernetes namespace detection via downward API."""
        monkeypatch.setenv("POD_NAMESPACE", "feature-test-123")

        settings = Settings(webhook_url="https://test.example.com")
        assert settings.current_namespace == "feature-test-123"
