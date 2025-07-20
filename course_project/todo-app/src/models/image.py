"""Data models for image operations."""

from typing import Optional

from pydantic import BaseModel


class ImageMetadata(BaseModel):
    """Metadata for cached images."""

    timestamp: str
    size_bytes: int
    url: str
    status: str = "success"


class ImageInfo(BaseModel):
    """Information about the current cached image."""

    status: str
    message: Optional[str] = None
    file_size: Optional[int] = None
    modified_time: Optional[str] = None
    metadata: Optional[ImageMetadata] = None
    last_fetch_time: Optional[str] = None
    next_auto_fetch: Optional[str] = None


class FetchResult(BaseModel):
    """Result of an image fetch operation."""

    status: str
    reason: Optional[str] = None
    error: Optional[str] = None
    timestamp: str
    size_bytes: Optional[int] = None
    url: Optional[str] = None
    last_fetch: Optional[str] = None
