# Docker to Kubernetes Translation Skill

## Purpose
Translate application runtime needs into container + K8s primitives.

## Capabilities

### 1. Identify Required Resources
- **Ports**: Detect exposed ports from Dockerfile or application config
- **Environment Variables**: Extract required env vars for configuration
- **Volumes**: Identify persistent storage needs and volume mounts

### 2. Decide K8s Resource Types
- **Deployment**: Stateless applications with replica management
- **Service**: Internal/external network exposure (ClusterIP, NodePort, LoadBalancer)
- **Ingress**: HTTP/HTTPS routing and TLS termination
- **ConfigMap/Secret**: Configuration and sensitive data management
- **PersistentVolumeClaim**: Persistent storage for stateful needs

### 3. Ensure Container Best Practices
- **Stateless Containers**: Verify containers don't rely on local state
- **Health Checks**: Implement liveness and readiness probes
- **Resource Limits**: Set CPU/memory requests and limits
- **Security Context**: Run as non-root, read-only filesystem where possible

## Output

### Valid Container + K8s Mapping
```yaml
# Example translation output
Application:
  image: my-app:1.0.0
  ports:
    - containerPort: 8080
  env:
    - name: DATABASE_URL
      valueFrom:
        secretKeyRef:
          name: app-secrets
          key: database-url
  resources:
    requests:
      memory: "128Mi"
      cpu: "100m"
    limits:
      memory: "256Mi"
      cpu: "500m"

K8s Resources:
  - Deployment (replicas: 3)
  - Service (ClusterIP, port: 80 -> 8080)
  - Ingress (host: app.example.com)
  - Secret (database credentials)
```

## Warnings for Anti-Patterns

### Container Anti-Patterns
- Running as root user
- Hardcoded secrets in image
- Missing health checks
- No resource limits defined
- Using `latest` tag instead of specific versions
- Large image sizes (missing multi-stage builds)

### K8s Anti-Patterns
- Using NodePort for production traffic
- Missing pod disruption budgets
- No horizontal pod autoscaler configured
- Secrets not encrypted at rest
- Missing network policies
- Single replica for critical services

## Translation Checklist

- [ ] Dockerfile follows best practices (multi-stage, non-root)
- [ ] All ports documented and mapped to Services
- [ ] Environment variables externalized to ConfigMaps/Secrets
- [ ] Persistent volumes identified and PVCs created
- [ ] Liveness and readiness probes configured
- [ ] Resource requests and limits set appropriately
- [ ] Security context configured (non-root, read-only rootfs)
- [ ] Horizontal Pod Autoscaler configured if needed
- [ ] Ingress rules defined for external access
- [ ] Network policies applied for isolation

## Common Mappings

| Docker Concept | Kubernetes Equivalent |
|----------------|----------------------|
| `EXPOSE` | `containerPort` in Pod spec |
| `ENV` | `env` or `envFrom` with ConfigMap/Secret |
| `VOLUME` | `volumeMounts` + PersistentVolumeClaim |
| `HEALTHCHECK` | `livenessProbe` / `readinessProbe` |
| `docker-compose` service | Deployment + Service |
| `docker-compose` network | Namespace / NetworkPolicy |
| `docker-compose` volume | PersistentVolume + PVC |
