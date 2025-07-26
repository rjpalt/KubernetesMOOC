FROM python:3.13-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends curl \
    && rm -rf /var/lib/apt/lists/*

# Install uv for dependency management
RUN pip install --no-cache-dir uv

# Copy dependency files first (for better Docker layer caching)
COPY pyproject.toml uv.lock ./

# Install dependencies
RUN uv sync --frozen --no-dev

# Copy the application files
COPY main.py settings.py database.py ./

# Create shared directory mount point BEFORE switching to non-root user
RUN mkdir -p /shared

# Create non-root user for security
RUN groupadd -r appuser && useradd -r -g appuser -m appuser

# Change ownership of /app, /shared, and cache directory to appuser
RUN chown -R appuser:appuser /app /shared
RUN mkdir -p /home/appuser/.cache && chown -R appuser:appuser /home/appuser/.cache

# Run everything as appuser from this point
USER appuser

# Set environment variable to force unbuffered output
ENV PYTHONUNBUFFERED=1

# Set default PORT to match our settings (3000)
ENV PORT=3000

# Expose port 3000
EXPOSE 3000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:$PORT/health/ready || exit 1

# Run the application using uv
CMD ["uv", "run", "python", "main.py"]
