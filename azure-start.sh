#!/bin/bash
set -e # Exit on any error

# --- Configuration ---
RESOURCE_GROUP="kubernetes-learning"
AKS_CLUSTER_NAME="kube-mooc"

echo "--- Starting Azure Kubernetes Service ---"
az aks start --name $AKS_CLUSTER_NAME --resource-group $RESOURCE_GROUP

echo "--- Verifying Cluster Status ---"
# Get the current power state code from Azure
STATUS=$(az aks show --name $AKS_CLUSTER_NAME --resource-group $RESOURCE_GROUP --query "powerState.code" -o tsv)

# Check if the status is "Running"
if [ "$STATUS" == "Running" ]; then
    echo "✅ Verification successful: Cluster is running."
else
    echo "⚠️ Verification failed: Cluster status is '$STATUS'."
    exit 1
fi