#!/bin/bash

# Build script for todo application Docker images
# Usage: ./build-images.sh <tag>
# Example: ./build-images.sh v1.0.0

set -e  # Exit on any error

# Check if tag parameter is provided
if [ $# -eq 0 ]; then
    echo "Warning: No tag provided"
    echo "If you continue, the tag 'latest' will be used."
    read -p "Are you sure you want to proceed? (y/N): " -n 1 -r
    echo    # Move to new line
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Build cancelled."
        echo "Usage: $0 <tag>"
        echo "Example: $0 v1.0.0"
        exit 1
    fi
    TAG="latest"
    echo "Using tag: latest"
else
    TAG=$1
fi

echo "Building Docker images with tag: $TAG"
echo "=========================================="

# Build frontend image
echo "Building frontend image (todo-app-fe:$TAG)..."
cd todo-app
if [ ! -f "Dockerfile" ]; then
    echo "Error: Dockerfile not found in todo-app directory"
    exit 1
fi

docker build -t todo-app-fe:$TAG .
if [ $? -eq 0 ]; then
    echo "✓ Frontend image built successfully: todo-app-fe:$TAG"
else
    echo "✗ Frontend image build failed"
    exit 1
fi

# Build backend image
echo ""
echo "Building backend image (todo-app-be:$TAG)..."
cd ../todo-backend
if [ ! -f "Dockerfile" ]; then
    echo "Error: Dockerfile not found in todo-backend directory"
    exit 1
fi

docker build -t todo-app-be:$TAG .
if [ $? -eq 0 ]; then
    echo "✓ Backend image built successfully: todo-app-be:$TAG"
else
    echo "✗ Backend image build failed"
    exit 1
fi

echo ""
echo "=========================================="
echo "✓ All images built successfully!"
echo "Images created:"
echo "  - todo-app-fe:$TAG"
echo "  - todo-app-be:$TAG"
echo ""
echo "You can now use these images in your Kubernetes manifests or docker-compose files."
