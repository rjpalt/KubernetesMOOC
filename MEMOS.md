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

## Port FOrwarding ##
```bash
kubectl port-forward hashresponse-dep-57bcc888d7-dj5vk 3003:3000
```

- port-forward targets a resource (in this case, a Pod) and forwards traffic from a local port (3003) to a port on that resource (3000).
- E.g. it pairs a local port to a port on the kubernetes managed resource.


---
# Docker Refresher #
## Docker Commands ##
Building a docker image:

```bash
docker build -t log-output-app .
```

Running a docker container:

```bash
docker run -d --name log-output-container log-output-app
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

