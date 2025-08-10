"""Backend service configuration settings using Pydantic Settings."""

import os
from pydantic import Field, computed_field
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
    debug: bool | None = Field(default=None, description="Debug mode (None = auto-detect)")

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

    @computed_field
    @property
    def is_production(self) -> bool:
        """Detect if running in production environment."""
        
        # Method 1: Check Kubernetes namespace via Downward API environment variables
        k8s_namespace = os.getenv("KUBERNETES_NAMESPACE") or os.getenv("POD_NAMESPACE")
        if k8s_namespace == "project":
            return True
        
        # Method 2: Check Kubernetes namespace via service account file (automatically mounted)
        try:
            with open("/var/run/secrets/kubernetes.io/serviceaccount/namespace", "r") as f:
                k8s_namespace = f.read().strip()
                if k8s_namespace == "project":
                    return True
        except (FileNotFoundError, PermissionError, OSError):
            # Not in Kubernetes or file not accessible
            pass
        
        # Method 3: Check explicit production environment markers
        if os.getenv("ENVIRONMENT") == "production":
            return True
        if os.getenv("NODE_ENV") == "production":
            return True
            
        # Default to development for local/feature environments
        return False

    @computed_field
    @property
    def debug_enabled(self) -> bool:
        """Determine debug mode with intelligent defaults."""
        # Explicit DEBUG environment variable takes precedence
        if self.debug is not None:
            return self.debug
            
        # Auto-detect based on environment
        # Production (project namespace): DEBUG=false for security
        # Development/Feature environments: DEBUG=true for convenience
        return not self.is_production

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
