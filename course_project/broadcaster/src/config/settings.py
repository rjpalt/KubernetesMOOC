"""Configuration settings for broadcaster service."""

import os
from typing import Literal

from pydantic import Field, computed_field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings with environment-aware defaults."""

    # Environment Detection
    environment: Literal["local", "development", "production"] = Field(
        default="local", description="Deployment environment"
    )

    # Server Configuration
    host: str = Field(default="0.0.0.0", description="Server host")
    port: int = Field(default=8002, description="Server port")
    log_level: str = Field(default="INFO", description="Log level")

    # NATS Configuration (Environment-Aware)
    nats_url: str = Field(default="", description="NATS server URL")
    nats_topic: str = Field(default="todos.events", description="NATS topic to subscribe")
    nats_queue_group: str = Field(default="broadcaster-workers", description="NATS queue group")
    nats_connect_timeout: int = Field(default=10, description="NATS connection timeout")
    nats_max_reconnect_attempts: int = Field(default=60, description="Max reconnection attempts")

    # Webhook Configuration
    webhook_url: str = Field(..., description="Webhook URL for HTTP POST (required)")
    webhook_timeout: int = Field(default=30, description="Webhook request timeout")
    webhook_retry_attempts: int = Field(default=3, description="Webhook retry attempts")

    # Metrics Configuration
    metrics_port: int = Field(default=7777, description="Prometheus metrics port")

    # Kubernetes Detection
    kubernetes_namespace: str | None = Field(default=None, description="Current Kubernetes namespace (auto-detected)")

    model_config = {"env_file": ".env", "case_sensitive": False}

    @computed_field
    @property
    def effective_nats_url(self) -> str:
        """Get environment-appropriate NATS URL."""
        if self.nats_url:
            return self.nats_url

        # Auto-detect environment if not explicitly set
        # Check if running in Kubernetes
        if os.path.exists("/var/run/secrets/kubernetes.io/serviceaccount"):
            # Kubernetes environment - use service DNS
            return "nats://nats:4222"
        elif os.environ.get("DOCKER_CONTAINER"):
            # Docker Compose environment
            return "nats://nats:4222"
        else:
            # Local development - might need port forwarding
            return "nats://localhost:4222"

    @computed_field
    @property
    def current_namespace(self) -> str | None:
        """Auto-detect current Kubernetes namespace."""
        if self.kubernetes_namespace:
            return self.kubernetes_namespace

        # Try to read from Kubernetes service account
        namespace_file = "/var/run/secrets/kubernetes.io/serviceaccount/namespace"
        if os.path.exists(namespace_file):
            try:
                with open(namespace_file) as f:
                    return f.read().strip()
            except Exception:
                pass

        # Try environment variable (set by Kubernetes downward API)
        return os.environ.get("POD_NAMESPACE")

    @computed_field
    @property
    def deployment_environment(self) -> str:
        """Determine deployment environment from namespace or explicit setting."""
        if self.environment != "local":
            return self.environment

        namespace = self.current_namespace
        if namespace:
            if namespace.startswith("feature-"):
                return "development"
            elif namespace == "project":
                return "production"
            elif namespace in ["default", "kube-system"]:
                return "production"  # Conservative default

        return "local"

    @computed_field
    @property
    def is_kubernetes(self) -> bool:
        """Check if running in Kubernetes."""
        return os.path.exists("/var/run/secrets/kubernetes.io/serviceaccount")

    @computed_field
    @property
    def debug_mode(self) -> bool:
        """Enable debug mode in development environments."""
        env = self.deployment_environment
        return env in ["local", "development"] or self.log_level == "DEBUG"


settings = Settings()
