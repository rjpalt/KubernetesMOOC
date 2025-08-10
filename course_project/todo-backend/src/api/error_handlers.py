"""Custom error handlers for information disclosure prevention.

This module provides custom exception handlers that sanitize error responses
to prevent information disclosure while maintaining proper logging for debugging.

Key security principles:
1. Generic error messages for clients
2. Detailed logging for internal debugging
3. Consistent error response format
4. No sensitive information in client responses
"""

import logging
from typing import Dict, Any

from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

from src.config.settings import settings

logger = logging.getLogger(__name__)


class ErrorSanitizer:
    """Sanitizes error responses to prevent information disclosure."""
    
    @staticmethod
    def sanitize_404_error(request: Request, exc: HTTPException) -> Dict[str, Any]:
        """Sanitize 404 errors with generic message."""
        # Log detailed information for debugging
        logger.warning(
            f"404 Not Found - Path: {request.url.path}, Method: {request.method}, "
            f"Original detail: {getattr(exc, 'detail', 'N/A')}"
        )
        
        # In development mode, include additional debug information
        if settings.debug_enabled:
            return {
                "detail": "Resource not found",
                "debug_info": {
                    "path": str(request.url.path),
                    "method": request.method,
                    "original_detail": getattr(exc, 'detail', 'N/A'),
                    "mode": "development"
                }
            }
        
        # Return generic message to client in production
        return {"detail": "Resource not found"}
    
    @staticmethod
    def sanitize_validation_error(request: Request, exc: RequestValidationError) -> Dict[str, Any]:
        """Sanitize validation errors to prevent internal detail exposure."""
        # Log detailed validation errors for debugging
        logger.warning(
            f"Validation Error - Path: {request.url.path}, Method: {request.method}, "
            f"Errors: {exc.errors()}"
        )
        
        # In development mode, include detailed validation errors
        if settings.debug_enabled:
            return {
                "detail": "Invalid request data",
                "debug_info": {
                    "validation_errors": exc.errors(),
                    "path": str(request.url.path),
                    "method": request.method,
                    "mode": "development"
                }
            }
        
        # Return generic validation message in production
        return {
            "detail": "Invalid request data"
        }
    
    @staticmethod
    def sanitize_server_error(request: Request, exc: Exception) -> Dict[str, Any]:
        """Sanitize server errors to prevent internal detail exposure."""
        # Log detailed server error for debugging
        logger.error(
            f"Server Error - Path: {request.url.path}, Method: {request.method}, "
            f"Error: {type(exc).__name__}: {str(exc)}",
            exc_info=True
        )
        
        # In development mode, include detailed error information
        if settings.debug_enabled:
            return {
                "detail": "Internal server error",
                "debug_info": {
                    "error_type": type(exc).__name__,
                    "error_message": str(exc),
                    "path": str(request.url.path),
                    "method": request.method,
                    "mode": "development"
                }
            }
        
        # Return generic server error message in production
        return {"detail": "Internal server error"}


async def custom_404_handler(request: Request, exc: HTTPException) -> JSONResponse:
    """Handle 404 errors with sanitized responses."""
    sanitized_response = ErrorSanitizer.sanitize_404_error(request, exc)
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content=sanitized_response
    )


async def custom_validation_error_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    """Handle validation errors with sanitized responses."""
    sanitized_response = ErrorSanitizer.sanitize_validation_error(request, exc)
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=sanitized_response
    )


async def custom_http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    """Handle HTTP exceptions with sanitized responses."""
    if exc.status_code == 404:
        return await custom_404_handler(request, exc)
    
    # For other HTTP exceptions, sanitize based on status code
    if exc.status_code >= 500:
        sanitized_response = ErrorSanitizer.sanitize_server_error(request, exc)
    else:
        # For 4xx errors (except 404), log but keep generic message
        logger.warning(
            f"HTTP {exc.status_code} - Path: {request.url.path}, Method: {request.method}, "
            f"Original detail: {getattr(exc, 'detail', 'N/A')}"
        )
        
        # In development mode, include debug information for client errors
        if settings.debug_enabled:
            sanitized_response = {
                "detail": "Client error",
                "debug_info": {
                    "status_code": exc.status_code,
                    "original_detail": getattr(exc, 'detail', 'N/A'),
                    "path": str(request.url.path),
                    "method": request.method,
                    "mode": "development"
                }
            }
        else:
            sanitized_response = {"detail": "Client error"}
    
    return JSONResponse(
        status_code=exc.status_code,
        content=sanitized_response
    )


async def custom_server_error_handler(request: Request, exc: Exception) -> JSONResponse:
    """Handle unhandled server errors with sanitized responses."""
    sanitized_response = ErrorSanitizer.sanitize_server_error(request, exc)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=sanitized_response
    )
