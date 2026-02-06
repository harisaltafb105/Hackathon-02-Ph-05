# Helm Values Contract: Todo App Chart

**Feature**: 005-k8s-deployment
**Date**: 2026-02-03
**Chart**: `todo-app`

## Overview

This document specifies the `values.yaml` schema for the Todo App Helm chart. All values are configurable at deploy time via `--set` or `-f` flags.

---

## Values Schema

### Global Settings

```yaml
# Global configuration applied to all services
global:
  # Image pull policy: Always, IfNotPresent, Never
  imagePullPolicy: IfNotPresent

  # Common labels applied to all resources
  labels:
    app: todo
    environment: development
```

### Secrets Configuration

```yaml
# Secrets - MUST be provided at deploy time
# NEVER commit actual values to version control
secrets:
  # Neon PostgreSQL connection string
  # Format: postgresql://user:password@host/database?sslmode=require
  databaseUrl: "PLACEHOLDER_DATABASE_URL"

  # Better Auth shared secret for JWT signing
  # Must match between frontend and backend
  betterAuthSecret: "PLACEHOLDER_BETTER_AUTH_SECRET"

  # OpenAI API key for AI agent
  # Format: sk-xxxxxxxxxxxxxxxx
  openaiApiKey: "PLACEHOLDER_OPENAI_API_KEY"
```

### Frontend Configuration

```yaml
frontend:
  # Enable/disable frontend deployment
  enabled: true

  # Replica count
  replicaCount: 1

  # Docker image configuration
  image:
    repository: todo-frontend
    tag: latest
    pullPolicy: IfNotPresent

  # Service configuration
  service:
    type: NodePort
    port: 3000
    targetPort: 3000
    nodePort: 30000

  # Resource limits
  resources:
    requests:
      cpu: 100m
      memory: 256Mi
    limits:
      cpu: 500m
      memory: 512Mi

  # Health probes
  probes:
    liveness:
      path: /api/health
      initialDelaySeconds: 30
      periodSeconds: 10
    readiness:
      path: /api/health
      initialDelaySeconds: 5
      periodSeconds: 5

  # Environment variables (non-sensitive)
  env:
    NODE_ENV: production
    NEXT_PUBLIC_API_URL: http://backend-svc:8000
```

### Backend Configuration

```yaml
backend:
  # Enable/disable backend deployment
  enabled: true

  # Replica count
  replicaCount: 1

  # Docker image configuration
  image:
    repository: todo-backend
    tag: latest
    pullPolicy: IfNotPresent

  # Service configuration
  service:
    type: ClusterIP
    port: 8000
    targetPort: 8000

  # Resource limits
  resources:
    requests:
      cpu: 100m
      memory: 256Mi
    limits:
      cpu: 500m
      memory: 512Mi

  # Health probes
  probes:
    liveness:
      path: /health
      initialDelaySeconds: 30
      periodSeconds: 10
    readiness:
      path: /health
      initialDelaySeconds: 5
      periodSeconds: 5

  # Environment variables (non-sensitive)
  env:
    PYTHONUNBUFFERED: "1"
    BETTER_AUTH_URL: http://frontend-svc:3000
```

### MCP Server Configuration

```yaml
mcpServer:
  # Enable/disable MCP server deployment
  enabled: true

  # Replica count
  replicaCount: 1

  # Docker image configuration
  image:
    repository: todo-mcp-server
    tag: latest
    pullPolicy: IfNotPresent

  # Service configuration
  service:
    type: ClusterIP
    port: 8001
    targetPort: 8001

  # Resource limits
  resources:
    requests:
      cpu: 100m
      memory: 256Mi
    limits:
      cpu: 500m
      memory: 512Mi

  # Health probes
  probes:
    liveness:
      path: /health
      initialDelaySeconds: 30
      periodSeconds: 10
    readiness:
      path: /health
      initialDelaySeconds: 5
      periodSeconds: 5

  # Environment variables (non-sensitive)
  env:
    BACKEND_URL: http://backend-svc:8000
```

### AI Agent Configuration

```yaml
aiAgent:
  # Enable/disable AI agent deployment
  enabled: true

  # Replica count
  replicaCount: 1

  # Docker image configuration
  image:
    repository: todo-ai-agent
    tag: latest
    pullPolicy: IfNotPresent

  # Service configuration
  service:
    type: ClusterIP
    port: 8002
    targetPort: 8002

  # Resource limits
  resources:
    requests:
      cpu: 100m
      memory: 256Mi
    limits:
      cpu: 500m
      memory: 512Mi

  # Health probes
  probes:
    liveness:
      path: /health
      initialDelaySeconds: 30
      periodSeconds: 10
    readiness:
      path: /health
      initialDelaySeconds: 5
      periodSeconds: 5

  # Environment variables (non-sensitive)
  env:
    MCP_SERVER_URL: http://mcp-server-svc:8001
    OPENAI_MODEL: gpt-4
```

---

## Required Values

The following values MUST be provided at deploy time:

| Value Path | Description | Example |
|------------|-------------|---------|
| `secrets.databaseUrl` | PostgreSQL connection string | `postgresql://user:pass@host/db` |
| `secrets.betterAuthSecret` | JWT signing secret | `my-secret-key-min-32-chars` |
| `secrets.openaiApiKey` | OpenAI API key | `sk-...` |

---

## Deploy Time Override Examples

### Minimal Deployment

```bash
helm install todo-app ./deploy/helm/todo-app \
  --set secrets.databaseUrl="$DATABASE_URL" \
  --set secrets.betterAuthSecret="$BETTER_AUTH_SECRET" \
  --set secrets.openaiApiKey="$OPENAI_API_KEY"
```

### Custom Replica Count

```bash
helm install todo-app ./deploy/helm/todo-app \
  --set secrets.databaseUrl="$DATABASE_URL" \
  --set secrets.betterAuthSecret="$BETTER_AUTH_SECRET" \
  --set secrets.openaiApiKey="$OPENAI_API_KEY" \
  --set backend.replicaCount=3
```

### Different NodePort

```bash
helm install todo-app ./deploy/helm/todo-app \
  --set secrets.databaseUrl="$DATABASE_URL" \
  --set secrets.betterAuthSecret="$BETTER_AUTH_SECRET" \
  --set secrets.openaiApiKey="$OPENAI_API_KEY" \
  --set frontend.service.nodePort=30001
```

### Using Values File

Create `my-values.yaml` (add to .gitignore):
```yaml
secrets:
  databaseUrl: "postgresql://..."
  betterAuthSecret: "..."
  openaiApiKey: "sk-..."

backend:
  replicaCount: 2
```

```bash
helm install todo-app ./deploy/helm/todo-app -f my-values.yaml
```

---

## Validation Rules

1. **secrets.databaseUrl**: Must be valid PostgreSQL URL format
2. **secrets.betterAuthSecret**: Must be at least 32 characters
3. **secrets.openaiApiKey**: Must start with `sk-`
4. **\*.replicaCount**: Must be >= 1
5. **\*.service.nodePort**: Must be in range 30000-32767
6. **\*.resources.limits**: Must be >= requests

---

## Default Values Summary

| Service | Replicas | Port | Service Type |
|---------|----------|------|--------------|
| frontend | 1 | 3000 | NodePort (30000) |
| backend | 1 | 8000 | ClusterIP |
| mcpServer | 1 | 8001 | ClusterIP |
| aiAgent | 1 | 8002 | ClusterIP |
