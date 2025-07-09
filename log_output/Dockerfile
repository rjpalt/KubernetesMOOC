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

# Copy the application
COPY app.py .

# Create non-root user for security
RUN groupadd -r appuser && useradd -r -g appuser -m appuser

# Change /app folder ownership to appuser instead of root
RUN chown -R appuser:appuser /app

# Create a cache directory for appuser (uv requires it for dependency installation)
RUN mkdir -p /home/appuser/.cache && chown -R appuser:appuser /home/appuser/.cache

# Run everything as appuser from this point
USER appuser

# Set environment variable to force unbuffered output
ENV PYTHONUNBUFFERED=1

# Set default PORT if not provided
ENV PORT=8000

# Expose port 8000
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:$PORT/health || exit 1

# Run the application using uv
CMD ["uv", "run", "python", "app.py"]
