"""
Pytest configuration for L2 staging integration tests.

Provides fixtures for:
- Staging backend URL from environment
- AsyncClient for API calls
- Unique ID generation for test data
"""

import os
import time
import random
import pytest
import pytest_asyncio
from httpx import AsyncClient


@pytest.fixture
def staging_backend_url() -> str:
    """
    Get staging backend URL from environment variable.
    
    Returns:
        Backend URL (e.g., https://staging-backend.example.com)
    
    Raises:
        AssertionError: If STAGING_BACKEND_URL not set
    """
    url = os.getenv("STAGING_BACKEND_URL")
    assert url, "STAGING_BACKEND_URL environment variable required"
    return url.rstrip("/")  # Remove trailing slash if present


@pytest_asyncio.fixture
async def staging_client(staging_backend_url: str) -> AsyncClient:
    """
    Async HTTP client for staging backend API.
    
    Configured with:
    - Base URL from environment
    - 30-second timeout (per standards)
    - Automatic connection cleanup
    
    Yields:
        AsyncClient instance for making API calls
    """
    async with AsyncClient(
        base_url=staging_backend_url,
        timeout=30.0,
        follow_redirects=True
    ) as client:
        yield client


@pytest.fixture
def unique_id_generator():
    """
    Generate unique IDs for test data using timestamps and random suffix.
    
    Combines millisecond timestamp with random suffix to prevent collisions
    when multiple tests run in the same millisecond.
    
    Returns:
        Function that takes a prefix and returns unique ID
    
    Example:
        >>> generate = unique_id_generator()
        >>> todo_text = generate("test_todo")
        >>> # Returns: "test_todo_1704123456789_5432"
    """
    def _generate(prefix: str) -> str:
        timestamp = int(time.time() * 1000)  # Milliseconds
        random_suffix = random.randint(1000, 9999)
        return f"{prefix}_{timestamp}_{random_suffix}"
    return _generate
