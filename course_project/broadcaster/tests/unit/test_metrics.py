"""Test Prometheus metrics accuracy."""

from src.metrics.prometheus import messages_processed_total, reset_metrics, webhook_errors_total


class TestPrometheusMetrics:
    """Test Prometheus metrics functionality."""

    def setup_method(self):
        """Reset metrics before each test."""
        reset_metrics()

    def test_message_processed_counter_increments(self):
        """Test that message counter increments correctly."""
        initial_count = messages_processed_total._value._value

        # Simulate processing a message
        messages_processed_total.inc()

        assert messages_processed_total._value._value == initial_count + 1

    def test_webhook_error_counter_increments(self):
        """Test that error counter increments on failures."""
        initial_count = webhook_errors_total._value._value

        # Simulate webhook error
        webhook_errors_total.inc()

        assert webhook_errors_total._value._value == initial_count + 1

    def test_metrics_endpoint_content(self, test_client):
        """Test that metrics endpoint returns proper format."""
        response = test_client.get("/metrics")
        assert response.status_code == 200

        content = response.text
        assert "broadcaster_messages_processed_total" in content
        assert "broadcaster_webhook_errors_total" in content
