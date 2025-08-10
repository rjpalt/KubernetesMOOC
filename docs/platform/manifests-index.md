# Manifests index

Purpose: explain where manifests live and their scope. No commands here.

Locations
- course_project/manifests/ — base and overlays for course project deployments
- cluster-manifests/ — cluster-scoped resources / examples
- Service-level manifests (e.g., within todo-app or todo-backend) — service-local references

Scope and intent
- Current repo keeps manifests for learning and development. Production GitOps is planned and will likely move manifests to a separate repo. This page will link to that repo when it exists.
- Do not assume these folders are authoritative for production.

Navigation
- Each manifests folder should contain a concise README explaining scope and linking back here.
- For details on application readiness and health endpoints, see the backend TEST_PLAN and service READMEs.
