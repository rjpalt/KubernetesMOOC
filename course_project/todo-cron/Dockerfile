# Use minimal Alpine Linux image
FROM alpine:3.19

# Install only essential packages
RUN apk add --no-cache \
    bash \
    curl \
    && rm -rf /var/cache/apk/*

# Create non-root user for security
RUN addgroup -g 1001 -S appgroup && \
    adduser -u 1001 -S appuser -G appgroup

# Copy the script
COPY create_wikipedia_todo.sh /usr/local/bin/create_wikipedia_todo.sh

# Make script executable and set ownership
RUN chmod +x /usr/local/bin/create_wikipedia_todo.sh && \
    chown appuser:appgroup /usr/local/bin/create_wikipedia_todo.sh

# Switch to non-root user
USER appuser

# Set default environment variables
ENV TODO_BACKEND_URL=http://localhost:8000
ENV WIKIPEDIA_RANDOM_URL=https://en.wikipedia.org/wiki/Special:Random
ENV LOG_LEVEL=INFO

# Default command
CMD ["/usr/local/bin/create_wikipedia_todo.sh"]
