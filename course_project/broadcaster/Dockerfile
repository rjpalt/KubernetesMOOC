# Multi-stage build for broadcaster service
FROM python:3.11-alpine AS builder

# Install uv for fast dependency management
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /usr/local/bin/

# Set up build environment
WORKDIR /app
COPY pyproject.toml uv.lock ./

# Install dependencies
RUN uv sync --frozen --no-dev

# Production stage
FROM python:3.11-alpine AS runtime

# Install runtime dependencies
RUN apk add --no-cache curl

# Create non-root user (matching project pattern)
RUN addgroup -g 1001 appuser && \
    adduser -u 1001 -G appuser -D -h /app appuser

# Copy uv and virtual environment from builder
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /usr/local/bin/
COPY --from=builder --chown=1001:1001 /app/.venv /app/.venv

# Set up application directory
WORKDIR /app
RUN chown appuser:appuser /app

# Copy application code
COPY --chown=1001:1001 src/ ./src/

# Switch to non-root user
USER 1001

# Create writable directories for read-only filesystem
RUN mkdir -p /tmp/broadcaster /var/tmp/broadcaster

# Environment configuration
ENV PATH="/app/.venv/bin:$PATH"
ENV PYTHONPATH="/app"
ENV PYTHONUNBUFFERED=1

# Expose ports (main service and metrics)
EXPOSE 8002 7777

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8002/health || exit 1

# Run application
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8002"]
