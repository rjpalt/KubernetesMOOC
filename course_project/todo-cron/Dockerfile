# Use Microsoft's official Azure CLI image (includes Alpine + Azure CLI pre-installed)
FROM mcr.microsoft.com/azure-cli:2.56.0

# Install additional packages needed for our scripts
RUN apk add --no-cache \
    bash \
    curl \
    postgresql-client \
    && rm -rf /var/cache/apk/*

# Create non-root user for security
RUN addgroup -g 1001 -S appgroup && \
    adduser -u 1001 -S appuser -G appgroup

# Copy both scripts
COPY create_wikipedia_todo.sh /usr/local/bin/create_wikipedia_todo.sh
COPY backup_database.sh /usr/local/bin/backup_database.sh

# Make scripts executable and set ownership
RUN chmod +x /usr/local/bin/create_wikipedia_todo.sh && \
    chmod +x /usr/local/bin/backup_database.sh && \
    chown appuser:appgroup /usr/local/bin/create_wikipedia_todo.sh && \
    chown appuser:appgroup /usr/local/bin/backup_database.sh

# Switch to non-root user
USER appuser

# Set default environment variables
ENV TODO_BACKEND_URL=http://localhost:8000
ENV WIKIPEDIA_RANDOM_URL=https://en.wikipedia.org/wiki/Special:Random
ENV LOG_LEVEL=INFO

# Default command
CMD ["/usr/local/bin/create_wikipedia_todo.sh"]
