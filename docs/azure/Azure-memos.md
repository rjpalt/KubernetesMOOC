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
