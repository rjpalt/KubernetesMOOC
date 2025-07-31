# Azure AKS Version of Course Project #

## Exercise 4.1 - Setting up Azure AKS environment ##
### Azure CLI Commands ###
Installing Azure CLI on macOS:
```bash
brew install azure-cli
```

```bash
Logging in to Azure:
```bash
az login
```

Checking the account:
```bash
az account show
```

Creating a resource group
```bash
az group create --name kubernetes-learning --location northeurope
```

### Setting up AKS Cluster ###
Creating an AKS cluster:
```bash
az aks create --resource-group kubernetes-learning --name kube-mooc --node-count 1 --enable-addons monitoring --generate-ssh-keys
```

## #Connecting Kubectl to AKS ###
```bash
az aks get-credentials --resource-group kubernetes-learning --name kube-mooc
```

Checking the connection:
```bash
kubectl get nodes
```bash
kubectl get nodes
```

Switching between local context and AKS context:
```bash
kubectl config get-contexts
kubectl config use-context <context-name>
```