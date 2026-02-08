# Dapr Component Authoring Skill

## Purpose
Generate portable, validated Dapr component YAML files for any infrastructure choice. This skill provides the canonical patterns, metadata fields, and validation rules for authoring Dapr components that work identically across local development (`dapr run`) and Kubernetes deployment.

## Input
- **Infrastructure choice**: The backing service type — Kafka (pub/sub), Database (state store), Secrets (secret store), or other supported Dapr component implementations
- **Environment context**: Local development, Minikube, or cloud Kubernetes cluster

## Output
- **Validated Dapr component YAML files**: Production-ready, secret-safe component definitions with all required metadata, scoping, and resiliency configuration

## Used By
- **Dapr Integration Agent** — as the primary reference for generating and validating all Dapr component YAML files

---

## Component YAML Structure

Every Dapr component follows this base structure:

```yaml
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: <component-name>          # Lowercase, hyphenated. Referenced by app code.
  namespace: <namespace>          # Omit for local dev; set for K8s.
  labels:
    app.kubernetes.io/part-of: <project-name>
    environment: <dev|staging|prod>
  annotations:
    dapr.io/component-description: "<what this component does>"
spec:
  type: <building-block>.<implementation>   # e.g., pubsub.kafka, state.redis
  version: v1                               # Component spec version
  metadata:
    - name: <key>
      value: <value>                        # Plain value (non-sensitive only)
    - name: <key>
      secretKeyRef:                         # Secret reference (sensitive values)
        name: <secret-name>
        key: <secret-key>
scopes:                                     # Optional: restrict to specific app IDs
  - <app-id-1>
  - <app-id-2>
```

### Naming Convention
```
Format: <building-block>-<implementation>[-<qualifier>]

Examples:
  pubsub-kafka              # Primary Kafka pub/sub
  pubsub-kafka-deadletter   # Dead-letter pub/sub
  statestore-redis          # Redis state store
  statestore-postgres       # PostgreSQL state store
  secretstore-local         # Local file secret store
  secretstore-k8s           # Kubernetes secret store
  binding-cron-reminders    # Cron input binding for reminders
  binding-smtp-email        # SMTP output binding for email
```

---

## Component Catalog

### 1. Pub/Sub — Kafka

The primary messaging component for event-driven communication.

#### Local Development
```yaml
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: pubsub-kafka
spec:
  type: pubsub.kafka
  version: v1
  metadata:
    - name: brokers
      value: "localhost:9092"
    - name: consumerGroup
      value: "default-consumer-group"
    - name: clientID
      value: "todo-app-local"
    - name: authType
      value: "none"
    - name: maxMessageBytes
      value: "1048576"
    - name: consumeRetryInterval
      value: "200ms"
    - name: version
      value: "2.0.0"
    - name: disableTls
      value: "true"
```

#### Kubernetes / Production
```yaml
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: pubsub-kafka
  namespace: todo-app
  labels:
    app.kubernetes.io/part-of: todo-app
    environment: production
spec:
  type: pubsub.kafka
  version: v1
  metadata:
    - name: brokers
      secretKeyRef:
        name: kafka-secrets
        key: brokers
    - name: consumerGroup
      value: "todo-app-prod"
    - name: clientID
      value: "todo-app-prod"
    - name: authType
      value: "password"
    - name: saslUsername
      secretKeyRef:
        name: kafka-secrets
        key: sasl-username
    - name: saslPassword
      secretKeyRef:
        name: kafka-secrets
        key: sasl-password
    - name: saslMechanism
      value: "PLAIN"
    - name: maxMessageBytes
      value: "1048576"
    - name: consumeRetryInterval
      value: "500ms"
    - name: version
      value: "2.0.0"
    - name: initialOffset
      value: "oldest"
  auth:
    secretStore: secretstore-k8s
scopes:
  - todo-api
  - notification-svc
  - analytics-svc
  - recurrence-svc
  - reminder-svc
  - search-indexer
```

#### Required Metadata Fields
| Field | Required | Description | Secret? |
|-------|----------|-------------|---------|
| `brokers` | Yes | Comma-separated broker addresses | Yes (prod) |
| `consumerGroup` | Yes | Default consumer group name | No |
| `clientID` | Yes | Client identifier for broker connections | No |
| `authType` | Yes | `none`, `password`, `mtls`, `oidc` | No |
| `saslUsername` | If authType=password | SASL username | Yes |
| `saslPassword` | If authType=password | SASL password | Yes |
| `maxMessageBytes` | Recommended | Max message size in bytes | No |
| `consumeRetryInterval` | Recommended | Retry interval on consume failure | No |
| `initialOffset` | Recommended | `oldest` or `newest` | No |
| `version` | Recommended | Kafka protocol version | No |

---

### 2. State Store — Redis

For caching, session state, and intermediate processing state.

#### Local Development
```yaml
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: statestore-redis
spec:
  type: state.redis
  version: v1
  metadata:
    - name: redisHost
      value: "localhost:6379"
    - name: redisPassword
      value: ""
    - name: actorStateStore
      value: "true"
    - name: keyPrefix
      value: "name"
    - name: enableTLS
      value: "false"
```

#### Kubernetes / Production
```yaml
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: statestore-redis
  namespace: todo-app
  labels:
    app.kubernetes.io/part-of: todo-app
    environment: production
spec:
  type: state.redis
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
    - name: actorStateStore
      value: "true"
    - name: keyPrefix
      value: "name"
    - name: enableTLS
      value: "true"
    - name: failover
      value: "true"
    - name: sentinelMasterName
      secretKeyRef:
        name: redis-secrets
        key: sentinel-master
  auth:
    secretStore: secretstore-k8s
scopes:
  - todo-api
  - reminder-svc
```

#### Required Metadata Fields
| Field | Required | Description | Secret? |
|-------|----------|-------------|---------|
| `redisHost` | Yes | `host:port` address | Yes (prod) |
| `redisPassword` | Yes | Connection password (empty string for no auth) | Yes |
| `actorStateStore` | Recommended | Enable actor state storage | No |
| `keyPrefix` | Recommended | `name` (app-id prefix), `none`, or custom | No |
| `enableTLS` | Recommended | TLS for connections | No |
| `failover` | Prod only | Enable sentinel failover | No |
| `sentinelMasterName` | If failover=true | Redis Sentinel master name | Yes |

---

### 3. State Store — PostgreSQL

For persistent state storage backed by the existing Neon PostgreSQL database.

#### Local Development
```yaml
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: statestore-postgres
spec:
  type: state.postgresql
  version: v1
  metadata:
    - name: connectionString
      value: "host=localhost user=postgres password=postgres port=5432 database=todoapp sslmode=disable"
    - name: tableName
      value: "dapr_state"
    - name: keyPrefix
      value: "name"
    - name: cleanupIntervalInSeconds
      value: "300"
```

#### Kubernetes / Production
```yaml
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: statestore-postgres
  namespace: todo-app
  labels:
    app.kubernetes.io/part-of: todo-app
    environment: production
spec:
  type: state.postgresql
  version: v1
  metadata:
    - name: connectionString
      secretKeyRef:
        name: postgres-secrets
        key: connection-string
    - name: tableName
      value: "dapr_state"
    - name: keyPrefix
      value: "name"
    - name: cleanupIntervalInSeconds
      value: "600"
  auth:
    secretStore: secretstore-k8s
scopes:
  - todo-api
```

---

### 4. Secret Store — Local File

For local development only. Reads secrets from a JSON file.

```yaml
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: secretstore-local
spec:
  type: secretstores.local.file
  version: v1
  metadata:
    - name: secretsFile
      value: "./secrets/local-secrets.json"
    - name: nestedSeparator
      value: ":"
```

**Secrets file format** (`secrets/local-secrets.json`):
```json
{
  "kafka-secrets": {
    "brokers": "localhost:9092"
  },
  "redis-secrets": {
    "host": "localhost:6379",
    "password": ""
  },
  "postgres-secrets": {
    "connection-string": "host=localhost user=postgres password=postgres port=5432 database=todoapp sslmode=disable"
  }
}
```

> **Never commit** the secrets file. Add `secrets/` to `.gitignore`.

---

### 5. Secret Store — Kubernetes

For Kubernetes deployments. Reads from native K8s Secrets.

```yaml
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: secretstore-k8s
  namespace: todo-app
spec:
  type: secretstores.kubernetes
  version: v1
  metadata: []
```

No extra metadata required — Dapr uses the sidecar's service account to read K8s Secrets from the same namespace.

---

### 6. Input Binding — Cron (Scheduled Triggers)

For periodic task execution (e.g., recurring task instance generation).

```yaml
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: binding-cron-recurrence
spec:
  type: bindings.cron
  version: v1
  metadata:
    - name: schedule
      value: "@every 15m"       # or cron expression: "0 */15 * * * *"
    - name: direction
      value: "input"
scopes:
  - recurrence-svc
```

#### Common Schedule Expressions
| Expression | Meaning |
|------------|---------|
| `@every 1m` | Every minute |
| `@every 15m` | Every 15 minutes |
| `@every 1h` | Every hour |
| `@daily` | Once per day at midnight |
| `0 0 9 * * *` | Every day at 9:00 AM |
| `0 0 */6 * * *` | Every 6 hours |

---

### 7. Output Binding — SMTP (Email Notifications)

For sending reminder and notification emails.

#### Local Development
```yaml
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: binding-smtp-email
spec:
  type: bindings.smtp
  version: v1
  metadata:
    - name: host
      value: "localhost"
    - name: port
      value: "1025"           # MailHog/MailPit local SMTP port
    - name: user
      value: ""
    - name: password
      value: ""
    - name: skipTLSVerify
      value: "true"
    - name: emailFrom
      value: "noreply@todo-app.local"
    - name: direction
      value: "output"
scopes:
  - notification-svc
```

#### Kubernetes / Production
```yaml
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: binding-smtp-email
  namespace: todo-app
spec:
  type: bindings.smtp
  version: v1
  metadata:
    - name: host
      secretKeyRef:
        name: smtp-secrets
        key: host
    - name: port
      value: "587"
    - name: user
      secretKeyRef:
        name: smtp-secrets
        key: user
    - name: password
      secretKeyRef:
        name: smtp-secrets
        key: password
    - name: skipTLSVerify
      value: "false"
    - name: emailFrom
      value: "noreply@todo-app.io"
    - name: direction
      value: "output"
  auth:
    secretStore: secretstore-k8s
scopes:
  - notification-svc
```

---

### 8. Output Binding — HTTP (Webhooks)

For webhook callbacks and external API integrations.

```yaml
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: binding-http-webhook
spec:
  type: bindings.http
  version: v1
  metadata:
    - name: url
      value: "https://hooks.example.com/todo-events"
    - name: direction
      value: "output"
scopes:
  - notification-svc
```

---

## Resiliency Policy

Pair every component with a resiliency policy to define retry, timeout, and circuit breaker behavior.

```yaml
apiVersion: dapr.io/v1alpha1
kind: Resiliency
metadata:
  name: todo-app-resiliency
spec:
  policies:
    retries:
      pubsubRetry:
        policy: exponential
        maxInterval: 30s
        maxRetries: 5
      stateRetry:
        policy: constant
        duration: 2s
        maxRetries: 3
    timeouts:
      defaultTimeout: 10s
      longTimeout: 30s
    circuitBreakers:
      pubsubBreaker:
        maxRequests: 1
        interval: 30s
        timeout: 60s
        trip: consecutiveFailures > 5
      stateBreaker:
        maxRequests: 1
        interval: 15s
        timeout: 30s
        trip: consecutiveFailures > 3

  targets:
    components:
      pubsub-kafka:
        outbound:
          retry: pubsubRetry
          timeout: defaultTimeout
          circuitBreaker: pubsubBreaker
        inbound:
          retry: pubsubRetry
          timeout: longTimeout
      statestore-redis:
        outbound:
          retry: stateRetry
          timeout: defaultTimeout
          circuitBreaker: stateBreaker
      statestore-postgres:
        outbound:
          retry: stateRetry
          timeout: longTimeout
          circuitBreaker: stateBreaker
```

---

## Subscription Configuration

Declarative subscriptions define which services consume which pub/sub topics.

```yaml
apiVersion: dapr.io/v2alpha1
kind: Subscription
metadata:
  name: todo-task-events-sub
spec:
  pubsubname: pubsub-kafka
  topic: todo.task.created
  routes:
    default: /api/events/task-created
  scopes:
    - notification-svc
    - analytics-svc
---
apiVersion: dapr.io/v2alpha1
kind: Subscription
metadata:
  name: todo-reminder-events-sub
spec:
  pubsubname: pubsub-kafka
  topic: todo.reminder.fired
  routes:
    default: /api/events/reminder-fired
  scopes:
    - notification-svc
```

### Subscription Naming Convention
```
Format: <topic-slug>-sub

Examples:
  todo-task-events-sub
  todo-reminder-events-sub
  todo-recurrence-events-sub
```

---

## File Organization

### Local Development
```
components/
  pubsub-kafka.yaml
  statestore-redis.yaml
  secretstore-local.yaml
  binding-cron-recurrence.yaml
  binding-smtp-email.yaml
  resiliency.yaml
subscriptions/
  todo-task-events-sub.yaml
  todo-reminder-events-sub.yaml
secrets/
  local-secrets.json          # .gitignored
```

### Kubernetes Deployment
```
deploy/dapr/
  components/
    pubsub-kafka.yaml
    statestore-redis.yaml
    statestore-postgres.yaml
    secretstore-k8s.yaml
    binding-smtp-email.yaml
    resiliency.yaml
  subscriptions/
    todo-task-events-sub.yaml
    todo-reminder-events-sub.yaml
```

---

## Portability Matrix

Each component includes local and production variants. Use this matrix to track environment parity:

| Component | Local Implementation | Production Implementation | Secret Store |
|-----------|---------------------|--------------------------|--------------|
| `pubsub-kafka` | Local Kafka/Redpanda (no auth) | Managed Kafka (SASL) | secretstore-k8s |
| `statestore-redis` | Local Redis (no auth) | Managed Redis (TLS + password) | secretstore-k8s |
| `statestore-postgres` | Local PostgreSQL | Neon PostgreSQL (SSL) | secretstore-k8s |
| `secretstore-*` | Local file (`local-secrets.json`) | Kubernetes Secrets | — |
| `binding-cron-*` | Same | Same | — |
| `binding-smtp-email` | MailHog/MailPit (port 1025) | SMTP relay (port 587, TLS) | secretstore-k8s |
| `binding-http-webhook` | Local endpoint | External webhook URL | secretstore-k8s |

---

## Validation Checklist

Before finalizing any Dapr component YAML, verify:

- [ ] `apiVersion` is `dapr.io/v1alpha1` (or `v2alpha1` for subscriptions)
- [ ] `kind` is `Component`, `Resiliency`, or `Subscription`
- [ ] `metadata.name` follows the naming convention (`<building-block>-<implementation>[-qualifier]`)
- [ ] `spec.type` matches a valid Dapr component type (e.g., `pubsub.kafka`, `state.redis`)
- [ ] `spec.version` is set to `v1`
- [ ] All sensitive metadata uses `secretKeyRef` instead of plain `value`
- [ ] `auth.secretStore` is set when `secretKeyRef` is used in production components
- [ ] `scopes` restrict the component to only the services that need it
- [ ] Local and production variants exist for every component
- [ ] Secrets file is `.gitignored` and never committed
- [ ] Resiliency policy is defined with retry, timeout, and circuit breaker for every component
- [ ] Subscription `routes.default` endpoint matches the actual handler path in the consuming service
- [ ] Subscription `pubsubname` matches the component `metadata.name` of the pub/sub component
- [ ] No hardcoded connection strings, passwords, or API keys appear anywhere

## Common Authoring Mistakes

| Mistake | Why It's Wrong | Correct Approach |
|---------|---------------|-----------------|
| Hardcoded `brokers` in production YAML | Leaks infrastructure details; not portable | Use `secretKeyRef` for all connection strings |
| Missing `scopes` | Every service gets access to every component | Scope to only the app IDs that need it |
| No `auth.secretStore` field | `secretKeyRef` won't resolve without it | Set `auth.secretStore` when using secret refs |
| Same component name, different types | Name collisions cause sidecar init failures | Use unique names: `statestore-redis` vs `statestore-postgres` |
| Omitting resiliency policy | Defaults may not match your SLA/timeout needs | Always define explicit retry, timeout, circuit breaker |
| `initialOffset: newest` without justification | Misses messages published before consumer started | Default to `oldest`; use `newest` only for real-time-only consumers |
| Plain `value` for passwords in K8s manifests | Secrets visible in YAML files and version control | Always use `secretKeyRef` + K8s Secret objects |
| Subscription `pubsubname` mismatch | Subscription silently fails to bind | Verify name matches the component's `metadata.name` exactly |
| Missing `direction` on bindings | Dapr may not initialize the binding correctly | Always set `direction` to `input` or `output` |

## Quick Reference: Dapr Component Types

| Building Block | Component Type | Common Implementations |
|----------------|---------------|----------------------|
| Pub/Sub | `pubsub.*` | `pubsub.kafka`, `pubsub.redis`, `pubsub.rabbitmq` |
| State Store | `state.*` | `state.redis`, `state.postgresql`, `state.mongodb` |
| Secret Store | `secretstores.*` | `secretstores.kubernetes`, `secretstores.local.file`, `secretstores.azure.keyvault` |
| Input Binding | `bindings.*` | `bindings.cron`, `bindings.kafka` (consumer), `bindings.rabbitmq` |
| Output Binding | `bindings.*` | `bindings.smtp`, `bindings.http`, `bindings.kafka` (producer), `bindings.twilio` |
| Configuration | `configuration.*` | `configuration.redis`, `configuration.postgresql` |
| Lock | `lock.*` | `lock.redis`, `lock.postgresql` |
