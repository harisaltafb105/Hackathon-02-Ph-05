# Failure & Retry Strategy Skill

## Purpose
Define retries, dead-letter queues (DLQs), and idempotency guarantees for every service-to-event combination in the system. This skill provides the decision framework for choosing the right resilience pattern based on service criticality, event type, and failure classification.

## Input
- **Service**: The consuming or producing service name and its role (e.g., `notification-svc`, `analytics-svc`, `recurrence-svc`)
- **Event type**: The Kafka event being processed (e.g., `todo.task.created`, `todo.reminder.fired`)

## Output
- **Resilience rules**: A complete failure-handling specification covering retry policy, dead-letter routing, idempotency mechanism, circuit breaker settings, timeout configuration, and alerting thresholds — tailored to the specific service + event combination

## Used By
- **Notification Scheduler Agent** (`notification-scheduler`) — for configuring channel-specific retry policies, DLQ handling, and delivery idempotency
- **Dapr Integration Agent** (`dapr-integration`) — for authoring Dapr resiliency YAML policies and component-level failure recovery paths

---

## Error Classification

Before choosing a retry strategy, classify the error. Every failure falls into one of four categories.

| Category | Definition | Examples | Action |
|----------|-----------|----------|--------|
| **Transient** | Temporary infrastructure issue; will self-heal | Network timeout, 503 Service Unavailable, Kafka broker leader election, connection reset | Retry with backoff |
| **Rate-Limited** | Upstream is throttling requests | 429 Too Many Requests, Kafka quota violation, SMTP rate limit | Retry with longer backoff; respect `Retry-After` header |
| **Permanent** | Request is fundamentally invalid; retrying won't help | 400 Bad Request, 404 Not Found, schema validation failure, malformed payload, deserialization error | Route to DLQ immediately |
| **Unknown** | Unrecognized error; cause unclear | Unexpected 500, unhandled exception, null pointer, OOM | Retry cautiously (limited attempts); route to DLQ if unresolved |

### Classification Decision Tree

```
ERROR received
  │
  ├─ HTTP 4xx (except 429)?
  │    └─ PERMANENT → DLQ immediately
  │
  ├─ HTTP 429?
  │    └─ RATE-LIMITED → Retry with Retry-After or extended backoff
  │
  ├─ HTTP 5xx?
  │    ├─ 503 Service Unavailable → TRANSIENT → Retry with backoff
  │    ├─ 502 Bad Gateway → TRANSIENT → Retry with backoff
  │    └─ 500 Internal Server Error → UNKNOWN → Limited retry, then DLQ
  │
  ├─ Connection timeout / reset?
  │    └─ TRANSIENT → Retry with backoff
  │
  ├─ Deserialization / schema error?
  │    └─ PERMANENT → DLQ immediately (poison message)
  │
  └─ Anything else?
       └─ UNKNOWN → Limited retry (max 2), then DLQ
```

---

## Retry Policies

### Policy Catalog

Define one of these named policies for each service + event pair.

#### 1. `aggressive` — Fast retries, short window
```
Use when: Low-latency required, failure is likely transient (e.g., internal service invocation)
Backoff: Exponential with jitter
Initial delay: 500ms
Max delay: 5s
Max retries: 3
Max window: 15s
```

#### 2. `standard` — Balanced default
```
Use when: Most event consumers, moderate reliability needs
Backoff: Exponential with jitter
Initial delay: 1s
Max delay: 30s
Max retries: 5
Max window: 5m
```

#### 3. `patient` — Slow retries, long window
```
Use when: External dependencies with known flakiness (SMTP, SMS, webhooks)
Backoff: Exponential with jitter
Initial delay: 2s
Max delay: 60s
Max retries: 8
Max window: 15m
```

#### 4. `critical` — Maximum retry effort
```
Use when: Business-critical events where data loss is unacceptable (completions, payments)
Backoff: Exponential with jitter
Initial delay: 1s
Max delay: 120s
Max retries: 12
Max window: 30m
```

#### 5. `none` — No retries
```
Use when: Idempotent side-effect-free operations, or when DLQ reprocessing is the only retry path
Backoff: N/A
Max retries: 0
Routing: DLQ on first failure
```

### Jitter Formula

Always apply jitter to prevent thundering herd on recovery:

```
actual_delay = base_delay * (2 ^ attempt) * (0.5 + random(0, 0.5))
capped_delay = min(actual_delay, max_delay)
```

---

## Dead-Letter Queue (DLQ) Strategy

### When Messages Enter the DLQ

A message is routed to the DLQ when:
1. All retry attempts exhausted (retryable error)
2. Permanent error detected on first attempt (non-retryable)
3. Deserialization failure (poison message)
4. Processing timeout exceeded
5. Circuit breaker is open and message cannot be held

### DLQ Topic Naming

```
Format: _<service-name>.deadletter

Examples:
  _notification-svc.deadletter
  _analytics-svc.deadletter
  _search-indexer.deadletter
  _recurrence-svc.deadletter
```

For channel-specific DLQs (notification service only):
```
  _notification-svc.deadletter.email
  _notification-svc.deadletter.sms
  _notification-svc.deadletter.push
```

### DLQ Message Envelope

Every DLQ entry wraps the original message with failure metadata:

```json
{
  "dlqId": "uuid-v4",
  "originalTopic": "todo.task.created",
  "originalEventId": "uuid (from envelope.eventId)",
  "originalTimestamp": "ISO-8601 (from envelope.timestamp)",
  "consumerService": "notification-svc",
  "consumerGroup": "notification-svc.task-alerts",
  "failureCategory": "transient | rate-limited | permanent | unknown",
  "retryAttempts": [
    {
      "attempt": 1,
      "timestamp": "ISO-8601",
      "error": "Connection timeout after 10s",
      "errorCode": "ETIMEDOUT",
      "httpStatus": null
    },
    {
      "attempt": 2,
      "timestamp": "ISO-8601",
      "error": "503 Service Unavailable",
      "errorCode": null,
      "httpStatus": 503
    }
  ],
  "totalRetries": 5,
  "firstFailureAt": "ISO-8601",
  "routedToDlqAt": "ISO-8601",
  "correlationId": "uuid (from envelope.correlationId)",
  "originalMessage": { }
}
```

### DLQ Retention & Alerting

| Setting | Value | Rationale |
|---------|-------|-----------|
| Retention | 30 days | Enough time for investigation and manual replay |
| Alert: new entries | > 10 per minute | Spike indicates systemic failure |
| Alert: age | oldest entry > 48 hours unprocessed | Investigate stale failures |
| Alert: depth | > 1000 entries total | Queue growing faster than drain rate |

### DLQ Reprocessing Modes

| Mode | When to Use | Command Pattern |
|------|-------------|-----------------|
| **Single replay** | Investigate and reprocess one message | Replay by `dlqId` |
| **Bulk replay** | Systemic issue resolved; reprocess all | Replay all entries for a `consumerService` |
| **Filtered replay** | Replay only certain error categories | Replay where `failureCategory = transient` |
| **Purge** | Messages confirmed unrecoverable | Delete entries older than threshold or by filter |

---

## Idempotency Patterns

Every consumer must be idempotent — processing the same event twice must not produce duplicate side effects.

### Pattern 1: Event ID Deduplication (Recommended Default)

Store processed `eventId` values and check before processing.

```
ON message received:
  IF eventId EXISTS in dedup store:
    ACK message (already processed)
    RETURN
  ELSE:
    PROCESS message
    STORE eventId in dedup store with TTL
    ACK message
```

**Dedup store options:**
| Store | Pros | Cons | Use When |
|-------|------|------|----------|
| Redis (via Dapr state store) | Fast, TTL-native, shared across instances | Requires Redis availability | Default for most services |
| PostgreSQL (via Dapr state store) | Durable, transactional with business data | Slower than Redis | When dedup must survive full Redis outage |
| In-memory (local) | Zero dependency, fastest | Lost on restart; not shared across replicas | Single-instance, non-critical services only |

**TTL for dedup entries:** Match the Kafka topic retention period (typically 7 days). Events older than retention can't arrive again from Kafka.

### Pattern 2: Idempotent Upsert

Make the operation itself idempotent by design.

```
Instead of: INSERT notification_log (id, user_id, message, ...)
Use:        INSERT notification_log (id, user_id, message, ...)
            ON CONFLICT (event_id) DO NOTHING
```

**Use when:** The consumer writes to a database and can use the `eventId` as a natural key or unique constraint.

### Pattern 3: Conditional State Check

Check the current state before applying the operation.

```
ON todo.task.completed received:
  READ current task status
  IF status == 'completed':
    ACK (already applied)
    RETURN
  ELSE:
    UPDATE status = 'completed'
    ACK
```

**Use when:** The operation is a state transition and the target state can be checked cheaply.

### Pattern 4: Transactional Outbox

Guarantee that the business operation and the event acknowledgment happen atomically.

```
BEGIN TRANSACTION
  PROCESS business logic
  WRITE result to database
  WRITE eventId to processed_events table
COMMIT TRANSACTION
ACK message
```

**Use when:** Exactly-once semantics are required and the consumer writes to a transactional database.

---

## Circuit Breaker Configuration

Circuit breakers prevent a failing dependency from consuming retry budget indefinitely.

### Circuit Breaker States

```
CLOSED (normal)
  │
  ├─ consecutiveFailures > threshold
  │    └─ OPEN (reject all requests; return fast failure)
  │         │
  │         ├─ timeout elapsed
  │         │    └─ HALF-OPEN (allow 1 probe request)
  │         │         │
  │         │         ├─ probe succeeds → CLOSED
  │         │         └─ probe fails → OPEN (reset timeout)
```

### Per-Dependency Configuration

| Dependency | Trip Threshold | Open Timeout | Half-Open Probes | Rationale |
|------------|---------------|-------------|------------------|-----------|
| Kafka broker | 5 consecutive failures | 60s | 1 | Broker recovery is usually fast |
| Redis state store | 3 consecutive failures | 30s | 1 | Redis failure is usually fast or permanent |
| PostgreSQL | 3 consecutive failures | 30s | 1 | Connection pool exhaustion recovers on cooldown |
| SMTP provider | 5 consecutive failures | 120s | 1 | Email providers have longer recovery cycles |
| SMS provider | 3 consecutive failures | 120s | 1 | SMS gateways can be slow to recover |
| External webhook | 5 consecutive failures | 60s | 2 | Webhooks may be temporarily unreachable |
| Dapr service invocation | 3 consecutive failures | 15s | 1 | Sidecar mesh recovers quickly |

---

## Timeout Configuration

Every async operation must have an explicit timeout. Never rely on defaults.

| Operation | Timeout | Rationale |
|-----------|---------|-----------|
| Kafka produce | 10s | Broker acknowledgment should be fast |
| Kafka consume (poll) | 30s | Allow for rebalancing |
| Dapr pub/sub publish | 10s | Sidecar-to-broker round trip |
| Dapr state get/set | 5s | State store should respond quickly |
| Dapr service invocation | 15s | Service-to-service via sidecar mesh |
| HTTP webhook call | 30s | External endpoints may be slow |
| SMTP send | 30s | SMTP handshake + delivery |
| SMS send | 15s | API-based, should be fast |
| Database query | 10s | Queries should be indexed and fast |
| Jobs API schedule | 5s | Lightweight Dapr API call |

---

## Dapr Resiliency YAML Integration

Translate the rules from this skill into Dapr resiliency YAML.

### Template: Service-Specific Resiliency

```yaml
apiVersion: dapr.io/v1alpha1
kind: Resiliency
metadata:
  name: <service-name>-resiliency
  namespace: <namespace>
spec:
  policies:
    retries:
      # Map to named retry policies from the catalog
      aggressive:
        policy: exponential
        maxInterval: 5s
        maxRetries: 3
      standard:
        policy: exponential
        maxInterval: 30s
        maxRetries: 5
      patient:
        policy: exponential
        maxInterval: 60s
        maxRetries: 8
      critical:
        policy: exponential
        maxInterval: 120s
        maxRetries: 12

    timeouts:
      fast: 5s
      default: 15s
      slow: 30s

    circuitBreakers:
      kafkaBreaker:
        maxRequests: 1
        interval: 60s
        timeout: 60s
        trip: consecutiveFailures > 5
      stateBreaker:
        maxRequests: 1
        interval: 30s
        timeout: 30s
        trip: consecutiveFailures > 3
      externalBreaker:
        maxRequests: 2
        interval: 120s
        timeout: 120s
        trip: consecutiveFailures > 5
      sidecarBreaker:
        maxRequests: 1
        interval: 15s
        timeout: 15s
        trip: consecutiveFailures > 3

  targets:
    components:
      pubsub-kafka:
        outbound:
          retry: standard
          timeout: default
          circuitBreaker: kafkaBreaker
        inbound:
          retry: standard
          timeout: slow
      statestore-redis:
        outbound:
          retry: aggressive
          timeout: fast
          circuitBreaker: stateBreaker
      statestore-postgres:
        outbound:
          retry: standard
          timeout: default
          circuitBreaker: stateBreaker
      binding-smtp-email:
        outbound:
          retry: patient
          timeout: slow
          circuitBreaker: externalBreaker
      binding-http-webhook:
        outbound:
          retry: patient
          timeout: slow
          circuitBreaker: externalBreaker

    apps:
      # Service invocation targets
      todo-api:
        retry: aggressive
        timeout: default
        circuitBreaker: sidecarBreaker
      notification-svc:
        retry: standard
        timeout: default
        circuitBreaker: sidecarBreaker
```

---

## Service + Event Resilience Matrix

Use this matrix to look up the correct resilience rules for any service + event combination.

### Notification Service

| Event | Retry Policy | Idempotency Pattern | DLQ | Circuit Breaker | Timeout |
|-------|-------------|--------------------|----|-----------------|---------|
| `todo.task.created` | `standard` | Event ID dedup (Redis) | `_notification-svc.deadletter` | kafkaBreaker | 15s |
| `todo.task.completed` | `standard` | Event ID dedup (Redis) | `_notification-svc.deadletter` | kafkaBreaker | 15s |
| `todo.task.priority-changed` | `standard` | Event ID dedup (Redis) | `_notification-svc.deadletter` | kafkaBreaker | 15s |
| `todo.reminder.fired` | `critical` | Idempotent upsert (PostgreSQL) | `_notification-svc.deadletter` | kafkaBreaker | 30s |
| Email dispatch | `patient` | Event ID dedup (Redis) | `_notification-svc.deadletter.email` | externalBreaker | 30s |
| SMS dispatch | `patient` | Event ID dedup (Redis) | `_notification-svc.deadletter.sms` | externalBreaker | 15s |

### Analytics Service

| Event | Retry Policy | Idempotency Pattern | DLQ | Circuit Breaker | Timeout |
|-------|-------------|--------------------|----|-----------------|---------|
| `todo.task.created` | `standard` | Idempotent upsert (PostgreSQL) | `_analytics-svc.deadletter` | kafkaBreaker | 10s |
| `todo.task.completed` | `standard` | Idempotent upsert (PostgreSQL) | `_analytics-svc.deadletter` | kafkaBreaker | 10s |
| `todo.task.priority-changed` | `standard` | Idempotent upsert (PostgreSQL) | `_analytics-svc.deadletter` | kafkaBreaker | 10s |
| `todo.batch.executed` | `standard` | Idempotent upsert (PostgreSQL) | `_analytics-svc.deadletter` | kafkaBreaker | 15s |

### Search Indexer

| Event | Retry Policy | Idempotency Pattern | DLQ | Circuit Breaker | Timeout |
|-------|-------------|--------------------|----|-----------------|---------|
| `todo.task.created` | `standard` | Idempotent upsert (index) | `_search-indexer.deadletter` | stateBreaker | 10s |
| `todo.task.updated` | `standard` | Idempotent upsert (index) | `_search-indexer.deadletter` | stateBreaker | 10s |
| `todo.task.deleted` | `aggressive` | Conditional state check | `_search-indexer.deadletter` | stateBreaker | 5s |
| `todo.task.tag-added` | `standard` | Idempotent upsert (index) | `_search-indexer.deadletter` | stateBreaker | 10s |
| `todo.task.tag-removed` | `standard` | Idempotent upsert (index) | `_search-indexer.deadletter` | stateBreaker | 10s |

### Recurrence Service

| Event | Retry Policy | Idempotency Pattern | DLQ | Circuit Breaker | Timeout |
|-------|-------------|--------------------|----|-----------------|---------|
| `todo.task.completed` | `critical` | Transactional outbox (PostgreSQL) | `_recurrence-svc.deadletter` | kafkaBreaker | 15s |
| `todo.recurrence.rule-created` | `critical` | Transactional outbox (PostgreSQL) | `_recurrence-svc.deadletter` | kafkaBreaker | 15s |

### Reminder Service

| Event | Retry Policy | Idempotency Pattern | DLQ | Circuit Breaker | Timeout |
|-------|-------------|--------------------|----|-----------------|---------|
| `todo.task.due-date-set` | `critical` | Event ID dedup (Redis) | `_reminder-svc.deadletter` | kafkaBreaker | 10s |
| `todo.task.due-date-changed` | `critical` | Event ID dedup (Redis) | `_reminder-svc.deadletter` | kafkaBreaker | 10s |
| `todo.reminder.snoozed` | `standard` | Event ID dedup (Redis) | `_reminder-svc.deadletter` | kafkaBreaker | 10s |
| Jobs API callback | `aggressive` | Conditional state check | `_reminder-svc.deadletter` | sidecarBreaker | 5s |

---

## Resilience Rule Definition Template

Use this template when defining rules for a new service + event pair.

```markdown
## Resilience Rules: [Service] consuming [Event]

**Consumer Group:** [consumer-group-name]
**Criticality:** Low / Medium / High / Critical
**Data Loss Tolerance:** Acceptable / Not Acceptable

### Error Classification Overrides
| Error | Default Category | Override | Reason |
|-------|-----------------|----------|--------|
| [specific error] | [default] | [override] | [why] |

### Retry Policy
- **Named policy:** [aggressive / standard / patient / critical / none]
- **Initial delay:** [ms]
- **Max delay:** [s]
- **Max retries:** [n]
- **Max window:** [duration]

### Dead-Letter Queue
- **DLQ topic:** [topic name]
- **Retention:** [days]
- **Alert threshold:** [entries/minute]
- **Reprocessing strategy:** [manual / automatic / filtered]

### Idempotency
- **Pattern:** [Event ID dedup / Idempotent upsert / Conditional state check / Transactional outbox]
- **Dedup store:** [Redis / PostgreSQL / In-memory]
- **Dedup TTL:** [duration]
- **Dedup key:** [field used for deduplication]

### Circuit Breaker
- **Named breaker:** [kafkaBreaker / stateBreaker / externalBreaker / sidecarBreaker]
- **Trip threshold:** [n consecutive failures]
- **Open timeout:** [duration]

### Timeouts
- **Processing timeout:** [duration]
- **Dependency timeouts:** [per-dependency list]

### Alerting
| Metric | Threshold | Severity | Action |
|--------|-----------|----------|--------|
| Retry rate | > [x]% | Warning | Investigate dependency health |
| DLQ inflow | > [n]/min | Critical | Page on-call; check downstream |
| Consumer lag | > [n] messages | Warning | Scale consumers or investigate |
| Circuit breaker open | > [n] minutes | Critical | Dependency is down; failover |
```

---

## Validation Checklist

Before finalizing resilience rules for any service + event pair:

- [ ] Error classification covers all known failure modes for this dependency
- [ ] Retry policy name matches one from the catalog (aggressive / standard / patient / critical / none)
- [ ] Jitter is applied to backoff (not pure exponential)
- [ ] Permanent errors skip retries and route to DLQ immediately
- [ ] DLQ topic follows naming convention (`_<service>.deadletter[.<channel>]`)
- [ ] DLQ message envelope includes all retry attempt metadata
- [ ] DLQ retention is set (default: 30 days)
- [ ] DLQ alerting thresholds are configured (depth, age, inflow rate)
- [ ] Idempotency pattern is specified with dedup store and TTL
- [ ] Circuit breaker is configured for every external dependency
- [ ] Every async operation has an explicit timeout (no defaults relied upon)
- [ ] Dapr resiliency YAML reflects the rules defined here
- [ ] Retry and timeout values are externalized (not hardcoded in application code)
- [ ] Resilience rules are documented in the service's failure recovery path

## Common Resilience Mistakes

| Mistake | Risk | Correct Approach |
|---------|------|-----------------|
| Retrying permanent errors | Wastes resources; delays DLQ processing | Classify errors first; route 4xx to DLQ immediately |
| No jitter on backoff | Thundering herd on recovery floods dependency | Always add random jitter: `delay * (0.5 + random(0, 0.5))` |
| Infinite retries | Consumer stalls on one bad message forever | Always set `maxRetries` and `maxWindow`; route to DLQ when exhausted |
| No idempotency on consumer | Duplicate processing on retry or rebalance | Choose an idempotency pattern; Event ID dedup is the safe default |
| DLQ without metadata | Can't diagnose or replay failures | Include original message, all retry attempts, error details, correlation ID |
| Same retry policy for all events | Critical events get under-retried; non-critical get over-retried | Match policy to event criticality and data loss tolerance |
| Circuit breaker without timeout | Breaker stays open forever if no probes | Always configure the open-state timeout for automatic half-open transition |
| Hardcoded retry values in code | Can't adjust without redeployment | Use Dapr resiliency YAML or externalized config; never hardcode |
| Swallowing errors silently | Failures disappear; no alerting, no DLQ entry | Log every error with correlation ID; route to DLQ if unrecoverable |
| Retrying without circuit breaker | Floods a failing dependency, making recovery slower | Pair every retry policy with a circuit breaker on the target dependency |
