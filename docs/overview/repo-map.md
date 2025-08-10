# Repository map

Purpose: quick orientation and canonical links. No duplication.

- Root
  - README.md — high-level intro; link to onboarding
  - docs/ — canonical documentation
    - overview/ — repo map, onboarding
    - development/ — local dev, script catalog
    - testing/ — project-wide testing index
    - platform/ — manifests index and platform notes
- course_project/
  - README.md — course-level intro and onboarding entry
  - DOCS_ROADMAP.md — roadmap and tracking for docs/DX
  - TESTING_OVERVIEW.md — project-wide testing strategy (to be added)
  - todo-backend/ — backend service
    - tests/TEST_PLAN.md — canonical backend testing plan
    - docker-compose.dev.yml — Postgres for local dev + test DB (authoritative for BE dev DB)
    - start-dev.sh, start-db.sh, test-all.sh — backend scripts
  - todo-app/ — frontend service
    - TEST_PLAN.md — canonical frontend testing plan (to be added)
  - manifests/ — K8s base/overlays for course project (see platform index)
- cluster-manifests/ — cluster-scoped manifests (see platform index)
- log_output/, ping-pong/ — additional services/utilities (see their READMEs)

See also:
- Onboarding: docs/overview/onboarding.md
- Local development: docs/development/local-dev.md
- Script catalog: docs/development/script-catalog.md
- Testing index: docs/testing/index.md
- Manifests index: docs/platform/manifests-index.md
