"""Application configuration settings using Pydantic Settings."""

from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Server configuration
    port: int = Field(default=8000, description="Server port")
    host: str = Field(default="0.0.0.0", description="Server host")
    debug: bool = Field(default=False, description="Debug mode")

    # Image configuration
    image_cache_path: Path = Field(default=Path("./images"), description="Path to image cache directory")
    image_update_interval_minutes: int = Field(default=10, description="Image update interval in minutes")
    picsum_url: str = Field(default="https://picsum.photos/1200", description="Picsum API URL")
    http_timeout: float = Field(default=30.0, description="HTTP request timeout in seconds")

    # Logging configuration
    log_level: str = Field(default="INFO", description="Logging level")

    # Template configuration
    template_directory: str = Field(default="templates", description="Template directory path")

    # Todo backend service configuration
    todo_backend_url: str = Field(default="http://localhost:8001", description="Todo backend service URL")
    todo_backend_timeout: float = Field(default=10.0, description="Todo backend request timeout in seconds")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Ensure directories exist
        self.image_cache_path.mkdir(exist_ok=True)

    @property
    def image_current_file(self) -> Path:
        """Get the path to the current image file."""
        return self.image_cache_path / "current.jpg"

    @property
    def image_metadata_file(self) -> Path:
        """Get the path to the image metadata file."""
        return self.image_cache_path / "metadata.txt"


# Global settings instance
settings = Settings()
