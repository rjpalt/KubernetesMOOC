# Ping-Pong Service

Simple HTTP service that responds with "pong N" and increments counter.

## Local Development


```bash
# Install dependencies
uv sync

# Run locally
uv run main.py
```

## Docker


```bash
# Build image
docker build -t ping-pong .

# Run container
docker run -p 8000:8000 ping-pong
```


## Usage

- `GET /pingpong` - Returns pong with incrementing counter
- `GET /health` - Health check endpoint

## Build Script

Use the provided build script for convenience:

```bash
# Make the script executable (only needed once)
chmod +x build.sh

# Build the image
./build.sh ping-pong-app:v1.0
```

## Kubernetes

Deploy using manifests in `manifests/` directory.