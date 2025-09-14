"""Prometheus metrics for broadcaster service."""

from prometheus_client import Counter, Gauge, Histogram

# Messages processed from NATS
messages_processed_total = Counter(
    "broadcaster_messages_processed_total",
    "Total messages processed from NATS",
    ["status"],  # success, error
)

# Webhook HTTP requests
webhook_requests_total = Counter("broadcaster_webhook_requests_total", "Total webhook HTTP requests", ["status_code"])

# NATS connection status
nats_connection_status = Gauge("broadcaster_nats_connected", "NATS connection status (1=connected, 0=disconnected)")

# Message processing latency
message_processing_duration = Histogram(
    "broadcaster_message_processing_duration_seconds",
    "Time spent processing messages",
    buckets=[0.001, 0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0],
)

# Webhook request latency
webhook_request_duration = Histogram(
    "broadcaster_webhook_request_duration_seconds",
    "Time spent sending webhook requests",
    buckets=[0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0, 30.0],
)
