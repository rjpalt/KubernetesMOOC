#!/bin/bash

# Check if tag argument is provided
if [ $# -eq 0 ]; then
    echo "Usage: $0 <image-tag>"
    echo "Example: $0 log-output-app:v1.0"
    exit 1
fi

IMAGE_TAG="$1"

echo "Building Docker image with tag: $IMAGE_TAG"

# Build the Docker image
docker build -t "$IMAGE_TAG" .

# Check if build was successful
if [ $? -eq 0 ]; then
    echo "✅ Successfully built image: $IMAGE_TAG"
    echo "To run: docker run -p 8000:8000 $IMAGE_TAG"
    echo "With custom port: docker run -p 8080:8080 -e PORT=8080 $IMAGE_TAG"
else
    echo "❌ Failed to build image"
    exit 1
fi
