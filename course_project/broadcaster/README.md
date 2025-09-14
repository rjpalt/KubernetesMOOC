# Broadcaster Service

A P## Configuration

The broadcaster service uses environment-aware configuration that automatically adapts based on the deployment context.

### Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `WEBHOOK_URL` | **Yes** | - | HTTP endpoint to receive webhook calls |
| `NATS_URL` | No | *Auto-detected* | NATS server connection URL |
| `NATS_TOPIC` | No | `todos.events` | NATS topic to subscribe to |
| `NATS_QUEUE_GROUP` | No | `broadcaster-workers` | Queue group for load balancing |
| `WEBHOOK_TIMEOUT` | No | `30` | Webhook request timeout (seconds) |
| `WEBHOOK_RETRY_ATTEMPTS` | No | `3` | Number of retry attempts for failed webhooks |
| `LOG_LEVEL` | No | `INFO` | Logging level (DEBUG, INFO, WARNING, ERROR) |
| `ENVIRONMENT` | No | `local` | Deployment environment (local, development, production) |

### Environment Detection

The service automatically detects the deployment environment and configures itself accordingly:

#### **Local Development**
- **Detection**: No Kubernetes service account present
- **NATS URL**: `nats://localhost:4222` (assumes port forwarding)
- **Debug Mode**: Enabled
- **Logging**: Verbose output

#### **Kubernetes Development** (feature-ex-c4-e6 namespace)
- **Detection**: Kubernetes namespace starting with `feature-`
- **NATS URL**: `nats://nats:4222` (service DNS)
- **Debug Mode**: Enabled
- **Logging**: Detailed for troubleshooting

#### **Kubernetes Production** (project namespace)
- **Detection**: `project` namespace or system namespaces
- **NATS URL**: `nats://nats:4222` (service DNS)
- **Debug Mode**: Disabled
- **Logging**: Production-level only

### Manual Environment Override

Override auto-detection by setting the `ENVIRONMENT` variable:

```bash
# Force production mode locally
ENVIRONMENT=production WEBHOOK_URL=https://api.example.com/webhook ./run.sh

# Force development mode in production
kubectl set env deployment/broadcaster ENVIRONMENT=development
```service that subscribes to NATS messages and forwards them via HTTP webhooks.

## Overview

The Broadcaster Service acts as a bridge between NATS messaging and HTTP webhooks, allowing NATS messages to be forwarded to external HTTP endpoints. It's designed for high availability with queue groups for load balancing and graceful error handling.

## Features

- **NATS Integration**: Subscribes to NATS topics with queue groups for load balancing
- **HTTP Webhooks**: Forwards messages to configurable HTTP endpoints with retry logic
- **Prometheus Metrics**: Exposes custom metrics for monitoring
- **Health Checks**: Kubernetes-ready health and readiness probes
- **Graceful Degradation**: Starts even when NATS is unavailable
- **Container Ready**: Docker container with non-root user and health checks

## Architecture

- **FastAPI Application**: Main HTTP server on port 8002
- **Background NATS Consumer**: Async subscription to NATS topics
- **Webhook Client**: HTTP client for forwarding messages
- **Prometheus Metrics**: Custom metrics on port 7777

## Configuration

The service is configured via environment variables:

### Required

- `WEBHOOK_URL`: HTTP endpoint for webhook delivery (required)

### Optional

- `HOST`: Server host (default: 0.0.0.0)
- `PORT`: Server port (default: 8002)
- `LOG_LEVEL`: Log level (default: INFO)
- `NATS_URL`: NATS server URL (default: nats://nats:4222)
- `NATS_TOPIC`: NATS topic to subscribe (default: todos.events)
- `NATS_QUEUE_GROUP`: Queue group name (default: broadcaster-workers)
- `NATS_CONNECT_TIMEOUT`: Connection timeout (default: 10)
- `NATS_MAX_RECONNECT_ATTEMPTS`: Max reconnect attempts (default: 60)
- `WEBHOOK_TIMEOUT`: Webhook request timeout (default: 30)
- `WEBHOOK_RETRY_ATTEMPTS`: Webhook retry attempts (default: 3)
- `METRICS_PORT`: Prometheus metrics port (default: 7777)

## Running the Service

### Local Development

```bash
# Set required environment variable
export WEBHOOK_URL=http://localhost:8080/webhook

# Install dependencies
uv sync

# Run the service
uv run python -m src.main
```

### Docker

```bash
# Build container
docker build -t broadcaster:latest .

# Run container
docker run -p 8002:8002 -p 7777:7777 \
  -e WEBHOOK_URL=http://host.docker.internal:8080/webhook \
  broadcaster:latest
```

## API Endpoints

- `GET /health`: Basic health check
- `GET /healthz`: Kubernetes-style health check
- `GET /ready`: Readiness probe

## Metrics

Prometheus metrics available on port 7777:

- `broadcaster_messages_processed_total`: Total messages processed from NATS
- `broadcaster_webhook_requests_total`: Total webhook HTTP requests
- `broadcaster_nats_connected`: NATS connection status
- `broadcaster_message_processing_duration_seconds`: Message processing latency
- `broadcaster_webhook_request_duration_seconds`: Webhook request latency

## Message Flow

1. Service subscribes to NATS topic with queue group
2. Incoming messages are parsed as JSON
3. Messages are forwarded to webhook URL via HTTP POST
4. Metrics are updated for success/failure
5. Errors are logged but don't crash the service

## Error Handling

- **NATS Unavailable**: Service starts, retries connection in background
- **Webhook Failures**: Logged, retried according to configuration, processing continues
- **Invalid Messages**: Logged and skipped, processing continues
- **Configuration Errors**: Service fails fast on startup

## Testing

```bash
# Run unit tests
uv run pytest tests/unit/

# Run integration tests
uv run pytest tests/integration/

# Run all tests
uv run pytest
```

## Development

The service follows established project patterns:

- FastAPI structure similar to todo-backend
- HTTP client patterns from todo-app
- Container patterns with uv and non-root user
- Prometheus metrics integration

## Queue Groups

The service uses NATS queue groups (`broadcaster-workers`) for load balancing:
- Multiple replicas can run simultaneously
- Messages are distributed across replicas
- Provides horizontal scaling capability

## Dependencies

- FastAPI: Web framework
- NATS.py: NATS client
- httpx: HTTP client
- Pydantic: Configuration management
- Prometheus Client: Metrics
- uvicorn: ASGI server

## Development Workflow

### Quick Start
```bash
# Set up development environment
./dev-setup.sh

# Run quality checks
./quality.sh

# Build container locally
./build.sh

# Run locally with Docker
WEBHOOK_URL=https://httpbin.org/post docker run -p 8002:8002 -p 7777:7777 broadcaster:latest
```

### Build and Deploy
```bash
# Build and push to Azure Container Registry
./build-and-push.sh

# Deploy to feature environment
kubectl apply -k course_project/manifests/overlays/development/

# Check deployment status
kubectl get pods -n feature-ex-c4-e6 -l app=broadcaster
```

### Code Quality Standards
- **Linting**: Uses ruff for code formatting and style checks
- **Testing**: Pytest with async support and coverage reporting
- **Coverage**: Minimum 85% code coverage required
- **Type Safety**: Pydantic models for configuration validation

````
