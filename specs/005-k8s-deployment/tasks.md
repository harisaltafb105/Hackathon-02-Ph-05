# Tasks: Phase IV Local Kubernetes Deployment

**Input**: Design documents from `/specs/005-k8s-deployment/`
**Prerequisites**: plan.md (required), spec.md (required), research.md, data-model.md, contracts/helm-values.md

**Tests**: No explicit test tasks included - validation is via kubectl commands and health checks

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story?] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

Infrastructure paths:
- `deploy/docker/` - Dockerfiles for each service
- `deploy/helm/todo-app/` - Helm chart root
- `deploy/helm/todo-app/templates/` - Kubernetes manifests
- `deploy/scripts/` - Automation scripts

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Create project structure and directory layout for Phase IV infrastructure

- [X] T001 Create deploy directory structure per plan.md in deploy/
- [X] T002 [P] Create deploy/docker/frontend/ directory
- [X] T003 [P] Create deploy/docker/backend/ directory
- [X] T004 [P] Create deploy/docker/mcp-server/ directory
- [X] T005 [P] Create deploy/docker/ai-agent/ directory
- [X] T006 Create deploy/helm/todo-app/ directory with subdirectories (templates/, templates/frontend/, templates/backend/, templates/mcp-server/, templates/ai-agent/)
- [X] T007 Create deploy/scripts/ directory

**Checkpoint**: Directory structure ready for infrastructure files

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure files that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No deployment work can begin until this phase is complete

### Dockerfiles (via Gordon/Docker AI)

- [X] T008 [P] Create Dockerfile for frontend (Next.js multi-stage build) in deploy/docker/frontend/Dockerfile
- [X] T009 [P] Create Dockerfile for backend (FastAPI multi-stage build) in deploy/docker/backend/Dockerfile
- [X] T010 [P] Create Dockerfile for MCP server in deploy/docker/mcp-server/Dockerfile
- [X] T011 [P] Create Dockerfile for AI agent in deploy/docker/ai-agent/Dockerfile

### Helm Chart Foundation

- [X] T012 Create Chart.yaml with metadata (name: todo-app, version: 1.0.0) in deploy/helm/todo-app/Chart.yaml
- [X] T013 Create values.yaml with all service configurations per contracts/helm-values.md in deploy/helm/todo-app/values.yaml
- [X] T014 Create _helpers.tpl with common template functions in deploy/helm/todo-app/templates/_helpers.tpl
- [X] T015 Create .helmignore file in deploy/helm/todo-app/.helmignore

### Kubernetes Shared Resources

- [X] T016 Create secrets.yaml template for sensitive env vars in deploy/helm/todo-app/templates/secrets.yaml
- [X] T017 Create configmap.yaml template for non-sensitive config in deploy/helm/todo-app/templates/configmap.yaml

### Automation Scripts

- [X] T018 [P] Create build-images.sh script for Docker builds in deploy/scripts/build-images.sh
- [X] T019 [P] Create deploy.sh script for Helm deployment in deploy/scripts/deploy.sh
- [X] T020 [P] Create validate.sh script for health checks in deploy/scripts/validate.sh

**Checkpoint**: Foundation ready - user story implementation can now begin

---

## Phase 3: User Story 1 - Deploy All Services (Priority: P1) 🎯 MVP

**Goal**: Deploy all 4 services (frontend, backend, mcp-server, ai-agent) to Minikube with Helm

**Independent Test**: Run `helm install todo-app ./deploy/helm/todo-app` and verify all pods reach Running status

**Agent**: `containerization-docker`, `helm-chart-generator`, `kubectl-ops`

### Frontend Deployment Templates

- [X] T021 [P] [US1] Create deployment.yaml for frontend in deploy/helm/todo-app/templates/frontend/deployment.yaml
- [X] T022 [P] [US1] Create service.yaml for frontend (NodePort:30000) in deploy/helm/todo-app/templates/frontend/service.yaml

### Backend Deployment Templates

- [X] T023 [P] [US1] Create deployment.yaml for backend in deploy/helm/todo-app/templates/backend/deployment.yaml
- [X] T024 [P] [US1] Create service.yaml for backend (ClusterIP:8000) in deploy/helm/todo-app/templates/backend/service.yaml

### MCP Server Deployment Templates

- [X] T025 [P] [US1] Create deployment.yaml for mcp-server in deploy/helm/todo-app/templates/mcp-server/deployment.yaml
- [X] T026 [P] [US1] Create service.yaml for mcp-server (ClusterIP:8001) in deploy/helm/todo-app/templates/mcp-server/service.yaml

### AI Agent Deployment Templates

- [X] T027 [P] [US1] Create deployment.yaml for ai-agent in deploy/helm/todo-app/templates/ai-agent/deployment.yaml
- [X] T028 [P] [US1] Create service.yaml for ai-agent (ClusterIP:8002) in deploy/helm/todo-app/templates/ai-agent/service.yaml

### Validation

- [X] T029 [US1] Run helm lint on chart in deploy/helm/todo-app/
- [X] T030 [US1] Build all Docker images using deploy/scripts/build-images.sh
- [X] T031 [US1] Deploy to Minikube using deploy/scripts/deploy.sh
- [X] T032 [US1] Verify all pods reach Running status with kubectl get pods (requires real DATABASE_URL)

**Checkpoint**: MVP complete - all services deployed and running on Minikube

---

## Phase 4: User Story 2 - Service Communication (Priority: P2)

**Goal**: Validate service-to-service communication works correctly

**Independent Test**: Create todo via frontend, verify it persists and chatbot can access it

**Agent**: `kubectl-ops`

**Depends on**: US1 (all services deployed)

### Environment Configuration

- [X] T033 [US2] Configure frontend environment to use backend-svc DNS in deploy/helm/todo-app/templates/frontend/deployment.yaml
- [X] T034 [US2] Configure backend environment to use DATABASE_URL from secrets in deploy/helm/todo-app/templates/backend/deployment.yaml
- [X] T035 [US2] Configure mcp-server to use backend-svc DNS in deploy/helm/todo-app/templates/mcp-server/deployment.yaml
- [X] T036 [US2] Configure ai-agent to use mcp-server-svc DNS in deploy/helm/todo-app/templates/ai-agent/deployment.yaml

### Validation

- [X] T037 [US2] Verify frontend can reach backend via service DNS
- [X] T038 [US2] Verify backend can connect to Neon PostgreSQL
- [X] T039 [US2] Verify MCP server can reach backend
- [X] T040 [US2] Verify AI agent can reach MCP server and OpenAI API
- [X] T041 [US2] Test end-to-end flow: create todo → backend → database → MCP → AI

**Checkpoint**: Service communication validated - full application flow works

---

## Phase 5: User Story 3 - Secrets Management (Priority: P2)

**Goal**: Ensure secrets are securely injected without committing to version control

**Independent Test**: Deploy with --set flags, verify env vars are available in pods

**Agent**: `helm-chart-generator`

**Can run in parallel with**: US2 (no dependencies between them)

### Secret Templates

- [X] T042 [US3] Ensure secrets.yaml properly encodes DATABASE_URL in deploy/helm/todo-app/templates/secrets.yaml
- [X] T043 [US3] Ensure secrets.yaml properly encodes BETTER_AUTH_SECRET in deploy/helm/todo-app/templates/secrets.yaml
- [X] T044 [US3] Ensure secrets.yaml properly encodes OPENAI_API_KEY in deploy/helm/todo-app/templates/secrets.yaml

### Secret References in Deployments

- [X] T045 [P] [US3] Add secretKeyRef for DATABASE_URL in backend deployment.yaml
- [X] T046 [P] [US3] Add secretKeyRef for BETTER_AUTH_SECRET in frontend and backend deployment.yaml
- [X] T047 [P] [US3] Add secretKeyRef for OPENAI_API_KEY in ai-agent deployment.yaml

### Validation

- [X] T048 [US3] Verify no secrets in committed files (grep for placeholders only)
- [X] T049 [US3] Deploy with --set overrides and verify pods start successfully
- [X] T050 [US3] Exec into pod and verify env vars are present

**Checkpoint**: Secrets management validated - secure credential injection works

---

## Phase 6: User Story 4 - Reproducible Deployment (Priority: P3)

**Goal**: Fresh machine deployment succeeds using only specs and Helm charts

**Independent Test**: Follow quickstart.md on clean environment, full stack deploys

**Agent**: `dev-environment-validator`, `phase4-deployment-orchestrator`

**Depends on**: US1, US2, US3 (deployment and secrets must work)

### Documentation

- [X] T051 [US4] Update deploy/scripts/build-images.sh with complete build commands
- [X] T052 [US4] Update deploy/scripts/deploy.sh with Helm install command and secret placeholders
- [X] T053 [US4] Create values-dev.yaml with development defaults in deploy/helm/todo-app/values-dev.yaml
- [X] T054 [US4] Verify quickstart.md matches actual deployment steps in specs/005-k8s-deployment/quickstart.md

### Validation

- [X] T055 [US4] Run full deployment from scratch following quickstart.md
- [X] T056 [US4] Verify deployment completes within 15 minutes
- [X] T057 [US4] Verify all functionality works after fresh deployment

**Checkpoint**: Reproducibility validated - any developer can deploy

---

## Phase 7: User Story 5 - Pod Health (Priority: P3)

**Goal**: All pods have liveness and readiness probes for self-healing

**Independent Test**: Kill a pod, verify automatic recovery within 60 seconds

**Agent**: `kubectl-ops`, `kagent`

**Can run in parallel with**: US4 (no dependencies between them)

### Health Probe Configuration

- [X] T058 [P] [US5] Add liveness and readiness probes to frontend deployment in deploy/helm/todo-app/templates/frontend/deployment.yaml
- [X] T059 [P] [US5] Add liveness and readiness probes to backend deployment in deploy/helm/todo-app/templates/backend/deployment.yaml
- [X] T060 [P] [US5] Add liveness and readiness probes to mcp-server deployment in deploy/helm/todo-app/templates/mcp-server/deployment.yaml
- [X] T061 [P] [US5] Add liveness and readiness probes to ai-agent deployment in deploy/helm/todo-app/templates/ai-agent/deployment.yaml

### Validation

- [X] T062 [US5] Verify all probes are configured via kubectl describe
- [X] T063 [US5] Kill a pod with kubectl delete pod and verify automatic restart
- [X] T064 [US5] Verify pod recovery completes within 60 seconds
- [X] T065 [US5] Run kagent cluster health analysis

**Checkpoint**: Health probes validated - self-healing infrastructure works

---

## Phase 8: User Story 6 - Helm Scaling (Priority: P4)

**Goal**: Services can scale up/down using Helm values

**Independent Test**: Upgrade with replicaCount=3, verify 3 pods running

**Agent**: `helm-chart-generator`, `kubectl-ops`, `kagent`

**Depends on**: US1, US5 (deployment and health probes must work)

### Scaling Configuration

- [X] T066 [US6] Ensure replicaCount is templated in frontend deployment.yaml
- [X] T067 [US6] Ensure replicaCount is templated in backend deployment.yaml
- [X] T068 [US6] Ensure replicaCount is templated in mcp-server deployment.yaml
- [X] T069 [US6] Ensure replicaCount is templated in ai-agent deployment.yaml

### Validation

- [X] T070 [US6] Scale backend to 3 replicas with helm upgrade --set backend.replicaCount=3
- [X] T071 [US6] Verify 3 backend pods are running within 2 minutes
- [X] T072 [US6] Scale back to 1 replica and verify graceful termination
- [X] T073 [US6] Run kagent to verify cluster health after scaling

**Checkpoint**: Scaling validated - horizontal scalability works

---

## Phase 9: Polish & Cross-Cutting Concerns

**Purpose**: Final validation and documentation updates

- [X] T074 Verify all success criteria from spec.md are met
- [X] T075 Update quickstart.md with any discovered issues or clarifications
- [X] T076 Run full validation suite: build → deploy → test → scale → health check
- [X] T077 Create final deployment verification checklist
- [X] T078 Document any known issues or limitations

---

## Dependencies & Execution Order

### Phase Dependencies

```
Phase 1: Setup ──────────────────────────────┐
                                              │
Phase 2: Foundational ───────────────────────┤
                                              │ BLOCKS
                                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                     User Story Phases                           │
│                                                                 │
│   Phase 3: US1 (P1) ────────┬──────────────────────────────────│
│   Deploy All Services       │                                   │
│                             │                                   │
│                             ▼                                   │
│   Phase 4: US2 (P2) ────────┬───── Phase 5: US3 (P2)          │
│   Service Communication     │      Secrets Management           │
│                             │      (parallel)                   │
│                             │                                   │
│                             ▼                                   │
│   Phase 6: US4 (P3) ────────┬───── Phase 7: US5 (P3)          │
│   Reproducible Deployment   │      Pod Health                   │
│                             │      (parallel)                   │
│                             │                                   │
│                             ▼                                   │
│   Phase 8: US6 (P4) ────────────────────────────────────────────│
│   Helm Scaling                                                  │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
                                              │
                                              ▼
Phase 9: Polish ──────────────────────────────┘
```

### User Story Dependencies

| Story | Depends On | Can Parallel With |
|-------|------------|-------------------|
| US1 (P1) | Foundational | None |
| US2 (P2) | US1 | US3 |
| US3 (P2) | Foundational | US2 |
| US4 (P3) | US1, US2, US3 | US5 |
| US5 (P3) | US1 | US4 |
| US6 (P4) | US1, US5 | None |

### Parallel Opportunities

Within each phase, tasks marked [P] can run in parallel:

```bash
# Phase 1: Create directories in parallel
T002, T003, T004, T005 can run together

# Phase 2: Create Dockerfiles in parallel
T008, T009, T010, T011 can run together

# Phase 2: Create scripts in parallel
T018, T019, T020 can run together

# Phase 3 (US1): Create all deployment templates in parallel
T021, T022, T023, T024, T025, T026, T027, T028 can run together

# Phase 5 (US3): Secret references in parallel
T045, T046, T047 can run together

# Phase 7 (US5): Health probes in parallel
T058, T059, T060, T061 can run together
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup (T001-T007)
2. Complete Phase 2: Foundational (T008-T020)
3. Complete Phase 3: User Story 1 (T021-T032)
4. **STOP and VALIDATE**: Verify all pods Running
5. Demo/checkpoint if ready

### Incremental Delivery

1. Setup + Foundational → Infrastructure ready
2. Add US1 → All services deployed (MVP!)
3. Add US2 + US3 → Full functionality with secure secrets
4. Add US4 + US5 → Production-ready with health and docs
5. Add US6 → Scalable deployment

### Agent Assignment

| Agent | Tasks |
|-------|-------|
| `dev-environment-validator` | T001-T007, T055-T057 |
| `containerization-docker` | T008-T011, T018, T030 |
| `helm-chart-generator` | T012-T017, T021-T028, T042-T047, T066-T069 |
| `kubectl-ops` | T029, T031-T041, T049-T050, T062-T065, T070-T073 |
| `kagent` | T065, T073 |
| `phase4-deployment-orchestrator` | T074-T078 |

---

## Task Summary

| Phase | User Story | Task Count | Parallel Tasks |
|-------|------------|------------|----------------|
| 1 | Setup | 7 | 4 |
| 2 | Foundational | 13 | 7 |
| 3 | US1 (P1) | 12 | 8 |
| 4 | US2 (P2) | 9 | 0 |
| 5 | US3 (P2) | 9 | 3 |
| 6 | US4 (P3) | 7 | 0 |
| 7 | US5 (P3) | 8 | 4 |
| 8 | US6 (P4) | 8 | 0 |
| 9 | Polish | 5 | 0 |
| **Total** | | **78** | **26** |

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story is independently testable at its checkpoint
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- Use AI-assisted tools (Gordon, kubectl-ai, kagent) per Constitution Principle XVIII
