# Ping-Pong Service

Simple HTTP service that responds with "pong N" and increments counter. The counter is persisted to a shared volume for communication with other services.

## Features

- Responds with "pong N" where N is an incrementing counter
- Persists counter to shared volume for inter-service communication
- Configurable via environment variables using Pydantic settings
- Health check endpoint for monitoring

## Local Development

```bash
# Install dependencies
uv sync

# Run locally (uses ./shared directory by default)
uv run main.py
```

The application will create a `shared` directory in the project root for local testing.

## Configuration

The application uses Pydantic settings with environment variable support:

- `PING_PONG_SHARED_VOLUME_PATH` - Path to shared volume (default: "shared")
- `PING_PONG_APP_PORT` - Application port (default: 3000)
- `PING_PONG_LOG_LEVEL` - Logging level (default: "INFO")

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

- `GET /pingpong` - Returns pong with incrementing counter (persists to shared volume)
- `GET /health` - Health check endpoint

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

Deploy using manifests in `manifests/` directory. Ensure you have:

1. A PersistentVolume and PersistentVolumeClaim for shared data
2. Volume mount configuration in deployment manifest
3. Environment variables for shared volume path

Example environment variables for Kubernetes:
```yaml
env:
- name: PING_PONG_SHARED_VOLUME_PATH
  value: "/shared"
```