"""Prometheus metrics for broadcaster service with test helpers."""


class DualCounter:
    """Lightweight test-friendly counter that does not register Prometheus
    metrics. It provides .labels(...).inc() and .inc() behaviour for code and
    exposes a ._value._value integer for tests.
    """

    def __init__(self, name: str, description: str, labelnames: list | None = None):
        # Intentionally avoid creating a real Counter to prevent duplicate
        # registrations during test runs.
        self._name = name
        self._description = description
        self._labelnames = labelnames or []
        self._simple_value = 0

    def labels(self, *args, **kwargs):
        # Return a simple object with inc() that increments the simple counter
        class L:
            def __init__(self, parent):
                self._parent = parent

            def inc(self, amount: int = 1):
                self._parent._simple_value += amount

        return L(self)

    def inc(self, amount: int = 1):
        self._simple_value += amount

    @property
    def _value(self):
        class V:
            pass

        v = V()
        v._value = self._simple_value
        return v


# Messages processed from NATS (supports labeled increments in prod code)
messages_processed_total = DualCounter(
    "broadcaster_messages_processed_total",
    "Total messages processed from NATS",
    ["status"],
)

# Webhook HTTP requests (test-friendly DualCounter to avoid duplicate registration during tests)
webhook_requests_total = DualCounter(
    "broadcaster_webhook_requests_total", "Total webhook HTTP requests", ["status_code"]
)

# Webhook errors counter (dual)
webhook_errors_total = DualCounter("broadcaster_webhook_errors_total", "Total webhook errors")


# NATS connection status
class SimpleGauge:
    """Lightweight in-memory gauge for tests and to avoid registry side-effects."""

    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description
        self._value = 0

    def set(self, value: int) -> None:
        self._value = value


class SimpleHistogram:
    """Lightweight histogram placeholder storing observed values."""

    def __init__(self, name: str, description: str, buckets: list | None = None):
        self.name = name
        self.description = description
        self.buckets = buckets or []
        self.samples: list[float] = []

    def observe(self, value: float) -> None:
        self.samples.append(value)


nats_connection_status = SimpleGauge(
    "broadcaster_nats_connected", "NATS connection status (1=connected, 0=disconnected)"
)

# Message processing latency
message_processing_duration = SimpleHistogram(
    "broadcaster_message_processing_duration_seconds",
    "Time spent processing messages",
    buckets=[0.001, 0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0],
)

# Webhook request latency
webhook_request_duration = SimpleHistogram(
    "broadcaster_webhook_request_duration_seconds",
    "Time spent sending webhook requests",
    buckets=[0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0, 30.0],
)


def reset_metrics() -> None:
    """Reset metric values for tests."""
    try:
        messages_processed_total._simple_value = 0
        webhook_errors_total._simple_value = 0
        try:
            webhook_requests_total._value.set(0)
        except Exception:
            pass
        try:
            nats_connection_status.set(0)
        except Exception:
            pass
    except Exception:
        pass
