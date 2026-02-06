# MCP Server Docker Container

Production-grade Docker container for the Model Context Protocol (MCP) Server component.

## Overview

The MCP Server provides protocol-level communication for the AI chatbot functionality. This container is designed for deployment in Kubernetes environments with security and performance optimizations.

## Image Details

- **Base Image**: `python:3.13-slim`
- **Build Strategy**: Multi-stage build (builder + production)
- **User**: Non-root user `mcpuser` (UID 1001)
- **Port**: 8001
- **Health Check**: HTTP GET to `/health` every 30s

## Security Features

- Multi-stage build to exclude build-time dependencies
- Non-root user execution (mcpuser:mcpuser)
- Minimal base image (slim variant)
- No secrets embedded in image layers
- Comprehensive .dockerignore to prevent sensitive file inclusion
- Read-only filesystem compatible (application code owned by mcpuser)

## Build Instructions

### Standard Build

```bash
# From project root
docker build -f deploy/docker/mcp-server/Dockerfile -t todo-mcp-server:latest .
```

### Build with Specific Version Tag

```bash
docker build -f deploy/docker/mcp-server/Dockerfile -t todo-mcp-server:1.0.0-local .
```

### No-Cache Build (Clean Build)

```bash
docker build --no-cache -f deploy/docker/mcp-server/Dockerfile -t todo-mcp-server:latest .
```

## Running Locally

### Basic Run

```bash
docker run -d \
  --name mcp-server \
  -p 8001:8001 \
  -e DATABASE_URL="postgresql://user:pass@host:5432/db" \
  -e OPENAI_API_KEY="your-openai-key" \
  todo-mcp-server:latest
```

### Run with Environment File

```bash
docker run -d \
  --name mcp-server \
  -p 8001:8001 \
  --env-file .env \
  todo-mcp-server:latest
```

### Run with Volume Mount (Development)

```bash
docker run -d \
  --name mcp-server \
  -p 8001:8001 \
  -v $(pwd)/backend:/app/backend \
  --env-file .env \
  todo-mcp-server:latest
```

## Environment Variables

### Required

| Variable | Description | Example |
|----------|-------------|---------|
| `DATABASE_URL` | PostgreSQL connection string | `postgresql://user:pass@db:5432/todo` |
| `OPENAI_API_KEY` | OpenAI API key for AI agent | `sk-...` |

### Optional

| Variable | Description | Default |
|----------|-------------|---------|
| `MCP_MODE` | Enable MCP server mode | `true` |
| `MCP_SERVER_HOST` | Server bind address | `0.0.0.0` |
| `MCP_SERVER_PORT` | Server port | `8001` |
| `PYTHONUNBUFFERED` | Disable Python output buffering | `1` |
| `PYTHONDONTWRITEBYTECODE` | Disable .pyc files | `1` |

## Health Checks

The container includes a built-in health check:

- **Endpoint**: `http://localhost:8001/health`
- **Interval**: 30 seconds
- **Timeout**: 5 seconds
- **Start Period**: 10 seconds
- **Retries**: 3

Check container health:

```bash
docker ps --filter name=mcp-server --format "table {{.Names}}\t{{.Status}}"
```

## Kubernetes Deployment

This image is designed for Kubernetes deployment via Helm charts:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: mcp-server
spec:
  replicas: 1
  selector:
    matchLabels:
      app: todo
      component: mcp-server
  template:
    metadata:
      labels:
        app: todo
        component: mcp-server
    spec:
      containers:
      - name: mcp-server
        image: todo-mcp-server:latest
        imagePullPolicy: Never  # For local K8s
        ports:
        - containerPort: 8001
          name: http
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: todo-secrets
              key: DATABASE_URL
        - name: OPENAI_API_KEY
          valueFrom:
            secretKeyRef:
              name: todo-secrets
              key: OPENAI_API_KEY
        livenessProbe:
          httpGet:
            path: /health
            port: 8001
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /health
            port: 8001
          initialDelaySeconds: 5
          periodSeconds: 5
        resources:
          requests:
            cpu: 100m
            memory: 256Mi
          limits:
            cpu: 500m
            memory: 512Mi
        securityContext:
          runAsUser: 1001
          runAsGroup: 1001
          allowPrivilegeEscalation: false
          readOnlyRootFilesystem: true
```

## Troubleshooting

### Container Fails to Start

Check logs:
```bash
docker logs mcp-server
```

### Health Check Failing

Verify the health endpoint is accessible:
```bash
docker exec mcp-server curl -f http://localhost:8001/health
```

### Permission Errors

Ensure files are owned by mcpuser in the image:
```bash
docker run --rm todo-mcp-server:latest ls -la /app/backend
```

## Image Size Optimization

Current optimizations:
- Multi-stage build (excludes build dependencies)
- Slim base image (~50MB vs ~400MB for full Python)
- No dev dependencies in production stage
- Comprehensive .dockerignore

Expected image size: ~200-300MB

Check image size:
```bash
docker images todo-mcp-server:latest
```

## Development Notes

### Current Implementation

The MCP server currently uses the same FastAPI application as the backend but runs on port 8001 with `MCP_MODE=true` environment variable. Future iterations may split this into a dedicated MCP server entry point.

### Potential Entry Point

If a dedicated MCP entry point is created (e.g., `backend/mcp/server.py`), update the CMD in the Dockerfile:

```dockerfile
CMD ["uvicorn", "backend.mcp.server:app", "--host", "0.0.0.0", "--port", "8001"]
```

## Related Files

- `deploy/docker/mcp-server/Dockerfile` - Main Dockerfile
- `deploy/docker/mcp-server/.dockerignore` - Build exclusions
- `deploy/helm/todo-app/templates/mcp-server-deployment.yaml` - K8s deployment
- `specs/005-k8s-deployment/data-model.md` - Infrastructure specification
