# Command Memos #

## Kubectl Commands ##

*Remember to have a Kubernetes cluster running and kubectl configured to interact with it.*

`k3d cluster create -a 2'`

```bash
kubectl create deployment hashgenerator-dep --image=<image-name>
```

- `kubectl create deployment`: This tells Kubernetes you want to create a new Deployment object.
“
- `hashgenerator-dep`: This is the name you're giving to your Deployment.

- `--image=jakousa/dwk-app1`: This specifies the container image that will be used to create the Pods managed by this Deployment.

1. The control plane created the Deployment resource named hashgenerator-dep.

2. This Deployment automatically created a child resource called a ReplicaSet. The ReplicaSet's job is to make sure a specific number of Pods (by default, one) are running.

3. The ReplicaSet then created a Pod.

4. The control plane's scheduler assigned this Pod to one of your available agent nodes (k3d-k3s-default-agent-0 or k3d-k3s-default-agent-1).

5. The agent node then pulled the jakousa/dwk-app1 image and started the container inside the Pod.

```bash

**Deployment of local image**

```bash
kubectl create deployment hashgenerator-dep --image=log-output-app
``` 

## Importing images to K3d ##

```bash
k3d image import todo-app:latest -c <your-cluster-name>
```



## Checking resources ##

```bash
kubectl get pods
```

Gets all teh pods in the current namespace.

## Checking Logs ##

```bash
kubectl logs -f hashgenerator-dep-<hash>
```

`-f` flag allows you to follow the logs in real-time.

## Ports ##

```bash
k3d cluster create --port 8082:30080@agent:0 -p 8081:80@loadbalancer --agents 2
```

**Checking available services**
```bash
kubectl get svc
```

## Scaling Replicas ##

1.
```bash
$ kubectl scale deployment/hashgenerator-dep --replicas=4
````

2.
```bash
kubectl set image deployment/hashgenerator-dep dwk-app1=jakousa/dwk-app1:hash_here
```

## Applying Manifests ##

```bash
kubectl apply -f manifests/deployment.yaml
```

*Note that the manifests.yaml file can be an URL or a local file path.*

## Deleting Resources ##

```bash
kubectl delete -f manifests/deployment.yaml
```

## Debugging Kubernetes ##

- Describe a resource to get more information about it:

```bash
kubectl describe pod <pod-name>
```

- Check the logs of a specific pod:

```bash
kubectl logs <pod-name>
```

- Worst case, delete the pod and let the Deployment recreate it:

```bash
kubectl delete pod <pod-name>
```

---
# Kubernetes and Networking #

## Port Forwarding ##
```bash
kubectl port-forward hashresponse-dep-57bcc888d7-dj5vk 3003:3000
```

- port-forward targets a resource (in this case, a Pod) and forwards traffic from a local port (3003) to a port on that resource (3000).
- E.g. it pairs a local port to a port on the kubernetes managed resource.

## Traffic Flow ##

### NodePort with k3d ###
1. **Host Machine (localhost:8082)** → Traffic enters through the host port mapped by k3d (`--port 8082:30080@agent:0`).
2. **NodePort (30080)** → Traffic is forwarded to the NodePort exposed by the Kubernetes Service.
3. **Service Port (2507)** → The Service routes traffic to the cluster-wide port defined in the Service manifest.
4. **Pod TargetPort (8000)** → Finally, the Service forwards traffic to the container's port (`targetPort`) where the application is listening.

### Summary ###
- Host: `localhost:8082`
- NodePort: `30080`
- Service Port: `2507`
- Pod TargetPort: `8000`

---

# Kubenretes and Storage #

## emptyDir Volume ##
- An `emptyDir` volume is created when a Pod is assigned to a Node and exists as long as that Pod is running on that Node.
- It is stored in the Node's filesystem and is deleted when the Pod is removed.
- Useful for temporary storage needs within a Pod.

Confgiuration example in `deployment.yaml`

```yaml
    spec:
      volumes: # Define volume
        - name: shared-image
          emptyDir: {}
      containers:
        - name: image-finder
          image: jakousa/dwk-app3-image-finder:b7fc18de2376da80ff0cfc72cf581a9f94d10e64
          volumeMounts: # Mount volume
          - name: shared-image
            mountPath: /usr/src/app/files
        - name: image-response
          image: jakousa/dwk-app3-image-response:b7fc18de2376da80ff0cfc72cf581a9f94d10e64
          volumeMounts: # Mount volume
          - name: shared-image
            mountPath: /usr/src/app/files
```

# Kubernetes and Namespaces #
 ## Accessing Namespaces ##
```bash
$ kubectl get pods -n kube-system
```

`-n kube-system` specifies the namespace to query.

To get all in all namespaces, use:
```bash
kubectl get all --all-namespaces
```

## Creating a Namespace ##
```bash
kubectl create namespace example-namespace
```

Optionally this can be done with a manifest:
```yaml
kind: Namespace
```

## Binding Manifests to a Namespace ##
To bind a manifest to a specific namespace, add the `metadata` section in your YAML file
```yaml
# ...
metadata:
  namespace: example-namespace
  name: example
# ...
```

Or, when applying the manifest, use flag `--namespace=my-namespace`

```bash
kubectl apply -f manifests/deployment.yaml --namespace=my-namespace
```

## Setting a Default Namespace ##
To set a default namespace for your kubectl commands, you can use:
```bash
kubectl config set-context --current --namespace=<name>
```

# Kubectx #
- List all contexts: `kubectx`
- Choose a context: `kubectx mycontext`

# Kubernetes and Labels #
## Labeling Resources ##
```bash
kubectl label po hashgenerator-dep-7b9b88f8bf-lvcv4 importance=great pod/hashgenerator-dep-7b9b88f8bf-lvcv4 labeled
```

## Listing Resources with Labels ##
```bash
kubectl get pod -l my-label
```

## Use cases ##
It's possible, for example to label nodes and then choose correct nodes for given containers.

First define in `deployment.yaml` how to select nodes:
```yaml
    ...
    spec:
      containers:
        - name: hashgenerator
          image: jakousa/dwk-app1:b7fc18de2376da80ff0cfc72cf581a9f94d10e64
      nodeSelector:
        networkquality: excellent
```

Now, what is required is a node with label `networkquality=excellent`. To create such a node, use:
```bash
kubectl label nodes k3d-k3s-default-agent-1 networkquality=excellent
```

This is a bit hamfisted approach, and using [affinity](https://kubernetes.io/docs/tasks/configure-pod-container/assign-pods-nodes-using-node-affinity/) is a more subtle approach. Also [tainsts and tolerations](https://kubernetes.io/docs/concepts/scheduling-eviction/taint-and-toleration/) can be used to control which pods can run on which nodes.


# Kubernetes and Secrets #
- Given to containers on runtime

Defining secrets in a manifest:
```yaml
# ...
containers:
  - name: imageagain
    envFrom:
      - secretRef:
          name: pixabay-apikey
```

This assumes that the secret pixabay-apikey defines the key as a variable called API_KEY. If the env name in the secret would be different, the longer form of definition could be used in the deployment.yaml:
```yaml
# ...
containers:
  - name: imageagain
    env:
      - name: API_KEY # ENV name passed to container
        valueFrom:
          secretKeyRef:
            name: pixabay-apikey
            key: API_KEY # ENV name in the secret
```

This would refer to a Secret manifest like this:
```yaml
apiVersion: v1
kind: Secret
metadata:
  name: pixabay-apikey
type: Opaque
data:
  API_KEY: <base64-encoded-value>
```

## ConfigMaps ##
- ConfigMaps are used to store non-sensitive configuration data in key-value pairs.

Example of a ConfigMap manifest:
```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: example-configmap
data:
  serverconfig.txt: |
    maxplayers=12
    difficulty=2
```

To reference a ConfigMap in a Pod, you can use it as an environment variable or mount it as a volume.
```yaml
apiVersion: v1
kind: Pod
metadata:
  name: example-pod
spec:
  containers:
  - name: example-container
    image: example-image
    env:
    - name: SERVER_CONFIG
      valueFrom:
        configMapKeyRef:
          name: example-configmap
          key: serverconfig.txt
    volumeMounts:
    - name: config-volume
      mountPath: /etc/config
  volumes:
  - name: config-volume
    configMap:
      name: example-configmap
```

# Using StatefulSets #
- StatefulSets are used for managing stateful applications, providing stable network identities and persistent storage.
- They ensure that the Pods are created in a specific order and maintain their identity across rescheduling

Requiremenets:
- Persistent Volumes (PVs) and Persistent Volume Claims (PVCs) for storage.
- Server that is headless, meaning it does not have a stable IP address or DNS name.

Example of a StatefulSet's service manifest:
```yaml
apiVersion: v1
kind: Service
metadata:
  name: redis-svc
  labels:
    app: redis
spec:
  ports:
  - port: 6379
    name: web
  clusterIP: None
  selector:
    app: redisapp
```

Note: `clusterIP: None` creates a headless service, allowing direct access to the Pods instead of routing through a load balancer.

- Creating a StatefulSet manifest:
```yaml
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: redis-stset
spec:
  serviceName: redis-svc
  replicas: 2
  selector:
    matchLabels:
      app: redisapp
  template:
    metadata:
      labels:
        app: redisapp
    spec:
      containers:
        - name: redisfiller
          image: jakousa/dwk-app5:54203329200143875187753026f4e93a1305ae26
        - name: redis
          image: redis:5.0
          ports:
            - name: web
              containerPort: 6379
          volumeMounts:
            - name: redis-data-storage
              mountPath: /data
  volumeClaimTemplates:
    - metadata:
        name: redis-data-storage
      spec:
        accessModes: ["ReadWriteOnce"]
        storageClassName: local-path
        resources:
          requests:
            storage: 100Mi
```

- Note that the `volumeClaimTemplates` section is used to define the Persistent Volume Claims (PVCs) for each Pod in the StatefulSet. Each Pod will get its own PVC based on this template.
- `local-path` is a storage class that allows the use of local storage on the node where the Pod is running. This is useful for development and testing purposes. It also forgos the creation of PCVs manually, as they are created automatically when the StatefulSet is applied.
- Note that the redisfiller app is always deployed in the same Pod as the redis container, so it can access the Redis service directly instead of going through the network.
- Each replica has a separate PVC, ensuring that data is preserved even if the Pod is rescheduled or restarted.
- With StatefulSets, pods are guaranteed to have tha same name and network identity (stable qualities) across rescheduling, which is crucial for stateful applications like databases. This means, that they will also get exactly the same PVCs. The content of the PVCs is not guaranteed to be the same, but the names are.

# Using Jobs #
- Jobs are used to run batch processes or one-time tasks in Kubernetes.
- They ensure that a specified number of Pods successfully terminate, and they can be used for tasks like database migrations, data processing, or any task that needs to run to completion.
- They, too are containerized and run in Pods, but they are not meant to be long-running like Deployments or StatefulSets.

Sample Job manifest:
```yaml
apiVersion: batch/v1
kind: Job
metadata:
  name: backup
spec:
  template:
    spec:
      containers:
      - name: backup
        image: jakousa/simple-backup-example
        env:
          - name: URL
            value: "postgres://postgres:example@postgres-svc:5432/postgres"
      restartPolicy: Never
```

- The `restartPolicy: Never` ensures that the Job does not restart failed Pods, which is typical for batch jobs.
- The Job will create a Pod that runs the specified container image and executes the backup task.

We could also add a `backoffLimit` to specify how many times the Job should retry before failing:
```yaml
spec:
  backoffLimit: 4
```

This means that if the Job fails, it will retry up to 4 times before marking the Job as failed.

## Using CronJobs ##
- CronJobs are used to run Jobs on a scheduled basis, similar to cron jobs in Linux.
- They allow you to define a schedule using a cron-like syntax.
Sample CronJob manifest:
```yaml
apiVersion: batch/v1
kind: CronJob
metadata:
  name: daily-backup
spec:
  schedule: "0 2 * * *"  # Runs every day at 2
  template:
    spec:
      containers:
      - name: backup
        image: jakousa/simple-backup-example
        env:
          - name: URL
            value: "postgres://postgres:example@postgres-svc:5432/postgres"
      restartPolicy: Never
```

---
# Docker Refresher #
## Docker Commands ##
Building a docker image:

```bash
docker build -t log-output-app .
```

Running a docker container:

```bash
docker run -p 8000:8000 todo-app-fe:2.2
```

Tailing the logs of a running container:

```bash
docker logs -f log-output-container
```

Exit log following mode: `Ctrl+C`

Checking running containers:

```bash
docker ps -a
```

Stopping and removing container:

```bash
docker stop log-output-container
docker rm log-output-container
```

Or force kill:

```bash
docker rm -f log-output-container
```

## Docker Compose Commands ##
Building and running services with Docker Compose:

```bash
docker-compose up --build -d
```

Stopping and removing services with Docker Compose including volumes:

```bash
docker-compose down -v
```

# Using Busybox for debugging #

## Setting up a Busybox Pod ##
```yaml
apiVersion: v1
kind: Pod
metadata:
  name: my-busybox
  labels:
    app: my-busybox
spec:
  containers:
  - image: busybox
    command:
      - sleep
      - "3600"
    imagePullPolicy: IfNotPresent
    name: busybox
  restartPolicy: Always
```
## Accessing the Busybox Pod ##
```bash
kubectl exec -it my-busybox -- wget -qO - http://todo-backend-svc:2345
```

Change name to your service name and port.

Also possible to try out with the real IP!

1. Get the IP of the service:

```bash
kubectl get svc
```
2. Use the IP in the command:

```bash
kubectl exec -it my-busybox -- wget -qO - http://<service-ip>:2345
```


Opening a shell in the Busybox Pod:

```bash
kubectl exec -it my-busybox -- sh
```

---
# Azure Kubernetes Service (AKS) #

## Azure CLI Commands ##
Installing Azure CLI on macOS:
```bash
brew install azure-cli
```

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

## Setting up AKS Cluster ##
Creating an AKS cluster:
```bash
az aks create --resource-group kubernetes-learning --name kube-mooc --node-count 1 --enable-addons monitoring --generate-ssh-keys
```

## Connecting Kubectl to AKS ##
```bash
az aks get-credentials --resource-group kubernetes-learning --name kube-mooc
```

Checking the connection:
```bash
kubectl get nodes
```

Switching between local context and AKS context:
```bash
kubectl config get-contexts
kubectl config use-context <context-name>
```

---
# Commands for the Gateway API creation #
1. az extension add --name alb
2. az extension add --name aks-preview --allow-preview true
3. RESOURCE_GROUP='kubernetes-learning'
4. AKS_NAME='kube-mooc'
5. az ad signed-in-user show --query id -o tsv
6. az role assignment create --assignee bc93447d-4d22-42bf-8852-88938a57dd5b --role "Contributor" --resource-group kubernetes-learning
7. az aks update -g $RESOURCE_GROUP -n $AKS_NAME --enable-managed-identity
8. az aks update -g $RESOURCE_GROUP -n $AKS_NAME --enable-oidc-issuer --enable-workload-identity --no-wait
9. az aks disable-addons -g $RESOURCE_GROUP -n $AKS_NAME --addons monitoring
10. az aks enable-addons -g $RESOURCE_GROUP -n $AKS_NAME --addons monitoring
11. IDENTITY_RESOURCE_NAME='azure-alb-identity'
12. mcResourceGroup=$(az aks show --resource-group $RESOURCE_GROUP --name $AKS_NAME --query "nodeResourceGroup" -o tsv)
13. mcResourceGroupId=$(az group show --name $mcResourceGroup --query id -otsv)
14. echo "Creating identity $IDENTITY_RESOURCE_NAME in resource group $RESOURCE_GROUP"
15. az identity create --resource-group $RESOURCE_GROUP --name $IDENTITY_RESOURCE_NAME
16. principalId="$(az identity show -g $RESOURCE_GROUP -n $IDENTITY_RESOURCE_NAME --query principalId -otsv)"
17. az role assignment create --assignee-object-id $principalId --assignee-principal-type ServicePrincipal --scope $mcResourceGroupId --role "acdd72a7-3385-48ef-bd42-f606fba81ae7"
18. AKS_OIDC_ISSUER="$(az aks show -n "$AKS_NAME" -g "$RESOURCE_GROUP" --query "oidcIssuerProfile.issuerUrl" -o tsv)"
19. HELM_NAMESPACE='azure-alb-system'
20. CONTROLLER_NAMESPACE='azure-alb-system'
21. az aks get-credentials --resource-group $RESOURCE_GROUP --name $AKS_NAME
22. kubectl create namespace azure-alb-system namespace/azure-alb-system created
23. helm install alb-controller oci://mcr.microsoft.com/application-lb/charts/alb-controller \
     --namespace $HELM_NAMESPACE \
     --version 1.7.9 \
     --set albController.namespace=$CONTROLLER_NAMESPACE \
     --set albController.podIdentity.clientID=$(az identity show -g $RESOURCE_GROUP -n azure-alb-identity --query clientId -o tsv)
24. kubectl get pods -n azure-alb-system
25. helm list -n $HELM_NAMESPACE
26. kubectl get pod -A -l app=alb-controller
27. kubectl get gatewayclass azure-alb-external -o yaml

Subnet for ALB Association
28. MC_RESOURCE_GROUP=$mcResourceGroup
29. MC_RESOURCE_GROUP_ID=$mcResourceGroupId
30. CLUSTER_SUBNET_ID=$(az vmss list --resource-group $MC_RESOURCE_GROUP --query '[0].virtualMachineProfile.networkProfile.networkInterfaceConfigurations[0].ipConfigurations[0].subnet.id' -o tsv)
31. read -d '' VNET_NAME VNET_RESOURCE_GROUP VNET_ID <<< $(az network vnet show --ids $CLUSTER_SUBNET_ID --query '[name, resourceGroup, id]' -o tsv)
32. echo "VNET_NAME=$VNET_NAME, VNET_RESOURCE_GROUP=$VNET_RESOURCE_GROUP, VNET_ID=$VNET_ID"
33. ALB_SUBNET_NAME='subnet-alb'
34. az network vnet show --resource-group $VNET_RESOURCE_GROUP --name $VNET_NAME --query "addressSpace.addressPrefixes" -o tsv
35. az network vnet subnet list --resource-group $VNET_RESOURCE_GROUP --vnet-name $VNET_NAME --query "[].{Name:name, Prefix:addressPrefix}" -o table
36. SUBNET_ADDRESS_PREFIX='10.226.0.0/24'
37. rasmuspaltschik@Rasmuss-MacBook-Pro KubernetesMOOC % az network vnet subnet create \
  --resource-group $VNET_RESOURCE_GROUP \
  --vnet-name $VNET_NAME \
  --name $ALB_SUBNET_NAME \
  --address-prefixes $SUBNET_ADDRESS_PREFIX \
  --delegations 'Microsoft.ServiceNetworking/trafficControllers'
(NetcfgSubnetRangeOutsideVnet) Subnet 'subnet-alb' is not valid because its IP address range is outside the IP address range of virtual network 'aks-vnet-34152116'.
Code: NetcfgSubnetRangeOutsideVnet
Message: Subnet 'subnet-alb' is not valid because its IP address range is outside the IP address range of virtual network 'aks-vnet-34152116'.
38. ALB_SUBNET_ID=$(az network vnet subnet show --name $ALB_SUBNET_NAME --resource-group $VNET_RESOURCE_GROUP --vnet-name $VNET_NAME --query '[id]' --output tsv)

Delegate the subnet to the ALB Controller
39. az role assignment create --assignee-object-id $principalId --assignee-principal-type ServicePrincipal --scope $mcResourceGroupId --role "fbc52c3f-28ad-4303-a892-8a056630b8f1"
40. az role assignment create --assignee-object-id $principalId --assignee-principal-type ServicePrincipal --scope $ALB_SUBNET_ID --role "4d97b98b-1d4f-4787-a291-c67834d212e7"

Install Application Load Balancer
41. ALB='default-alb'
42. 
```bash
tee -a nsa2-alb.yaml > /dev/null <<EOF

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
43. kubectl create namespace nsa2
44.kubectl apply -f nsa2-alb.yaml
45. kubectl -n nsa2 get applicationloadbalancer
46. kubectl -n nsa2 get applicationloadbalancer default-alb -o yaml -w
47. Create the Gateway resource
48. kubectl apply -f manifests/shared/k8s-nsa2-gateway.yaml
49. fqdn=$(kubectl get gateway k8s-nsa2-gateway -n nsa2 -o jsonpath='{.status.addresses[0].value}')

---
# Kustomization #
## Kustomization Basics ##
Apply a kustomization with kubectl:
```bash
kubectl apply -k .
```

Check what kustomization would apply:
```bash
kubectl kustomize .
```

---
# Scaling in Kubernetes #
Example of setting resources in a deployment manifest:
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: cpushredder-dep
spec:
  replicas: 1
  selector:
    matchLabels:
      app: cpushredder
  template:
    metadata:
      labels:
        app: cpushredder
    spec:
      containers:
        - name: cpushredder
          image: jakousa/dwk-app7:e11a700350aede132b62d3b5fd63c05d6b976394
          resources:
            limits:
              cpu: "150m"
              memory: "100Mi"
```

Note the last three rows: it sets limits to memory and CPU. Cpu is calculated in one thousand of CPU cores. 150m means 150 milli CPU, which is 0.15 CPU cores, which is 15% of a single CPU core.

## Horizontal Pod Autoscaling ##
Horizontal Pod Autoscaler is a Kubernetes resource that defines autoscaling for a deployment of replica set based on observed CPU utilization or other select metrics.

Example of a HPA manifest:
```yaml
apiVersion: autoscaling/v1
kind: HorizontalPodAutoscaler
metadata:
  name: cpushredder-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: cpushredder-dep
  minReplicas: 1
  maxReplicas: 6
  targetCPUUtilizationPercentage: 50
```
- `scaleTargetRef` specifies the target deployment to scale. It targets the Deployment kind that has the specified name in this case.
- `minReplicas` and `maxReplicas` define the minimum and maximum number of pod replicas that the HPA can scale to.
- `targetCPUUtilizationPercentage` specifies the desired CPU utilization percentage for the pods. The HPA will adjust the number of replicas to maintain this target utilization.

## Scaling Down and Stability in Kubernetes ##
It is possible to determine what is the scaledown behaviour by definining stabilizationWindowSeconds to less or more than default 300. `stabilizationWindowSeconds` controls the time window for which the HPA will wait before scaling down.
```yaml
behavior:
  scaleDown:
    stabilizationWindowSeconds: 30
```

### Scaling Nodes ###
It is also possible to configure scaling for whole nodes in a Kubernetes cluster. This can be achieved using the Cluster Autoscaler, which automatically adjusts the size of the cluster based on the resource requests of the pods.

This might also move pods between nodes to optimize resource utilization. In this case we want to use the `Pod DisruptionBudget`, which allows us to specify the minimum number of pods that must be available during voluntary disruptions OR maximum for unavailable pods.

```yaml
apiVersion: policy/v1beta1
kind: PodDisruptionBudget
metadata:
  name: example-app-pdb
spec:
  maxUnavailable: 50%
  selector:
    matchLabels:
      app: example-app
```

## Vertical Pod Autoscaler (VPA) ##
There's also a possibility of using a vertical pod autoscaler that handles the scaling vertically, juicing your machine up and down as requested.