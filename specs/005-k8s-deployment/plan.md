# Implementation Plan: Phase IV Local Kubernetes Deployment

**Branch**: `005-k8s-deployment` | **Date**: 2026-02-03 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/005-k8s-deployment/spec.md`

## Summary

Deploy the existing Full-Stack Todo Application (Phase II) and AI-Powered Chatbot (Phase III) to local Kubernetes using Docker containerization, Helm charts for packaging, and AI-assisted DevOps tooling (kubectl-ai, kagent, Gordon). The deployment is fully spec-driven, reproducible, and maintains all existing application functionality without modification.

## Technical Context

**Language/Version**:
- Backend: Python 3.13 (FastAPI)
- Frontend: TypeScript/Node.js 20+ (Next.js)
- Infrastructure: YAML (Helm, Kubernetes manifests)

**Primary Dependencies**:
- Docker Desktop with Docker AI (Gordon)
- Minikube (local Kubernetes)
- Helm v3+
- kubectl with kubectl-ai extension
- kagent for cluster intelligence

**Storage**: External Neon PostgreSQL (via DATABASE_URL)

**Testing**:
- Pod health verification via kubectl
- End-to-end flow validation via frontend
- kagent cluster health analysis

**Target Platform**: Local Minikube cluster (Windows/macOS/Linux)

**Project Type**: Infrastructure/DevOps (no application code changes)

**Performance Goals**:
- All pods running within 5 minutes of Helm install
- Pod recovery within 60 seconds after termination
- Scaling operations complete within 2 minutes

**Constraints**:
- Minikube resource limits (recommended: 4 CPU, 8GB RAM)
- Local-only deployment (no cloud)
- External database connectivity required

**Scale/Scope**:
- 4 services (frontend, backend, mcp-server, ai-agent)
- Single Minikube cluster
- 1-3 replicas per service

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Evidence |
|-----------|--------|----------|
| XIV. Infrastructure-Only Phase | ✅ PASS | No application logic changes; Dockerfiles and Helm only |
| XV. Spec-Driven Infrastructure | ✅ PASS | All work driven by spec.md; plan follows spec → plan → tasks |
| XVI. Local-First Cloud-Native | ✅ PASS | Minikube only; no AWS/GCP/Azure configurations |
| XVII. Reproducible Deployment | ✅ PASS | Helm charts + documented steps; fresh machine deployable |
| XVIII. AI-Assisted DevOps Sovereignty | ✅ PASS | Gordon for Dockerfiles; kubectl-ai for deployments; kagent for health |
| XIX. Failure Diagnosis Protocol | ✅ PASS | All failures diagnosed via kubectl-ai/kagent before fix |
| IV. Monorepo Boundaries | ✅ PASS | Infrastructure code separate from application (deploy/ directory) |
| IX. Stateless Server Law | ✅ PASS | All services remain stateless; database is external |

**Gate Result**: ✅ All constitution checks PASS. Proceeding to Phase 0.

## Project Structure

### Documentation (this feature)

```text
specs/005-k8s-deployment/
├── spec.md              # Feature specification
├── plan.md              # This file
├── research.md          # Phase 0: Technology research
├── data-model.md        # Phase 1: Infrastructure model
├── quickstart.md        # Phase 1: Deployment guide
├── checklists/          # Validation checklists
│   └── requirements.md  # Spec quality checklist
└── contracts/           # Phase 1: Helm value contracts
    └── helm-values.md   # Values.yaml specification
```

### Source Code (repository root)

```text
# Phase IV Infrastructure Structure
deploy/
├── docker/
│   ├── frontend/
│   │   └── Dockerfile           # Next.js container
│   ├── backend/
│   │   └── Dockerfile           # FastAPI container
│   ├── mcp-server/
│   │   └── Dockerfile           # MCP server container
│   └── ai-agent/
│       └── Dockerfile           # AI agent container
│
├── helm/
│   └── todo-app/
│       ├── Chart.yaml           # Helm chart metadata
│       ├── values.yaml          # Default values
│       ├── values-dev.yaml      # Development overrides
│       ├── templates/
│       │   ├── _helpers.tpl     # Template helpers
│       │   ├── frontend/
│       │   │   ├── deployment.yaml
│       │   │   └── service.yaml
│       │   ├── backend/
│       │   │   ├── deployment.yaml
│       │   │   └── service.yaml
│       │   ├── mcp-server/
│       │   │   ├── deployment.yaml
│       │   │   └── service.yaml
│       │   ├── ai-agent/
│       │   │   ├── deployment.yaml
│       │   │   └── service.yaml
│       │   ├── configmap.yaml
│       │   └── secrets.yaml
│       └── .helmignore
│
└── scripts/
    ├── build-images.sh          # Docker build script
    ├── deploy.sh                # Helm deploy script
    └── validate.sh              # Health check script

# Existing Application Structure (UNCHANGED)
frontend/                        # Next.js app (Phase II)
backend/                         # FastAPI app (Phase II + III)
```

**Structure Decision**: Infrastructure code placed in `deploy/` directory, completely separate from application code in `frontend/` and `backend/`. This maintains monorepo boundaries per Constitution Principle IV.

## Complexity Tracking

> No complexity violations. All tooling is mandated by Constitution Phase IV Technology Stack.

| Decision | Justification | Mandated By |
|----------|---------------|-------------|
| 4 separate Dockerfiles | One per service as required | FR-001 to FR-004 |
| Helm charts (not raw kubectl) | Constitution Principle XV | Phase IV Tech Stack |
| AI-assisted tooling | Gordon, kubectl-ai, kagent required | Principle XVIII |

---

## Phase 0: Research & Technology Decisions

### R-001: Docker Multi-Stage Builds for Optimization

**Decision**: Use multi-stage Docker builds for all services

**Rationale**:
- Reduces final image size by 50-70%
- Separates build dependencies from runtime
- Improves security by minimizing attack surface

**Alternatives Considered**:
- Single-stage builds: Larger images, includes build tools
- Distroless images: More complex, limited debugging

### R-002: Helm Chart Structure

**Decision**: Single umbrella chart with subcharts for each service

**Rationale**:
- Enables atomic deployment of entire stack
- Allows individual service upgrades via Helm release
- Centralized values.yaml for environment configuration

**Alternatives Considered**:
- Separate charts per service: More complex coordination
- Kustomize: Less templating power, not mandated by constitution

### R-003: Service Communication Pattern

**Decision**: Internal ClusterIP services with DNS-based discovery

**Rationale**:
- Kubernetes native service discovery
- No external dependencies for service mesh
- Simple configuration via environment variables

**Alternatives Considered**:
- NodePort for all: Exposes internal services unnecessarily
- Ingress for internal: Overkill for local development

### R-004: Secret Injection Strategy

**Decision**: Kubernetes Secrets created from Helm values with `--set` overrides

**Rationale**:
- No secrets in committed files (Constitution Principle III)
- Developer provides values at deploy time
- Compatible with future CI/CD integration

**Alternatives Considered**:
- External secret manager: Out of scope for Phase IV
- Sealed secrets: Adds complexity for local dev

### R-005: Health Probe Configuration

**Decision**: HTTP health endpoints with progressive timeouts

**Rationale**:
- FastAPI has built-in health check capability
- Next.js supports health endpoint configuration
- Kubernetes native probe support

**Configuration**:
- Liveness: `/health` endpoint, 30s initial delay, 10s period
- Readiness: `/ready` endpoint, 5s initial delay, 5s period

---

## Phase 1: Infrastructure Model & Contracts

### Service Topology

```
┌─────────────────────────────────────────────────────────────────┐
│                      Minikube Cluster                            │
│                                                                  │
│  ┌──────────────┐     ┌──────────────┐     ┌──────────────┐    │
│  │   Frontend   │────▶│   Backend    │────▶│  MCP Server  │    │
│  │  (Next.js)   │     │  (FastAPI)   │     │              │    │
│  │   :3000      │     │   :8000      │     │   :8001      │    │
│  └──────────────┘     └──────────────┘     └──────────────┘    │
│         │                    │                    │             │
│         │                    │                    ▼             │
│         │                    │            ┌──────────────┐      │
│         │                    │            │   AI Agent   │      │
│         │                    │            │              │      │
│         │                    │            │   :8002      │      │
│         │                    │            └──────────────┘      │
│         │                    │                    │             │
│         ▼                    ▼                    ▼             │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │                   Kubernetes Services                     │  │
│  │  frontend-svc (NodePort) | backend-svc | mcp-svc | ai-svc│  │
│  └──────────────────────────────────────────────────────────┘  │
│                              │                                  │
└──────────────────────────────│──────────────────────────────────┘
                               │
                               ▼
                    ┌──────────────────┐
                    │  Neon PostgreSQL │
                    │   (External)     │
                    └──────────────────┘
                               │
                               ▼
                    ┌──────────────────┐
                    │    OpenAI API    │
                    │   (External)     │
                    └──────────────────┘
```

### Port Allocation

| Service | Container Port | Service Type | Exposed Port |
|---------|---------------|--------------|--------------|
| Frontend | 3000 | NodePort | 30000 |
| Backend | 8000 | ClusterIP | 8000 |
| MCP Server | 8001 | ClusterIP | 8001 |
| AI Agent | 8002 | ClusterIP | 8002 |

### Environment Variables

| Variable | Service(s) | Source | Required |
|----------|-----------|--------|----------|
| `DATABASE_URL` | backend | K8s Secret | Yes |
| `BETTER_AUTH_SECRET` | frontend, backend | K8s Secret | Yes |
| `BETTER_AUTH_URL` | backend | ConfigMap | Yes |
| `OPENAI_API_KEY` | ai-agent | K8s Secret | Yes |
| `BACKEND_URL` | frontend, mcp-server | ConfigMap | Yes |
| `MCP_SERVER_URL` | ai-agent | ConfigMap | Yes |

### Docker Image Tags

| Image | Tag Pattern | Example |
|-------|-------------|---------|
| todo-frontend | `{version}-{git-sha}` | `1.0.0-abc1234` |
| todo-backend | `{version}-{git-sha}` | `1.0.0-abc1234` |
| todo-mcp-server | `{version}-{git-sha}` | `1.0.0-abc1234` |
| todo-ai-agent | `{version}-{git-sha}` | `1.0.0-abc1234` |

---

## Phase 2: Implementation Tasks

### Task Overview by User Story

| User Story | Tasks | Priority |
|------------|-------|----------|
| US1: Deploy All Services | T001-T008 | P1 |
| US2: Service Communication | T009-T011 | P2 |
| US3: Secrets Management | T012-T014 | P2 |
| US4: Reproducible Deployment | T015-T017 | P3 |
| US5: Pod Health | T018-T020 | P3 |
| US6: Helm Scaling | T021-T022 | P4 |

### Detailed Task Breakdown

See `tasks.md` (generated by `/sp.tasks`) for complete task list with:
- Dependencies
- Expected inputs/outputs
- Responsible agents
- Acceptance criteria

---

## Agent Assignments

| Agent | Responsibilities | Tasks |
|-------|-----------------|-------|
| `dev-environment-validator` | Minikube/Docker/Helm setup | T001 |
| `containerization-docker` | Dockerfile creation via Gordon | T002-T005 |
| `helm-chart-generator` | Helm chart templates | T006-T008, T012-T014 |
| `kubectl-ops` | Kubernetes deployments via kubectl-ai | T009-T011, T018-T020 |
| `kagent` | Cluster health analysis | T021-T022 |
| `phase4-deployment-orchestrator` | Coordination, validation | All phases |

---

## Risk Mitigation Actions

| Risk | Mitigation Task | Owner |
|------|-----------------|-------|
| Minikube resource exhaustion | Document min requirements in quickstart.md | T015 |
| Database connectivity | Validate Neon access before deploy | T009 |
| Docker build failures | Use Gordon AI for troubleshooting | T002-T005 |
| Secret misconfiguration | Fail-fast validation in deploy script | T012 |

---

## Validation Checkpoints

### Checkpoint 1: Environment Ready (after T001)
- [ ] Minikube running with sufficient resources
- [ ] Docker Desktop operational
- [ ] Helm v3+ installed
- [ ] kubectl context set to minikube

### Checkpoint 2: Images Built (after T005)
- [ ] All 4 Docker images built successfully
- [ ] Images available in local registry
- [ ] No build errors or warnings

### Checkpoint 3: Helm Charts Ready (after T008)
- [ ] Chart.yaml valid
- [ ] values.yaml contains all placeholders
- [ ] Templates render without errors
- [ ] `helm lint` passes

### Checkpoint 4: Deployment Complete (after T011)
- [ ] All pods in Running state
- [ ] All services have endpoints
- [ ] Frontend accessible via NodePort
- [ ] Backend responds to health checks

### Checkpoint 5: Full Validation (after T022)
- [ ] End-to-end flow works (create todo → chatbot sees it)
- [ ] Secrets correctly injected
- [ ] Health probes passing
- [ ] kagent reports cluster healthy

---

## Next Steps

1. Run `/sp.tasks` to generate detailed task list
2. Execute tasks in order with assigned agents
3. Validate at each checkpoint
4. Document any deviations in ADR if needed
