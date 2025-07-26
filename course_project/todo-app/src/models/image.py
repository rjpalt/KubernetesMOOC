"""Data models for image operations."""

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
    message: str | None = None
    file_size: int | None = None
    modified_time: str | None = None
    metadata: ImageMetadata | None = None
    last_fetch_time: str | None = None
    next_auto_fetch: str | None = None


class FetchResult(BaseModel):
    """Result of an image fetch operation."""

    status: str
    reason: str | None = None
    error: str | None = None
    timestamp: str
    size_bytes: int | None = None
    url: str | None = None
    last_fetch: str | None = None
