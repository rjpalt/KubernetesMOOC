#!/usr/bin/env python3

import os
from pathlib import Path
from pydantic import field_validator
from pydantic_settings import BaseSettings
from typing import Optional


class PingPongSettings(BaseSettings):
    """
    Ping-pong application settings with environment variable support.
    
    Environment variables are prefixed with PING_PONG_ (e.g., PING_PONG_SHARED_VOLUME_PATH).
    Also supports .env file loading.
    """
    
    # Shared volume configuration
    shared_volume_path: str = "shared"
    counter_file_name: str = "ping_pong_counter.txt"
    
    # Server configuration
    app_port: int = 3000
    host: str = "0.0.0.0"
    
    # Logging configuration
    log_level: str = "INFO"
    
    class Config:
        env_prefix = "PING_PONG_"
        env_file = ".env"
        case_sensitive = False
    
    @field_validator('shared_volume_path')
    @classmethod
    def validate_shared_path(cls, v):
        """Ensure the shared volume path exists or can be created"""
        shared_path = Path(v)
        shared_path.mkdir(parents=True, exist_ok=True)
        return str(shared_path)
    
    @field_validator('log_level')
    @classmethod
    def validate_log_level(cls, v):
        """Ensure log level is valid"""
        valid_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
        if v.upper() not in valid_levels:
            raise ValueError(f'Log level must be one of {valid_levels}')
        return v.upper()
    
    @field_validator('app_port')
    @classmethod
    def validate_port(cls, v):
        """Ensure port is in valid range"""
        if not (1 <= v <= 65535):
            raise ValueError('Port must be between 1 and 65535')
        return v
    
    @property
    def counter_file_path(self) -> str:
        """Get the full path to the counter file"""
        return str(Path(self.shared_volume_path) / self.counter_file_name)


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
    print(f"  Shared volume path: {settings.shared_volume_path}")
    print(f"  Counter file path: {settings.counter_file_path}")
    print(f"  App port: {settings.app_port}")
    print(f"  Log level: {settings.log_level}")
    print(f"  Host: {settings.host}")
