"""Backend service configuration settings using Pydantic Settings."""

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

    # Database configuration
    postgres_host: str = Field(default="localhost", description="PostgreSQL host")
    postgres_port: int = Field(default=5432, description="PostgreSQL port")
    postgres_db: str = Field(default="todoapp", description="PostgreSQL database name")
    postgres_user: str = Field(description="PostgreSQL username")
    postgres_password: str = Field(description="PostgreSQL password")
    
    # SQL debugging
    sql_debug: bool = Field(default=False, description="Enable SQL query debugging")

    # CORS configuration
    cors_origins: str = Field(
        default="*",
        description="Allowed CORS origins (comma-separated)",
    )

    # API configuration
    api_title: str = Field(default="Todo Backend API", description="API title")
    api_description: str = Field(default="Backend service for managing todos", description="API description")
    api_version: str = Field(default="1.0.0", description="API version")

    @property
    def cors_origins_list(self) -> list[str]:
        """Get CORS origins as list, handling string input from environment."""
        if self.cors_origins == "*":
            return ["*"]
        return [origin.strip() for origin in self.cors_origins.split(",")]

    @property
    def database_url(self) -> str:
        """Construct database URL from individual components."""
        return f"postgresql+asyncpg://{self.postgres_user}:{self.postgres_password}@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"


# Global settings instance
settings = Settings()
