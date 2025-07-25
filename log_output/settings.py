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
    
    # Ping-pong service configuration (HTTP communication)
    # By default uses localhost for local development, for kubernetes deployment needs to be
    # over-written with the service name DNS and port
    # Use env variables LOG_APP_PING_PONG_SERVICE_HOST and LOG_APP_PING_PONG_SERVICE_PORT
    ping_pong_service_host: str = "localhost"
    ping_pong_service_port: int = 3000
    
    # Server configuration
    app_port: int = 8000
    log_server_port: int = 8001
    host: str = "0.0.0.0"
    
    # Application behavior
    log_interval_seconds: int = 5
    
    # ConfigMap configuration
    config_file_path: str = "/config/information.txt"
    message: Optional[str] = None  # ConfigMap environment variable
    require_config_in_k8s: bool = False  # Set to True to require ConfigMap in all environments
    
    # Startup-time cached values
    _config_file_content: Optional[str] = None
    _config_initialized: bool = False
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        # For local development, try local config file first
        self._setup_config_path()
        
    def _setup_config_path(self):
        """Setup the config file path, preferring local development path if available"""
        # Check if we have a local config file for development
        local_config_path = Path(__file__).parent / "config" / "information.txt"
        
        if local_config_path.exists():
            self.config_file_path = str(local_config_path)
        # Otherwise use the default Kubernetes path
        # (self.config_file_path already set to "/config/information.txt")
        
    def initialize_config(self) -> None:
        """
        Initialize configuration at startup. Call this once when the app starts.
        Will fail fast if required configuration is missing in deployment environments.
        """
        if self._config_initialized:
            return
            
        # Read config file content once at startup
        self._config_file_content = self._read_config_file_startup()
        
        # Check if we're likely in a Kubernetes environment
        is_k8s_env = os.path.exists('/var/run/secrets/kubernetes.io/serviceaccount')
        
        # Fail fast if we require config and are missing it in K8s
        if self.require_config_in_k8s and is_k8s_env:
            if self._config_file_content is None:
                raise RuntimeError(f"Required ConfigMap file not found at {self.config_file_path} in Kubernetes environment")
            if self.message is None:
                raise RuntimeError("Required MESSAGE environment variable not set in Kubernetes environment")
        
        self._config_initialized = True
    
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
    
    @field_validator('app_port', 'log_server_port', 'ping_pong_service_port')
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
    
    def _read_config_file_startup(self) -> Optional[str]:
        """
        Read the content of the configuration file at startup.
        Returns None if file doesn't exist or can't be read.
        Handles all deployment scenarios gracefully.
        """
        try:
            with open(self.config_file_path, 'r', encoding='utf-8') as f:
                content = f.read().strip()
                return content if content else None
        except FileNotFoundError:
            # File doesn't exist - normal in local dev or Docker without ConfigMap
            return None
        except PermissionError:
            # No permission to read file
            return None
        except Exception:
            # Any other error reading file
            return None

    def read_config_file(self) -> Optional[str]:
        """
        Read the content of the configuration file.
        Returns None if file doesn't exist or can't be read.
        Handles all deployment scenarios gracefully.
        
        DEPRECATED: Use get_config_info() instead, which uses cached startup values.
        """
        return self._read_config_file_startup()
    
    def get_config_info(self) -> tuple[Optional[str], Optional[str]]:
        """
        Get both configuration pieces: file content and environment variable.
        Returns tuple of (file_content, env_message).
        Uses values cached at startup for consistency.
        """
        if not self._config_initialized:
            self.initialize_config()
        return self._config_file_content, self.message


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
    print(f"  Config file path: {settings.config_file_path}")
    print(f"  MESSAGE env var: {settings.message}")
    
    # Test config reading
    file_content, env_message = settings.get_config_info()
    print(f"  Config file content: {file_content}")
    print(f"  Config env message: {env_message}")
