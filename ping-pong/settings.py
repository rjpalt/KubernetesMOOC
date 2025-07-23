#!/usr/bin/env python3

from typing import Optional

from pydantic import field_validator
from pydantic_settings import BaseSettings


class PingPongSettings(BaseSettings):
    """
    Ping-pong application settings with environment variable support.

    Environment variables are prefixed with PING_PONG_ (e.g., PING_PONG_APP_PORT).
    Also supports .env file loading.
    """

    # Server configuration
    app_port: int = 3000
    host: str = "0.0.0.0"

    # Logging configuration
    log_level: str = "INFO"

    class Config:
        env_prefix = "PING_PONG_"
        env_file = ".env"
        case_sensitive = False

    @field_validator("log_level")
    @classmethod
    def validate_log_level(cls, v):
        """Ensure log level is valid"""
        valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if v.upper() not in valid_levels:
            raise ValueError(f"Log level must be one of {valid_levels}")
        return v.upper()

    @field_validator("app_port")
    @classmethod
    def validate_port(cls, v):
        """Ensure port is in valid range"""
        if not (1 <= v <= 65535):
            raise ValueError("Port must be between 1 and 65535")
        return v


# Global settings instance - lazy loaded
_settings: Optional[PingPongSettings] = None


def get_settings() -> PingPongSettings:
    """
    Get the global settings instance.
    Creates it on first call (singleton pattern).
    """
    global _settings
    if _settings is None:
        _settings = PingPongSettings()
    return _settings


def reload_settings() -> PingPongSettings:
    """
    Force reload settings (useful for testing).
    """
    global _settings
    _settings = None
    return get_settings()


if __name__ == "__main__":
    # For testing/debugging the settings
    settings = get_settings()
    print("Current ping-pong settings:")
    print(f"  App port: {settings.app_port}")
    print(f"  Log level: {settings.log_level}")
    print(f"  Host: {settings.host}")
