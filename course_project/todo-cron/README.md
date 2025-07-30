# Todo Cron Service

A minimal CronJob service that creates todo items with random Wikipedia articles to read.

## Features

- Fetches random Wikipedia articles using the Special:Random endpoint
- Creates todo items via the todo-backend API
- Minimal Docker image (~20MB) based on Alpine Linux
- Configurable via environment variables
- Comprehensive error handling and logging
- Health check support

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `TODO_BACKEND_URL` | `http://localhost:8000` | URL of the todo-backend service |
| `WIKIPEDIA_RANDOM_URL` | `https://en.wikipedia.org/wiki/Special:Random` | Wikipedia random article endpoint |
| `LOG_LEVEL` | `INFO` | Logging level (DEBUG, INFO, ERROR) |

## Local Development

### Prerequisites
- bash
- curl
- Running todo-backend service

### Testing the Script
```bash
# Make script executable
chmod +x create_wikipedia_todo.sh

# Test with todo-backend running
TODO_BACKEND_URL=http://localhost:8000 LOG_LEVEL=DEBUG ./create_wikipedia_todo.sh

# Health check
TODO_BACKEND_URL=http://localhost:8000 ./create_wikipedia_todo.sh health
```

## Docker Image

The Docker image is built on Alpine Linux 3.19 for minimal size:
- Base image: ~7MB
- With curl and bash: ~20MB total
- Non-root user for security
- Single executable script

### Build
```bash
docker build -t todo-cron:latest .
```

### Run
```bash
docker run --rm \
  -e TODO_BACKEND_URL=http://host.docker.internal:8000 \
  -e LOG_LEVEL=DEBUG \
  todo-cron:latest
```

## Error Handling

The service handles various error scenarios:
- Network connectivity issues
- Backend service unavailability
- Invalid Wikipedia responses
- HTTP errors from todo-backend

All errors are logged with appropriate detail for debugging.

## Security

- Runs as non-root user (UID 1001)
- Minimal attack surface (only bash and curl)
- No sensitive data in environment variables
- Secure defaults for logging
