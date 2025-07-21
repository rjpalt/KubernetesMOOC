FROM python:3.13-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends curl \
    && rm -rf /var/lib/apt/lists/*

# Install uv for faster dependency resolution
RUN pip install --no-cache-dir uv

# Copy dependency files
COPY pyproject.toml uv.lock ./

# Install dependencies
RUN uv sync --frozen --no-dev

# Copy application code
COPY src/ ./src/

## Create a new system group and a user appuser (-r for system account)
RUN groupadd -r appuser && useradd -r -g appuser -m appuser

## Change /app folder ownership to appuser instead of root
## App can now write to /app without root privileges (including images directory)
RUN chown -R appuser:appuser /app

## Create a cache directory for appuser (uv requires it for dependency installation)
RUN mkdir -p /home/appuser/.cache && chown -R appuser:appuser /home/appuser/.cache

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
CMD ["uv", "run", "python", "-m", "src.main"]
