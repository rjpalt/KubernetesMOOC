# TODO - Project Tasks

## Current Sprint: Observability, Advanced Deployments & GitOps (Chapter 4)

### Phase 1: Application Health & Probes (Exercises 4.1, 4.2)
- [ ] **Goal:** Implement readiness probes to improve application stability and startup logic.
- [ ] **Actions:**
    - [x] Implement `ReadinessProbe` for Ping-pong and Log output apps (Ex 4.1).
    - [ ] Implement probes for the main project (Ex 4.2).
    - [ ] **Technical Debt:** Fix frontend internal API exposure without breaking backend functionality.
    - [ ] **CI/CD Health:** Investigate and fix the failing documentation deployment workflow.

### Phase 2: Advanced Observability & Deployments (Exercises 4.3, 4.4)
- [ ] **Goal:** Explore advanced monitoring with Prometheus and implement canary deployments.
- [ ] **Actions:**
    - [ ] Complete Prometheus query exercise (Ex 4.3).
    - [ ] Implement canary `AnalysisTemplate` for the Ping-pong app (Ex 4.4).

### Phase 3: Core Feature Enhancement (Exercises 4.5, 4.6)
- [ ] **Goal:** Add core features to the todo application and improve testing.
- [ ] **Actions:**
    - [ ] Implement "Done" status update feature (PUT endpoint) (Ex 4.5).
    - [ ] Create "broadcaster" service with NATS integration (Ex 4.6).
    - [ ] **Testing Improvement:** Enhance E2E tests (map to user stories, implement test data cleanup).

### Phase 4: GitOps Adoption (Exercises 4.7 - 4.10)
- [ ] **Goal:** Transition the project to a GitOps-centric deployment model using ArgoCD.
- [ ] **Actions:**
    - [ ] Migrate Log output app to GitOps (Ex 4.7).
    - [ ] Migrate the main project to GitOps for the `main` branch (Ex 4.8).
    - [ ] Establish `staging` and `production` environments with GitOps promotion (Ex 4.9).
    - [ ] **Production Readiness:** Migrate production database to DBaaS.
    - [ ] Separate application code and Kubernetes configuration into dedicated repositories (Ex 4.10).

## Future Enhancements
- [ ] **Federated Authentication:** Implement a federated authentication solution (e.g., OpenID Connect).
- [ ] **Security Hardening:**
    - [ ] Configure Dependabot for automated dependency updates.
    - [ ] Configure CodeQL for static analysis security scanning.
- [ ] **Advanced Preview Environments:** Replace `nip.io` with a proper DNS and certificate solution (ExternalDNS, cert-manager).
- [ ] **Documentation:** Automate OpenAPI documentation publishing.

## Recently Completed
- [x] **Resource Management & Scaling (Exercises 3.11 & 3.12):** Established resource quotas, enabled cluster monitoring, and configured autoscaling for production workloads.
- [x] **CI/CD Pipeline Reliability Fix:** Resolved critical GitHub Actions deployment failures by implementing a robust multi-layer health check strategy, replacing unreliable port-forwarding.
- [x] **E2E Testing Foundation:** Implemented a comprehensive Playwright E2E test suite with support for local (Docker Compose) and remote (Kubernetes) execution environments.
- [x] **E2E Testing CI Integration:** Automated the execution of the Playwright E2E suite in a GitHub Actions workflow that runs after feature branch deployments, providing direct feedback on pull requests.
