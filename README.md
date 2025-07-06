# KubernetesSubmissions

## Exercises

### Chapter 2

- [1.1](https://github.com/rjpalt/KubernetesMOOC/tree/1.1/log_output)
- [1.2](https://github.com/rjpalt/KubernetesMOOC/tree/1.2/course_project)
    - Command to add local image: `k3d image import todo-app:latest`
    - Command to add option for local image: `kubectl edit deployment todo-app-server`
    - Command to deploy: `kubectl create deployment todo-app-server --image=todo-app`
    - Command to check logging: `kubectl logs -f todo-app-server-<hash>`