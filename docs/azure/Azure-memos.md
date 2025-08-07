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
docker tag ping-pong-app:3.1 kubemooc.azurecr.io/ping-pong-app:3.1
```

Pushing the image to ACR:
```bash
docker push kubemooc.azurecr.io/ping-pong-app:3.1
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

See Microsoft Learn documentation for details: https://learn.microsoft.com/en-us/azure/aks/app-routing

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

-----

# Deploying an Application to Azure Kubernetes Service (AKS) with Application Gateway for Containers

## Introduction

This tutorial provides a comprehensive walkthrough for deploying the Azure Application Gateway for Containers (ALB) and using it to expose a sample application via the Kubernetes Gateway API. This guide is intended for students and developers who want a detailed, step-by-step process that includes not only the "how" but also the "why" for each major action.

A quick note on complexity: if you are familiar with this process on other cloud platforms like Google Kubernetes Engine (GKE), you may notice that the Azure setup involves more explicit steps. This is because Azure's security model requires the user to manually provision and configure the underlying networking (VNet, subnets) and identity components (Managed Identity, role assignments). While this requires more initial setup, it provides granular control over your cloud architecture.

We will cover five main phases:

1.  **Preparing the AKS Cluster and Azure Identity**: We will configure the AKS cluster with the necessary features for secure communication with Azure and create a dedicated identity for the ALB controller.
2.  **Installing the ALB Controller**: We will deploy the controller software into our Kubernetes cluster using Helm.
3.  **Configuring Azure Networking**: We will prepare our virtual network by creating and delegating a dedicated subnet for the Application Gateway resources.
4.  **Provisioning the Gateway Resources**: We will instruct the controller to provision the Application Gateway infrastructure in Azure and define our traffic entry point using the Gateway API.
5.  **Deploying and Exposing a Sample Application**: We will deploy a sample application and use an `HTTPRoute` resource to make it accessible through our new gateway.

-----

## Phase 1: Cluster and Identity Preparation

In this phase, we'll set up the foundational components. We will enable Workload Identity on our AKS cluster and create a specific Managed Identity for the ALB controller to use when interacting with Azure APIs.

### 1.1. Set Environment Variables

First, define some environment variables for your resource group and AKS cluster name to make subsequent commands easier to run and read.

```bash
RESOURCE_GROUP='kubernetes-learning'
AKS_NAME='kube-mooc'
```

### 1.2. Enable AKS Features for Workload Identity

We need to enable two key features on the AKS cluster.

  * **OIDC Issuer**: OIDC (OpenID Connect) is an authentication standard. By enabling it, we turn our AKS cluster's API server into a trusted **issuer** of security tokens. It can now vouch for the identity of workloads running inside it.
  * **Workload Identity**: This is the feature that uses the OIDC tokens. It allows a Kubernetes **workload** (a pod) to exchange its native Kubernetes token for an Azure Active Directory (AD) token.

**Why we do this**: This entire mechanism enables secure, passwordless access to Azure. The pod proves its identity to Azure using a trusted token from Kubernetes, eliminating the need to store and manage sensitive credentials like client secrets inside the cluster.

```bash
az aks update -g $RESOURCE_GROUP -n $AKS_NAME --enable-oidc-issuer --enable-workload-identity --no-wait
```

### 1.3. Create a Managed Identity for the ALB Controller

A **Managed Identity** is an identity in Azure AD that is automatically managed by Azure. Think of it as a service account for an Azure resource or application. It eliminates the need for developers to manage credentials because authentication is handled seamlessly in the background. We create a User-Assigned Managed Identity that the ALB controller will use to act on our behalf.

```bash
IDENTITY_RESOURCE_NAME='azure-alb-identity'

az identity create --resource-group $RESOURCE_GROUP --name $IDENTITY_RESOURCE_NAME
```

### 1.4. Grant the Identity Initial Permissions

The ALB controller needs to be able to see the resources within the AKS node resource group. We'll grant it the `Reader` role.

**Why is the `Reader` role enough here?** Following the principle of least privilege, we grant only the permissions needed at each stage. At this point, the controller only needs to read information about the cluster's resources. We will grant more powerful permissions, like the ability to modify networking, later when they are specifically required.

First, get the resource group ID for the AKS nodes (this is auto-generated by AKS and usually prefixed with `MC_`). Then, get the Principal ID of the identity we just created.

```bash
mcResourceGroup=$(az aks show --resource-group $RESOURCE_GROUP --name $AKS_NAME --query "nodeResourceGroup" -o tsv)
mcResourceGroupId=$(az group show --name $mcResourceGroup --query id -otsv)
principalId="$(az identity show -g $RESOURCE_GROUP -n $IDENTITY_RESOURCE_NAME --query principalId -otsv)"
```

Now, create the role assignment. We use the unique ID for the "Reader" role here.

```bash
az role assignment create --assignee-object-id $principalId --assignee-principal-type ServicePrincipal --scope $mcResourceGroupId --role "acdd72a7-3385-48ef-bd42-f606fba81ae7"
```

### 1.5. Establish a Federated Credential Trust

This is the final step in setting up Workload Identity. We create a trust relationship between a specific Kubernetes Service Account (which the ALB controller will use) and the Azure Managed Identity we created. This tells Azure to trust tokens issued by our Kubernetes cluster for that service account.

```bash
AKS_OIDC_ISSUER="$(az aks show -n "$AKS_NAME" -g "$RESOURCE_GROUP" --query "oidcIssuerProfile.issuerUrl" -o tsv)"

az identity federated-credential create --name "azure-alb-identity" \
    --identity-name "$IDENTITY_RESOURCE_NAME" \
    --resource-group $RESOURCE_GROUP \
    --issuer "$AKS_OIDC_ISSUER" \
    --subject "system:serviceaccount:azure-alb-system:alb-controller-sa"
```

-----

## Phase 2: Installing the ALB Controller

With the identity and cluster prepared, we can now install the ALB controller software into our cluster. This controller is the "brain" that runs inside Kubernetes, watching for custom resources that define how traffic should be managed.

### 2.1. Set Namespace Variables

**Why do we need namespaces?** Kubernetes namespaces provide a way to create logical partitions within a cluster. They are used to organize resources, prevent naming conflicts, and apply access controls. We will create a dedicated `azure-alb-system` namespace to keep the ALB components isolated from our own applications.

```bash
HELM_NAMESPACE='azure-alb-system'
CONTROLLER_NAMESPACE='azure-alb-system'
```

### 2.2. Configure kubectl

**Why do we need to configure `kubectl` (again)?** The `kubeconfig` file on your local machine stores cluster connection details, including authentication tokens which can expire over time. Running `az aks get-credentials` ensures your connection information is fresh and your token is valid before you begin interacting with the cluster.

```bash
az aks get-credentials --resource-group $RESOURCE_GROUP --name $AKS_NAME
```

### 2.3. Create the Namespace

Create the dedicated namespace in Kubernetes where the controller and its components will reside.

```bash
kubectl create namespace $HELM_NAMESPACE
```

### 2.4. Install the Controller with Helm

We use Helm, the package manager for Kubernetes, to install the ALB controller.

**What does Helm do under the hood?** When you run `helm install`, it performs several actions:

1.  It fetches a **chart**, which is a package of pre-configured Kubernetes YAML templates for the application (in this case, ALB).
2.  It uses the values from the `--set` flags to fill in variables within those templates (e.g., injecting the Client ID of our managed identity).
3.  It renders the final YAML manifests for all the necessary Kubernetes resources, such as the `Deployment` for the controller pods, a `ServiceAccount` for them to use, and the `ClusterRoles` and `ClusterRoleBindings` that grant them permissions within Kubernetes.
4.  It sends these final manifests to the Kubernetes API server to create the resources.
5.  It tracks all these created resources as a single "release," making it easy to manage, upgrade, or uninstall them later.

<!-- end list -->

```bash
helm install alb-controller oci://mcr.microsoft.com/application-lb/charts/alb-controller \
     --namespace $HELM_NAMESPACE \
     --version 1.7.9 \
     --set albController.namespace=$CONTROLLER_NAMESPACE \
     --set albController.podIdentity.clientID=$(az identity show -g $RESOURCE_GROUP -n azure-alb-identity --query clientId -o tsv)
```

### 2.5. Verify the Controller Pods

Check that the controller pods are running successfully in the cluster.

```bash
kubectl get pods -n $HELM_NAMESPACE
```

You should see two pods with a status of `Running`.

-----

## Phase 3: Configuring Azure Networking

**Why do we need to set up networking?** The ALB Controller runs inside Kubernetes (the control plane), but the Application Gateway itself is a managed Azure service that processes traffic (the data plane). We need to prepare a place in our Azure Virtual Network for this data plane to live.

**Why a dedicated subnet?** Creating a separate subnet for the ALB provides critical **isolation**. It prevents IP address conflicts with your AKS nodes and allows you to apply different Network Security Group rules to your ingress traffic than to your cluster nodes. Furthermore, the ALB service requires a special permission on its subnet called a **delegation**, and dedicating a subnet ensures this delegation doesn't interfere with other resources.

**What is the architectural impact?** This creates a clear separation of concerns. The ALB lives in its own dedicated network segment, acting as a secure, managed entry point. It is controlled by Kubernetes resources but is not mixed in with the application node pools.

### 3.1. Get VNet Information

First, we need to identify the Virtual Network (VNet) that our AKS cluster is using.

```bash
VNET_NAME=$(az network vnet list --resource-group $mcResourceGroup --query "[0].name" -o tsv)
VNET_RESOURCE_GROUP=$mcResourceGroup
```

### 3.2. Create a Dedicated Subnet for the ALB

Now, we will create the new subnet. This process involves first inspecting the network to find a valid, unused IP address range.

**Understanding IP Ranges (CIDR Notation)**: IP ranges are defined using CIDR notation, like `10.224.0.0/12`. The number after the `/` indicates how many bits of the IP address are fixed as the network prefix. A smaller number (like `/12`) means a larger network with more available IPs, while a larger number (like `/24`) means a smaller network.

Let's find the address space of your VNet.

```bash
az network vnet show --resource-group $VNET_RESOURCE_GROUP --name $VNET_NAME --query "addressSpace.addressPrefixes" -o tsv
```

Let's assume the output is `10.224.0.0/12`. A `/12` prefix means the first 12 bits are fixed. The IP address `10.224.0.0` in binary starts with `00001010.1110...`. The `/12` boundary is within the second octet. The range of this second octet is from `11100000` (224) to `11101111` (239). Therefore, the full IP range for this VNet is **`10.224.0.0` to `10.239.255.255`**. Any subnet we create must fall within this range.

Next, list existing subnets to ensure the range you pick is not already in use.

```bash
az network vnet subnet list --resource-group $VNET_RESOURCE_GROUP --vnet-name $VNET_NAME --query "[].{Name:name, Prefix:addressPrefix}" -o table
```

Based on the output, choose an unused `/24` CIDR block and create the new subnet. The `--delegations` flag is mandatory.

```bash
ALB_SUBNET_NAME='subnet-alb'
SUBNET_ADDRESS_PREFIX='10.226.0.0/24' # Example: Change if this range is in use

az network vnet subnet create \
  --resource-group $VNET_RESOURCE_GROUP \
  --vnet-name $VNET_NAME \
  --name $ALB_SUBNET_NAME \
  --address-prefixes $SUBNET_ADDRESS_PREFIX \
  --delegations 'Microsoft.ServiceNetworking/trafficControllers'
```

### 3.3. Delegate Final Permissions

The ALB identity needs two more permissions to manage the gateway and join the new subnet.

```bash
ALB_SUBNET_ID=$(az network vnet subnet show --name $ALB_SUBNET_NAME --resource-group $VNET_RESOURCE_GROUP --vnet-name $VNET_NAME --query id --output tsv)

# Delegate role to manage the gateway resource itself
az role assignment create --assignee-object-id $principalId --assignee-principal-type ServicePrincipal --scope $mcResourceGroupId --role "fbc52c3f-28ad-4303-a892-8a056630b8f1"

# Delegate role to join the subnet
az role assignment create --assignee-object-id $principalId --assignee-principal-type ServicePrincipal --scope $ALB_SUBNET_ID --role "4d97b98b-1d4f-4787-a291-c67834d212e7"
```

-----

## Phase 4: Provisioning the Gateway Resources

Now we instruct the controller to create the Application Gateway infrastructure and define our traffic entrypoint.

### 4.1. Create the ApplicationLoadBalancer Resource

We will now create a Kubernetes resource of `kind: ApplicationLoadBalancer`. When the ALB controller sees this, it will start provisioning the actual gateway in Azure. We will create this resource in a new namespace, `nsa2`.

First, create the namespace.

```bash
kubectl create namespace nsa2
```

Now, create a YAML file named `nsa2-alb.yaml`. The `tee` command is a convenient way to do this from the shell. Note that `spec.associations` points to the ID of the subnet we just created.

```bash
ALB='default-alb'

tee nsa2-alb.yaml > /dev/null <<EOF
apiVersion: alb.networking.azure.io/v1
kind: ApplicationLoadBalancer
metadata:
  name: $ALB
  namespace: nsa2
spec:
  associations:
  - $ALB_SUBNET_ID
EOF
```

Apply the manifest to the cluster.

```bash
kubectl apply -f nsa2-alb.yaml
```

### 4.2. Verify the ApplicationLoadBalancer Provisioning

This provisioning step can take a few minutes. You can watch its status until the `reason` for the `Deployment` type becomes `Ready`.

```bash
kubectl -n nsa2 get applicationloadbalancer default-alb -o yaml -w
```

Press `Ctrl + C` to exit once you see the `Ready` status.

### 4.3. Create the Gateway Resource

With the infrastructure ready, we can now create a standard Kubernetes `Gateway` resource. This defines the listener for our traffic.

Create a file named `k8s-nsa2-gateway.yaml`:

```yaml
apiVersion: gateway.networking.k8s.io/v1
kind: Gateway
metadata:
  name: k8s-nsa2-gateway
  namespace: nsa2
spec:
  gatewayClassName: azure-alb-external
  listeners:
    - name: http
      protocol: HTTP
      port: 80
      allowedRoutes:
        namespaces:
          from: Same
```

Apply the manifest:

```bash
kubectl apply -f k8s-nsa2-gateway.yaml
```

### 4.4. Get the Gateway's Public Address

The Application Gateway will be assigned a public Fully Qualified Domain Name (FQDN). Retrieve it and store it in a variable.

```bash
fqdn=$(kubectl get gateway k8s-nsa2-gateway -n nsa2 -o jsonpath='{.status.addresses[0].value}')
echo $fqdn
```

-----

## Phase 5: Deploying and Exposing a Sample Application

Finally, we deploy a sample web app and use an `HTTPRoute` to connect it to our gateway.

### 5.1. Deploy and Expose the Application

Create an Nginx deployment and expose it internally with a `ClusterIP` Service.

```bash
# Create the deployment
kubectl create deployment nsa2-webapp --image=nginx:latest -n nsa2

# Create the service
kubectl expose deployment nsa2-webapp --port=80 --type=ClusterIP -n nsa2
```

### 5.2. Create the HTTPRoute

The `HTTPRoute` resource tells the gateway how to route incoming traffic. It links the gateway (`parentRefs`) to a backend service (`backendRefs`).

Create a file named `nsa2-webapp-route.yaml`:

```yaml
apiVersion: gateway.networking.k8s.io/v1
kind: HTTPRoute
metadata:
  name: nsa2-webapp-route
  namespace: nsa2
spec:
  parentRefs:
    - name: k8s-nsa2-gateway
  rules:
    - matches:
        - path:
            type: PathPrefix
            value: "/"
      backendRefs:
        - name: nsa2-webapp
          kind: Service
          port: 80
```

Apply the manifest:

```bash
kubectl apply -f nsa2-webapp-route.yaml
```

-----

## Phase 6: Verification

Your application should now be accessible to the internet. You can test it by opening the gateway's public address in your browser or by using a command-line tool like `curl`.

```bash
curl http://$fqdn
```

You should see the "Welcome to nginx\!" default page.

## Custom Health Checks for ALB ##

### Troubleshooting "no healthy upstream" Error

When using Azure Application Gateway for Containers, you may encounter the error "no healthy upstream" when trying to access your application through HTTPRoute. This error indicates that the ALB Controller considers your backend service unhealthy.

**Root Cause:**
By default, Azure ALB performs health checks on the root path (`/`) of your backend services. If your application doesn't implement a root endpoint or returns a non-2xx status code, the ALB marks it as unhealthy and refuses to route traffic to it.

**Diagnostic Steps:**
1. **Verify service health directly**: Test your service endpoints within the cluster
   ```bash
   kubectl run test-pod --image=busybox --rm -it --restart=Never -n exercises -- wget -qO- http://your-service:port/
   kubectl run test-pod --image=busybox --rm -it --restart=Never -n exercises -- wget -qO- http://your-service:port/health
   ```

2. **Check ALB Controller logs**: Look for health check failures
   ```bash
   kubectl logs -n azure-alb-system -l app=alb-controller --tail=100 | grep -i health
   ```

**Solution: Custom Health Check Policy**
Create a `HealthCheckPolicy` resource to specify a custom health check endpoint for services that don't implement the root path:

```yaml
apiVersion: alb.networking.azure.io/v1
kind: HealthCheckPolicy
metadata:
  name: ping-pong-health-check
  namespace: exercises
spec:
  targetRef:
    group: ""
    kind: Service
    name: ping-pong-svc
  default:
    interval: 5s
    timeout: 2s
    unhealthyThreshold: 3
    healthyThreshold: 2
    http:
      path: "/health"
```

This policy tells the ALB Controller to use `/health` instead of `/` for health checks on the specified service.

**References:**
- [Google Cloud troubleshooting guide](https://cloud.google.com/kubernetes-engine/docs/how-to/deploying-gateways#no-healthy-upstream)
- [Azure ALB health probe configuration](https://learn.microsoft.com/en-us/azure/application-gateway/for-containers/custom-health-probe#default-health-probe)

# Setting up Kubernetes to use Azure Key Vault for Secrets Management #

## Resource Discovery
```bash
# Example pattern - you'll need to adapt with your actual values
RESOURCE_GROUP="kubernetes-learning"
AKS_CLUSTER="kube-mooc"

# Fetch and store cluster info
AKS_RESOURCE_ID=$(az aks show --resource-group $RESOURCE_GROUP --name $AKS_CLUSTER --query id -o tsv)
SUBSCRIPTION_ID=$(az account show --query id -o tsv)

# Echo the values for verification
echo "AKS Resource ID: $AKS_RESOURCE_ID"
echo "Subscription ID: $SUBSCRIPTION_ID"
```

## Identity Management
```bash
IDENTITY_NAME="keyvault-identity-kube-mooc"

# Create a Managed Identity for AKS to access Key Vault
az identity create --resource-group $RESOURCE_GROUP --name $IDENTITY_NAME

# Fetch the created identity details
IDENTITY_CLIENT_ID=$(az identity show --resource-group $RESOURCE_GROUP --name $IDENTITY_NAME --query clientId -o tsv)
IDENTITY_PRINCIPAL_ID=$(az identity show --resource-group $RESOURCE_GROUP --name $IDENTITY_NAME --query principalId -o tsv)

# Echo the identity details for verification
echo "Managed Identity Client ID: $IDENTITY_CLIENT_ID"
echo "Managed Identity Principal ID: $IDENTITY_PRINCIPAL_ID"
```

## AKS Cluster Infromation
```bash
# Get the managed cluster resource group (where AKS creates its resources)
MC_RESOURCE_GROUP=$(az aks show --resource-group $RESOURCE_GROUP --name $AKS_CLUSTER --query "nodeResourceGroup" -o tsv)
echo "MC Resource Group: $MC_RESOURCE_GROUP"

# Get the OIDC issuer URL (needed for workload identity)
AKS_OIDC_ISSUER=$(az aks show --resource-group $RESOURCE_GROUP --name $AKS_CLUSTER --query "oidcIssuerProfile.issuerUrl" -o tsv)
echo "OIDC Issuer: $AKS_OIDC_ISSUER"
```

## AKV Creation and Configuration
```bash
KEYVAULT_NAME="kv-kubemooc-$(date +%s)"
echo "Key Vault Name: $KEYVAULT_NAME"
```

Create the Key Vault:
```bash
# Create the Key Vault
az keyvault create \
  --name $KEYVAULT_NAME \
  --resource-group $RESOURCE_GROUP \
  --location northeurope \
  --enable-rbac-authorization

# Get the Key Vault resource ID for future use
KEYVAULT_ID=$(az keyvault show --name $KEYVAULT_NAME --resource-group $RESOURCE_GROUP --query id -o tsv)
echo "Key Vault ID: $KEYVAULT_ID"
```

Assigning yourself permissions into the Key Vault:
```bash
# Check your identity
az account show --query "user.name" -o tsv

# Get your user object ID
USER_OBJECT_ID=$(az ad signed-in-user show --query id -o tsv)

# Assign yourself Key Vault Contributor role
az role assignment create \
  --assignee-object-id $USER_OBJECT_ID \
  --assignee-principal-type User \
  --scope $KEYVAULT_ID \
  --role "Key Vault Secrets Officer"
```


## Storing Postgres Credentials in Key Vault
First go to the fodler with your secrets and check the secrets you have:


Setting the secrets in the Key Vault:
```bash
# Set the Postgres admin user
az keyvault secret set \
  --vault-name $KEYVAULT_NAME \
  --name "postgres-user" \
  --value "$DECODED_USER"

# Set the Postgres admin password
az keyvault secret set \
  --vault-name $KEYVAULT_NAME \
  --name "postgres-password" \
  --value "$DECODED_PASSWORD"

# Verify secrets are set
az keyvault secret list --vault-name $KEYVAULT_NAME --query "[].name" -o table
```

## Granting your AKS Managed Identity Access to Key Vault
```bash
az role assignment create \
  --assignee-object-id $IDENTITY_PRINCIPAL_ID \
  --assignee-principal-type ServicePrincipal \
  --scope $KEYVAULT_ID \
  --role "Key Vault Secrets User"
```

## Taking the secrets from Key Vault in your AKS cluster

### Enable CSI Secrets Store Driver
```bash
az aks enable-addons \
  --addons azure-keyvault-secrets-provider \
  --name $AKS_CLUSTER \
  --resource-group $RESOURCE_GROUP
```

### Workload identity bridging
```bash
# Create a federated credential for the Postgres service account in Azure
az identity federated-credential create \
  --name "postgres-workload-identity" \
  --identity-name $IDENTITY_NAME \
  --resource-group $RESOURCE_GROUP \
  --issuer $AKS_OIDC_ISSUER \
  --subject "system:serviceaccount:project:postgres-service-account"
```

Key concept: The --subject parameter defines exactly which Kubernetes ServiceAccount Azure will trust. The format is system:serviceaccount:NAMESPACE:SERVICE_ACCOUNT_NAME.

### Creating the Service Account and Secret Provider Class

```yaml
apiVersion: v1
kind: ServiceAccount
metadata:
  name: postgres-service-account
  namespace: project
  annotations:
    azure.workload.identity/client-id: 9b82dc92-8be2-4de4-90e4-e99eefb44e9f
```

```yaml
apiVersion: secrets-store.csi.x-k8s.io/v1
kind: SecretProviderClass
metadata:
  name: postgres-secret-provider
  namespace: project
spec:
  provider: azure
  parameters:
    usePodIdentity: "false"
    useVMManagedIdentity: "false"
    clientID: "9b82dc92-8be2-4de4-90e4-e99eefb44e9f"
    keyvaultName: "kv-kubemooc-1754386572"
    tenantId: "b7cff52d-a4ec-4367-903c-5cf05c061aca"
    objects: |
      array:
        - |
          objectName: postgres-user
          objectType: secret
        - |
          objectName: postgres-password
          objectType: secret
  secretObjects:
  - secretName: postgres-secret
    type: Opaque
    data:
    - objectName: postgres-user
      key: USER
    - objectName: postgres-password
      key: PASSWORD

```

provider: azure - Uses the Azure Key Vault provider
clientID - Your managed identity that can access Key Vault
keyvaultName - Which Key Vault to pull from
objects - Lists which secrets to fetch from Key Vault
secretObjects - Creates a Kubernetes secret with the exact name and keys your StatefulSet expects
The critical mapping happens in secretObjects.data:

Key Vault postgres-user becomes Kubernetes secret key USER
Key Vault postgres-password becomes Kubernetes secret key PASSWORD

### Changes to the Postgres StatefulSet
```yaml
      serviceAccountName: postgres-service-account
      volumes:
      - name: secrets-store
        csi:
          driver: secrets-store.csi.k8s.io
          readOnly: true
          volumeAttributes:
            secretProviderClass: "postgres-secret-provider"
          ...
          volumeMounts:
            - name: secrets-store
              mountPath: "/mnt/secrets-store"
              readOnly: true
            - name: postgres-data-storage
              mountPath: /var/lib/postgresql/data
              subPath: postgres
```

Azure Key Vault Integration with AKS - Big Picture Summary
What We Accomplished
Successfully migrated from SOPS-encrypted local secrets to Azure Key Vault integration for the postgres service in our course project.

Architecture Overview

┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐│   Azure Key     │    │   Kubernetes     │    │   Application   ││     Vault       │◄──►│   CSI Driver     │◄──►│     Pods        ││                 │    │                  │    │                 ││ postgres-user   │    │ postgres-secret  │    │ POSTGRES_USER   ││ postgres-pass   │    │ (K8s Secret)     │    │ POSTGRES_PASS   │└─────────────────┘    └──────────────────┘    └─────────────────┘
Key Components Created
Azure Managed Identity (keyvault-identity-kube-mooc)

Identity that can access Key Vault secrets
Granted "Key Vault Secrets User" role
Workload Identity Bridge

Federated credential linking Azure identity to Kubernetes ServiceAccount
Enables passwordless authentication from pods to Azure
Kubernetes ServiceAccount (postgres-service-account)

Annotated with Azure managed identity client ID
Used by postgres pods for authentication
SecretProviderClass (postgres-secret-provider)

Configuration defining which Key Vault secrets to fetch
Maps Key Vault secret names to Kubernetes secret keys
Creates standard Kubernetes Secret that applications expect
StatefulSet Integration

Added ServiceAccount reference
Added CSI volume mount (triggers secret fetching)
Environment variables unchanged - complete application transparency
The Magic
Application sees no difference: Same environment variables, same secret references
CSI driver handles complexity: Authentication, fetching, mapping all transparent
Production-ready security: No secrets stored in containers or manifests
Centralized management: All secrets managed in Azure Key Vault
Key Learning
The CSI Secrets Store driver creates a bridge between Azure Key Vault (cloud-native secret storage) and Kubernetes Secrets (what applications expect), providing enterprise-grade secret management without changing application code.

This pattern eliminates the need for SOPS files, provides automatic secret rotation capabilities, and centralizes secret management in Azure's secure vault service.

---
# CSI Secrets Store Driver and Managed Storage #
Excellent question! CSI is a fundamental concept in modern Kubernetes. Let me break it down:

## What is CSI (Container Storage Interface)?

**CSI is a standardized API** that allows external storage systems to plug into Kubernetes without needing to modify Kubernetes core code.

## The Problem CSI Solves:

**Before CSI:**
- Storage drivers were built into Kubernetes core
- Adding new storage required changing Kubernetes source code
- Cloud providers had to wait for Kubernetes releases
- Hard to maintain and update storage integrations

**With CSI:**
- Storage drivers are external plugins
- Cloud providers can develop and update independently
- Kubernetes just provides the interface
- Much more flexible and maintainable

## CSI Architecture in Kubernetes:

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Kubernetes    │────│   CSI Driver    │────│  External       │
│   Core          │    │   (Plugin)      │    │  Storage        │
│                 │    │                 │    │  System         │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## Your Two CSI Use Cases:

### 1. CSI Secrets Store Driver (Azure Key Vault)
```yaml
# Secret Provider Class
spec:
  provider: azure  # ← CSI driver for Azure Key Vault
```

**What happens:**
- CSI driver connects to Azure Key Vault
- Fetches secrets and mounts them as files
- Creates Kubernetes secrets automatically
- Handles authentication via workload identity

### 2. CSI Storage Driver (Azure Disk)
```yaml
# PVC with managed-csi
spec:
  storageClassName: managed-csi  # ← CSI driver for Azure Disk
```

**What happens:**
- CSI driver provisions Azure Disk storage
- Attaches disk to the node
- Formats and mounts the disk
- Handles all Azure API calls

## CSI Components:

**1. CSI Controller:**
- Runs as a deployment
- Handles volume provisioning/deletion
- Talks to external storage APIs

**2. CSI Node Plugin:**
- Runs as a DaemonSet (on every node)
- Handles mounting/unmounting on nodes
- Formats disks, creates filesystem

**3. CSI Driver Registration:**
- Registers capabilities with Kubernetes
- Tells K8s what operations it supports

## In AKS Specifically:

**Pre-installed CSI Drivers:**
- `disk.csi.azure.com` (Azure Disks) → Your `managed-csi`
- `file.csi.azure.com` (Azure Files)
- `secrets-store.csi.k8s.io` (Secrets Store) → Your Key Vault integration

## The Beauty of CSI:

**Uniform Interface:**
- Same PVC syntax works with AWS EBS, Google Persistent Disk, Azure Disk
- Same secret mounting works with AWS Secrets Manager, Azure Key Vault, HashiCorp Vault
- Kubernetes doesn't need to know the specifics

**Your Experience:**
```yaml
# You write standard Kubernetes YAML
persistentVolumeClaim:
  claimName: image-cache-pvc

# CSI driver handles all the Azure-specific magic behind the scenes
```

CSI makes Kubernetes truly cloud-agnostic while giving cloud providers the flexibility to innovate on their storage solutions!

Similar code found with 2 license types

# GitHub Deployment Pipeline Creation with Azure Cloud #

Implementing Workload Identity authentication for GitHub Actions to enable secure, passwordless CI/CD pipelines with Azure Container Registry (ACR) and Azure Kubernetes Service (AKS).

**Why Workload Identity?** Traditional CI/CD authentication uses long-lived service principal credentials stored as GitHub secrets. Workload Identity eliminates this security risk by using OpenID Connect (OIDC) federation - GitHub Actions receives temporary JWT tokens that Azure validates in real-time without storing any secrets.

**The Authentication Flow:**
1. GitHub Actions requests a JWT token from GitHub's OIDC issuer
2. Azure validates the token against the trusted relationship we establish
3. Azure grants temporary access to the specified resources
4. No credentials stored in GitHub repository

## Create Managed Identity for GitHub Actions ##

Creates a dedicated Azure identity that GitHub Actions will assume during pipeline execution.

```bash
az identity create \
  --resource-group kubernetes-learning \
  --name github-actions-todo-cd \
  --location northeurope
```

**Why a dedicated identity?** Separation of concerns - this identity has only the permissions needed for CI/CD operations, following the principle of least privilege.

## Assign Permissions to Managed Identity ##

Grant the minimum required permissions for the CI/CD pipeline: container image push and Kubernetes deployment.

### 1. Capture the Subscription ID
```bash
SUBSCRIPTION_ID=$(az account show --query id --output tsv)
```

### 2. Get the Managed Identity Client ID
```bash
GITHUB_IDENTITY=$(az identity show --resource-group kubernetes-learning --name github-actions-todo-cd --query clientId --output tsv)
```

### 3. Assign ACR Push Role to Managed Identity
```bash
az role assignment create \
  --assignee $GITHUB_IDENTITY \
  --role AcrPush \
  --scope /subscriptions/$SUBSCRIPTION_ID/resourceGroups/kubernetes-learning/providers/Microsoft.ContainerRegistry/registries/kubemooc
```

**What this enables:** The identity can push Docker images to the `kubemooc` registry. The `AcrPush` role includes permissions to authenticate, push images, and manage repository metadata.

### 4. Grant AKS Contributor Role to Managed Identity
```bash
az role assignment create \
  --assignee $GITHUB_IDENTITY \
  --role "Azure Kubernetes Service Contributor Role" \
  --scope /subscriptions/$SUBSCRIPTION_ID/resourceGroups/kubernetes-learning/providers/Microsoft.ContainerService/managedClusters/kube-mooc
```

**What this enables:** The identity can connect to the AKS cluster, retrieve kubeconfig credentials, and execute kubectl commands for deployment operations.

## Configuring Federated Credential Trust ##

Establishes the OIDC trust relationship between your GitHub repository and the Azure Managed Identity.

```bash
az identity federated-credential create \
  --name "github-actions-ci-cd" \
  --identity-name "github-actions-todo-cd" \
  --resource-group "kubernetes-learning" \
  --issuer "https://token.actions.githubusercontent.com" \
  --subject "repo:rjpalt/KubernetesMOOC:ref:refs/heads/main"
```

**Critical Security Configuration:**
- `--issuer`: GitHub's OIDC endpoint that Azure will trust
- `--subject`: Restricts access to only the `main` branch of the specified repository
- This prevents unauthorized access from forks, pull requests, or other branches

**Alternative subjects for different use cases:**
- `repo:owner/repo:pull_request` - Allow from pull requests
- `repo:owner/repo:ref:refs/heads/dev` - Allow from specific branch
- `repo:owner/repo:environment:production` - Allow from specific environment

## Collect Information for GitHub Repository Configuration ##

Gather the values needed to configure GitHub repository secrets and workflow files.

```bash
echo "=== GitHub Repository Secrets ==="
echo "AZURE_CLIENT_ID: $(az identity show --resource-group kubernetes-learning --name github-actions-todo-cd --query clientId --output tsv)"
echo "AZURE_TENANT_ID: $(az account show --query tenantId --output tsv)"
echo "AZURE_SUBSCRIPTION_ID: $(az account show --query id --output tsv)"
echo ""
echo "=== Azure Resource Information ==="
echo "ACR_LOGIN_SERVER: kubemooc.azurecr.io"
echo "AKS_CLUSTER_NAME: kube-mooc"
echo "AKS_RESOURCE_GROUP: kubernetes-learning"
```

**Required GitHub Secrets:**
- `AZURE_CLIENT_ID`: Managed Identity identifier for authentication
- `AZURE_TENANT_ID`: Azure Active Directory tenant identifier
- `AZURE_SUBSCRIPTION_ID`: Azure subscription scope identifier

**Workflow Variables:**
- `ACR_LOGIN_SERVER`: Container registry endpoint for image operations
- `AKS_CLUSTER_NAME`: Target Kubernetes cluster for deployments
- `AKS_RESOURCE_GROUP`: Azure resource group containing the cluster

**Security Note:** Unlike Service Principal authentication, no `AZURE_CLIENT_SECRET` is required. The OIDC token serves as the authentication mechanism.

### GitHub Actions and Azure Credentials ###
```yaml
name: Deploy to AKS - Todo Application

on:
  push:
    branches: [ main ]
    paths:
      - 'course_project/**'

permissions:
  id-token: write  # This permission allows GitHub Actions to request and write OIDC tokens
  contents: read   # Required for checkout

  [... other parts of pipeline ...]

- name: Azure Login via Workload Identity
  uses: azure/login@v2
  with:
    client-id: ${{ secrets.AZURE_CLIENT_ID }}
    tenant-id: ${{ secrets.AZURE_TENANT_ID }}
    subscription-id: ${{ secrets.AZURE_SUBSCRIPTION_ID }}
  
  [... other parts of pipeline ...]
```

**OIDC Authentication Flow:**
1. GitHub Actions generates an OIDC token (using id-token: write)
2. `azure/login` action sends this token + the three IDs to Azure
3. Azure validates the token against your federated credential (github-actions-ci-cd)
4. Azure returns a temporary access token for the managed identity (github-actions-todo-cd)
5. The action sets Azure CLI authentication context

**Key Insights:**
- The "identity" is your Azure Managed Identity (github-actions-todo-cd). GitHub Actions doesn't have its own managed identity - it uses OIDC to assume your Azure Managed Identity.
- **Session-based permissions**: Once authenticated, the pipeline receives ALL permissions of the managed identity for the duration of the JWT session (typically 30-60 minutes max).
- **No persistent credentials**: JWT expires, session ends, no stored secrets anywhere.

### Manifest Handling in CI/CD ###

**Important**: The pipeline does NOT modify the main branch. Here's what actually happens:

1. `checkout` action creates a **local copy** of your repo in the runner's temporary workspace
2. `kustomize edit set image` modifies **only the local copy** in the runner
3. `kubectl apply -k .` deploys from **the modified local copy**
4. **No changes are pushed back** to the main branch

**The flow:**
```
GitHub Repo (main) → Runner Workspace → Modify Locally → Deploy to AKS
                   ↑                                   ↑
              (read-only)                      (deploy only)
```

This approach maintains **GitOps principles** while enabling **dynamic image tag updates** at deployment time.

### Deployment Tracking (Stopgap Solution) ###

**Current Approach Limitations:**
- Git repository shows static image tags (`latest` or fixed versions)
- Actual deployments use dynamic commit SHA tags
- Configuration drift between repo and cluster state

**Stopgap Monitoring Commands:**
```bash
# Check currently deployed image tags
kubectl get deployment todo-backend -o jsonpath='{.spec.template.spec.containers[0].image}'
kubectl get deployment todo-app -o jsonpath='{.spec.template.spec.containers[0].image}'

# View deployment history
kubectl rollout history deployment/todo-backend
kubectl rollout history deployment/todo-app

# Compare repo vs cluster state
echo "Repo kustomization:"
cat course_project/manifests/base/kustomization.yaml | grep -A5 images
echo "Deployed images:"
kubectl get deployments -o jsonpath='{range .items[*]}{.metadata.name}: {.spec.template.spec.containers[0].image}{"\n"}{end}'
```

**Acceptable for Learning Because:**
- Pipeline functionality and security remain intact
- Easy to verify actual deployed state when needed
- Focuses learning on Kubernetes rather than complex GitOps tooling
- Common development pattern before full GitOps implementation

### Making Configuration Drift Explicit ###

**Problem:** Git manifests show static/placeholder tags while deployments use dynamic commit SHAs, creating confusion about what's actually deployed.

**Solution:** Use **intentionally obvious placeholder tags** that make it clear the manifests are managed by automation:

```yaml
# Example from manifests/base/todo-be/deployment.yaml
containers:
- name: todo-backend
  # WARNING: This image tag is automatically updated by CI/CD pipeline
  # DO NOT manually edit - tag gets replaced with commit SHA during deployment
  image: kubemooc.azurecr.io/todo-app-be:PLACEHOLDER-UPDATED-BY-CICD
```

**Why This Works:**
- **Prevents manual edits**: Obvious placeholder prevents accidental manual changes
- **Self-documenting**: Comments explain the CI/CD replacement behavior
- **Kustomize compatible**: Pipeline still uses `kustomize edit set image` normally
- **Deployment verification**: Forces developers to check actual cluster state

**Pipeline behavior remains unchanged:**
```bash
# CI/CD still works exactly the same way
kustomize edit set image kubemooc.azurecr.io/todo-app-be:abc123def
kubectl apply -k .
```

**Alternative approaches for "latest" behavior:**
- Use ACR webhook triggers (advanced Azure Container Registry feature)
- Implement image digest references instead of tags (most reliable)
- Use Flux/ArgoCD image reflector controllers (full GitOps solution)

### Enforcing CI/CD-Only Deployments ###

**Architectural Benefit:** Using placeholder tags **intentionally breaks** local `kubectl apply` commands, enforcing proper development workflows:

```bash
# Local development (correct approach)
cd course_project
docker-compose up --build              # ✅ Works - proper local testing

# Direct Kubernetes deployment (now prevented)
kubectl apply -k manifests/base/       # ❌ Fails - placeholder tag doesn't exist
```

**Why This Is Good Practice:**
- **Prevents configuration drift**: No accidental local deployments with wrong tags
- **Enforces testing workflow**: Developers must use docker-compose for local testing
- **Maintains audit trail**: All production deployments go through Git + CI/CD
- **Security compliance**: No bypassing authentication and approval processes
- **Consistency**: Same deployment process for all environments

**The Proper Workflow:**
1. **Local development**: `docker-compose up` for rapid iteration
2. **Integration testing**: Push to feature branch → CI runs tests
3. **Production deployment**: Merge to main → CI/CD deploys with real image tags

**Emergency Override (if needed):**
```bash
# Only for emergencies - temporarily fix placeholder tag
kubectl set image deployment/todo-app-fe todo-app-fe=kubemooc.azurecr.io/todo-app-fe:actual-tag
```

This pattern is used by many organizations to **prevent deployment accidents** and ensure **proper process compliance**.

## Handling Volumes with Azure CSI Driver ##

### Azure Storage Classes Comparison

**managed-csi (Azure Disk):**
- Uses Azure Disk storage (SSD/HDD volumes)
- Access mode: ReadWriteOnce only (single pod attachment)
- Best for: Database storage, application data requiring persistence
- Deployment strategy: Requires `Recreate` for rolling updates

**azurefile-csi (Azure Files):**
- Uses Azure File Share storage (SMB/NFS network file system)
- Access mode: ReadWriteMany supported (multiple pod sharing)
- Best for: Shared content, logs, configuration files, image caches
- Deployment strategy: Supports `RollingUpdate` (zero downtime)

**Why azurefile-csi for Image Cache:**
The frontend image cache stores random images from the internet that multiple pods can safely share. Since the content is non-critical and read-heavy, Azure Files' ReadWriteMany capability allows smooth rolling updates without deployment downtime, unlike Azure Disk's single-pod limitation.

### Troubleshooting PVC Storage Class Changes

**Problem:** Cannot change storage class or access mode of an existing PVC - "spec is immutable after creation"

**Root Cause:** Kubernetes PVCs are immutable after creation. You cannot change `storageClassName` or `accessModes` on an existing PVC.

**Solution Process:**
1. **Delete the deployment first**: The PVC will be stuck in "Terminating" state if any pods are still using it
   ```bash
   kubectl delete deployment todo-app-fe -n project
   ```

2. **Delete the PVC**: Once no pods are using it, the PVC can be deleted
   ```bash
   kubectl delete pvc image-cache-pvc -n project
   ```

3. **Redeploy with new configuration**: Apply the updated manifests with the correct storage class
   ```bash
   kubectl apply -k course_project/manifests/base/todo-fe/
   ```

**Expected Results:**
- Old PVC: `managed-csi` with `RWO` (ReadWriteOnce)
- New PVC: `azurefile-csi` with `RWX` (ReadWriteMany)

**Diagnostic Commands:**
```bash
# Check PVC status and what's using it
kubectl describe pvc image-cache-pvc -n project

# Check if pods are still using the PVC
kubectl get pods -n project -o wide

# Verify new PVC has correct storage class
kubectl get pvc -n project
```

### CI/CD Pipeline Health Check Issues

**Problem:** `kubectl wait --for=condition=ready pod` timing out during rolling deployments, even when pods are actually ready.

**Root Cause:** During rolling updates, there can be multiple pods with the same label selector:
- Old pods in "Terminating" state
- New pods in "Running" state
- The `kubectl wait` command waits for ALL pods matching the selector to be ready

**Symptoms:**
```bash
# CI/CD shows timeout
timed out waiting for the condition on pods/todo-app-fe-567c49c6cd-z6dv5

# But pods are actually ready
kubectl describe pod → Status: Running, Ready: True
```

**Solution:** Replace individual pod waits with deployment-focused verification:
```yaml
# Instead of waiting for all pods with a label
kubectl wait --for=condition=ready pod -l app=todo-app-fe -n project --timeout=120s

# Use deployment rollout status (already in pipeline) + find ready pod
kubectl rollout status deployment/todo-app-fe -n project --timeout=300s
READY_POD=$(kubectl get pods -n project -l app=todo-app-fe --field-selector=status.phase=Running -o jsonpath='{.items[0].metadata.name}')
```

**Why This Works:**
- `kubectl rollout status` waits for deployment to be stable
- Field selector filters only running pods
- Avoids race conditions with terminating pods during rolling updates
