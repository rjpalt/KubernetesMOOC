# Auth Proxy Sidecar

Azure Prometheus Authentication Sidecar for Kubernetes deployments.

## Overview

This sidecar container handles Azure AD authentication for Prometheus queries, automatically managing token refresh and providing a simple proxy interface.

## Features

- **Automatic Token Management**: Acquires and refreshes Azure AD tokens every 30 minutes
- **Prometheus Query Proxy**: Forwards authenticated requests to Azure Monitor Prometheus
- **Health Monitoring**: Provides detailed health status including token validity
- **Fail-Fast Design**: Exits immediately if Azure authentication cannot be established
- **Comprehensive Logging**: Detailed logging for debugging authentication issues

## Endpoints

### `/health` - Health Check
Returns the current status of the authentication sidecar.

**Response Example:**
```json
{
  "status": "healthy",
  "token_valid": true,
  "expires_at": "2025-09-07T15:30:00Z",
  "time_to_expiry": "0:29:45.123456",
  "timestamp": "2025-09-07T15:00:15Z"
}
```

### `/api/v1/query` - Prometheus Query Proxy
Proxies Prometheus queries to Azure Monitor with authentication.

**Request:**
- Method: `POST`
- Content-Type: `application/x-www-form-urlencoded`
- Body: `query=<prometheus_query>`

**Example:**
```bash
curl -X POST http://localhost:8080/api/v1/query \
  -d "query=up"
```

## Development

### Prerequisites
- Python 3.11+
- uv package manager
- Azure credentials configured (DefaultAzureCredential)

### Setup
```bash
# Install dependencies
uv sync --group dev

# Run application
uv run python app.py
```

### Code Quality
```bash
# Run linting
uv run ruff check .

# Format code
uv run ruff format .
```

### Testing
```bash
# Run tests
uv run pytest

# Run tests with coverage
uv run pytest --cov=app
```

### Docker Build

#### Local Development (Multi-Architecture)
```bash
# Build for both ARM64 (Apple Silicon) and AMD64 (AKS)
./build.sh

# Test the local ARM64 build
./build.sh --test

# Run locally on Apple Silicon
docker run -p 8080:8080 auth-proxy-sidecar:latest-arm64
```

#### Production Deployment to AKS
```bash
# Build and push to Azure Container Registry
export REGISTRY=kubemooc.azurecr.io
export IMAGE_NAME=auth-proxy-sidecar
export TAG=v1.0.0
./build-and-push.sh

# Or build AMD64 only for AKS
docker build --platform linux/amd64 -t auth-proxy-sidecar:amd64 .
```

**Prerequisites:**
- Azure CLI installed and authenticated (`az login`)
- Access to kubemooc.azurecr.io registry
- Docker buildx for multi-architecture builds

**Architecture Notes:**
- Local development on Apple Silicon requires ARM64 images
- AKS clusters use AMD64 architecture
- The build scripts handle both architectures automatically

## Deployment

The sidecar is designed to run alongside applications that need authenticated access to Azure Monitor Prometheus. It handles all authentication complexity and provides a simple HTTP interface.

### Kubernetes Sidecar Pattern
```yaml
spec:
  containers:
  - name: main-app
    image: your-app:latest
  - name: auth-proxy
    image: auth-proxy-sidecar:latest
    ports:
    - containerPort: 8080
```

## Error Handling

The sidecar follows a fail-fast approach:
- **Startup**: Exits immediately if initial Azure authentication fails
- **Runtime**: Provides detailed error responses for debugging
- **Health**: Returns 503 status when authentication is unavailable

## Monitoring

Monitor the sidecar using:
- Health endpoint for readiness/liveness probes
- Application logs for authentication events
- Container metrics for resource usage

## Security

- Uses DefaultAzureCredential for secure authentication
- No credentials stored in application code
- Automatic token refresh prevents long-lived tokens
- Detailed logging for security auditing
