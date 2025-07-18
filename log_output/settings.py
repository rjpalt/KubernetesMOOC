#!/usr/bin/env python3

import os
from pathlib import Path
from pydantic import field_validator
from pydantic_settings import BaseSettings
from typing import Optional


class AppSettings(BaseSettings):
    """
    Application settings with environment variable support and sensible defaults.
    
    Environment variables are prefixed with LOG_APP_ (e.g., LOG_APP_SHARED_LOG_PATH).
    Also supports .env file loading.
    """
    
    # Logging configuration
    shared_log_path: str = "tmp/logs/output.txt"
    log_level: str = "INFO"
    
    # Shared volume configuration (for ping-pong communication)
    shared_volume_path: str = "shared"
    ping_pong_counter_file: str = "ping_pong_counter.txt"
    
    # Server configuration
    app_port: int = 8000
    log_server_port: int = 8001
    host: str = "0.0.0.0"
    
    # Application behavior
    log_interval_seconds: int = 5
    
    class Config:
        env_prefix = "LOG_APP_"
        env_file = ".env"
        case_sensitive = False
    
    @field_validator('shared_log_path')
    @classmethod
    def validate_log_path(cls, v):
        """Ensure the parent directory exists for the log file"""
        log_path = Path(v)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        return str(log_path)
    
    @field_validator('log_level')
    @classmethod
    def validate_log_level(cls, v):
        """Ensure log level is valid"""
        valid_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
        if v.upper() not in valid_levels:
            raise ValueError(f'Log level must be one of {valid_levels}')
        return v.upper()
    
    @field_validator('app_port', 'log_server_port')
    @classmethod
    def validate_ports(cls, v):
        """Ensure ports are in valid range"""
        if not (1 <= v <= 65535):
            raise ValueError('Port must be between 1 and 65535')
        return v
    
    @field_validator('log_interval_seconds')
    @classmethod
    def validate_interval(cls, v):
        """Ensure interval is reasonable"""
        if v < 1:
            raise ValueError('Log interval must be at least 1 second')
        return v
    
    @property
    def ping_pong_counter_file_path(self) -> str:
        """Get the full path to the ping-pong counter file"""
        from pathlib import Path
        return str(Path(self.shared_volume_path) / self.ping_pong_counter_file)


# Global settings instance - lazy loaded
_settings: Optional[AppSettings] = None


def get_settings() -> AppSettings:
    """
    Get the global settings instance.
    Creates it on first call (singleton pattern).
    """
    global _settings
    if _settings is None:
        _settings = AppSettings()
    return _settings


def reload_settings() -> AppSettings:
    """
    Force reload settings (useful for testing).
    """
    global _settings
    _settings = None
    return get_settings()


# Convenience function for common use cases
def get_shared_log_path() -> str:
    """Get the shared log file path"""
    return get_settings().shared_log_path


def get_log_server_port() -> int:
    """Get the log server port"""
    return get_settings().log_server_port


def get_app_port() -> int:
    """Get the main app port"""
    return get_settings().app_port


if __name__ == "__main__":
    # For testing/debugging the settings
    settings = get_settings()
    print("Current settings:")
    print(f"  Shared log path: {settings.shared_log_path}")
    print(f"  App port: {settings.app_port}")
    print(f"  Log server port: {settings.log_server_port}")
    print(f"  Log interval: {settings.log_interval_seconds}s")
    print(f"  Log level: {settings.log_level}")
    print(f"  Host: {settings.host}")
