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
 