# Local-to-Cloud Promotion Skill

## Purpose
Ensure zero-code-change migration from Minikube to cloud-managed Kubernetes clusters (AKS, GKE, OKE). This skill provides the systematic process for promoting Helm charts, Dapr components, and Kafka configurations from a locally validated environment to cloud staging and production — without touching application source code.

## Input
- **Helm charts**: Existing Phase IV/V Helm charts validated on Minikube (chart templates, `values.yaml`, environment overrides)
- **Dapr configs**: Component YAML files (pub/sub, state stores, secret stores, bindings, resiliency policies, subscriptions)
- **Kafka topic definitions**: Topic names, partition counts, replication factors, schema contracts

## Output
- **Cloud-ready deployment plan**: A complete, actionable promotion plan covering values overrides, Dapr component swaps, Kafka connectivity changes, pre-flight checks, rollout steps, and rollback procedures — all achievable through configuration changes only

## Used By
- **Cloud Deployment Agent** (`cloud-k8s-deployer`) — as the primary reference for executing local-to-cloud promotions

---

## The Zero-Code-Change Principle

The foundation of this skill is that **application code never changes between environments**. All environment differences are absorbed by:

1. **Helm values overrides** — different `values-{env}.yaml` files per environment
2. **Dapr component swaps** — same component names, different backing implementations
3. **Kubernetes Secrets / ConfigMaps** — environment-specific configuration injected at deploy time
4. **Dapr resiliency policies** — environment-tuned retry, timeout, and circuit breaker settings

If a promotion step requires a code change, it is a **design failure** that must be fixed at the architecture level before proceeding.

```
┌──────────────┐    values-local.yaml     ┌──────────────┐
│   App Code   │ ──────────────────────── │   Minikube   │
│  (immutable) │    values-staging.yaml   ├──────────────┤
│              │ ──────────────────────── │ Cloud Staging│
│              │    values-prod.yaml      ├──────────────┤
│              │ ──────────────────────── │  Cloud Prod  │
└──────────────┘                          └──────────────┘
     SAME                                   DIFFERENT
   container                               configuration
     image                                    only
```

---

## Promotion Ladder

Every service follows this four-stage promotion ladder. A service cannot advance without passing the gate at each stage.

| Stage | Environment | Purpose | Gate Criteria |
|-------|-------------|---------|---------------|
| **L1** | Local Docker Compose | Basic service health, contract tests | Container builds, healthcheck passes, API contract valid |
| **L2** | Local Kubernetes (Minikube) | Helm chart validation, Dapr sidecar injection | Helm lint clean, `helm template` valid, Dapr sidecar healthy, all pods Running |
| **C1** | Cloud Staging | Full integration with managed services | Kafka connected, Dapr components bound, E2E tests pass, latency p95 within budget |
| **C2** | Cloud Production | Canary → progressive rollout | Error rate < 0.1%, Kafka consumer lag stable, rollback tested, monitoring active |

### Stage Tracking Template
```markdown
## Promotion Status: [Service Name]

| Stage | Status | Date Passed | Validated By | Notes |
|-------|--------|-------------|--------------|-------|
| L1 — Docker Compose | ✅ Passed / ❌ Failed / ⏳ Pending | | | |
| L2 — Minikube | ✅ / ❌ / ⏳ | | | |
| C1 — Cloud Staging | ✅ / ❌ / ⏳ | | | |
| C2 — Cloud Production | ✅ / ❌ / ⏳ | | | |
```

---

## Promotion Process: L2 (Minikube) → C1 (Cloud Staging)

This is the primary promotion boundary where the most configuration changes occur.

### Step 1: Inventory What Changes

Identify every configuration delta between local and cloud. **Nothing else should change.**

| Layer | Local (Minikube) | Cloud (Staging) | Change Mechanism |
|-------|-----------------|-----------------|------------------|
| Container images | Local registry / `minikube image load` | Cloud registry (ACR, GCR, OCIR) | Helm `image.repository` + `image.tag` |
| Ingress | `minikube tunnel` / NodePort | Cloud Load Balancer / Ingress Controller | Helm `ingress.*` values |
| Kafka brokers | `localhost:9092` or in-cluster Kafka | Managed Kafka / Confluent Cloud endpoint | Dapr pub/sub component metadata |
| State store | Local Redis (no auth) | Managed Redis (TLS + auth) | Dapr state store component metadata |
| Secrets | Local file (`secretstore-local`) | K8s Secrets / Cloud Vault | Dapr secret store component swap |
| TLS | Disabled or self-signed | Cloud-provisioned certificates | Helm `ingress.tls` + cert-manager |
| Resource limits | Minimal (dev-sized) | Production-sized | Helm `resources.*` values |
| Replicas | 1 | 2+ (per SLA) | Helm `replicaCount` |
| Dapr resiliency | Relaxed timeouts | Production-tuned | Resiliency YAML override |
| Monitoring | None or local Prometheus | Cloud-native (Azure Monitor, Cloud Monitoring, OCI Monitoring) | Helm annotations + Dapr tracing config |

### Step 2: Create Cloud Values Override

Create `values-staging.yaml` that overrides only what differs from `values.yaml`:

```yaml
# values-staging.yaml — Cloud staging overrides
# Only override what changes. Everything else inherits from values.yaml.

replicaCount: 2

image:
  repository: <cloud-registry>/<project>/<service>
  tag: <git-sha-or-semver>
  pullPolicy: Always

ingress:
  enabled: true
  className: nginx                    # or cloud-specific: alb, gce
  annotations:
    cert-manager.io/cluster-issuer: letsencrypt-staging
  hosts:
    - host: <service>.staging.<domain>
      paths:
        - path: /
          pathType: Prefix
  tls:
    - secretName: <service>-tls-staging
      hosts:
        - <service>.staging.<domain>

resources:
  requests:
    cpu: 200m
    memory: 256Mi
  limits:
    cpu: 1000m
    memory: 512Mi

autoscaling:
  enabled: true
  minReplicas: 2
  maxReplicas: 6
  targetCPUUtilizationPercentage: 75
```

### Step 3: Swap Dapr Components for Cloud Backends

Replace local Dapr component files with cloud-targeted versions. **The component names stay the same** so application code doesn't change.

#### Pub/Sub: Local Kafka → Managed Kafka
```yaml
# Local: brokers = localhost:9092, authType = none
# Cloud: brokers = managed endpoint, authType = password/mtls

apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: pubsub-kafka              # SAME name as local
  namespace: todo-app-staging
spec:
  type: pubsub.kafka              # SAME type
  version: v1
  metadata:
    - name: brokers
      secretKeyRef:               # Secret ref instead of plain value
        name: kafka-secrets
        key: brokers
    - name: authType
      value: "password"           # Auth enabled for cloud
    - name: saslUsername
      secretKeyRef:
        name: kafka-secrets
        key: sasl-username
    - name: saslPassword
      secretKeyRef:
        name: kafka-secrets
        key: sasl-password
    - name: initialOffset
      value: "oldest"
  auth:
    secretStore: secretstore-k8s
```

#### State Store: Local Redis → Managed Redis
```yaml
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: statestore-redis          # SAME name as local
  namespace: todo-app-staging
spec:
  type: state.redis               # SAME type
  version: v1
  metadata:
    - name: redisHost
      secretKeyRef:
        name: redis-secrets
        key: host
    - name: redisPassword
      secretKeyRef:
        name: redis-secrets
        key: password
    - name: enableTLS
      value: "true"               # TLS enabled for cloud
  auth:
    secretStore: secretstore-k8s
```

#### Secret Store: Local File → Kubernetes Secrets
```yaml
# Local uses: secretstores.local.file (reads from JSON file)
# Cloud uses: secretstores.kubernetes (reads from K8s Secrets)

apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: secretstore-k8s           # Cloud secret store
  namespace: todo-app-staging
spec:
  type: secretstores.kubernetes
  version: v1
  metadata: []
```

### Step 4: Create Cloud Kubernetes Secrets

Populate the secrets that Dapr components reference:

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: kafka-secrets
  namespace: todo-app-staging
type: Opaque
stringData:
  brokers: "<managed-kafka-endpoint>:9093"
  sasl-username: "<username>"
  sasl-password: "<password>"
---
apiVersion: v1
kind: Secret
metadata:
  name: redis-secrets
  namespace: todo-app-staging
type: Opaque
stringData:
  host: "<managed-redis-endpoint>:6380"
  password: "<password>"
---
apiVersion: v1
kind: Secret
metadata:
  name: postgres-secrets
  namespace: todo-app-staging
type: Opaque
stringData:
  connection-string: "<neon-postgres-connection-string>"
```

> **Never commit** these Secret manifests with real values. Use sealed-secrets, external-secrets-operator, or apply them manually / via CI pipeline secrets.

### Step 5: Tune Resiliency for Cloud

Cloud environments have different latency and failure profiles than local:

```yaml
apiVersion: dapr.io/v1alpha1
kind: Resiliency
metadata:
  name: todo-app-resiliency
  namespace: todo-app-staging
spec:
  policies:
    retries:
      pubsubRetry:
        policy: exponential
        maxInterval: 60s          # Longer for cloud (was 30s local)
        maxRetries: 8             # More retries for transient cloud errors
      stateRetry:
        policy: constant
        duration: 3s              # Slightly longer for managed services
        maxRetries: 5
    timeouts:
      defaultTimeout: 15s         # Increased for cloud network latency
      longTimeout: 45s
    circuitBreakers:
      pubsubBreaker:
        maxRequests: 2
        interval: 60s
        timeout: 120s             # Longer recovery for managed Kafka
        trip: consecutiveFailures > 8
```

### Step 6: Deploy and Validate

```bash
# 1. Push container images to cloud registry
docker tag <service>:<tag> <cloud-registry>/<project>/<service>:<tag>
docker push <cloud-registry>/<project>/<service>:<tag>

# 2. Create namespace and secrets
kubectl create namespace todo-app-staging
kubectl apply -f secrets/staging/ -n todo-app-staging

# 3. Install/upgrade Dapr on cloud cluster (match local version)
helm upgrade --install dapr dapr/dapr --namespace dapr-system --version <pinned-version>

# 4. Apply cloud Dapr components
kubectl apply -f deploy/dapr/components/staging/ -n todo-app-staging
kubectl apply -f deploy/dapr/subscriptions/ -n todo-app-staging

# 5. Deploy application via Helm with staging overrides
helm upgrade --install <release> ./charts/<service> \
  -f charts/<service>/values.yaml \
  -f charts/<service>/values-staging.yaml \
  --namespace todo-app-staging \
  --atomic \
  --timeout 5m \
  --history-max 3

# 6. Verify
kubectl get pods -n todo-app-staging
kubectl get dapr components -n todo-app-staging
kubectl logs <pod> -c daprd -n todo-app-staging | head -50
```

---

## Promotion Process: C1 (Cloud Staging) → C2 (Cloud Production)

This is a narrower delta — mostly scaling, TLS, and monitoring changes.

### Configuration Differences

| Setting | Staging | Production | Override |
|---------|---------|------------|---------|
| Replicas | 2 | 3+ (per SLA) | `replicaCount` |
| HPA max | 6 | 10+ | `autoscaling.maxReplicas` |
| TLS issuer | `letsencrypt-staging` | `letsencrypt-prod` | `ingress.annotations` |
| Domain | `*.staging.domain` | `*.domain` | `ingress.hosts` |
| Resource limits | Moderate | Full production sizing | `resources.*` |
| Kafka consumer group | `*-staging` | `*-prod` | Dapr component metadata |
| Monitoring | Basic | Full alerting + dashboards | Annotations + cloud config |
| Rollout strategy | Direct | Canary → Progressive | Deployment strategy or Argo Rollouts |

### Production Values Override
```yaml
# values-production.yaml

replicaCount: 3

image:
  repository: <cloud-registry>/<project>/<service>
  tag: <release-semver>       # Pinned semver, never SHA in prod
  pullPolicy: IfNotPresent    # Use cached images for speed

ingress:
  annotations:
    cert-manager.io/cluster-issuer: letsencrypt-prod
  hosts:
    - host: <service>.<domain>
      paths:
        - path: /
          pathType: Prefix
  tls:
    - secretName: <service>-tls-prod
      hosts:
        - <service>.<domain>

resources:
  requests:
    cpu: 500m
    memory: 512Mi
  limits:
    cpu: 2000m
    memory: 1Gi

autoscaling:
  enabled: true
  minReplicas: 3
  maxReplicas: 12
  targetCPUUtilizationPercentage: 70
```

---

## Deployment Diff Report Template

Generate this report before every promotion to verify only configuration changes:

```markdown
## Deployment Diff: [Source Env] → [Target Env]
**Service:** [service-name]
**Date:** [ISO date]
**Promoted By:** [who]

### Container Image
| | Source | Target | Change Type |
|-|--------|--------|-------------|
| Repository | [local-reg] | [cloud-reg] | Config only |
| Tag | [tag] | [tag] | Identical / Config only |

### Helm Values Delta
| Key | Source Value | Target Value | Change Type |
|-----|-------------|--------------|-------------|
| replicaCount | 1 | 2 | Config only |
| resources.requests.cpu | 50m | 200m | Config only |
| ingress.hosts[0].host | app.local | app.staging.domain | Config only |

### Dapr Components Delta
| Component | Local Implementation | Cloud Implementation | Name Changed? |
|-----------|---------------------|---------------------|---------------|
| pubsub-kafka | localhost:9092, no auth | managed:9093, SASL | No (zero-code) |
| statestore-redis | localhost:6379, no TLS | managed:6380, TLS | No (zero-code) |

### Code Changes Required
| File | Change | Justification |
|------|--------|---------------|
| _(none — zero-code-change)_ | | |

> If any row appears in "Code Changes Required", the promotion is **BLOCKED**.
> Fix the architecture so the change can be absorbed by configuration.

### Risk Assessment
- [ ] All changes are configuration-only (no code changes)
- [ ] Container image is identical binary (same SHA)
- [ ] Rollback plan documented
- [ ] Monitoring and alerts configured for target environment
```

---

## Pre-Flight Checklist

Run before every promotion. All items must pass.

### L2 → C1 (Minikube → Cloud Staging)
- [ ] Container images pushed to cloud registry with correct tags
- [ ] Cloud cluster is reachable (`kubectl cluster-info`)
- [ ] Target namespace exists with resource quotas configured
- [ ] All Kubernetes Secrets created in target namespace
- [ ] Dapr is installed on cloud cluster (version matches local)
- [ ] Cloud Dapr component YAMLs use `secretKeyRef` (no plain values for sensitive data)
- [ ] Dapr component names are identical to local (zero-code-change guarantee)
- [ ] `helm lint` passes with cloud values overlay
- [ ] `helm template` renders valid YAML with cloud values overlay
- [ ] `helm diff` shows only expected configuration changes
- [ ] Kafka topics exist on managed Kafka (or auto-creation enabled)
- [ ] Network connectivity verified: pods → Kafka brokers, pods → Redis, pods → PostgreSQL
- [ ] No hardcoded `localhost`, `127.0.0.1`, or `minikube` references in any config
- [ ] Rollback command documented: `helm rollback <release> <revision>`

### C1 → C2 (Cloud Staging → Cloud Production)
- [ ] All E2E tests pass on staging
- [ ] Kafka consumer lag is stable and within thresholds on staging
- [ ] Error rate < 0.1% over 24h observation on staging
- [ ] Latency p95 within budget on staging
- [ ] Production Kubernetes Secrets created
- [ ] TLS certificates issued (cert-manager or manual)
- [ ] HPA configured and tested
- [ ] Monitoring dashboards created for production
- [ ] Alerting rules configured (error rate, latency, pod restarts)
- [ ] Canary / progressive rollout strategy defined
- [ ] Rollback tested on staging environment
- [ ] On-call team notified of deployment window

---

## Common Promotion Blockers

| Blocker | Symptom | Root Cause | Fix |
|---------|---------|------------|-----|
| Image pull failure | `ImagePullBackOff` | Image not in cloud registry or wrong credentials | Push image; verify `imagePullSecrets` |
| Dapr sidecar crash | `CrashLoopBackOff` on `daprd` container | Component YAML invalid or secret not found | Validate component YAML; check K8s Secret exists |
| Kafka connection timeout | Consumer lag infinite, no messages consumed | Wrong broker address, network policy blocking, auth failure | Verify broker endpoint; check SASL credentials; test connectivity from pod |
| Secret not found | Dapr init error: `secret not found` | K8s Secret missing or wrong namespace | Create secret in correct namespace |
| DNS resolution failure | `could not resolve host` | Service name hardcoded to local hostname | Use Dapr service invocation (app-id) not raw hostnames |
| TLS handshake error | `x509: certificate signed by unknown authority` | Self-signed cert used in cloud or missing CA | Use cert-manager with proper issuer; configure trust chain |
| Resource quota exceeded | `forbidden: exceeded quota` | Cloud namespace quota too low for requested resources | Increase quota or reduce resource requests |
| Helm values conflict | Template render error | Incompatible values between base and override | Run `helm template` with overlay to debug; fix values structure |
| Code references `localhost` | Connection refused in cloud | Hardcoded local address in app config | Replace with env var or Dapr service invocation — **architecture fix required** |

---

## File Organization for Multi-Environment

```
charts/
  <service>/
    Chart.yaml
    values.yaml                 # Base defaults (shared)
    values-local.yaml           # Minikube overrides
    values-staging.yaml         # Cloud staging overrides
    values-production.yaml      # Cloud production overrides
    templates/
      ...

deploy/
  dapr/
    components/
      local/                    # Local Dapr components
        pubsub-kafka.yaml
        statestore-redis.yaml
        secretstore-local.yaml
        resiliency.yaml
      staging/                  # Cloud staging Dapr components
        pubsub-kafka.yaml       # Same name, cloud backend
        statestore-redis.yaml
        secretstore-k8s.yaml
        resiliency.yaml
      production/               # Cloud production Dapr components
        pubsub-kafka.yaml
        statestore-redis.yaml
        secretstore-k8s.yaml
        resiliency.yaml
    subscriptions/              # Shared across environments
      todo-task-events-sub.yaml
      todo-reminder-events-sub.yaml

secrets/
  local-secrets.json            # .gitignored
  staging/                      # .gitignored — K8s Secret manifests
  production/                   # .gitignored — K8s Secret manifests
```

---

## Quick Reference: What Changes Per Environment

| Configuration Layer | Local → Staging | Staging → Production |
|--------------------|-----------------|---------------------|
| **App code** | Nothing | Nothing |
| **Container image** | Registry path only | Tag (SHA → semver) |
| **Helm values** | `values-local.yaml` → `values-staging.yaml` | `values-staging.yaml` → `values-production.yaml` |
| **Dapr component names** | Nothing | Nothing |
| **Dapr component metadata** | Endpoints + auth credentials (via secretKeyRef) | Consumer group suffix, tuning params |
| **Dapr resiliency** | Relaxed → moderate | Moderate → strict |
| **K8s Secrets** | Local file → K8s Secrets | Different credential values |
| **Ingress** | NodePort / tunnel → LoadBalancer | Staging domain → prod domain + prod TLS |
| **Replicas** | 1 → 2 | 2 → 3+ |
| **Resources** | Minimal → moderate | Moderate → production-sized |
| **Monitoring** | None → basic | Basic → full alerting + dashboards |

## Validation Rule

After completing any promotion plan, apply this final check:

```
FOR EACH file in application source code (frontend/, backend/):
  ASSERT file is IDENTICAL across all environments
  IF different → PROMOTION BLOCKED — fix architecture

FOR EACH Dapr component:
  ASSERT metadata.name is IDENTICAL across all environments
  IF different → PROMOTION BLOCKED — apps reference components by name

FOR EACH Helm chart template:
  ASSERT template files are IDENTICAL across all environments
  ONLY values-{env}.yaml files differ
  IF template changed → PROMOTION BLOCKED — use conditional templating instead
```
