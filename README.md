# KubernetesSubmissions

## CI/CD Pipeline

The repository includes automated testing via GitHub Actions for the todo-app project:

- **Triggers**: Changes to `course_project/todo-app/**` only
- **Tests**: Unit tests, integration tests, container build validation
- **Local testing**: Use `act` to run GitHub Actions locally
  ```bash
  brew install act  # macOS
  act --job test-backend # Backend tests
  act --job test-frontend # Frontend tests
  act --job test-microservice-integration # Microservice integration tests
  ```

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
- [1.9](https://github.com/rjpalt/KubernetesMOOC/tree/1.9/ping-pong)
    - **Note: The link is to ping-pong service, but the ingress is found in [log_output folder](https://github.com/rjpalt/KubernetesMOOC/blob/1.9/log_output/manifests/ingress.yaml)**
    - Command to start cluster with specific ports: `k3d cluster create -p 8080:80@loadbalancer -a 2`
    - Command to import both logout and todo-app images: 
      ```bash
      k3d image import log-output:1.7
      k3d image import ping-pong-app:1.9
      ```
    - Command to apply manifests for ping-pong: `kubectl apply -f ping-pong/manifests/`
    - Command to apply manifests for log-output (incl. shared ingress): `kubectl apply -f log_output/manifests/`
    - Command to check everything is running: `kubectl get pods,svc,ingress`
    - Command to check ingress for todo-app: `curl http://localhost:8080/`
    - Command to check ingress for ping-pong: `curl http://localhost:8080/pingpong`
- [1.10](https://github.com/rjpalt/KubernetesMOOC/tree/1.10/log_output)
    - **Note: This exercise uses the log-generator and log-server images**
    - **Note: The manifests used are generator-server-ingress.yaml, deployment.yaml, generator-service.yaml, logserver-service.yaml**
    - Command to start cluster with specific ports: `k3d cluster create -p 8080:80@loadbalancer -a 2`
    - Commands to import both log-output generator and log-server images:
      ```bash
      k3d image import log-generator:1.10
      k3d image import log-server:1.10
      ```
    - Command to apply manifests for log-generator and log-server:
      ```bash
      kubectl apply -f log_output/manifests/deployment.yaml
      ```
    - Command to apply service manifests:
      ```bash
      kubectl apply -f log_output/manifests/generator-service.yaml
      kubectl apply -f log_output/manifests/logserver-service.yaml
      ```
    - command to apply ingress manifest:
      ```bash
      kubectl apply -f log_output/manifests/generator-server-ingress.yaml
      ```
    - Command to check everything is running: `kubectl get pods,svc,ingress`
    - Command to check ingress for log-generator: `curl http://localhost:8080/health`
    - Command to check log-generator is logging: `kubectl logs -f <log-generator-pod-name>`
    - Command to check log-server is serving the logs: `curl http://localhost:8080/logs`
- [1.11](https://github.com/rjpalt/KubernetesMOOC/tree/1.11/ping-pong)
  - **Note: all commands are run in the ping-pong folder! The exercise was implemented in the separate ping-pong folder to keep refactors separate from the log output service implemented previously.**
  - Command to start cluster with specific ports: `k3d cluster create -p 8080:80@loadbalancer -a 2`
  - Commands to import both ping-pong-app and log-output images:
    ```bash
    k3d image import ping-pong-app:1.11
    k3d image import log-output:1.11
    ```
  - Command to create a persistent volume tmp folder:
    ```bash
    docker exec k3d-k3s-default-agent-0 mkdir -p /tmp/kube
    ```
  - Command to apply persistent volume for shared counter:
    ```bash
    kubectl apply -f ping-pong/manifests/ping-pong-pv.yaml
    ```
  - Command to apply persistent volume claim for shared counter:
    ```bash
    kubectl apply -f ping-pong/manifests/ping-pong-pvc.yaml
    ```
  - Command to apply deployment manifest for ping-pong:
    ```bash
    kubectl apply -f ping-pong/manifests/deployment.yaml
    ```

    **Note: The deployment.yaml file has initContainer section to fix permissions on the shared volume.' The Dockerfiles for the images only grant access to appuser and the access to shared fodler in the persistent volume needs to be granted separately.**
  - Command to apply service manifests for ping-pong and log output:
    ```bash
    kubectl apply -f ping-pong/manifests/ping-pong-service.yaml
    kubectl apply -f log_output/manifests/log-output-service.yaml
    ```
  - Command to apply ingress manifest for ping-pong and log output:
    ```bash
    kubectl apply -f manifests/ingress.yaml
    ```
  - Command to check everything is running: `kubectl get pv,pvc,pods,svc,ingress`
  - Command to check ingress for ping-pong: `curl http://localhost:8080/pingpong`
  - Command to check ingress for log-output: `curl http://localhost:8080/`
  - Command to check shared counter file in the persistent volume:
    ```bash
    kubectl exec -it <insert-pod-name-here> -c log-output -- cat /shared/ping_pong_counter.txt
    ```
- [1.12](https://github.com/rjpalt/KubernetesMOOC/tree/1.12/course_project/todo-app)
  - Command to start cluster with specific ports: `k3d cluster create -p 8080:80@loadbalancer -a 2`
  - Command to create tmp folder in the k3d cluster:
    ```bash
    docker exec k3d-k3s-default-agent-0 mkdir -p /tmp/kube
    ```
  - Command to import todo app image:
    ```bash
    k3d image import todo-app:1.12
    ```
  - Command to apply persistent volume for image cache:
    ```bash
    kubectl apply -f manifests/persistentvolume.yaml
    ```
  - Command to apply persistent volume claim for image cache:
    ```bash
    kubectl apply -f manifests/persistentvolumeclaim.yaml
    ```
  - Command to apply deployment manifest for todo app:
    ```bash
    kubectl apply -f manifests/deployment.yaml
    ```
  - Command to apply service manifest for todo app:
    ```bash
    kubectl apply -f manifests/service.yaml
    ```
  - Command to apply ingress manifest for todo app:
    ```bash
    kubectl apply -f manifests/ingress.yaml
    ```
  - Command to check everything is running: `kubectl get pv,pvc,pods,svc,ingress`
  - Command to check ingress for todo app: `curl http://localhost:8080/`
  - Command to check shared image cache file in the persistent volume:
    ```bash
    kubectl exec -it <insert-pod-name-here> -c todo-app-server -- ls /images
    ```
- [1.13](https://github.com/rjpalt/KubernetesMOOC/tree/1.13/course_project/todo-app)
  - Command to start cluster with specific ports: `k3d cluster create -p 8080:80@loadbalancer -a 2`
  - Command to create tmp folder in the k3d cluster:
    ```bash
    docker exec k3d-k3s-default-agent-0 mkdir -p /tmp/kube
    ```
  - Command to import todo app image:
    ```bash
    k3d image import todo-app:1.13
    ```
  - Command to apply all manifests for todo app (All manifests are unchanged from the previous exercise except deployment image tag):
    ```bash
    kubectl apply -f manifests/
    ```
  - Command to check everything is running: `kubectl get pv,pvc,pods,svc,ingress`
  - Command to check ingress for todo app: `curl http://localhost:8080/`
  - Command to check shared image cache file in the persistent volume:
    ```bash
    kubectl exec -it <insert-pod-name-here> -c todo-app-server -- ls /images
    ``` 
### Chapter 3

- [2.1](https://github.com/rjpalt/KubernetesMOOC/tree/2.1/ping-pong)
  - Command to start cluster with specific ports: `k3d cluster create -p 8080:80@loadbalancer -a 2`
  - Command to add container iamges for ping-pong and log-output:
    ```bash
    k3d image import ping-pong-app:2.1
    k3d image import log-output-app:2.1
    ```
  - Command to apply manifests for ping-pong:
    ```bash
    kubectl apply -f manifests/log-output-deployment.yaml
    kubectl apply -f manifests/ping-pong-deployment.yaml
    kubectl apply -f manifests/log-output-service.yaml
    kubectl apply -f manifests/ping-pong-service.yaml
    kubectl apply -f manifests/ingress.yaml
    ```
  - Command to check everything is running: `kubectl get pv,pvc,pods,svc,ingress`
  - Command to check log-output-app logs are correct:
    ```bash
    kubectl logs -f log-output-app-<hash>
    ```
  - Command to check ping the pingpong endpoint:
    ```bash
    curl http://localhost:8080/pingpong
    ```
- [2.2](https://github.com/rjpalt/KubernetesMOOC/tree/2.2/course_project)
  - **Note: All of the Kubernetes manifests have been moved to folder `course_projectmanifests/` and all kubectl commands are run from the course_project folder.**
  - Command to start cluster with specific ports: `k3d cluster create -p 8080:80@loadbalancer -a 2`
  - Command to create tmp folder in the k3d cluster:
    ```bash
    docker exec k3d-k3s-default-agent-0 mkdir -p /tmp/kube
    ```
  - Command to add container images for todo-app backend and frontend:
    ```bash
    k3d image import todo-app-be:2.2
    k3d image import todo-app-fe:2.2
    ```
  - Command to apply backend manifests:
    ```bash
    kubectl apply -f manifests/todo-be/
    ```
  - Command to apply frontend manifests:
    ```bash
    kubectl apply -f manifests/todo-fe/
    ```
  - Command to apply shared ingress manifest:
    ```bash
    kubectl apply -f manifests/shared/
    ```
  
    


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
