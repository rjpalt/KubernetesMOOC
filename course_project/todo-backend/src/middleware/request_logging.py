"""Request logging middleware for comprehensive request/response monitoring.

Provides structured JSON logging of all HTTP requests and responses
for Grafana monitoring and debugging. Yeah. Yeahs.
"""

import json
import logging
import time
import uuid
from collections.abc import Callable
from enum import Enum

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

# Create dedicated logger for request monitoring
request_logger = logging.getLogger("request_logger")


class ErrorType(Enum):
    """HTTP error type classification for monitoring."""

    VALIDATION_ERROR = "VALIDATION_ERROR"
    NOT_FOUND = "NOT_FOUND"
    CLIENT_ERROR = "CLIENT_ERROR"
    SERVER_ERROR = "SERVER_ERROR"


class LogEvent(Enum):
    """Log event types for structured logging."""

    REQUEST = "REQUEST"
    RESPONSE = "RESPONSE"
    VALIDATION_ERROR = "VALIDATION_ERROR"
    NOT_FOUND_ERROR = "NOT_FOUND_ERROR"
    CLIENT_ERROR = "CLIENT_ERROR"
    SERVER_ERROR = "SERVER_ERROR"


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Middleware to log all HTTP requests and responses with structured data."""

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Process request and log details."""
        start_time = time.time()

        # Generate or extract correlation ID
        request_id = self._get_or_generate_request_id(request)

        # Log incoming request
        request_data = {
            "request_id": request_id,
            "event": LogEvent.REQUEST.value,
            "timestamp": time.time(),
            "method": request.method,
            "path": request.url.path,
            "query_params": str(request.query_params) if request.query_params else None,
            "user_agent": request.headers.get("user-agent"),
            "client_ip": self._get_client_ip(request),
        }

        # Log request as JSON
        request_logger.info(json.dumps(request_data))

        # Process request
        response = await call_next(request)

        # Add correlation ID to response headers
        response.headers["X-Request-ID"] = request_id

        # Calculate response time
        process_time = time.time() - start_time

        # Log response
        response_data = {
            "request_id": request_id,
            "event": LogEvent.RESPONSE.value,
            "timestamp": time.time(),
            "method": request.method,
            "path": request.url.path,
            "status_code": response.status_code,
            "response_time_ms": round(process_time * 1000, 2),
        }

        # Add error classification for monitoring
        error_info = self._classify_error(response.status_code)
        if error_info:
            response_data.update(error_info)

        # Log response as JSON
        request_logger.info(json.dumps(response_data))

        return response

    def _get_or_generate_request_id(self, request: Request) -> str:
        """Get existing request ID from headers or generate new one."""
        # Check for existing correlation ID from load balancer/proxy
        request_id = request.headers.get("X-Request-ID")

        if request_id:
            return request_id

        # Generate new UUID for correlation
        return str(uuid.uuid4())

    def _classify_error(self, status_code: int) -> dict | None:
        """Classify HTTP status codes for error monitoring.

        Args:
            status_code: HTTP status code

        Returns:
            Dictionary with error classification or None for success codes
        """
        if status_code < 400:
            return None

        # Define error classification mapping
        error_classifications = {
            422: (ErrorType.VALIDATION_ERROR, LogEvent.VALIDATION_ERROR),
            404: (ErrorType.NOT_FOUND, LogEvent.NOT_FOUND_ERROR),
        }

        # Check for specific error codes first
        if status_code in error_classifications:
            error_type, log_event = error_classifications[status_code]
            return {
                "error": True,
                "error_type": error_type.value,
                "event": log_event.value,
            }

        # Fall back to range-based classification
        if status_code >= 500:
            return {
                "error": True,
                "error_type": ErrorType.SERVER_ERROR.value,
                "event": LogEvent.SERVER_ERROR.value,
            }
        elif status_code >= 400:
            return {
                "error": True,
                "error_type": ErrorType.CLIENT_ERROR.value,
                "event": LogEvent.CLIENT_ERROR.value,
            }

        return None

    def _get_client_ip(self, request: Request) -> str:
        """Extract client IP address from request."""
        # Check for forwarded headers (common in production)
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()

        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip

        # Fall back to client host
        if request.client:
            return request.client.host

        return "unknown"
