"""Backend service configuration settings using Pydantic Settings."""

from typing import List

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Backend application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Server configuration
    port: int = Field(default=8001, description="Server port")
    host: str = Field(default="0.0.0.0", description="Server host")
    debug: bool = Field(default=False, description="Debug mode")

    # Logging configuration
    log_level: str = Field(default="INFO", description="Logging level")

    # CORS configuration
    cors_origins: List[str] = Field(
        default=["*"], description="Allowed CORS origins", json_schema_extra={"env": "CORS_ORIGINS"}
    )

    # API configuration
    api_title: str = Field(default="Todo Backend API", description="API title")
    api_description: str = Field(default="Backend service for managing todos", description="API description")
    api_version: str = Field(default="1.0.0", description="API version")

    @property
    def cors_origins_list(self) -> List[str]:
        """Get CORS origins as list, handling string input from environment."""
        if isinstance(self.cors_origins, str):
            return [origin.strip() for origin in self.cors_origins.split(",")]
        return self.cors_origins


# Global settings instance
settings = Settings()
