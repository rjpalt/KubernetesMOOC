#!/bin/bash

# Build and push script for AKS deployment
set -e

# Configuration
REGISTRY=${REGISTRY:-"kubemooc.azurecr.io"}
IMAGE_NAME=${IMAGE_NAME:-"auth-proxy-sidecar"}
TAG=${TAG:-"latest"}

echo "🔄 Exporting dependencies to requirements-simple.txt..."
uv export --format requirements.txt --no-dev --no-hashes --no-header --no-annotate --no-emit-project --output-file requirements-simple.txt

echo "🔐 Logging into Azure Container Registry..."
if ! az acr login --name kubemooc; then
    echo "❌ Failed to login to Azure Container Registry"
    echo "💡 Make sure you're logged into Azure CLI with 'az login'"
    echo "💡 And have access to kubemooc.azurecr.io registry"
    exit 1
fi

echo "🏗️  Building multi-architecture image for AKS..."

# Enable buildx if not already available
docker buildx create --use --name multiarch-builder 2>/dev/null || docker buildx use multiarch-builder

# Build and push multi-architecture image
docker buildx build \
    --platform linux/amd64,linux/arm64 \
    --tag "${REGISTRY}/${IMAGE_NAME}:${TAG}" \
    --tag "${REGISTRY}/${IMAGE_NAME}:$(date +%Y%m%d-%H%M%S)" \
    --push \
    .

echo "✅ Multi-architecture image built and pushed successfully!"
echo "📦 Image: ${REGISTRY}/${IMAGE_NAME}:${TAG}"
echo ""
echo "🚀 Deploy to AKS with:"
echo "  kubectl set image deployment/auth-proxy-sidecar auth-proxy=${REGISTRY}/${IMAGE_NAME}:${TAG}"
echo ""
echo "💡 To configure:"
echo "  export REGISTRY=kubemooc.azurecr.io"
echo "  export IMAGE_NAME=auth-proxy-sidecar"
echo "  export TAG=v1.0.0"
echo ""
echo "⚠️  Prerequisites:"
echo "  - Azure CLI installed and logged in (az login)"
echo "  - Docker buildx enabled for multi-architecture builds"
