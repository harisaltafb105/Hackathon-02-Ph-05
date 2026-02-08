# Data Model: Intermediate & Advanced Todo Features

**Feature**: 006-advanced-todo-features
**Date**: 2026-02-07

## Entity Overview

```
┌──────────────┐         ┌──────────────┐
│    Task      │ 1 ──── *│   Reminder   │
│  (extended)  │         │   (new)      │
└──────────────┘         └──────────────┘
```

## Task (Extended)

Existing `tasks` table with 5 new columns added.

| Field | Type | Nullable | Default | Index | Notes |
|-------|------|----------|---------|-------|-------|
| `id` | UUID | NO | uuid4() | PK | Existing |
| `title` | VARCHAR(500) | NO | — | — | Existing |
| `description` | VARCHAR(5000) | YES | NULL | — | Existing |
| `completed` | BOOLEAN | NO | false | — | Existing |
| `created_at` | TIMESTAMP | NO | utcnow() | — | Existing |
| `updated_at` | TIMESTAMP | NO | utcnow() | — | Existing |
| `user_id` | VARCHAR | NO | — | idx_user_id | Existing |
| **`priority`** | **VARCHAR(10)** | **NO** | **"none"** | **idx_tasks_priority** | **NEW** — enum: none, low, medium, high, urgent |
| **`tags`** | **TEXT[]** | **NO** | **{}** | **idx_tasks_tags (GIN)** | **NEW** — PostgreSQL array |
| **`due_date`** | **DATE** | **YES** | **NULL** | **idx_tasks_due_date** | **NEW** — no time component |
| **`recurrence_rule`** | **VARCHAR(200)** | **YES** | **NULL** | **—** | **NEW** — simplified RRULE string |
| **`recurrence_group_id`** | **UUID** | **YES** | **NULL** | **idx_tasks_recurrence_group** | **NEW** — links recurring instances |

### New Indexes

| Name | Columns | Type | Purpose |
|------|---------|------|---------|
| `idx_tasks_priority` | `priority` | B-tree | Priority filtering/sorting |
| `idx_tasks_tags` | `tags` | GIN | Array containment queries |
| `idx_tasks_due_date` | `due_date` | B-tree | Date filtering/sorting |
| `idx_tasks_recurrence_group` | `recurrence_group_id` | B-tree | Recurring chain lookups |
| `idx_tasks_user_priority` | `user_id, priority` | B-tree (composite) | User-scoped priority queries |
| `idx_tasks_user_due_date` | `user_id, due_date` | B-tree (composite) | User-scoped overdue queries |

### Priority Enum Values

| Value | Ordinal | Display Color |
|-------|---------|---------------|
| `none` | 0 | Gray |
| `low` | 1 | Blue |
| `medium` | 2 | Yellow |
| `high` | 3 | Orange |
| `urgent` | 4 | Red |

### Recurrence Rule Format

Simplified subset of RFC 5545 RRULE:

```
FREQ=DAILY
FREQ=WEEKLY;BYDAY=MO,WE,FR
FREQ=MONTHLY;BYMONTHDAY=15
FREQ=DAILY;UNTIL=2026-06-01
FREQ=WEEKLY;BYDAY=MO;UNTIL=2026-12-31
```

| Component | Required | Values | Example |
|-----------|----------|--------|---------|
| `FREQ` | YES | DAILY, WEEKLY, MONTHLY | `FREQ=WEEKLY` |
| `BYDAY` | NO (WEEKLY default: same weekday) | MO,TU,WE,TH,FR,SA,SU | `BYDAY=MO,WE,FR` |
| `BYMONTHDAY` | NO (MONTHLY default: same day) | 1-31 | `BYMONTHDAY=15` |
| `UNTIL` | NO (infinite if omitted) | YYYY-MM-DD | `UNTIL=2026-06-01` |

### Tag Validation Rules

- Lowercase only (normalized on write)
- Allowed characters: `[a-z0-9_-]`
- Max length per tag: 50 characters
- Max tags per task: 20
- Leading/trailing whitespace stripped
- Invalid characters silently stripped

---

## Reminder (New)

New `reminders` table.

| Field | Type | Nullable | Default | Index | Notes |
|-------|------|----------|---------|-------|-------|
| `id` | UUID | NO | uuid4() | PK | |
| `task_id` | UUID | NO | — | idx_reminders_task_id | FK → tasks.id ON DELETE CASCADE |
| `user_id` | VARCHAR | NO | — | idx_reminders_user_id | User isolation |
| `trigger_at` | TIMESTAMP | NO | — | — | When to fire |
| `status` | VARCHAR(20) | NO | "pending" | — | Enum: pending, triggered, cancelled |
| `created_at` | TIMESTAMP | NO | utcnow() | — | |

### Indexes

| Name | Columns | Type | Purpose |
|------|---------|------|---------|
| `idx_reminders_task_id` | `task_id` | B-tree | Cascade delete lookups |
| `idx_reminders_user_id` | `user_id` | B-tree | User-scoped queries |
| `idx_reminders_trigger_status` | `trigger_at, status` | B-tree (composite) | Find pending reminders to fire |

### Reminder Status Lifecycle

```
 ┌─────────┐     trigger_at arrives     ┌──────────┐
 │ PENDING │ ─────────────────────────→ │ TRIGGERED│
 └─────────┘                            └──────────┘
      │
      │ parent task completed
      ▼
 ┌──────────┐
 │CANCELLED │
 └──────────┘
```

### Cascade Behaviors

| Trigger | Action |
|---------|--------|
| Task deleted | All associated reminders deleted (DB CASCADE) |
| Task completed | All `pending` reminders set to `cancelled` (application code) |
| Recurring task generates new instance | If parent had reminder rule, new `pending` reminder created for new instance |

---

## Migration Strategy

Since the project uses `SQLModel.metadata.create_all()` (not Alembic):

1. **New columns on Task**: All new fields have defaults or are nullable. `create_all()` will add columns. Existing rows will get default values automatically.
2. **New table Reminder**: `create_all()` will create the table.
3. **Indexes**: `create_all()` will create indexes defined in `__table_args__`.
4. **No data migration needed**: Existing tasks will have `priority="none"`, `tags=[]`, `due_date=null`, `recurrence_rule=null`, `recurrence_group_id=null`.

**Risk**: If `create_all()` doesn't add columns to existing tables (it only creates missing tables), manual `ALTER TABLE` may be needed. Mitigation: Test with existing data; if columns not added, use raw SQL migration as documented in quickstart.md.
