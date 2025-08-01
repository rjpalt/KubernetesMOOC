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

# Setting up Azure COntainer Registry (ACR) #

Docs are here: https://learn.microsoft.com/en-us/azure/aks/cluster-container-registry-integration?tabs=azure-cli

Creating an ACR:
```bash
az acr create --resource-group kubernetes-learning --name kubemooc --sku Basic
```

## Attaching ACR to AKS ##
```bash
az aks update --name kube-mooc --resource-group kubernetes-learning --atta
ch-acr kubemooc
```

**Note: Might have to do from the GUI**

## Pushing images to ACR ##
Logging in to ACR:
```bash
az acr login --name kubemooc
```

Tagging the image:
```bash
docker tag ping-pong-app:3.1  kubemooc.azurecr.io/ping-pong-app:3.1
```

## Manifest changes for Azure AKS ##

### Postgres StatefulSet ###
Change the `storageClassName` from `local-path` to `managed-csi` because the original storage type isn't available in Azure Kubernetes Service, which causes the database pod's storage request to fail. This fix allows Kubernetes to use a valid class that automatically provisions a persistent Azure Disk, enabling the PostgreSQL pod to start correctly.

```yaml
spec:
  volumeClaimTemplates:
    - metadata:
        name: postgres-data-storage
      spec:
        accessModes: ["ReadWriteOnce"]
        storageClassName: managed-csi # Changed from local-path to managed-csi
        resources:
          requests:
            storage: 100Mi
```

Add the `subPath` property to the database's volume mount because the PostgreSQL startup script requires a completely empty directory for initialization, and the root of the persistent disk is not empty (it contains a lost+found). This one-line change in the StatefulSet manifest mounts a clean subdirectory from the disk instead, allowing the database to initialize and start successfully.
```yaml
volumeMounts:
    - name: postgres-data-storage
        mountPath: /var/lib/postgresql/data
        subPath: postgres # Added subPath to ensure a clean directory for PostgreSQL initialization
```

More info here: https://learn.microsoft.com/en-us/azure/aks/azure-csi-disk-storage-provision

# Docker changes #
The AKS does not support mac or Windows images, so we need to build the image on a Linux machine. The Dockerfile is already set up for that. Command to explicitly build the image for Linux:
```bash
docker build --platform linux/amd64 -t log-output-app:3.1 .
```

After that the app needs to be tagged:
```bash
docker tag log-output-app:3.1 kubemooc.azurecr.io/log-output-app:3.1
```

And then pushed to the ACR:
```bash
docker push kubemooc.azurecr.io/log-output-app:3.1
```

Command to check the tags of the images in the ACR:
```bash
az acr repository show-tags --name kubemooc --repository log-output-app --output table
```

### Enabling AKS App Routing for Ingress ###
To enable AKS App Routing, you need to create an App Routing add-on. This will allow you to use the Azure Application Gateway for ingress traffic management.

- AKS requires manual ingress controller setup (GKE has it built-in)
- App Routing add-on provides managed NGINX ingress controller
- Ingress resource must reference the correct ingress class to be processed
- External IP provisioning takes 2-3 minutes after proper configuration

```bash
az aks approuting enable --resource-group kubernetes-learning --name kube-mooc
```

Check app routing status:
```bash
kubectl get pods -n app-routing-system
```

Check available ingressClass:
```bash
kubectl get ingressclass
```

The deployed ingressClass has to bereferenced in the Ingress manifest. Update the Ingress manifest to use the Azure Application Gateway ingress class:
```yaml
spec:
  ingressClassName: webapprouting.kubernetes.azure.com
```
Get the ingress IP address:
```bash
kubectl get ingress
```