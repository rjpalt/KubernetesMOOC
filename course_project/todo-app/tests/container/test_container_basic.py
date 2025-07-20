"""
Basic container validation tests.
These tests verify that the application starts correctly in a container environment.
"""

import subprocess
import pytest
import time
import httpx
from typing import Generator


def test_docker_build_succeeds():
    """Test that the Docker image builds successfully."""
    result = subprocess.run(
        ["docker", "build", "-t", "todo-app:test", "."],
        capture_output=True,
        text=True,
        timeout=300  # 5 minutes timeout for build
    )
    
    assert result.returncode == 0, f"Docker build failed: {result.stderr}"
    # Docker buildx outputs to stderr, not stdout
    output = result.stdout + result.stderr
    assert ("Successfully tagged todo-app:test" in output or 
            "Successfully built" in output or 
            "naming to docker.io/library/todo-app:test" in output), f"Build success not detected in output: {output[:500]}"


def test_container_starts_and_responds():
    """Test that the container starts and responds to health checks."""
    container_name = "todo-test-basic"
    
    # Clean up any existing container
    subprocess.run(["docker", "rm", "-f", container_name], capture_output=True)
    
    try:
        # Start container (map 8000 to 8081 to avoid conflicts)
        start_result = subprocess.run(
            ["docker", "run", "-d", "--name", container_name, "-p", "8081:8000", "todo-app:test"],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        assert start_result.returncode == 0, f"Failed to start container: {start_result.stderr}"
        
        # Wait for container to be ready
        time.sleep(15)
        
        # Check container is running
        ps_result = subprocess.run(
            ["docker", "ps", "--filter", f"name={container_name}", "--format", "{{.Status}}"],
            capture_output=True,
            text=True
        )
        
        assert "Up" in ps_result.stdout, f"Container is not running: {ps_result.stdout}"
        
        # Try to connect to health endpoint
        try:
            with httpx.Client() as client:
                response = client.get("http://localhost:8081/health", timeout=10)
                assert response.status_code == 200, f"Health check failed with status {response.status_code}"
                
                health_data = response.json()
                assert health_data.get("status") == "healthy", f"Unexpected health status: {health_data}"
            
        except httpx.RequestError as e:
            pytest.fail(f"Failed to connect to container health endpoint: {e}")
    
    finally:
        # Cleanup
        subprocess.run(["docker", "stop", container_name], capture_output=True)
        subprocess.run(["docker", "rm", container_name], capture_output=True)


def test_container_environment_setup():
    """Test that the container has the correct environment setup."""
    result = subprocess.run(
        ["docker", "run", "--rm", "todo-app:test", "python", "--version"],
        capture_output=True,
        text=True,
        timeout=30
    )
    
    assert result.returncode == 0, f"Failed to check Python version: {result.stderr}"
    assert "Python 3.13" in result.stdout, f"Expected Python 3.13, got: {result.stdout}"


def test_container_has_required_dependencies():
    """Test that the container has all required dependencies installed."""
    result = subprocess.run(
        ["docker", "run", "--rm", "todo-app:test", "uv", "run", "python", "-c", 
         "import fastapi, uvicorn, httpx, aiofiles, PIL, jinja2, pydantic; print('All dependencies available')"],
        capture_output=True,
        text=True,
        timeout=30
    )
    
    assert result.returncode == 0, f"Missing dependencies: {result.stderr}"
    assert "All dependencies available" in result.stdout
