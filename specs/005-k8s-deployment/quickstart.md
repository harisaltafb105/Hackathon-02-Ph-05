# Quickstart: Phase IV Local Kubernetes Deployment

**Feature**: 005-k8s-deployment
**Date**: 2026-02-03
**Estimated Time**: 15 minutes

## Prerequisites

Before starting, ensure you have the following installed:

| Tool | Minimum Version | Check Command | Install Guide |
|------|-----------------|---------------|---------------|
| Docker Desktop | 4.x | `docker --version` | [docker.com](https://docker.com) |
| Minikube | 1.32+ | `minikube version` | [minikube.sigs.k8s.io](https://minikube.sigs.k8s.io/docs/start/) |
| kubectl | 1.29+ | `kubectl version --client` | Included with Minikube |
| Helm | 3.14+ | `helm version` | [helm.sh](https://helm.sh/docs/intro/install/) |

### Optional AI Tools

| Tool | Purpose | Install |
|------|---------|---------|
| Gordon (Docker AI) | Dockerfile optimization | Included in Docker Desktop |
| kubectl-ai | AI-assisted deployments | `kubectl krew install ai` |
| kagent | Cluster health analysis | See [kagent docs](https://github.com/kagent-dev/kagent) |

---

## Quick Start (5 Steps)

### Step 1: Start Minikube

```bash
# Start with recommended resources
minikube start --cpus=4 --memory=8192 --disk-size=40g

# Verify cluster is running
kubectl get nodes
```

Expected output:
```
NAME       STATUS   ROLES           AGE   VERSION
minikube   Ready    control-plane   1m    v1.29.x
```

### Step 2: Build Docker Images

```bash
# Navigate to repository root
cd /path/to/Phase-04

# Configure Docker to use Minikube's Docker daemon
eval $(minikube docker-env)

# Build all images
./deploy/scripts/build-images.sh
```

Alternatively, build individually:
```bash
docker build -t todo-frontend:latest -f deploy/docker/frontend/Dockerfile frontend/
docker build -t todo-backend:latest -f deploy/docker/backend/Dockerfile .
docker build -t todo-mcp-server:latest -f deploy/docker/mcp-server/Dockerfile .
docker build -t todo-ai-agent:latest -f deploy/docker/ai-agent/Dockerfile .
```

### Step 3: Prepare Secrets

Create environment variables with your actual values:
```bash
# Linux/macOS
export DATABASE_URL="postgresql://user:pass@your-neon-host/dbname"
export BETTER_AUTH_SECRET="your-better-auth-secret"
export OPENAI_API_KEY="sk-your-openai-key"

# Windows PowerShell
$env:DATABASE_URL = "postgresql://user:pass@your-neon-host/dbname"
$env:BETTER_AUTH_SECRET = "your-better-auth-secret"
$env:OPENAI_API_KEY = "sk-your-openai-key"
```

### Step 4: Deploy with Helm

```bash
# Install the Helm chart with secrets
helm install todo-app ./deploy/helm/todo-app \
  --set secrets.databaseUrl="$DATABASE_URL" \
  --set secrets.betterAuthSecret="$BETTER_AUTH_SECRET" \
  --set secrets.openaiApiKey="$OPENAI_API_KEY"
```

Wait for pods to be ready:
```bash
kubectl get pods -w
```

Expected output (after ~2 minutes):
```
NAME                          READY   STATUS    RESTARTS   AGE
frontend-xxxxx                1/1     Running   0          2m
backend-xxxxx                 1/1     Running   0          2m
mcp-server-xxxxx              1/1     Running   0          2m
ai-agent-xxxxx                1/1     Running   0          2m
```

### Step 5: Access the Application

```bash
# Get the frontend URL
minikube service frontend-svc --url
```

Open the URL in your browser (typically `http://192.168.x.x:30000`).

---

## Verification Checklist

After deployment, verify:

- [ ] All pods are Running: `kubectl get pods`
- [ ] All services have endpoints: `kubectl get endpoints`
- [ ] Frontend loads in browser
- [ ] Can create a todo item
- [ ] Can chat with AI chatbot
- [ ] Chatbot can see created todos

---

## Common Operations

### View Logs

```bash
# Frontend logs
kubectl logs -l component=frontend -f

# Backend logs
kubectl logs -l component=backend -f

# All logs
kubectl logs -l app=todo -f
```

### Restart a Service

```bash
kubectl rollout restart deployment/backend
```

### Scale a Service

```bash
# Via kubectl
kubectl scale deployment/backend --replicas=3

# Via Helm upgrade
helm upgrade todo-app ./deploy/helm/todo-app \
  --set backend.replicaCount=3
```

### Uninstall

```bash
helm uninstall todo-app
```

### Stop Minikube

```bash
minikube stop
```

---

## Troubleshooting

### Pods Not Starting

```bash
# Check pod events
kubectl describe pod <pod-name>

# Check for resource issues
kubectl top nodes
kubectl top pods
```

### Image Pull Errors

Ensure Docker is using Minikube's daemon:
```bash
eval $(minikube docker-env)
docker images | grep todo
```

### Secret Issues

Verify secrets are mounted:
```bash
kubectl exec -it <pod-name> -- env | grep -E "DATABASE|AUTH|OPENAI"
```

### Database Connection Failures

1. Verify Neon database is accessible from local machine
2. Check DATABASE_URL format: `postgresql://user:pass@host/db?sslmode=require`
3. Ensure Minikube can reach external hosts: `minikube ssh -- curl -I https://your-neon-host`

### Port Conflicts

If port 30000 is in use:
```bash
# Change NodePort in Helm values
helm upgrade todo-app ./deploy/helm/todo-app \
  --set frontend.service.nodePort=30001
```

---

## Resource Requirements

### Minimum (Functional)

| Resource | Value |
|----------|-------|
| CPU | 2 cores |
| Memory | 4 GB |
| Disk | 20 GB |

### Recommended (Comfortable)

| Resource | Value |
|----------|-------|
| CPU | 4 cores |
| Memory | 8 GB |
| Disk | 40 GB |

---

## Known Issues and Limitations

### Windows with Git Bash

When using Git Bash on Windows, the `/` character in Helm `--set` values may be incorrectly expanded to `C:/Program Files/Git/`. Use `//` or PowerShell for path values:

```bash
# Git Bash workaround for health probe paths
--set 'frontend.probes.liveness.path=//'
```

### System Memory Constraints

If your system has less than 8GB RAM available, start Minikube with reduced resources:

```bash
minikube start --cpus=2 --memory=3072
```

This may result in slower pod startup times.

### Loading Images into Minikube

When building images with the local Docker daemon (not Minikube's daemon), load images manually:

```bash
minikube image load todo-frontend:latest
minikube image load todo-backend:latest
minikube image load todo-mcp-server:latest
minikube image load todo-ai-agent:latest
```

### Health Probe Timing

If pods restart frequently due to health probe failures:
- Increase `initialDelaySeconds` for liveness probes to 60+ seconds
- Increase `failureThreshold` to 10 for services with slow startup

```bash
helm upgrade todo-app ./deploy/helm/todo-app \
  --set backend.probes.liveness.initialDelaySeconds=60 \
  --set backend.probes.liveness.failureThreshold=10
```

---

## Next Steps

- Run `/sp.tasks` to see implementation task list
- Review [plan.md](./plan.md) for architecture details
- Check [data-model.md](./data-model.md) for infrastructure schemas
