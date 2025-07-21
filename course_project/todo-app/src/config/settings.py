"""Application configuration settings."""

import os
from pathlib import Path


class Settings:
    """Application settings loaded from environment variables."""

    def __init__(self):
        # Server configuration
        self.port: int = int(os.environ.get("PORT", "8000"))
        self.host: str = os.environ.get("HOST", "0.0.0.0")
        self.debug: bool = os.environ.get("DEBUG", "false").lower() == "true"

        # Image configuration
        self.image_cache_path: Path = Path(os.environ.get("IMAGE_CACHE_PATH", "./images"))
        self.image_update_interval_minutes: int = int(os.environ.get("IMAGE_UPDATE_INTERVAL_MINUTES", "10"))
        self.picsum_url: str = os.environ.get("PICSUM_URL", "https://picsum.photos/1200")
        self.http_timeout: float = float(os.environ.get("HTTP_TIMEOUT", "30.0"))

        # Logging configuration
        self.log_level: str = os.environ.get("LOG_LEVEL", "INFO")

        # Template configuration
        self.template_directory: str = os.environ.get("TEMPLATE_DIRECTORY", "templates")
        
        # Todo backend service configuration
        self.todo_backend_url: str = os.environ.get("TODO_BACKEND_URL", "http://localhost:8001")
        self.todo_backend_timeout: float = float(os.environ.get("TODO_BACKEND_TIMEOUT", "10.0"))

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


# Global settings instance - because apparently you need everything to be global
settings = Settings()
