# AI Agent Docker Image

Production-ready Docker image for the Todo App AI Agent service.

## Overview

The AI Agent is a specialized instance of the backend that provides AI-powered task management capabilities through OpenAI integration and MCP (Model Context Protocol) tools.

### Image Specifications

| Attribute | Value |
|-----------|-------|
| **Image Name** | `todo-ai-agent` |
| **Base Image** | `python:3.13-slim` |
| **Port** | 8002 |
| **User** | appuser (UID: 1001, GID: 1001) |
| **Health Check** | `/health` endpoint |
| **Image Size** | ~92 MB |

## Building the Image

### Quick Build

```bash
cd deploy/docker/ai-agent
./build.sh
```

### Custom Version

```bash
./build.sh 1.2.3
```

### Manual Build

```bash
docker build -f Dockerfile -t todo-ai-agent:1.0.0-local -t todo-ai-agent:latest ../../../
```

## Running the Container

### Local Development

```bash
docker run -d \
  --name ai-agent \
  -p 8002:8002 \
  -e OPENAI_API_KEY="your-openai-api-key" \
  -e DATABASE_URL="postgresql://user:pass@host:5432/db" \
  -e BETTER_AUTH_URL="http://localhost:3000" \
  -e BETTER_AUTH_SECRET="your-secret" \
  -e MCP_SERVER_URL="http://mcp-server:8001" \
  todo-ai-agent:latest
```

### With Environment File

```bash
docker run -d \
  --name ai-agent \
  -p 8002:8002 \
  --env-file ../../../.env \
  todo-ai-agent:latest
```

## Environment Variables

### Required

| Variable | Description | Example |
|----------|-------------|---------|
| `OPENAI_API_KEY` | OpenAI API key for GPT-4 | `sk-...` |
| `DATABASE_URL` | PostgreSQL connection string | `postgresql://user:pass@db:5432/todo` |
| `BETTER_AUTH_URL` | Frontend authentication URL | `http://frontend:3000` |
| `BETTER_AUTH_SECRET` | JWT signing secret | `your-secret-here` |
| `MCP_SERVER_URL` | MCP server endpoint | `http://mcp-server:8001` |

### Optional

| Variable | Description | Default |
|----------|-------------|---------|
| `AI_AGENT_MODE` | Identifies this as AI agent instance | `true` |

## Health Checks

The container includes built-in health monitoring:

- **Endpoint**: `http://localhost:8002/health`
- **Interval**: 30 seconds
- **Timeout**: 3 seconds
- **Retries**: 3
- **Start Period**: 5 seconds

Test health check:

```bash
curl http://localhost:8002/health
```

## Security Features

### Non-Root User
- Runs as `appuser` (UID: 1001)
- No root privileges in container
- Follows principle of least privilege

### Minimal Attack Surface
- Based on slim Python image (no unnecessary tools)
- Multi-stage build (no build dependencies in final image)
- No secrets in image layers

### Secrets Management
- Environment variables for runtime secrets
- Never hardcoded in Dockerfile
- Kubernetes secrets integration ready

## Image Structure

```
todo-ai-agent:latest
├── /app                          (Working directory)
│   └── backend/                  (Application code)
│       ├── main.py              (FastAPI app)
│       ├── chat/                (AI agent modules)
│       │   ├── agent.py        (OpenAI integration)
│       │   ├── tools.py        (MCP tools)
│       │   └── service.py      (Business logic)
│       ├── config.py           (Settings)
│       ├── models.py           (Database models)
│       └── routers/            (API routes)
└── /usr/local/lib/python3.13/  (Dependencies)
```

## Kubernetes Deployment

This image is designed for Kubernetes deployment:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: ai-agent
spec:
  replicas: 1
  template:
    spec:
      containers:
      - name: ai-agent
        image: todo-ai-agent:latest
        ports:
        - containerPort: 8002
        env:
        - name: OPENAI_API_KEY
          valueFrom:
            secretKeyRef:
              name: todo-secrets
              key: OPENAI_API_KEY
        livenessProbe:
          httpGet:
            path: /health
            port: 8002
          initialDelaySeconds: 30
          periodSeconds: 10
```

## Troubleshooting

### Container Won't Start

Check logs:
```bash
docker logs ai-agent
```

### Health Check Failing

Verify port and endpoint:
```bash
docker exec ai-agent curl http://localhost:8002/health
```

### Missing Environment Variables

Inspect container environment:
```bash
docker exec ai-agent env | grep -E "(OPENAI|DATABASE|MCP)"
```

### Permission Denied

Ensure proper ownership:
```bash
docker exec ai-agent ls -la /app
```

Should show `appuser` as owner.

## Development

### Rebuilding After Code Changes

```bash
./build.sh --no-cache
```

### Testing Locally

```bash
# Start with debug logging
docker run -it --rm \
  -p 8002:8002 \
  --env-file ../../../.env \
  todo-ai-agent:latest \
  uvicorn backend.main:app --host 0.0.0.0 --port 8002 --log-level debug
```

### Inspecting the Image

```bash
# View layers
docker history todo-ai-agent:latest

# Inspect configuration
docker inspect todo-ai-agent:latest

# Access shell (for debugging)
docker run -it --rm --entrypoint bash todo-ai-agent:latest
```

## Best Practices

1. **Always use specific version tags in production**
   - Bad: `todo-ai-agent:latest`
   - Good: `todo-ai-agent:1.0.0-local`

2. **Never include secrets in the image**
   - Use Kubernetes secrets
   - Use environment variables at runtime

3. **Keep images small**
   - Current size: ~92 MB
   - Multi-stage build removes build dependencies

4. **Test health checks before deployment**
   - Ensure `/health` endpoint responds correctly
   - Verify proper startup time

## Related Documentation

- [Backend API Documentation](../backend/README.md)
- [Kubernetes Deployment Guide](../../helm/README.md)
- [AI Chatbot Specification](../../../specs/004-ai-chatbot/)
- [Infrastructure Model](../../../specs/005-k8s-deployment/data-model.md)

## Support

For issues or questions:
1. Check container logs
2. Verify environment variables
3. Test health endpoint
4. Review Phase IV deployment documentation
