FROM python:3.13-slim

# Set working directory
WORKDIR /app

# Copy the application
COPY app.py .

# Make the script executable
RUN chmod +x app.py

# Set environment variable to force unbuffered output (For debugging purposes)
ENV PYTHONUNBUFFERED=1

# Run the application
CMD ["python3", "app.py"]
