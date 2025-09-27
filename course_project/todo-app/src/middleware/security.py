"""Security middleware for frontend XSS prevention. Verrah Secure."""

import logging
from collections.abc import Callable

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger(__name__)


class FrontendSecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Security headers middleware optimized for frontend application."""

    def __init__(self, app):
        """Initialize frontend security headers middleware."""
        super().__init__(app)

    def _get_frontend_csp_policy(self) -> str:
        """Get Content Security Policy optimized for frontend with HTMX."""
        # CSP that allows HTMX while preventing XSS
        return (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline' https://unpkg.com; "  # Allow HTMX from CDN
            "style-src 'self' 'unsafe-inline'; "  # Allow inline styles
            "img-src 'self' data: https: http:; "  # Allow external images
            "font-src 'self' https:; "
            "connect-src 'self'; "
            "frame-src 'none'; "
            "object-src 'none'; "
            "base-uri 'self'; "
            "form-action 'self'; "
            "frame-ancestors 'none'"
        )

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Add security headers to frontend responses."""
        response = await call_next(request)

        # Basic security headers for all responses
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"

        # Content-specific security headers
        content_type = response.headers.get("content-type", "")

        if "text/html" in content_type:
            # HTML responses get full CSP
            response.headers["Content-Security-Policy"] = self._get_frontend_csp_policy()
            # X-XSS-Protection for legacy browsers
            response.headers["X-XSS-Protection"] = "1; mode=block"

        elif "application/json" in content_type:
            # JSON responses get restrictive CSP
            response.headers["Content-Security-Policy"] = "default-src 'none'"

        logger.debug(f"Added frontend security headers to {request.url.path}")
        return response
