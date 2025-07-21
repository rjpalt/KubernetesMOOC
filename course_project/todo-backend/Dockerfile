FROM python:3.13-slim

# Set working directory
WORKDIR /app

# Install uv for faster dependency resolution
RUN pip install uv

# Copy dependency files
COPY pyproject.toml ./
COPY uv.lock* ./

# Install dependencies
RUN uv sync --frozen

# Create non-root user
RUN useradd -m -u 1001 appuser
RUN chown -R appuser:appuser /app
USER appuser

# Copy application code
COPY --chown=appuser:appuser . .

# Expose port
EXPOSE 8000

# Run the application
CMD ["uv", "run", "uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
