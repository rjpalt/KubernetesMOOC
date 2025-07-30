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