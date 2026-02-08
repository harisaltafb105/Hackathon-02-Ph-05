# Event Schema Governance Skill

## Purpose
Prevent breaking changes in Kafka events. This skill provides the rules, review process, and tooling patterns for evolving event schemas safely — ensuring that producers can add capabilities without destroying existing consumers.

## Input
- **Event definitions**: New or modified event schemas (envelope + payload), including field names, types, required/optional status, and default values

## Output
- **Versioned schema contracts**: Validated, compatibility-checked event schemas with explicit version numbers, compatibility mode assignments, and migration plans when breaking changes are unavoidable

## Used By
- **Kafka Event Architect Agent** (`kafka-event-architect`) — as the authoritative reference for schema review, versioning decisions, and compatibility enforcement

---

## The Canonical Event Envelope

Every Kafka event in this project must use this envelope. The envelope fields are **frozen** — they cannot be renamed, retyped, or removed.

```json
{
  "eventId": "string (UUID v4)",
  "eventType": "string (<domain>.<entity>.<action>)",
  "eventVersion": "string (semver: major.minor.patch)",
  "timestamp": "string (ISO-8601 with timezone)",
  "source": "string (producing service app-id)",
  "correlationId": "string (UUID v4, propagated across event chains)",
  "payload": { }
}
```

### Envelope Field Rules

| Field | Type | Required | Mutable | Governance Rule |
|-------|------|----------|---------|-----------------|
| `eventId` | UUID v4 | Yes | No | Unique per event instance. Used for idempotency dedup. |
| `eventType` | string | Yes | No | Follows `<domain>.<entity>.<action>` convention. Cannot change after first publish. |
| `eventVersion` | semver | Yes | No | Incremented per schema change. Consumers use this for routing. |
| `timestamp` | ISO-8601 | Yes | No | Set by producer at publish time. Always includes timezone offset. |
| `source` | string | Yes | No | Dapr app-id of the producing service. Single writer principle. |
| `correlationId` | UUID v4 | Yes | No | Propagated from the originating request through all downstream events. |
| `payload` | object | Yes | Yes | Feature-specific data. Subject to schema governance rules below. |

---

## Schema Compatibility Modes

Every topic is assigned a compatibility mode. This mode determines what changes are allowed without a breaking version bump.

### Mode Definitions

| Mode | Allowed Changes | Prohibited Changes | Use When |
|------|----------------|-------------------|----------|
| **BACKWARD** | Add optional fields with defaults. Remove optional fields. | Add required fields. Change field types. Rename fields. | Default for most topics. New consumers can read old messages. |
| **FORWARD** | Remove optional fields. Add required fields with defaults. | Change field types. Rename fields. | Consumers are updated before producers. |
| **FULL** | Add/remove optional fields with defaults only. | Any required field change. Any type change. Any rename. | Critical business events (payments, completions). |
| **NONE** | Anything. | Nothing prohibited. | Internal/technical topics only (`_service.deadletter`). |

### Default Assignment

```
Domain events     → BACKWARD (recommended default)
Integration events → BACKWARD
Critical events    → FULL (payments, completions, deletions)
System events     → NONE
Dead-letter topics → NONE
```

---

## Change Classification

When an event schema is modified, classify the change before applying it.

### Safe Changes (No Version Bump Required)

These changes are compatible under BACKWARD and FULL modes:

| Change | Example | Why Safe |
|--------|---------|----------|
| Add optional field with default | `"priority": null` added to payload | Old consumers ignore unknown fields; new consumers get default |
| Add documentation/description | JSON Schema `description` updated | No wire format change |
| Relax validation constraint | `maxLength: 50` → `maxLength: 100` | Existing data still valid |

### Minor Changes (Patch/Minor Version Bump)

These require a `eventVersion` minor bump (e.g., `1.0.0` → `1.1.0`):

| Change | Example | Required Action |
|--------|---------|-----------------|
| Add optional field without default | `"tags": []` added | Bump minor. Consumers must handle field absence. |
| Deprecate a field (mark for removal) | `"legacyStatus"` marked deprecated | Bump minor. Add deprecation notice. Set removal timeline. |
| Tighten validation constraint | `maxLength: 100` → `maxLength: 50` | Bump minor. Verify existing data complies. |

### Breaking Changes (Major Version Bump)

These require a `eventVersion` major bump (e.g., `1.x.x` → `2.0.0`) and a migration plan:

| Change | Example | Why Breaking |
|--------|---------|-------------|
| Remove a field | `"legacyStatus"` deleted | Consumers reading this field get null/error |
| Rename a field | `"dueDate"` → `"due_date"` | Old consumers can't find the field |
| Change field type | `"priority": "string"` → `"priority": "integer"` | Deserialization fails for old consumers |
| Add required field without default | `"tenantId": required, no default` | Old messages lack the field; consumer validation fails |
| Change field semantics | `"status"` values change from `["open","closed"]` to `["pending","done","archived"]` | Consumer business logic breaks |
| Change partition key | `orderId` → `userId` | Ordering guarantees broken for existing consumers |

---

## Schema Review Process

Every event schema change must pass this review before merge.

### Step 1: Classify the Change

```
INPUT:  Diff of old schema → new schema
OUTPUT: Classification (Safe / Minor / Breaking)
```

Compare field-by-field:
- New fields added? → Check if optional with default
- Fields removed? → Breaking
- Fields renamed? → Breaking
- Field types changed? → Breaking
- Required/optional changed? → Check direction (required→optional is safe; optional→required is breaking)
- Default values changed? → Minor
- Validation constraints changed? → Check direction (relaxing is safe; tightening is minor)

### Step 2: Check Compatibility Mode

```
IF change is Breaking AND topic mode is BACKWARD or FULL:
  → REJECT change on current topic
  → Require migration plan (see Breaking Change Migration below)

IF change is Minor AND topic mode is FULL:
  → REJECT unless field is optional with default
  → Require explicit approval

IF change is Safe:
  → APPROVE
```

### Step 3: Validate Schema Artifact

Run the schema through structural validation:

```
CHECK: All envelope fields present and correctly typed
CHECK: eventVersion is incremented appropriately for change classification
CHECK: All required payload fields have types defined
CHECK: All optional fields have explicit default values
CHECK: No PII fields without encryption annotation
CHECK: No fields named with reserved prefixes (_internal, __meta)
CHECK: Field names use camelCase consistently
CHECK: Enum values are exhaustive and documented
CHECK: Nested objects have their own versioning consideration documented
```

### Step 4: Consumer Impact Assessment

For every consumer of the topic, verify:

```
FOR EACH consumer of this topic:
  CAN consumer deserialize the new schema?
    IF NO → consumer must be updated first (or change is blocked)
  DOES consumer use any removed/renamed fields?
    IF YES → consumer must be updated first (or change is blocked)
  DOES consumer validate against strict schema?
    IF YES → verify new fields don't fail validation
```

Output as a table:

```markdown
### Consumer Impact Assessment

| Consumer | Consumer Group | Impact | Action Required | Update Deadline |
|----------|---------------|--------|-----------------|-----------------|
| notification-svc | notification-svc.task-alerts | None — ignores new field | None | — |
| analytics-svc | analytics-svc.event-tracking | Low — new optional field available | Optional: start reading `priority` | Sprint N+1 |
| search-indexer | search-indexer.task-updates | Breaking — reads removed `legacyStatus` | Must update before migration | Before cutover |
```

---

## Breaking Change Migration Runbook

When a breaking change is unavoidable, follow this process.

### Phase 1: Prepare (Week 1)

1. Define the new schema with major version bump (e.g., `2.0.0`)
2. Create a new topic if the breaking change affects the partition key or event type:
   - New topic: `todo.task.created.v2`
   - Old topic: `todo.task.created` (continues operating)
3. If partition key and event type are unchanged, same topic can be used with dual-version publishing
4. Document the migration in the schema registry

### Phase 2: Dual-Publish (Week 2-3)

```
Producer publishes BOTH:
  → Old schema (v1) to original topic/format
  → New schema (v2) to new topic or same topic with new version

All existing consumers continue reading v1 — no disruption.
```

### Phase 3: Consumer Cutover (Week 3-4)

```
FOR EACH consumer (ordered by criticality, least critical first):
  1. Update consumer code to read v2 schema
  2. Deploy updated consumer
  3. Verify consumer processes v2 events correctly
  4. Monitor for errors (24h observation minimum)
  5. Mark consumer as "migrated" in tracking table
```

### Phase 4: Deprecation (Week 5)

```
WHEN all consumers are migrated to v2:
  1. Stop dual-publishing — producer sends v2 only
  2. Set retention on old topic to 7 days (allow rollback window)
  3. After 7 days, delete old topic (or mark as deprecated in registry)
  4. Update schema registry: v1 marked DEPRECATED
```

### Migration Tracking Template

```markdown
## Schema Migration: [event-type] v1 → v2

| Phase | Status | Start Date | End Date | Owner |
|-------|--------|------------|----------|-------|
| Prepare | ✅ / ⏳ | | | |
| Dual-Publish | ✅ / ⏳ | | | |
| Consumer Cutover | ✅ / ⏳ | | | |
| Deprecation | ✅ / ⏳ | | | |

### Consumer Migration Status
| Consumer | Status | Migrated Date | Verified By |
|----------|--------|---------------|-------------|
| notification-svc | ✅ Migrated / ⏳ Pending / 🔄 In Progress | | |
| analytics-svc | | | |
| search-indexer | | | |
```

---

## Schema Registry Patterns

### Registry as Source of Truth

The schema registry is the single source of truth for all event schemas. Schemas are registered before any producer publishes.

```
Workflow:
  1. Author schema → 2. Register in registry → 3. Set compatibility mode
  → 4. Producer references registered schema → 5. Consumer validates against registry
```

### Registry Entry Format

Each schema registration should include:

```json
{
  "subject": "<topic-name>-value",
  "version": 1,
  "schema": "{ ... JSON Schema / Avro / Protobuf ... }",
  "schemaType": "JSON",
  "compatibility": "BACKWARD",
  "metadata": {
    "owner": "<producing-service>",
    "domain": "<bounded-context>",
    "classification": "domain-event | integration-event | system-event",
    "piiFields": [],
    "deprecatedFields": [],
    "createdAt": "ISO-8601",
    "lastModified": "ISO-8601"
  }
}
```

### Subject Naming Convention

```
Format: <topic-name>-value

Examples:
  todo.task.created-value
  todo.reminder.fired-value
  todo.recurrence.instance-created-value

For key schemas (if partition key has a schema):
  <topic-name>-key
```

---

## Schema Definition Template

Use this template when defining a new event schema or modifying an existing one.

```markdown
## Event Schema: [eventType]

**Topic:** [topic-name]
**Compatibility Mode:** [BACKWARD / FORWARD / FULL / NONE]
**Current Version:** [semver]
**Owner (Producer):** [service-name]
**Classification:** [Domain / Integration / System / Command]

### Envelope + Payload

```json
{
  "eventId": "uuid-v4",
  "eventType": "[domain].[entity].[action]",
  "eventVersion": "[major].[minor].[patch]",
  "timestamp": "2026-01-15T10:30:00.000Z",
  "source": "[producing-service]",
  "correlationId": "uuid-v4",
  "payload": {
    "fieldName": {
      "type": "[string|integer|boolean|number|array|object]",
      "required": true,
      "default": null,
      "description": "[what this field represents]",
      "pii": false,
      "since": "1.0.0",
      "deprecated": false,
      "deprecatedSince": null,
      "removalVersion": null
    }
  }
}
```

### Field Inventory

| Field | Type | Required | Default | Since | Deprecated | PII | Description |
|-------|------|----------|---------|-------|------------|-----|-------------|
| [name] | [type] | [y/n] | [value] | [ver] | [y/n] | [y/n] | [desc] |

### Change History

| Version | Date | Change | Classification | Migration Required |
|---------|------|--------|---------------|-------------------|
| 1.0.0 | [date] | Initial schema | — | No |
| 1.1.0 | [date] | Added `priority` (optional, default: null) | Minor | No |
| 2.0.0 | [date] | Changed `status` type from string to enum | Breaking | Yes — see migration [link] |
```

---

## Reference: Todo Application Event Schemas

### `todo.task.created` (v1.0.0)

```json
{
  "eventId": "uuid",
  "eventType": "todo.task.created",
  "eventVersion": "1.0.0",
  "timestamp": "ISO-8601",
  "source": "todo-api",
  "correlationId": "uuid",
  "payload": {
    "taskId": { "type": "string", "required": true, "description": "UUID of the created task" },
    "userId": { "type": "string", "required": true, "description": "Owner user ID (tenant isolation key)" },
    "title": { "type": "string", "required": true, "description": "Task title" },
    "description": { "type": "string", "required": false, "default": null, "description": "Task description" },
    "status": { "type": "string", "required": true, "default": "pending", "description": "Initial task status" },
    "createdAt": { "type": "string", "required": true, "description": "ISO-8601 creation timestamp" }
  }
}
```
**Compatibility:** BACKWARD | **Topic:** `todo.task.created` | **Consumers:** notification-svc, analytics-svc, search-indexer

### `todo.task.completed` (v1.0.0)

```json
{
  "eventId": "uuid",
  "eventType": "todo.task.completed",
  "eventVersion": "1.0.0",
  "timestamp": "ISO-8601",
  "source": "todo-api",
  "correlationId": "uuid",
  "payload": {
    "taskId": { "type": "string", "required": true },
    "userId": { "type": "string", "required": true },
    "completedAt": { "type": "string", "required": true, "description": "ISO-8601 completion timestamp" },
    "previousStatus": { "type": "string", "required": true, "description": "Status before completion" }
  }
}
```
**Compatibility:** FULL | **Topic:** `todo.task.completed` | **Consumers:** notification-svc, analytics-svc, recurrence-svc

### `todo.task.priority-changed` (v1.0.0)

```json
{
  "eventId": "uuid",
  "eventType": "todo.task.priority-changed",
  "eventVersion": "1.0.0",
  "timestamp": "ISO-8601",
  "source": "todo-api",
  "correlationId": "uuid",
  "payload": {
    "taskId": { "type": "string", "required": true },
    "userId": { "type": "string", "required": true },
    "oldPriority": { "type": "string", "required": false, "default": null, "description": "Previous priority (null if first assignment)" },
    "newPriority": { "type": "string", "required": true, "description": "New priority value: low|medium|high|critical" }
  }
}
```
**Compatibility:** BACKWARD | **Topic:** `todo.task.priority-changed` | **Consumers:** notification-svc, analytics-svc

### `todo.reminder.fired` (v1.0.0)

```json
{
  "eventId": "uuid",
  "eventType": "todo.reminder.fired",
  "eventVersion": "1.0.0",
  "timestamp": "ISO-8601",
  "source": "reminder-svc",
  "correlationId": "uuid",
  "payload": {
    "taskId": { "type": "string", "required": true },
    "userId": { "type": "string", "required": true },
    "reminderId": { "type": "string", "required": true },
    "scheduledAt": { "type": "string", "required": true, "description": "Originally scheduled fire time" },
    "firedAt": { "type": "string", "required": true, "description": "Actual fire time" }
  }
}
```
**Compatibility:** BACKWARD | **Topic:** `todo.reminder.fired` | **Consumers:** notification-svc

---

## Governance Checklist

Run before approving any schema change.

### For All Changes
- [ ] Change classified as Safe / Minor / Breaking
- [ ] `eventVersion` incremented according to classification
- [ ] All envelope fields present and unchanged
- [ ] Field names use camelCase
- [ ] All required fields have types defined
- [ ] All optional fields have explicit default values
- [ ] No PII fields without `pii: true` annotation
- [ ] No sensitive data (passwords, tokens, secrets) in any field
- [ ] Change history updated in schema definition
- [ ] Schema registered in registry before producer deploys

### For Minor Changes
- [ ] New fields are optional with defaults
- [ ] Deprecated fields marked with `deprecatedSince` and `removalVersion`
- [ ] Consumer impact assessment completed (all consumers can handle change)

### For Breaking Changes
- [ ] Migration plan documented with all four phases (Prepare, Dual-Publish, Cutover, Deprecation)
- [ ] Consumer migration tracking table created
- [ ] New topic created if partition key or event type changed
- [ ] Dual-publish implementation reviewed
- [ ] Rollback plan documented (revert to v1 publishing)
- [ ] All consumer teams notified with migration deadline
- [ ] Minimum 7-day rollback window after deprecation

## Common Governance Violations

| Violation | Risk | Prevention |
|-----------|------|------------|
| Adding required field without default to existing schema | All old messages fail deserialization for new consumers | Always make new fields optional with defaults |
| Renaming a field for "consistency" | All consumers reading old name break | Never rename — add new field, deprecate old one |
| Changing `string` to `enum` retroactively | Old messages with non-enum values fail validation | Add enum as new optional field; deprecate old string field |
| Removing a field without deprecation period | Consumers crash on missing field | Mark deprecated first; set removal version ≥ 2 minor releases ahead |
| Publishing without registering schema | No compatibility check runs; breaking change slips through | Registry-first workflow: register → validate → publish |
| Same `eventVersion` for different schemas | Consumer can't distinguish which schema to apply | Always bump version on any schema change, no matter how small |
| PII in event payload unencrypted | GDPR/compliance violation; data exposed to all consumers | Flag PII fields; require field-level encryption or event-carried state transfer |
| Changing partition key silently | Ordering guarantees broken for all consumers | Partition key changes are always a major version bump with new topic |
