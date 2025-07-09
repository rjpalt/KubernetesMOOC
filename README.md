# KubernetesSubmissions

## Exercises

### Chapter 2

- [1.1](https://github.com/rjpalt/KubernetesMOOC/tree/1.1/log_output)
- [1.2](https://github.com/rjpalt/KubernetesMOOC/tree/1.2/course_project/)
    - Command to add local image: `k3d image import todo-app:latest`
    - Command to add option for local image: `kubectl edit deployment todo-app-server`
    - Command to deploy: `kubectl create deployment todo-app-server --image=todo-app`
    - Command to check logging: `kubectl logs -f todo-app-server-<hash>`
- [1.3](https://github.com/rjpalt/KubernetesMOOC/tree/1.3/log_output)
    - Command to add local image: `k3d image import log-output-app:1.3`
    - Command to deploy: `kubectl apply -f manifests/deployment.yaml`
    - Command to check logging: `kubectl logs -f log-output-<hash>`
- [1.4](https://github.com/rjpalt/KubernetesMOOC/tree/1.4/course_project/)
    - Command to add local image: `k3d image import todo-app:latest`
    - Command to deploy: `kubectl apply -f manifests/deployment.yaml`
    - Command to check logging: `kubectl logs -f todo-app-server-<hash`
- [1.5](https://github.com/rjpalt/KubernetesMOOC/tree/1.5/course_project/)
    - Command to build local image: `docker build -t todo-app:1.5 .`
    - Command to import local image: `k3d image import todo-app:1.5`
    - Command to apply manifests: `kubectl apply -f manifests/deployment.yaml`
        - *Note that running Kubernetes cluster is expected*
    - Command for port forwarding: `kubectl port-forward todo-app-server-<hash> 3003:8000`
- [1.6](https://github.com/rjpalt/KubernetesMOOC/tree/1.6/course_project/)
    - Command to start the k3d cluster: `k3d cluster create --port 8082:30080@agent:0 -p 8081:80@loadbalancer --agents 2`
    - Command to import latest image: `k3d image import todo-app:latest`
    - Command to apply deployment manifest: `kubectl apply -f deployment.yaml`
    - Command to apply service manifest: `kubectl apply -f service.yaml`
    - Check that service is running: `curl http://localhost:8082`
- [1.7](https://github.com/rjpalt/KubernetesMOOC/tree/1.7/log_output)
    - Command to start cluster with specific ports: `k3d cluster create -p "8080:80@loadbalancer" -a 2`
    - Command to import latest image: `k3d image import log-output:1.7`
    - Command to apply deployment manifest: `kubectl apply -f log_output/manifests/deployment.yaml`
    - Command to apply service manifest: `kubectl apply -f log_output/manifests/service.yaml`
    - Command to apply ingress manifest: `kubectl apply -f log_output/manifests/ingress.yaml`
    - Command to check everything is running: `kubectl get pods,svc,ingress`
    - Command to check ingress: `curl http://localhost:8080/`
- [1.8](https://github.com/rjpalt/KubernetesMOOC/tree/1.8/course_project/)
    - Command to start cluster with specific ports: `k3d cluster create -p 8080:80@loadbalancer -a 2`
    - Command to import latest image: `k3d image import todo-app:1.5`
    - Command to apply manifests: `kubectl apply -f course_project/todo-app/manifests/`
    - Command to check everything is running: `kubectl get pods,svc,ingress`
    - Command to check ingress: `curl http://localhost:8080/health`


## Cleanup Script

The repository includes a comprehensive cleanup script (`cleanup.sh`) that helps you reset your development environment by properly shutting down Kubernetes resources before cleaning up Docker containers, networks, and the k3d cluster.

### What the script does:
- **Gracefully shuts down Kubernetes resources** - Deletes deployments, services, and pods in proper order with graceful termination
- **Handles stuck pods** - Force deletes any pods that refuse to terminate gracefully
- **Deletes k3d clusters** - Completely shuts down your Kubernetes cluster after resource cleanup
- **Stops and removes all Docker containers** - Cleans up any running or stopped containers
- **Removes custom Docker networks** - Cleans up networking resources (preserves default networks)
- **Cleans up Docker system** - Removes unused build cache and dangling images
- **Preserves Docker images** - Your built images remain available for reuse
- **Skips Docker volumes** - Leaves volumes untouched for safety

### Usage:
```bash
./cleanup.sh
```

### Additional cleanup:
If you want to remove unused Docker images as well:
```bash
docker image prune -a
```

**Warning:** This script will remove all Docker containers. Make sure you don't have any important data in containers before running it.
