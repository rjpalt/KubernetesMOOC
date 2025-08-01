# KubernetesSubmissions

## Code Quality & Pre-commit Hooks

Pre-commit hooks are configured for automated code quality checks:

- **Configuration**: `.pre-commit-config.yaml` with course_project code quality enforcement
- **Tools**: Black formatting, isort imports, flake8 linting via shared configs
- **Activation**: Run `pre-commit install` from repository root to enable git hooks
- **Manual check**: Use `course_project/quality.sh --check` for manual validation

## CI/CD Pipeline

The repository includes automated testing via GitHub Actions for the todo-app project:

- **Triggers**: Changes to `course_project/**` only
- **Tests**: Unit tests, integration tests, container build validation
- **Local testing**: Use `act` to run GitHub Actions locally
  ```bash
  brew install act  # macOS
  
  # Create a .secrets file with test credentials (already gitignored)
  cp .secrets.example .secrets
  
  # Run specific jobs
  act --job test-backend # Backend tests
  act --job test-frontend # Frontend tests
  act --job code-quality # Code quality checks
  
  # Run all jobs
  act
  ```

## Exercises

See [Common Commands](docs/exercises/common-commands.md) for frequently used patterns.

### Chapter 2

- [1.1](https://github.com/rjpalt/KubernetesMOOC/tree/1.1/log_output) - Basic deployment - [Commands](docs/exercises/1.1-commands.md)
- [1.2](https://github.com/rjpalt/KubernetesMOOC/tree/1.2/course_project/) - Manual deployment - [Commands](docs/exercises/1.2-commands.md)
- [1.3](https://github.com/rjpalt/KubernetesMOOC/tree/1.3/log_output) - Manifest-based deployment - [Commands](docs/exercises/1.3-commands.md)
- [1.4](https://github.com/rjpalt/KubernetesMOOC/tree/1.4/course_project/) - Todo app with manifests - [Commands](docs/exercises/1.4-commands.md)
- [1.5](https://github.com/rjpalt/KubernetesMOOC/tree/1.5/course_project/) - Port forwarding - [Commands](docs/exercises/1.5-commands.md)
- [1.6](https://github.com/rjpalt/KubernetesMOOC/tree/1.6/course_project/) - Services introduction - [Commands](docs/exercises/1.6-commands.md)
- [1.7](https://github.com/rjpalt/KubernetesMOOC/tree/1.7/log_output) - Services and Ingress - [Commands](docs/exercises/1.7-commands.md)
- [1.8](https://github.com/rjpalt/KubernetesMOOC/tree/1.8/course_project/) - Todo app with ingress - [Commands](docs/exercises/1.8-commands.md)
- [1.9](https://github.com/rjpalt/KubernetesMOOC/tree/1.9/ping-pong) - Multi-service deployment - [Commands](docs/exercises/1.9-commands.md)
- [1.10](https://github.com/rjpalt/KubernetesMOOC/tree/1.10/log_output) - Log generator and server - [Commands](docs/exercises/1.10-commands.md)
- [1.11](https://github.com/rjpalt/KubernetesMOOC/tree/1.11/ping-pong) - Persistent volumes - [Commands](docs/exercises/1.11-commands.md)
- [1.12](https://github.com/rjpalt/KubernetesMOOC/tree/1.12/course_project/todo-app) - Image caching with PV - [Commands](docs/exercises/1.12-commands.md)
- [1.13](https://github.com/rjpalt/KubernetesMOOC/tree/1.13/course_project/todo-app) - Updated image deployment - [Commands](docs/exercises/1.13-commands.md)

### Chapter 3

- [2.1](https://github.com/rjpalt/KubernetesMOOC/tree/2.1/ping-pong) - Resource management - [Commands](docs/exercises/2.1-commands.md)
- [2.2](https://github.com/rjpalt/KubernetesMOOC/tree/2.2/course_project) - Microservices architecture - [Commands](docs/exercises/2.2-commands.md)
- [2.3](https://github.com/rjpalt/KubernetesMOOC/tree/2.3/ping-pong) - Namespaces introduction - [Commands](docs/exercises/2.3-commands.md)
- [2.4](https://github.com/rjpalt/KubernetesMOOC/tree/2.4/course_project) - Todo app with namespaces - [Commands](docs/exercises/2.4-commands.md)
- [2.5](https://github.com/rjpalt/KubernetesMOOC/tree/2.5/ping-pong) - ConfigMaps and organization - [Commands](docs/exercises/2.5-commands.md)
- [2.6](https://github.com/rjpalt/KubernetesMOOC/tree/2.6/course_project) - Environment configuration - [Commands](docs/exercises/2.6-commands.md)
- [2.7](https://github.com/rjpalt/KubernetesMOOC/tree/2.7/ping-pong) - Secrets and database - [Commands](docs/exercises/2.7-commands.md)
- [2.8](https://github.com/rjpalt/KubernetesMOOC/tree/2.8/course_project) - Full stack with PostgreSQL - [Commands](docs/exercises/2.8-commands.md)
- [2.9](https://github.com/rjpalt/KubernetesMOOC/tree/2.9/course_project) - CronJobs - [Commands](docs/exercises/2.9-commands.md)
- [2.10](https://github.com/rjpalt/KubernetesMOOC/tree/2.10/course_project) - Monitoring with Prometheus, Grafana, and Loki - [Commands](docs/exercises/2.10-commands.md)
  - Architecture note: Frontend handles form validation before internal backend API calls. Direct backend testing requires port-forwarding to service.
  - Screenshots of logging and Loki running in Grafana:
    - ![Image of logs to backend](https://github.com/user-attachments/assets/a883577e-17bd-465f-aae4-c2c0fc1aa576)
    - ![Image of things showing in Grafana/Loki](https://github.com/user-attachments/assets/1cba766c-f513-4b75-8ccc-87f6e7c0d1fb) 

### Chapter 4

- [3.1](https://github.com/rjpalt/KubernetesMOOC/tree/3.1/ping-pong) - Azure resource setup - [Commands](docs/exercises/3.1-commands.md) and [Azure Memos](docs/azure/Azure-memos.md)
- [3.2](https://github.com/rjpalt/KubernetesMOOC/tree/3.2/ping-pong)
  - **Note**: AKS does not come with a default ingress controller. I have added the NGINX ingress controller to the exercises namespace. See the [Azure Memos section Enabling AKS App Routing for Ingress](docs/azure/Azure-memos.md#enabling-aks-app-routing-for-ingress) for details.

## Cleanup Script

The repository includes a comprehensive cleanup script (`cleanup.sh`) that helps you reset your development environment by properly shutting down Kubernetes resources before cleaning up Docker containers, networks, and the k3d cluster.

Separate scripts for Azure environment stop and start the AKS cluster from incurring extra costs while not in use. These are found in the root directory as `azure-stop.sh` and `azure-start.sh`.

### What the script does:
- **Cleans up Helm releases** - Properly uninstalls Prometheus, Grafana, and Loki monitoring stacks
- **Deletes monitoring namespaces** - Removes prometheus and loki-stack namespaces with cascade cleanup
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
