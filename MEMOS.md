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

**Deployment of local image**

```bash
kubectl create deployment hashgenerator-dep --image=log-output-app
``` 
image import

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

