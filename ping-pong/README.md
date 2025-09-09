# Ping-Pong Service

Simple HTTP service that responds with "pong N" and increments counter. The counter is persisted to a PostgreSQL database for reliable storage. **Features canary deployment with Azure Prometheus monitoring via sidecar authentication proxy.**

## Features

- Responds with "pong N" where N is an incrementing counter stored in PostgreSQL
- Database-backed persistence for reliable counter storage
- **Smart database reconnection**: Automatically retries database connections when dependencies become available
- Configurable via environment variables using Pydantic settings
- Health check and readiness endpoints for monitoring with dependency cascade
- **Sidecar Authentication Proxy**: Azure Prometheus integration for automated canary analysis

## Kubernetes Deployment

### SOPS Secret Management

Secrets are encrypted with SOPS and stored in Git. Apply them using:

```bash
# Apply SOPS-encrypted secrets
sops --decrypt manifests/ping-pong/azure-workload-identity-secret.enc.yaml | kubectl apply -f -
sops --decrypt manifests/ping-pong/ping-pong-secret.enc.yaml | kubectl apply -f -
sops --decrypt manifests/ping-pong/postgres-secret.enc.yaml | kubectl apply -f -
```

### Canary Deployment

Deploy using Argo Rollouts with automated Azure Prometheus analysis:

```bash
# Apply manifests
kubectl apply -f manifests/ping-pong/prometheus-auth-serviceaccount.yaml
kubectl apply -f manifests/ping-pong/ping-pong-service.yaml
kubectl apply -f manifests/ping-pong/ping-pong-analysis-template-sidecar.yaml
kubectl apply -f manifests/ping-pong/ping-pong-rollout.yaml

# Trigger deployment
kubectl argo rollouts set image ping-pong-app ping-pong=kubemooc.azurecr.io/ping-pong-app:4.4.3 -n exercises
kubectl argo rollouts get rollout ping-pong-app -n exercises --watch
```

**Canary Flow**: 25% → Analysis → 50% → Analysis → 75% → Analysis → 100%
**Automated Rollback**: If CPU metrics exceed thresholds

### Container Architecture

**Multi-container pod** with main application and authentication sidecar:
- **ping-pong** (port 3000): Core service with database integration  
- **prometheus-auth-sidecar** (port 8080): Azure authentication proxy for analysis queries
- **Secrets**: Database credentials via SOPS-encrypted `ping-pong-app-secret`

### Sidecar Container: Prometheus Authentication Proxy  
- **Image**: `kubemooc.azurecr.io/auth-proxy-sidecar:latest`
- **Port**: 8080 (authentication proxy)
- **Responsibilities**: Azure authentication, Prometheus API proxy
- **Secrets**: Azure credentials via SOPS-encrypted `azure-workload-identity-secret`

### Network Communication
- **Internal**: Containers communicate via localhost within pod
- **External**: AnalysisRun controllers access sidecar via `ping-pong-svc:8080`
- **Service Discovery**: Kubernetes service exposes both app (2507) and auth-proxy (8080) ports

## Local Development

See [LOCAL_DEVELOPMENT.md](LOCAL_DEVELOPMENT.md) for detailed instructions on:

1. **Running server locally with containerized database** - Best for development and debugging
2. **Running everything in Docker Compose** - Full containerized environment

Quick start:
```bash
# Install dependencies
uv sync

# Option 1: Local server + containerized DB
docker run -d --name postgres-local -e POSTGRES_DB=pingpong -e POSTGRES_USER=postgres -e POSTGRES_PASSWORD=postgres -p 5432:5432 postgres:15-alpine
uv run python main.py

# Option 2: Everything in containers
docker-compose up --build
```

## Configuration

The application uses Pydantic settings with environment variable support:

- `PING_PONG_APP_PORT` - Application port (default: 3000)
- `PING_PONG_LOG_LEVEL` - Logging level (default: "INFO")
- `PING_PONG_DB_HOST` - Database host (default: "localhost")
- `PING_PONG_DB_PORT` - Database port (default: 5432)
- `PING_PONG_DB_NAME` - Database name (default: "pingpong")
- `PING_PONG_DB_USER` - Database user (default: "postgres")
- `PING_PONG_DB_PASSWORD` - Database password (default: "postgres")

## Docker

```bash
# Build image
docker build -t ping-pong .

# Run container with shared volume
docker run -p 3000:3000 -v shared_data:/shared ping-pong
```

## Docker Compose Integration

For testing with log-output service integration:

```bash
# Run both ping-pong and log-output services
docker-compose up --build

# Test ping-pong service
curl http://localhost:3000/pingpong

# Check log-output integration
curl http://localhost:8000/
```

The docker-compose setup demonstrates persistent volume sharing between services.


## Usage

- `GET /pingpong` - Returns pong with incrementing counter (persists to database)
- `GET /health` - Health check endpoint (always returns 200 OK)
- `GET /health/ready` - Readiness check endpoint (returns 503 if database unavailable)

## Database Resilience Architecture

The service implements smart database reconnection for Kubernetes readiness probes:

### Readiness Probe Behavior
- **Database unavailable**: Service stays running but reports "not ready" (0/1 Ready)
- **Database becomes available**: Service automatically reconnects and becomes ready (1/1 Running)
- **No manual intervention required**: Readiness probes continuously retry every 10 seconds

### Implementation Details
- Each database query (`get_counter`, `increment_counter`) checks if connection pool exists
- If pool is uninitialized, attempts reconnection via `await self.initialize()`
- On connection failures, pool is reset to `None` to force retry on next probe
- Graceful error handling prevents application crashes during database outages

This design enables proper Kubernetes dependency management where services become ready only when their dependencies are available.

## Shared Volume Integration

The service writes the current counter value to a shared file for communication with other services:

- Counter file: `{shared_volume_path}/ping_pong_counter.txt`
- File contains the current counter value as plain text
- Other services can read this file to access the ping-pong count

## Build Script

Use the provided build script for convenience:

```bash
# Make the script executable (only needed once)
chmod +x build.sh

# Build the image
./build.sh ping-pong-app:v1.0
```

## Kubernetes

Deploy using manifests in `manifests/` directory. This exercise demonstrates persistent volume sharing between ping-pong and log-output services.

### Prerequisites

1. A PersistentVolume and PersistentVolumeClaim for shared data
2. Volume mount configuration in deployment manifest
3. Environment variables for shared volume path
4. Proper permissions on the shared volume (handled by initContainer)

### Deployment Steps

```bash
# 1. Create the persistent volume directory on k3d node
docker exec k3d-k3s-default-agent-0 mkdir -p /tmp/kube

# 2. Apply PersistentVolume
kubectl apply -f manifests/ping-pong-pv.yaml

# 3. Apply PersistentVolumeClaim
kubectl apply -f manifests/ping-pong-pvc.yaml

# 4. Apply deployment (includes both ping-pong and log-output containers)
kubectl apply -f manifests/deployment.yaml

# 5. Apply services
kubectl apply -f manifests/ping-pong-service.yaml
kubectl apply -f manifests/log-output-service.yaml

# 6. Apply ingress
kubectl apply -f manifests/ingress.yaml
```

### Verification

```bash
# Check all resources
kubectl get pv,pvc,pods,svc,ingress

# Test ping-pong endpoint
curl http://localhost:8080/pingpong

# Test log-output endpoint
curl http://localhost:8080/

# Verify shared counter file
kubectl exec -it <pod-name> -c ping-pong -- cat /shared/ping_pong_counter.txt
```

### Architecture Notes

- **Database resilience**: Implements smart reconnection for readiness probe dependency management
- **Readiness cascade**: Database → Ping-pong → Log-output dependency chain with automatic recovery
- **No crash on startup**: Applications stay running even when dependencies are unavailable
- **Kubernetes-native**: Proper use of readiness probes for orchestrated service startup
- **Persistent storage**: Counter persists across pod restarts via PostgreSQL database

Example environment variables for Kubernetes:
```yaml
env:
- name: PING_PONG_SHARED_VOLUME_PATH
  value: "/shared"
- name: LOG_APP_SHARED_VOLUME_PATH
  value: "/shared"
```