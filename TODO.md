# TODO - Project Tasks

## Current Sprint: Resource Management & Scaling (Exercises 3.11 & 3.12)

### Phase 0: Prerequisite Knowledge (You)
- [x] **Action:** Read the course section on scaling and watch the video. This will provide the necessary background for the next steps.

### Phase 1: Resource Governance (Exercise 3.11)
- [x] **Goal:** Establish resource limits and namespace quotas.
- [x] **Actions:**
    - [x] Define CPU/memory requests and limits for all project deployments.
    - [x] Implement ResourceQuota objects for production and feature namespaces.

### Phase 1.5: Debugging Feature Deployments
- [x] **Goal:** Diagnose why `ResourceQuotas` were not enforced in feature branch deployments.
- [x] **Actions:**
    - [x] Investigate the deployment function's handling of kustomize overlays.
    - [x] Verify that `resourcequota.yaml` is correctly included in the kustomize build.
    - [x] Confirm the deployment function has sufficient permissions to apply `ResourceQuotas`.

### Phase 2: Monitoring & Autoscaling (Exercise 3.12)
- [x] **Goal:** Enable monitoring and configure automatic scaling.
- [x] **Architectural Plan:**
    - [x] **1. Enable Cluster Monitoring:**
        - [x] Enable Azure Monitor for containers on the AKS cluster.
        - [x] Enable the Azure Managed Prometheus add-on.
    - [x] **2. Implement Autoscaling (Production Only):**
        - [x] Implement Horizontal Pod Autoscalers (HPA) for frontend and backend.
        - [x] Verify the Cluster Autoscaler is enabled on the node pool.
    - [x] **3. Validate End-to-End:**
        - [x] Confirm logs and metrics are visible in Azure Monitor.
        - [x] Perform a load test to trigger and observe HPA and Cluster Autoscaler activity.

### Phase 3: Validation & Learning
- [ ] **Goal:** See the system work.
- [ ] **Action:** Perform a simple load simulation to trigger and observe both pod and node scaling.

## Next Up
- [ ] **Review CI/CD Pipeline:** Audit the `main` branch's deployment workflow for optimizations and best practices.

## Future Enhancements
- [ ] **Security Hardening:**
    - [ ] Configure Dependabot for automated dependency updates.
    - [ ] Configure CodeQL for static analysis security scanning.
    - [ ] Enforce branch protection rules on `main`.
- [ ] **GitOps:** Implement a GitOps workflow using a separate configuration repository for tracking deployed state.
    - [ ] Switch production environment from containerized database to DBaaS. Use existing prod PostgreSQL instance.
- [ ] **Advanced Preview Environments:** Replace `nip.io` with a proper DNS and certificate solution (ExternalDNS, cert-manager).
- [ ] **Documentation:** Automate OpenAPI documentation publishing.

## Recently Completed
- [x] **CI/CD Pipeline Reliability Fix:** Resolved critical GitHub Actions deployment failures by implementing a robust multi-layer health check strategy, replacing unreliable port-forwarding.
- [x] **E2E Testing Foundation:** Implemented a comprehensive Playwright E2E test suite with support for local (Docker Compose) and remote (Kubernetes) execution environments.
- [x] **E2E Testing CI Integration:** Automated the execution of the Playwright E2E suite in a GitHub Actions workflow that runs after feature branch deployments, providing direct feedback on pull requests.
