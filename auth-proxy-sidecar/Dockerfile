FROM python:3.11-slim

# Create non-root user
RUN groupadd --gid 1000 appuser && \
    useradd --uid 1000 --gid appuser --shell /bin/bash --create-home appuser

# Install system dependencies and uv
RUN apt-get update && \
    apt-get install -y --no-install-recommends curl && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/* && \
    pip install --no-cache-dir uv

# Set up application directory with proper ownership
WORKDIR /app
RUN chown appuser:appuser /app

# Switch to non-root user
USER appuser

# Copy requirements and install dependencies
COPY --chown=appuser:appuser requirements.txt .
RUN uv venv /home/appuser/.venv && \
    /home/appuser/.venv/bin/pip install --no-cache-dir -r requirements.txt

# Add venv to PATH
ENV PATH="/home/appuser/.venv/bin:${PATH}"

# Copy application
COPY --chown=appuser:appuser app.py .

# Expose port
EXPOSE 8080

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8080/health || exit 1

# Run application
CMD ["python", "app.py"]
