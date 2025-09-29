# TODO - Project Tasks

## Current Sprint: Observability, Advanced Deployments & GitOps (Chapter 4)

### Phase 1: Application Health & Probes (Exercises 4.1, 4.2) - ✅ COMPLETE
- [x] **Goal:** Implement readiness probes to improve application stability and startup logic.
- [x] **Actions:**
    - [x] Implement `ReadinessProbe` for Ping-pong and Log output apps (Ex 4.1).
    - [x] Implement probes for the main project (Ex 4.2).

### Phase 2: Advanced Observability & Deployments (Exercises 4.3, 4.4) - ✅ COMPLETE
- [x] **Goal:** Explore advanced monitoring with Prometheus and implement canary deployments.
- [x] **Actions:**
    - [x] Complete Prometheus query exercise (Ex 4.3).
    - [x] Implement canary `AnalysisTemplate` for the Ping-pong app (Ex 4.4).

### Phase 3: Core Feature Enhancement (Exercises 4.5, 4.6) - ✅ COMPLETE
- [x] **Goal:** Add core features to the todo application and improve testing.
- [x] **Actions:**
    - [x] Implement "Done" status update feature (PUT endpoint) (Ex 4.5).
    - [x] Create "broadcaster" service with NATS integration (Ex 4.6).
    - [x] **Testing Improvement:** Enhance E2E tests (map to user stories, implement test data cleanup).

### Phase 4: Initial GitOps Migration (Exercise 4.7) - ✅ COMPLETE
- [x] **Goal:** Take the first step into GitOps by migrating a single, non-critical service.
- [x] **Actions:**
    - [x] Migrate Log output app to GitOps (Ex 4.7).

### Phase 5: Full Project GitOps Adoption (Exercises 4.8 & 4.9) - ✅ COMPLETE (4.8)
- [x] **Goal:** Transition the main application to a full GitOps workflow with environment promotion.
- [x] **Actions:**
    - [x] Migrate the main project to GitOps for the `main` branch (Ex 4.8).
    - [ ] **Establish Staging Environment & Promotion Workflow (Ex 4.9):**
        - [ ] **Epic 1: Foundational Infrastructure Hardening**
            - [ ] **Work Package 1.1: Production DBaaS Migration:** Migrate the production database to a dedicated, managed DBaaS instance.
            - [ ] **Work Package 1.2: Staging Environment Scaffolding:** Create the `staging` namespace, Kustomize overlay, and configure a separate database and unique ingress routing.
        - [ ] **Epic 2: Staging Environment CI/CD Integration & Validation**
            - [ ] **Work Package 2.1: Automated Staging Deployment:** Create a CI/CD workflow (triggered on merge to `main`) that deploys release candidates to the `staging` GitHub environment.
            - [ ] **Work Package 2.2: Advanced Test Suite Integration:** Integrate L2 (service integration) and L3 (E2E) smoke tests into the staging deployment pipeline.
        - [ ] **Epic 3: Production Promotion & Workflow Optimization**
            - [ ] **Work Package 3.1: Staging-to-Production Promotion:** Implement a manual promotion process using a `production` GitHub environment that triggers an Argo Rollouts canary deployment.

### Phase 6: Production Hardening & CI/CD Optimization
- [ ] **Goal:** Improve reliability, performance, and security by validating changes in a dedicated staging environment before production promotion.
- [ ] **Actions:**
    - [ ] **Observability:** Validate and re-establish Prometheus and Grafana monitoring in the staging environment.
    - [ ] **Production Readiness:** Execute **Work Package 1.1 (Production DBaaS Migration)**.
    - [ ] **CI/CD Health:** Disable the failing documentation deployment workflow to reduce pipeline noise.
    - [ ] **CI/CD Reliability (Validated in Staging):** Execute **Work Package 2.2 (Advanced Test Suite Integration)**. This requires QA expertise to define comprehensive L2/L3 smoke tests.
    - [ ] **CI/CD Performance:** Parallelize `course_project` image push jobs to reduce pipeline execution time.
    - [ ] **Frontend Security:** Fix frontend internal API exposure without breaking backend functionality.

### Phase 7: Architectural Refactoring (Exercise 4.10)
- [ ] **Goal:** Decouple application code from Kubernetes configuration to improve maintainability and prepare for advanced deployment strategies.
- [ ] **Actions:**
    - [ ] Separate application code and Kubernetes configuration into dedicated repositories (Ex 4.10).

## Next Sprint: Extending Kubernetes (Chapter 5)

### Phase 8: Custom Resource Definition (CRD) & Controller (Exercise 5.1)
- [ ] **Goal:** Build a custom controller to extend the Kubernetes API.
- [ ] **Tech Focus:** Golang.
- [ ] **Actions:**
    - [ ] **MVP:** Create a `DummySite` CRD and a controller that reconciles it by fetching a URL and creating a basic HTML page.
    - [ ] **Enhancement:** Incrementally improve the controller with more robust features (e.g., status updates, error handling).

### Phase 9: Service Mesh & Advanced Traffic Management (Exercises 5.2, 5.3)
- [ ] **Goal:** Implement and manage a service mesh using Istio.
- [ ] **Actions:**
    - [ ] Install Istio and deploy the sample application (Ex 5.2).
    - [ ] Migrate the `log-output` app to the service mesh and implement traffic splitting between two versions of a new `greeter` service (Ex 5.3).

### Phase 10: Advanced Container Patterns & Serverless (Exercises 5.4, 5.6, 5.7)
- [ ] **Goal:** Explore advanced pod design and event-driven serverless architectures.
- [ ] **Actions:**
    - [ ] Implement an application using `init` and `sidecar` containers (Ex 5.4).
    - [ ] Install and configure Knative for serverless deployments (Ex 5.6).
    - [ ] Convert the `ping-pong` application to run as a serverless service (Ex 5.7).
    - [ ] **Event-Driven CronJob:** Convert the `create_wikipedia_todo` cronjob into a serverless function triggered by NATS events.

### Phase 11: Security & Ecosystem (Exercises 5.5, 5.8)
- [ ] **Goal:** Broaden knowledge of the cloud-native ecosystem and improve security posture.
- [ ] **Actions:**
    - [ ] **NATS Security:** Implement Role-Based Access Control (RBAC) for the NATS deployment to enforce the principle of least privilege.
    - [ ] Conduct a comparative analysis of Kubernetes platforms (e.g., Rancher vs. OpenShift) (Ex 5.5).
    - [ ] Map out personal and project usage of tools within the CNCF Landscape (Ex 5.8).

## Technical Debt & Maintenance Backlog
- [ ] *No items currently in the backlog.*

## Future Enhancements
- [ ] **Federated Authentication:** Implement a federated authentication solution (e.g., OpenID Connect).
- [ ] **Security Hardening:**
    - [ ] Configure Dependabot for automated dependency updates.
    - [ ] Configure CodeQL for static analysis security scanning.
- [ ] **Advanced Preview Environments:** Replace `nip.io` with a proper DNS and certificate solution (ExternalDNS, cert-manager).
- [ ] **Documentation:** Automate OpenAPI documentation publishing.

## Recently Completed
- [x] **GitOps Migration - Main Application (Exercise 4.8):** Successfully transitioned the entire todo-application stack to a fully automated GitOps workflow using ArgoCD. Established a pure GitOps pattern where all production deployments are triggered by Git commits, managed by a single ArgoCD Application, and automatically synced to the cluster. The new workflow (Code → Build → Git Commit → ArgoCD Sync → Deployment) eliminates manual kubectl operations, provides a complete audit trail, and enables self-healing configuration drift correction. This foundational implementation paves the way for multi-environment promotion strategies.
- [x] **GitOps Migration - Log Output Service (Exercise 4.7):** Successfully implemented complete GitOps workflow using ArgoCD, Kustomize, and GitHub Actions. Established automated deployment pipeline (Code → Build → Manifest Update → ArgoCD Sync → Deployment) with zero-downtime deployments. Created reusable base + overlay pattern for Kubernetes manifests, implemented CI/CD automation with Azure ACR integration, and achieved end-to-end validation. ArgoCD accessible at https://20.54.1.117 with operational GitOps foundation ready for scaling to additional services. Implementation serves as proven pattern for future service migrations.
- [x] **Broadcaster Service with NATS Integration (Exercise 4.6):** Implemented comprehensive event-driven architecture with NATS message broker integration. Created broadcaster service that consumes todo events and publishes webhooks to external systems. Established Azure Managed Prometheus monitoring with custom metrics (broadcaster_messages_processed_total, broadcaster_webhook_errors_total). Deployed production-ready monitoring dashboard in Azure Managed Grafana with real-time visualization of message flow from backend → NATS → broadcaster → webhook delivery. Fixed configuration alignment for consistent port usage (8002) across all service components.
- [x] **E2E Test Enhancement for "Done" Feature:** Implemented comprehensive E2E test suite enhancement with 4 new test cases covering complete user journeys for marking todos as "Done". Established production-grade data cleanup infrastructure with advanced HTMX compatibility solutions. Achieved 100% test success rate (20/20 tests passing) with zero regressions and industry-leading technical innovations.
- [x] **Argo Rollouts with Azure Prometheus Integration (Exercise 4.4):** Implemented enterprise-grade sidecar authentication proxy pattern for automated CPU-based analysis and rollback. Established organizational standard for Azure service authentication with SOPS encryption and Workload Identity federation.
- [x] **Resource Management & Scaling (Exercises 3.11 & 3.12):** Established resource quotas, enabled cluster monitoring, and configured autoscaling for production workloads.
- [x] **CI/CD Pipeline Reliability Fix:** Resolved critical GitHub Actions deployment failures by implementing a robust multi-layer health check strategy, replacing unreliable port-forwarding.
- [x] **E2E Testing Foundation:** Implemented a comprehensive Playwright E2E test suite with support for local (Docker Compose) and remote (Kubernetes) execution environments.
- [x] **E2E Testing CI Integration:** Automated the execution of the Playwright E2E suite in a GitHub Actions workflow that runs after feature branch deployments, providing direct feedback on pull requests.
