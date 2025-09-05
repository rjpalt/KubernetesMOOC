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
- [3.2](https://github.com/rjpalt/KubernetesMOOC/tree/3.2/ping-pong) - AKS App Routing and Ingress - [Commands](docs/exercises/3.2-commands.md) and [Azure Memos](docs/azure/Azure-memos.md)
  - **Note**: AKS does not come with a default ingress controller. I have added the NGINX ingress controller to the exercises namespace. See the [Azure Memos section Enabling AKS App Routing for Ingress](docs/azure/Azure-memos.md#enabling-aks-app-routing-for-ingress) for details.
- [3.3](https://github.com/rjpalt/KubernetesMOOC/tree/3.3/ping-pong) - AKS Gateway API - [Commands](docs/exercises/3.3-commands.md) and [Azure Memos](docs/azure/Azure-memos.md)
- [3.4](https://github.com/rjpalt/KubernetesMOOC/tree/3.4/ping-pong) - Gateway API Route Rewriting - [Commands](docs/exercises/3.4-commands.md)
- [3.5](https://github.com/rjpalt/KubernetesMOOC/tree/3.5/course_project) - Refactor + Gateway API for Course Project - [Commands](docs/exercises/3.5-commands.md) and [Azure Memos](docs/azure/Azure-memos.md)
- [3.6](https://github.com/rjpalt/KubernetesMOOC/tree/3.6/course_project) - CD Pipeline can be found here: [pipeline yaml](.github/workflows/aks-cd.yaml) and example pipeline run [here](https://github.com/rjpalt/KubernetesMOOC/actions/runs/16798189696)
  - **Note**: The pipelien shows a failure, which was fixed for the next commit, which failed as well. The latter failure for frontend was due to health checks timing out even though the deployment was successful. The problem has been patched and should show correct in consequent runs. The problem is documented in Azure memos [here](docs/azure/Azure-memos.md#aks-gateway-api-health-checks).
- [3.7](https://github.com/rjpalt/KubernetesMOOC/tree/3.7/course_project)
  - Note: Current solution is intentionally simplified for the course and has known security/DevOps gaps. See submission notes and [Azure Memos](docs/azure/Azure-memos.md).
    - Gateway API gets crowded with per-environment path prefixes (e.g., http://d9hqaucbbyazhfem.fz53.alb.azure.com/feature-ex-3-7/)
    - Overlay maintenance overhead: HTTPRoute patches in the feature overlay must be updated whenever new endpoints are introduced
    - QA/preview environments are publicly reachable; no edge auth/allowlisting yet
    - Federated credentials are created per feature branch on an existing managed identity; lifecycle cleanup after branch deletion is not automated yet
    - In a real setup, prefer per-env DNS and stronger isolation; for the course we keep a single ALB and path-based routing
  - Real-life approach (concise):
    - Per-env hostnames (feature-<branch>.preview.example.com) via ExternalDNS + cert-manager; avoid path-prefix crowding
    - Use shared ALB/Gateway for all feature environments; keep production on separate ALB/Gateway for blast radius isolation
    - Add NetworkPolicies and edge auth (Entra ID or OAuth proxy) for preview environment security
    - Consider Azure Functions-based provisioning service: GitHub Actions → OIDC → Azure Function → provision resources; improves security and centralized control
- [3.8](https://github.com/rjpalt/KubernetesMOOC/tree/3.8/course_project) - The environment teardown workflow is implemented in the [cleanup-feature-environment.yaml](.github/workflows/cleanup-feature-environment.yaml) [here](https://github.com/rjpalt/KubernetesMOOC/actions/runs/16858557720/job/47755265970) is an example of the workflow run for deleted branch ex-3-8.
- [3.9](https://github.com/rjpalt/KubernetesMOOC/tree/3.9/course_project) - Implemented Azure Functions for environment provisioning, DBaas for feature environment
  - The revamp of the environment is still a bit in progress. The feature environment is now using a DBaaS solution while production si still using the containerized PostgreSQL. Over the following exercises I will revamp the situation.
  - Now the feature environment uses DNS based routing isntead of using the HTTPRoute URL reqriting, which was clunky. The solution uses nip.io and still has a little bit of work to be done, but it's coming up.
- [3.10](https://github.com/rjpalt/KubernetesMOOC/tree/3.10/course_project) - Containerized database backups to Azure Blob Storage
  - The backup script is located in the [course_project/todo-cron/backup_database.sh](course_project/todo-cron/backup_database.sh) file.
  - The related scripts are located in the [course_project/manifests/base/todo-cron](course_project/manifests/base/todo-cron) directory.
  - Note that the backup script is using a service account with a key and not a managed identity due to technical difficulties in enabling the federated identity token wihin the AKS cluster. This is a stop-gap solution that will be removed in the next step to replace the whole database with a DBaaS solution.
  - The related workflows are running correctly, but they, too, will be refactgored for better usability in the next step.
  - ![Image of backups](https://github.com/user-attachments/assets/9aab15e7-0d98-4f42-ba34-abcc7bf72f18)
- [3.11](https://github.com/rjpalt/KubernetesMOOC/tree/3.11/course_project)
  - Implemented resource limits and resource quotas
  - Later one triggered also a need to define resource quotas for an init-container and the statefulset for PostgreSQL
- [3.12](https://github.com/rjpalt/KubernetesMOOC/tree/3.12/course_project) - HPA and Monitoring
  - **Monitoring Stack**: Azure Monitor for Containers + Azure Managed Prometheus enabled cluster-wide
  - **Autoscaling Strategy**: Production-only HPAs (backend: 1-5 pods, frontend: 1-3 pods) + Cluster Autoscaler (1-5 nodes)
  - **Access**: Azure Portal → Log Analytics Workspace for application logs, Azure Monitor → Metrics for Prometheus data
  - **Implementation**: CPU-based scaling (70% threshold), 60s scale-up/300s scale-down stabilization
  - ![Image of logs in Azure Log Analytics Workspace](https://github.com/user-attachments/assets/51d1aa3b-c5bf-4528-834b-5c2bbd951b78)
 
### Chapter 5

- [4.1](https://github.com/rjpalt/KubernetesMOOC/tree/4.1/ping-pong)
  - ![Starting](https://github.com/user-attachments/assets/25b1046d-0121-4fcf-a409-d11b77957512)
  - ![Waiting for database](https://github.com/user-attachments/assets/ca175f52-34c8-4828-9390-5994929748d7)
  - ![State after database has started](https://github.com/user-attachments/assets/5f582bad-cf8c-4585-960f-826fe4adf547)  
- [4.2](https://github.com/user-attachments/assets/92d5b9ae-0029-4df5-bda6-694748cc126b)
  - ![State after starting a database with corrupted password](https://github.com/user-attachments/assets/92d5b9ae-0029-4df5-bda6-694748cc126b)
  - First command shows the readiness state (0/1)
  - Second command outlines health probe endpoints, timeouts and failure threshold for all probe types
  - Third shows that the pod is not ready even though the pod is running
  - Fourth command intenrally tests the readiness probe endpoint returning 503
  - Fifth command tests the liveness probe which DOES give 200 as expected

# Exercise 3.9: DBaaS vs DIY Containerized Docker #
In this project I decided to change to Azure managed PostgreSQL. The main reasons, on a theoretical side of things, are that running a production and test environment Database yourself gets very thorny quite fast. It's ok, if you have a very simple app that jsut uses a simple PostgreSQL, but if you intend to scale up, it turns into a bottleneck quite fast. I can quickly come up with scenarios where building your own backup system, high availability (HA) solution, redundancy, and maintenance/updates turns into a sysadmin's nightmare. These will require automation and the automation will require upkeep on their behalf and you need to handle it yourself. I would not, personally, want to be responsible of that pile of things if I can avoid it; it is prone to accidents and mistakes and definitely to human errors.

In my opinion DBaaS is actually a very good option to offload database management to a cloud provider if it aligns with your security and data residency requirements. In my opinion, data residency, or very strict data retention policies on your own prem (think of Defense industry, banking) are the only cases where I see alegitimate case to maintaining your own databases. Especially if we have a larger enterprise that requires 24/7/365 operations for teh databases, they need to hire seasoned database administrators on top of the capital expenses for the hardware. If it's a hard requirement, then it must be footed, but in case it is not, most enterprises will probably save with DBaaS solutions. That comes with a caveat, though, having good practices is the key as it's quite eaasy to run your cloud environment very inefficiently and costly.

Now, that is all for the people thinkign about expenses. I decided to implement DBaaS switch for this project and it was not without a hitch. The main driver for the change was that doing mnual backups for a containerized database just felt wrong. Also, managing all the security, networking etc. for the database would be a very challenging case if I would have to do something like implement geo-replication and high-availability while still managing the ACIDity of the database. I just want to outsource to this to a service that will handle it for me. Yes, I could make it work in my very limited scenario, but any larger app will not have the same luxury. Also, I was curious to see how to implement the DBaaS in an AKS cluster, so it was a good learning opportunity.

Going to the cloud the operations will move from uptime, maintenance etc. to managing identity, accesses and security. Building the correct architecture for resource and identity orchestration is its own show and couses a lot of headaches and debugging sessions even in a simple scenario. My environment now has two database servers, one for feature environments and another one for production. Both have managed identities and the feature server has federation for managed identities so I can federate each created namespace in my AKS cluster to be able to access the database from their unique namespace. I have not really gone and tinkered with the firewalls, networking etc., but it would be the next thing to do.

The aim, and reason I spent a lot of hours on this, was to try out something like a developer platform like approach. I have now automation that sets up for every feature branch their own environment with own database and DNS namespace for running tests and checking how the app works. Next step would be to implement E2E tests with playwright to really take advantage out of the separate environments. Under the hood there are Azure Function that handle the provisioning and Kubernetes deployments so that I do not need to over-provision my GitHub Actions runners to be able to deploy things into my AKS cluster.


## Development & Environment Management

The repository includes comprehensive tooling for local development and environment management:

### Quick Commands (Makefile)
```bash
make help           # Show all available commands
make local-dev      # Run app locally (uv) + Docker DB
make compose-up     # Run full stack via docker-compose
make test           # Run all tests (backend + frontend)
make quality        # Code formatting and linting
make azure-start    # Start AKS cluster
make azure-stop     # Stop AKS cluster (save costs)
make clean          # Clean local environment
```

### Environment Cleanup Scripts

**Local development cleanup:**
```bash
./cleanup.sh        # Comprehensive k3d/Docker cleanup
```

**Azure environment management:**
```bash
./azure-stop.sh     # Stop AKS cluster (avoid charges)
./azure-start.sh    # Restart AKS cluster
```

### Cleanup Script Details
The `cleanup.sh` script provides comprehensive environment reset:
- **Kubernetes cleanup** - Helm releases, namespaces, deployments, stuck pods
- **k3d cluster removal** - Complete cluster shutdown after resource cleanup  
- **Docker cleanup** - Containers, networks, build cache (preserves images/volumes)
- **Graceful termination** - Proper shutdown order with force cleanup for stuck resources

**Warning:** This removes all Docker containers. Ensure no important data before running.
