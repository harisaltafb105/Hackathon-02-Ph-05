# Event-Driven Feature Mapping Skill

## Purpose
Map Todo application features to their Kafka events and Dapr API bindings. This skill provides the translation layer between feature specifications and the event-driven infrastructure, producing clear producer/consumer responsibility assignments for every feature.

## Input
- **Feature spec**: The feature specification (from `specs/<feature>/spec.md`) describing what the feature does, its data model, and its state transitions
- **Event schema**: The event envelope and payload schemas (from Kafka Event Architect or existing event contracts)

## Output
- **Producer/consumer responsibilities**: A complete mapping of which services produce which events and which services consume them, including Dapr API bindings, topic assignments, and trigger conditions

## Used By
- **Advanced Features Architect Agent** — for designing event hooks when building intermediate/advanced Todo features
- **Kafka Event Architect Agent** — for validating producer/consumer boundaries and topic-to-service mappings

---

## Core Mapping Process

### Step 1: Feature Decomposition
Break the feature into state-changing operations. Each state change is a candidate for an event.

```
Feature: [Feature Name]
  Operation 1: [verb] [noun] → State Change → Candidate Event
  Operation 2: [verb] [noun] → State Change → Candidate Event
  ...
```

**Example:**
```
Feature: Priority System
  Operation 1: Set priority       → priority_changed  → todo.task.priority-changed
  Operation 2: Escalate priority  → priority_escalated → todo.task.priority-escalated
  Operation 3: Clear priority     → priority_cleared   → todo.task.priority-changed (payload: newPriority=null)
```

### Step 2: Event Classification
Classify each candidate event by type:

| Classification | Description | Kafka Behavior | Example |
|----------------|-------------|----------------|---------|
| **Domain Event** | Core business state change | Persistent, retained | `todo.task.created` |
| **Integration Event** | Cross-service notification | Persistent, consumed | `todo.reminder.fired` |
| **System Event** | Infrastructure/operational | Short retention, monitoring | `todo.system.health-check` |
| **Command Event** | Trigger for async processing | Consumed and acknowledged | `todo.recurrence.generate-instances` |

### Step 3: Producer Assignment
Assign exactly one producing service per event:

```
Rule: Single Writer Principle
  - One service owns one event type
  - The service that owns the aggregate state produces the event
  - If multiple services could produce the same event, the aggregate owner wins
```

### Step 4: Consumer Assignment
Map consumers to events with their purpose and Dapr binding:

```
Consumer Mapping:
  Event: [event-name]
  Consumer 1: [service] — Purpose: [why] — Dapr API: [binding]
  Consumer 2: [service] — Purpose: [why] — Dapr API: [binding]
```

### Step 5: Dapr API Binding
Map each event flow to its Dapr component:

| Dapr API | Use Case | Configuration |
|----------|----------|---------------|
| **Pub/Sub** | Async event distribution (Kafka-backed) | `pubsub.kafka` component |
| **Service Invocation** | Synchronous request-reply between services | `invokeMethod` |
| **State Management** | Caching intermediate event state | `statestore` component |
| **Bindings (Input)** | External trigger → service (webhooks, cron) | Input binding component |
| **Bindings (Output)** | Service → external system (email, SMS) | Output binding component |
| **Jobs API** | Scheduled/recurring task triggers | Jobs API with reminder schedule |

---

## Feature-to-Event Mapping Template

Use this template for every feature mapping:

```markdown
## Feature: [Feature Name]
**Spec Reference:** specs/<feature>/spec.md
**Status:** Proposed | Approved | Implemented

### State Changes
| Operation | State Change | Event Name | Classification |
|-----------|-------------|------------|----------------|
| [verb noun] | [old → new] | [domain.entity.action] | [Domain/Integration/System/Command] |

### Producer Responsibilities
| Event | Producing Service | Trigger Condition | Partition Key | Idempotency Key |
|-------|-------------------|-------------------|---------------|-----------------|
| [event-name] | [service] | [when this fires] | [key field] | [dedup field] |

### Consumer Responsibilities
| Event | Consuming Service | Consumer Group | Purpose | Dapr API | Error Strategy |
|-------|-------------------|----------------|---------|----------|----------------|
| [event-name] | [service] | [group-name] | [why consuming] | [pub/sub, invoke, etc.] | [retry/DLQ] |

### Kafka Topic Mapping
| Topic Name | Events Carried | Partitions | Retention | Cleanup |
|------------|---------------|------------|-----------|---------|
| [topic] | [event-1, event-2] | [count] | [duration] | [policy] |

### Dapr Component Mapping
| Component | Type | Bound To | Configuration |
|-----------|------|----------|---------------|
| [name] | [pub/sub, state, binding] | [service(s)] | [key settings] |

### Event Payload Schema
Event: [event-name]
Version: [semver]
```json
{
  "eventId": "uuid",
  "eventType": "[domain.entity.action]",
  "eventVersion": "1.0.0",
  "timestamp": "ISO-8601",
  "source": "[producing-service]",
  "correlationId": "uuid",
  "payload": {
    // feature-specific fields
  }
}
```
```

---

## Reference Mappings: Todo Application Features

### Basic CRUD Features
| Feature | Events | Producer | Consumers | Dapr API |
|---------|--------|----------|-----------|----------|
| Create Task | `todo.task.created` | todo-api | notification-svc, analytics-svc | Pub/Sub |
| Update Task | `todo.task.updated` | todo-api | notification-svc, search-indexer | Pub/Sub |
| Delete Task | `todo.task.deleted` | todo-api | search-indexer, analytics-svc | Pub/Sub |
| Complete Task | `todo.task.completed` | todo-api | notification-svc, analytics-svc, recurrence-svc | Pub/Sub |

### Intermediate Features
| Feature | Events | Producer | Consumers | Dapr API |
|---------|--------|----------|-----------|----------|
| Priority Change | `todo.task.priority-changed` | todo-api | notification-svc (if escalated), analytics-svc | Pub/Sub |
| Tag Added | `todo.task.tag-added` | todo-api | search-indexer | Pub/Sub |
| Tag Removed | `todo.task.tag-removed` | todo-api | search-indexer | Pub/Sub |
| Due Date Set | `todo.task.due-date-set` | todo-api | reminder-svc (schedule reminder) | Pub/Sub |
| Due Date Changed | `todo.task.due-date-changed` | todo-api | reminder-svc (reschedule) | Pub/Sub |
| Filter/Search | _(read-only, no events)_ | — | — | Service Invocation |

### Advanced Features
| Feature | Events | Producer | Consumers | Dapr API |
|---------|--------|----------|-----------|----------|
| Recurring Task Rule Created | `todo.recurrence.rule-created` | todo-api | recurrence-svc (schedule generation) | Pub/Sub |
| Recurrence Instance Generated | `todo.recurrence.instance-created` | recurrence-svc | todo-api (create task instance) | Pub/Sub |
| Reminder Scheduled | `todo.reminder.scheduled` | reminder-svc | — (internal state) | Jobs API |
| Reminder Fired | `todo.reminder.fired` | reminder-svc | notification-svc (dispatch) | Pub/Sub + Output Binding |
| Reminder Snoozed | `todo.reminder.snoozed` | todo-api | reminder-svc (reschedule) | Pub/Sub |
| Bulk Operation | `todo.batch.executed` | todo-api | analytics-svc, search-indexer | Pub/Sub |

---

## Dapr-Specific Mapping Patterns

### Pattern 1: Pub/Sub Event Distribution (Most Common)
```
[Producer Service]
    → Dapr Sidecar (publish to pubsub.kafka)
        → Kafka Topic
            → Dapr Sidecar (subscribe) → [Consumer Service A]
            → Dapr Sidecar (subscribe) → [Consumer Service B]
```
**Dapr Component:** `pubsub.kafka`
**Config Keys:** `brokers`, `consumerGroup`, `authRequired`

### Pattern 2: Jobs API for Scheduled Events
```
[Service] → Dapr Jobs API (schedule job)
    → At scheduled time: Dapr invokes callback endpoint
        → [Service] handles callback → publishes domain event
```
**Use For:** Reminders, recurring task instance generation, scheduled notifications
**Dapr API:** `/v1.0-alpha1/jobs/<name>` (schedule), callback to app endpoint

### Pattern 3: Service Invocation for Synchronous Reads
```
[Frontend API] → Dapr Service Invocation → [Search Service]
    → Response returned synchronously
```
**Use For:** Search queries, filter execution, task detail retrieval
**Dapr API:** `/v1.0/invoke/<app-id>/method/<method>`

### Pattern 4: Output Binding for External Dispatch
```
[Notification Service] → Dapr Output Binding → [Email/SMS/Push Provider]
```
**Use For:** Sending reminder notifications, email digests, webhook callbacks
**Dapr Component:** `bindings.smtp`, `bindings.twilio`, `bindings.http`

---

## Validation Checklist

Before finalizing any feature-to-event mapping, verify:

- [ ] Every state-changing operation has at least one event defined
- [ ] Each event has exactly one producing service (Single Writer Principle)
- [ ] All consumer services have a named consumer group
- [ ] Kafka topic names follow `<domain>.<bounded-context>.<event-name>` convention
- [ ] Event payloads include the standard envelope (eventId, eventType, eventVersion, timestamp, source, correlationId)
- [ ] Partition keys ensure correct ordering for business invariants
- [ ] Dead-letter and retry strategies are specified for every consumer
- [ ] Dapr component type is identified for each integration point
- [ ] Read-only operations (search, filter, list) are NOT mapped to events
- [ ] Idempotency keys are defined for at-least-once consumers
- [ ] Jobs API is used for time-triggered events (reminders, recurrence) instead of polling

## Common Mapping Mistakes

| Mistake | Why It's Wrong | Correct Approach |
|---------|---------------|-----------------|
| Multiple producers for one event | Breaks event ownership, causes ordering issues | Assign one aggregate owner as the single producer |
| Events for read operations | Reads don't change state; events represent state changes | Use Dapr Service Invocation for reads |
| Missing consumer group name | Causes unintended message sharing or duplication | Always name: `<service>.<purpose>` |
| Synchronous calls where async is sufficient | Creates tight coupling and cascading failures | Use Pub/Sub for fire-and-forget notifications |
| Using Pub/Sub for request-reply | Kafka is not designed for synchronous request-reply | Use Dapr Service Invocation for request-reply |
| Polling for scheduled tasks | Wasteful and imprecise timing | Use Dapr Jobs API for scheduled triggers |
| Hardcoded topic names in services | Prevents environment-specific configuration | Use Dapr component metadata for topic resolution |

## Quick Reference: Event Naming Convention

```
Format: <domain>.<bounded-context>.<event-name>

Domain:       todo (application domain)
Context:      task | reminder | recurrence | batch | system
Event Name:   <past-tense-verb> (created, updated, deleted, completed, fired, scheduled)

Examples:
  todo.task.created
  todo.task.priority-changed
  todo.reminder.fired
  todo.recurrence.instance-created
  todo.batch.executed
  todo.system.health-check
```

## Quick Reference: Consumer Group Naming

```
Format: <service-name>.<purpose>

Examples:
  notification-svc.task-alerts
  analytics-svc.event-tracking
  search-indexer.task-updates
  recurrence-svc.completion-handling
  reminder-svc.due-date-scheduling
```
