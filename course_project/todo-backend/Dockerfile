# Multi-stage build for smaller final image
# Stage 1: Builder stage
FROM python:3.13-alpine AS builder

# Set working directory
WORKDIR /app

# Install build dependencies (needed for some Python packages like asyncpg)
RUN apk add --no-cache --virtual .build-deps \
    gcc \
    musl-dev \
    libffi-dev \
    postgresql-dev \
    && apk add --no-cache curl

# Install uv for dependency management
RUN pip install --no-cache-dir uv

# Copy dependency files
COPY pyproject.toml uv.lock ./

# Install dependencies
RUN uv sync --frozen --no-dev

# Stage 2: Runtime stage
FROM python:3.13-alpine AS runtime

# Set working directory
WORKDIR /app

# Install only runtime dependencies
RUN apk add --no-cache curl libpq

# Copy Python virtual environment from builder stage
COPY --from=builder /app/.venv /app/.venv

# Copy application code
COPY src/ ./src/

# Create non-root user for security
RUN addgroup -g 1001 -S appuser && \
    adduser -S -D -H -u 1001 -s /sbin/nologin -G appuser appuser

# Change /app folder ownership to appuser instead of root
RUN chown -R appuser:appuser /app

# Run everything as appuser from this point
USER appuser

# Set Python path to include current directory for module imports
ENV PYTHONPATH=/app

# Expose port
EXPOSE 8001

# Set default PORT if not provided
ENV PORT=8001

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:$PORT/health || exit 1

# Run the application
CMD ["/app/.venv/bin/python", "-m", "src.main"]
