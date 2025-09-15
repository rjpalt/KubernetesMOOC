"""Metrics endpoint for tests and basic instrumentation."""

from fastapi import APIRouter, Response

from ...metrics.prometheus import messages_processed_total, webhook_errors_total

router = APIRouter()


@router.get("/metrics")
def metrics() -> Response:
    """Return a simple Prometheus-style text including key metric names.

    This endpoint is intentionally lightweight for tests and returns metric
    names and values from the in-memory DualCounter wrappers.
    """
    lines = []
    try:
        lines.append("# HELP broadcaster_messages_processed_total Total messages processed from NATS")
        lines.append("# TYPE broadcaster_messages_processed_total counter")
        lines.append(f"broadcaster_messages_processed_total {messages_processed_total._value._value}")
    except Exception:
        pass

    try:
        lines.append("# HELP broadcaster_webhook_errors_total Total webhook errors")
        lines.append("# TYPE broadcaster_webhook_errors_total counter")
        lines.append(f"broadcaster_webhook_errors_total {webhook_errors_total._value._value}")
    except Exception:
        pass

    body = "\n".join(lines) + "\n"
    return Response(content=body, media_type="text/plain; version=0.0.4")
