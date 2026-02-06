# Phase 0 Research: Phase IV Local Kubernetes Deployment

**Feature**: 005-k8s-deployment
**Date**: 2026-02-03
**Status**: Complete

## Research Summary

This document captures technology decisions and research findings for Phase IV deployment infrastructure.

---

## R-001: Docker Multi-Stage Builds

### Question
What Docker build strategy optimizes image size and security for production-like deployments?

### Research Findings

**Multi-stage builds** provide optimal balance:
- **Stage 1 (Builder)**: Install build dependencies, compile assets
- **Stage 2 (Runtime)**: Copy only production artifacts, minimal base image

**Frontend (Next.js)**:
```dockerfile
# Stage 1: Build
FROM node:20-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

# Stage 2: Runtime
FROM node:20-alpine AS runner
WORKDIR /app
ENV NODE_ENV=production
COPY --from=builder /app/.next/standalone ./
COPY --from=builder /app/.next/static ./.next/static
COPY --from=builder /app/public ./public
CMD ["node", "server.js"]
```

**Backend (FastAPI)**:
```dockerfile
# Stage 1: Build
FROM python:3.13-slim AS builder
WORKDIR /app
RUN pip install uv
COPY pyproject.toml ./
RUN uv pip install --system --no-cache -r pyproject.toml

# Stage 2: Runtime
FROM python:3.13-slim AS runner
WORKDIR /app
COPY --from=builder /usr/local/lib/python3.13/site-packages /usr/local/lib/python3.13/site-packages
COPY backend/ ./backend/
ENV PYTHONUNBUFFERED=1
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Decision
Use multi-stage builds for all services to reduce image size by 50-70%.

### Alternatives Rejected
- **Single-stage**: Larger images (500MB+ vs 150MB), includes dev tools
- **Distroless**: Limited debugging capability, more complex base image setup

---

## R-002: Helm Chart Architecture

### Question
What Helm chart structure best supports atomic deployment with flexible per-service configuration?

### Research Findings

**Option A: Umbrella Chart with Subcharts**
```
todo-app/
├── Chart.yaml
├── values.yaml
├── charts/
│   ├── frontend/
│   ├── backend/
│   ├── mcp-server/
│   └── ai-agent/
```
- Pros: Clear separation, individual chart versioning
- Cons: More complex dependency management

**Option B: Single Chart with Multiple Templates** (Selected)
```
todo-app/
├── Chart.yaml
├── values.yaml
├── templates/
│   ├── frontend/
│   │   ├── deployment.yaml
│   │   └── service.yaml
│   ├── backend/
│   │   ├── deployment.yaml
│   │   └── service.yaml
│   └── ...
```
- Pros: Simpler structure, single values.yaml, easier versioning
- Cons: All services share chart version

### Decision
Use single Helm chart with organized template directories per service. Simpler for local development without sacrificing functionality.

### Alternatives Rejected
- **Kustomize**: Not mandated by constitution; less templating power
- **Raw kubectl**: Violates Constitution Principle XV (spec-driven infrastructure)

---

## R-003: Kubernetes Service Types

### Question
What service types should be used for internal and external communication?

### Research Findings

| Service | Access Pattern | Recommended Type |
|---------|---------------|------------------|
| Frontend | External (browser) | NodePort |
| Backend | Internal only | ClusterIP |
| MCP Server | Internal only | ClusterIP |
| AI Agent | Internal only | ClusterIP |

**NodePort for Frontend**:
- Minikube-compatible (no LoadBalancer)
- Accessible via `minikube service` command
- Port range: 30000-32767

**ClusterIP for Backend Services**:
- No external exposure needed
- DNS-based discovery: `backend-svc.default.svc.cluster.local`
- More secure (not directly reachable)

### Decision
- Frontend: NodePort (port 30000)
- All others: ClusterIP with internal DNS

### Alternatives Rejected
- **Ingress for frontend**: More complex, requires ingress controller
- **NodePort for all**: Unnecessary exposure, port management overhead

---

## R-004: Secret Management Strategy

### Question
How should secrets be injected without committing them to version control?

### Research Findings

**Option A: Helm --set Flags** (Selected)
```bash
helm install todo-app ./deploy/helm/todo-app \
  --set secrets.databaseUrl="$DATABASE_URL" \
  --set secrets.betterAuthSecret="$BETTER_AUTH_SECRET" \
  --set secrets.openaiApiKey="$OPENAI_API_KEY"
```
- Pros: Simple, no additional tooling, compatible with CI/CD
- Cons: Long command lines, secrets in shell history

**Option B: External Values File**
```bash
helm install todo-app ./deploy/helm/todo-app \
  -f ./secrets-values.yaml  # .gitignored
```
- Pros: Reusable, organized
- Cons: Risk of accidental commit if not careful

**Option C: Kubernetes Secrets Pre-creation**
```bash
kubectl create secret generic todo-secrets \
  --from-env-file=.env
```
- Pros: Standard K8s approach
- Cons: Two-step process, secrets exist before Helm

### Decision
Helm `--set` flags for simplicity. Document in quickstart.md with clear examples.

### Alternatives Rejected
- **Sealed Secrets**: Out of scope for Phase IV (local dev)
- **External Secrets Operator**: Requires cloud provider, out of scope

---

## R-005: Health Probe Configuration

### Question
What health check endpoints and timing configurations ensure reliable pod lifecycle management?

### Research Findings

**FastAPI Health Endpoint**:
```python
@app.get("/health")
def health_check():
    return {"status": "healthy"}

@app.get("/ready")
def readiness_check():
    # Could check DB connection here
    return {"status": "ready"}
```

**Next.js Health Endpoint**:
```typescript
// pages/api/health.ts
export default function handler(req, res) {
  res.status(200).json({ status: 'healthy' })
}
```

**Probe Timing (per Kubernetes best practices)**:

| Probe | Initial Delay | Period | Timeout | Failure Threshold |
|-------|--------------|--------|---------|-------------------|
| Liveness | 30s | 10s | 5s | 3 |
| Readiness | 5s | 5s | 3s | 3 |

### Decision
- Add `/health` and `/ready` endpoints to all services
- Use HTTP probes with progressive timeouts
- Liveness starts after 30s (allow slow startup)
- Readiness starts after 5s (quick traffic routing)

---

## R-006: Minikube Resource Configuration

### Question
What are minimum and recommended resource allocations for local development?

### Research Findings

**Minimum Requirements** (functional but slow):
- CPUs: 2
- Memory: 4GB
- Disk: 20GB

**Recommended Requirements** (comfortable development):
- CPUs: 4
- Memory: 8GB
- Disk: 40GB

**Minikube Start Command**:
```bash
minikube start --cpus=4 --memory=8192 --disk-size=40g
```

**Per-Pod Resource Limits** (Helm values):
```yaml
frontend:
  resources:
    requests:
      cpu: 100m
      memory: 256Mi
    limits:
      cpu: 500m
      memory: 512Mi

backend:
  resources:
    requests:
      cpu: 100m
      memory: 256Mi
    limits:
      cpu: 500m
      memory: 512Mi
```

### Decision
Document minimum and recommended requirements in quickstart.md. Set conservative resource limits in Helm values.

---

## Research Completion Checklist

- [x] R-001: Docker build strategy decided
- [x] R-002: Helm chart structure decided
- [x] R-003: Service types decided
- [x] R-004: Secret management decided
- [x] R-005: Health probes decided
- [x] R-006: Resource requirements decided

**All NEEDS CLARIFICATION items resolved. Ready for Phase 1.**
