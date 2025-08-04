#!/bin/bash

# Unified build script for both ping-pong and log-output applications
# Usage: ./build-apps.sh [tag]
# Example: ./build-apps.sh v1.0

set -e  # Exit on any error

TAG=${1:-latest}

echo "🚀 Building both ping-pong and log-output applications with tag: $TAG"
echo ""

# Build log-output app
echo "📦 Building log-output application..."
echo "🔨 Building log-output-app:$TAG from log_output/Dockerfile..."
docker build -f log_output/Dockerfile -t log-output-app:$TAG log_output/

if [ $? -eq 0 ]; then
    echo "✅ Successfully built log-output-app:$TAG"
else
    echo "❌ Failed to build log-output-app image"
    exit 1
fi

echo ""

# Build ping-pong app
echo "📦 Building ping-pong application..."
echo "🔨 Building ping-pong-app:$TAG from ping-pong/Dockerfile..."
docker build -f ping-pong/Dockerfile -t ping-pong-app:$TAG ping-pong/

if [ $? -eq 0 ]; then
    echo "✅ Successfully built ping-pong-app:$TAG"
else
    echo "❌ Failed to build ping-pong-app image"
    exit 1
fi

echo ""
echo "🎉 All images built successfully with tag: $TAG"
echo ""
echo "Built images:"
echo "  - log-output-app:$TAG"
echo "  - ping-pong-app:$TAG"
echo ""
echo "To import into k3d cluster, run:"
echo "  k3d image import log-output-app:$TAG -c <your-cluster-name>"
echo "  k3d image import ping-pong-app:$TAG -c <your-cluster-name>"
echo ""
echo "To push to registry (if needed):"
echo "  docker push log-output-app:$TAG"
echo "  docker push ping-pong-app:$TAG"
