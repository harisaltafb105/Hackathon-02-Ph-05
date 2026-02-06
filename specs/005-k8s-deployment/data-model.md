# Infrastructure Model: Phase IV Local Kubernetes Deployment

**Feature**: 005-k8s-deployment
**Date**: 2026-02-03
**Status**: Complete

## Overview

This document defines the infrastructure entities, their relationships, and configuration schemas for Phase IV deployment.

---

## Infrastructure Entities

### 1. Docker Image

Container images built from application source code.

| Attribute | Type | Description |
|-----------|------|-------------|
| `name` | string | Image name (e.g., `todo-frontend`) |
| `tag` | string | Version tag (e.g., `1.0.0-abc1234`) |
| `dockerfile` | path | Path to Dockerfile |
| `context` | path | Build context directory |
| `baseImage` | string | Base image reference |
| `ports` | integer[] | Exposed ports |
| `buildArgs` | map | Build-time arguments |

**Images to Build**:
| Image Name | Dockerfile Path | Build Context | Base Image |
|------------|-----------------|---------------|------------|
| `todo-frontend` | `deploy/docker/frontend/Dockerfile` | `frontend/` | `node:20-alpine` |
| `todo-backend` | `deploy/docker/backend/Dockerfile` | `.` (root) | `python:3.13-slim` |
| `todo-mcp-server` | `deploy/docker/mcp-server/Dockerfile` | `.` (root) | `python:3.13-slim` |
| `todo-ai-agent` | `deploy/docker/ai-agent/Dockerfile` | `.` (root) | `python:3.13-slim` |

---

### 2. Kubernetes Deployment

Declarative specification for running containerized services.

| Attribute | Type | Description |
|-----------|------|-------------|
| `name` | string | Deployment name |
| `replicas` | integer | Number of pod replicas |
| `image` | string | Docker image reference |
| `containerPort` | integer | Application port |
| `resources` | object | CPU/memory requests and limits |
| `env` | object[] | Environment variable references |
| `probes` | object | Liveness and readiness configuration |
| `labels` | map | Kubernetes labels |

**Deployments**:
| Name | Image | Replicas | Port | Labels |
|------|-------|----------|------|--------|
| `frontend` | `todo-frontend:latest` | 1 | 3000 | `app: todo, component: frontend` |
| `backend` | `todo-backend:latest` | 1 | 8000 | `app: todo, component: backend` |
| `mcp-server` | `todo-mcp-server:latest` | 1 | 8001 | `app: todo, component: mcp-server` |
| `ai-agent` | `todo-ai-agent:latest` | 1 | 8002 | `app: todo, component: ai-agent` |

---

### 3. Kubernetes Service

Network abstraction for exposing deployments.

| Attribute | Type | Description |
|-----------|------|-------------|
| `name` | string | Service name |
| `type` | enum | `ClusterIP`, `NodePort`, `LoadBalancer` |
| `port` | integer | Service port |
| `targetPort` | integer | Container port |
| `nodePort` | integer | External port (NodePort only) |
| `selector` | map | Pod selector labels |

**Services**:
| Name | Type | Port | Target Port | Node Port | Selector |
|------|------|------|-------------|-----------|----------|
| `frontend-svc` | NodePort | 3000 | 3000 | 30000 | `component: frontend` |
| `backend-svc` | ClusterIP | 8000 | 8000 | - | `component: backend` |
| `mcp-server-svc` | ClusterIP | 8001 | 8001 | - | `component: mcp-server` |
| `ai-agent-svc` | ClusterIP | 8002 | 8002 | - | `component: ai-agent` |

---

### 4. Kubernetes Secret

Encrypted storage for sensitive configuration.

| Attribute | Type | Description |
|-----------|------|-------------|
| `name` | string | Secret name |
| `type` | string | Secret type (Opaque, tls, etc.) |
| `data` | map | Base64-encoded key-value pairs |

**Secrets**:
| Name | Keys | Referenced By |
|------|------|---------------|
| `todo-secrets` | `DATABASE_URL`, `BETTER_AUTH_SECRET`, `OPENAI_API_KEY` | All deployments |

---

### 5. Kubernetes ConfigMap

Non-sensitive configuration storage.

| Attribute | Type | Description |
|-----------|------|-------------|
| `name` | string | ConfigMap name |
| `data` | map | Key-value configuration pairs |

**ConfigMaps**:
| Name | Keys | Values |
|------|------|--------|
| `todo-config` | `BETTER_AUTH_URL` | `http://frontend-svc:3000` |
| | `BACKEND_URL` | `http://backend-svc:8000` |
| | `MCP_SERVER_URL` | `http://mcp-server-svc:8001` |
| | `NODE_ENV` | `production` |

---

### 6. Helm Chart

Package containing all Kubernetes resources.

| Attribute | Type | Description |
|-----------|------|-------------|
| `name` | string | Chart name |
| `version` | semver | Chart version |
| `appVersion` | string | Application version |
| `dependencies` | object[] | Chart dependencies |

**Chart Metadata**:
```yaml
apiVersion: v2
name: todo-app
description: Todo Application with AI Chatbot - Kubernetes Deployment
type: application
version: 1.0.0
appVersion: "1.0.0"
```

---

## Entity Relationships

```
┌──────────────┐
│  Helm Chart  │
│  (todo-app)  │
└──────┬───────┘
       │ contains
       ▼
┌──────────────────────────────────────────────────────────┐
│                     Templates                             │
│                                                          │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐      │
│  │ Deployments │  │  Services   │  │  ConfigMap  │      │
│  │   (4x)      │  │    (4x)     │  │    (1x)     │      │
│  └──────┬──────┘  └──────┬──────┘  └─────────────┘      │
│         │                │                               │
│         │ uses           │ exposes                       │
│         ▼                ▼                               │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐      │
│  │   Images    │  │    Pods     │  │   Secret    │      │
│  │   (4x)      │  │   (4x)      │  │    (1x)     │      │
│  └─────────────┘  └─────────────┘  └─────────────┘      │
│                                                          │
└──────────────────────────────────────────────────────────┘
```

---

## Resource Requirements

### Per-Service Defaults

```yaml
resources:
  requests:
    cpu: 100m
    memory: 256Mi
  limits:
    cpu: 500m
    memory: 512Mi
```

### Total Cluster Requirements

| Resource | Minimum | Recommended |
|----------|---------|-------------|
| CPU | 800m (0.8 cores) | 2000m (2 cores) |
| Memory | 2Gi | 4Gi |
| Pods | 4 | 4-12 |

---

## Health Probe Schema

### Liveness Probe

```yaml
livenessProbe:
  httpGet:
    path: /health
    port: <containerPort>
  initialDelaySeconds: 30
  periodSeconds: 10
  timeoutSeconds: 5
  failureThreshold: 3
```

### Readiness Probe

```yaml
readinessProbe:
  httpGet:
    path: /ready
    port: <containerPort>
  initialDelaySeconds: 5
  periodSeconds: 5
  timeoutSeconds: 3
  failureThreshold: 3
```

---

## Environment Variable Injection

### From Secret

```yaml
env:
  - name: DATABASE_URL
    valueFrom:
      secretKeyRef:
        name: todo-secrets
        key: DATABASE_URL
```

### From ConfigMap

```yaml
env:
  - name: BACKEND_URL
    valueFrom:
      configMapKeyRef:
        name: todo-config
        key: BACKEND_URL
```

---

## Validation Rules

1. **Image Names**: Must match pattern `todo-[component]:[version]`
2. **Port Ranges**: NodePort must be 30000-32767
3. **Resource Limits**: Must not exceed cluster capacity
4. **Secret Keys**: All required keys must be present before deployment
5. **Labels**: All resources must have `app: todo` label
