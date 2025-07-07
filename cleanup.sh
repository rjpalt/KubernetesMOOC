#!/bin/bash

# Cleanup script for Docker and Kubernetes resources
# This script will stop and remove all running containers, and delete the k3d cluster

set -e  # Exit on any error

echo "Starting cleanup process..."

# Delete k3d cluster FIRST (before killing Docker containers)
echo "Deleting k3d cluster..."
if k3d cluster list 2>/dev/null | grep -q "k3s-default"; then
    k3d cluster delete k3s-default
    echo "k3d cluster deleted"
elif k3d cluster list 2>/dev/null | grep -q -E "^\s*\*"; then
    # Delete the currently active cluster if no default found
    CLUSTER_NAME=$(k3d cluster list | grep -E "^\s*\*" | awk '{print $2}')
    echo "Deleting active cluster: $CLUSTER_NAME"
    k3d cluster delete "$CLUSTER_NAME"
    echo "k3d cluster deleted"
else
    echo "No k3d cluster found to delete"
fi

# Stop and remove all Docker containers
echo "Stopping all Docker containers..."
if [ "$(docker ps -q)" ]; then
    docker stop $(docker ps -q)
    echo "All containers stopped"
else
    echo "No running containers found"
fi

echo "Removing all Docker containers..."
if [ "$(docker ps -aq)" ]; then
    docker rm $(docker ps -aq)
    echo "All containers removed"
else
    echo "No containers to remove"
fi

# Remove Docker networks (except default ones)
echo "Removing custom Docker networks..."
CUSTOM_NETWORKS=$(docker network ls --filter type=custom --format "{{.Name}}" | grep -v "bridge\|host\|none" || true)
if [ -n "$CUSTOM_NETWORKS" ]; then
    echo "$CUSTOM_NETWORKS" | xargs -r docker network rm
    echo "Custom networks removed"
else
    echo "No custom networks to remove"
fi

# Skip Docker volumes cleanup (not needed for this project)
echo "Skipping Docker volumes cleanup..."

# Optional: Clean up Docker system (removes unused images, build cache, etc.)
echo "Cleaning up Docker system..."
docker system prune -f
echo "Docker system cleaned up"

echo "Cleanup complete! Your system is now clean."
echo "Note: Docker images are preserved. Use 'docker image prune -a' to remove unused images."
