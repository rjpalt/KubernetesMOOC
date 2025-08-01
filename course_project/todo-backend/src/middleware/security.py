"""Security middleware for XSS prevention and security headers."""

import logging
from collections.abc import Callable

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger(__name__)


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Middleware to add security headers for XSS and other attack prevention."""

    def __init__(self, app, csp_policy: str | None = None):
        """Initialize security headers middleware.

        Args:
            app: FastAPI application instance
            csp_policy: Custom Content Security Policy, uses default if None
        """
        super().__init__(app)
        self.csp_policy = csp_policy or self._get_default_csp_policy()

    def _get_default_csp_policy(self) -> str:
        """Get default Content Security Policy for API endpoints."""
        # Strict CSP for API - no inline scripts, restrict sources
        return (
            "default-src 'self'; "
            "script-src 'self' 'strict-dynamic'; "
            "style-src 'self' 'unsafe-inline'; "
            "img-src 'self' data: https:; "
            "font-src 'self'; "
            "connect-src 'self'; "
            "media-src 'none'; "
            "object-src 'none'; "
            "frame-src 'none'; "
            "worker-src 'none'; "
            "frame-ancestors 'none'; "
            "form-action 'self'; "
            "base-uri 'self'; "
            "upgrade-insecure-requests"
        )

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Add security headers to all responses."""
        response = await call_next(request)

        # X-Content-Type-Options: Prevent MIME type sniffing
        response.headers["X-Content-Type-Options"] = "nosniff"

        # X-Frame-Options: Prevent clickjacking
        response.headers["X-Frame-Options"] = "DENY"

        # Content-Security-Policy: Prevent XSS and other injection attacks
        response.headers["Content-Security-Policy"] = self.csp_policy

        # X-XSS-Protection: Enable XSS filtering (legacy browsers)
        response.headers["X-XSS-Protection"] = "1; mode=block"

        # Referrer-Policy: Control referrer information
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"

        # Permissions-Policy: Disable unnecessary browser features
        response.headers["Permissions-Policy"] = (
            "geolocation=(), microphone=(), camera=(), payment=(), usb=(), screen-wake-lock=()"
        )

        logger.debug(f"Added security headers to response for {request.url.path}")
        return response


class XSSProtectionMiddleware(BaseHTTPMiddleware):
    """Middleware for additional XSS protection measures."""

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Process request and response for XSS protection."""
        response = await call_next(request)

        # Ensure JSON responses have correct content type
        if response.headers.get("content-type", "").startswith("application/json"):
            # Additional protection for JSON responses
            response.headers["X-Content-Type-Options"] = "nosniff"

            # Prevent JSON hijacking
            if request.method == "GET":
                response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"

        return response
