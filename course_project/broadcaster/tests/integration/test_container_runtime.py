"""Test container build and runtime behavior."""

import subprocess
import time
from pathlib import Path

import docker
import pytest
import requests


class TestContainerBuild:
    """Test broadcaster container build and execution."""

    def test_container_builds_successfully(self):
        """Test that the container builds without errors."""
        result = subprocess.run(
            ["docker", "build", "-t", "broadcaster:test", "."],
            capture_output=True,
            text=True,
            cwd=Path(__file__).parent.parent.parent,
        )
        assert result.returncode == 0, f"Container build failed: {result.stderr}"
        # Docker output can appear in either stdout or stderr depending on version
        combined_output = result.stdout + result.stderr
        # Modern Docker may use different tagging output format
        assert (
            "Successfully tagged broadcaster:test" in combined_output
            or "naming to docker.io/library/broadcaster:test" in combined_output
        )

    def test_dockerfile_security_practices(self):
        """Test that Dockerfile follows security best practices."""
        dockerfile_path = Path(__file__).parent.parent.parent / "Dockerfile"
        dockerfile_content = dockerfile_path.read_text()

        # Check for non-root user
        assert "USER 1001" in dockerfile_content
        assert "adduser" in dockerfile_content or "useradd" in dockerfile_content

        # Check for health check
        assert "HEALTHCHECK" in dockerfile_content

        # Check for proper ports
        assert "EXPOSE 8002 7777" in dockerfile_content

    @pytest.mark.slow
    def test_container_starts_and_responds(self):
        """Test that the container starts and health endpoints respond."""
        client = docker.from_env()

        # Build container
        image, _ = client.images.build(path=str(Path(__file__).parent.parent.parent), tag="broadcaster:test", rm=True)

        # Start container with test webhook
        container = client.containers.run(
            "broadcaster:test",
            ports={"8002/tcp": 8002, "7777/tcp": 7777},
            environment={"WEBHOOK_URL": "https://httpbin.org/post"},
            detach=True,
            remove=True,
        )

        try:
            # Wait for startup
            time.sleep(15)

            # Test health endpoint
            response = requests.get("http://localhost:8002/health", timeout=10)
            assert response.status_code == 200
            health_data = response.json()
            assert "status" in health_data

            # Test metrics endpoint
            response = requests.get("http://localhost:8002/metrics", timeout=10)
            assert response.status_code == 200
            metrics_text = response.text
            assert "broadcaster_" in metrics_text

        finally:
            container.stop()
