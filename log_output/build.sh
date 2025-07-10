#!/bin/bash

# Usage: ./build.sh [tag]
# Example: ./build.sh 1.10

TAG=${1:-latest}

# Build both container images for the multi-container log-output service

echo "🔨 Building log generator container..."
docker build -f Dockerfile.generator -t log-generator:$TAG .

# Check if generator build was successful
if [ $? -eq 0 ]; then
    echo "✅ Successfully built log-generator:$TAG"
else
    echo "❌ Failed to build log-generator image"
    exit 1
fi

echo ""
echo "🔨 Building log server container..."
docker build -f Dockerfile.logserver -t log-server:$TAG .

# Check if log server build was successful
if [ $? -eq 0 ]; then
    echo "✅ Successfully built log-server:$TAG"
else
    echo "❌ Failed to build log-server image"
    exit 1
fi

echo ""
echo "🎉 Both images built successfully with tag: $TAG"
echo ""
echo "To import into k3d cluster, run:"
echo "k3d image import log-generator:$TAG -c <your-cluster-name>"
echo "k3d image import log-server:$TAG -c <your-cluster-name>"
echo ""
echo "Then deploy with:"
echo "kubectl apply -f manifests/"
