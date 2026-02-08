# Feature Specification: Intermediate & Advanced Todo Features

**Feature Branch**: `006-advanced-todo-features`
**Created**: 2026-02-07
**Status**: Draft
**Input**: User description: "Generate a precise, implementation-ready specification for completing ONLY the Intermediate and Advanced feature set of an already working Full-Stack Todo Application with an AI Chatbot. This specification is intentionally feature-scoped and infrastructure-agnostic — no Kafka, Dapr, K8s, cloud, CI/CD, or monitoring."

## Scope & Boundaries

### In Scope
- **Intermediate**: Priority levels, tags/labels, search, filtering, sorting
- **Advanced**: Due dates, reminders (application logic only), recurring tasks (recurrence logic only)
- Database schema extensions to existing Task model
- Backend API endpoint additions and modifications
- Frontend UI enhancements for new features
- AI Chatbot natural language support for new features

### Explicitly Out of Scope
- Kafka event publishing/consuming (covered by separate event-driven spec)
- Dapr component configuration (covered by dapr-integration agent)
- Kubernetes deployment changes (covered by Phase IV/V deployment specs)
- CI/CD pipeline changes (covered by cicd-observability agent)
- Monitoring and observability instrumentation
- Cloud deployment configurations
- Notification delivery mechanisms (email, SMS, push) — only the reminder *scheduling logic* is in scope
- External calendar integrations

### Baseline Assumptions
- Existing Task model: `id` (UUID), `title` (str), `description` (str|null), `completed` (bool), `created_at` (datetime), `updated_at` (datetime), `user_id` (str)
- Existing CRUD endpoints: GET/POST `/api/{user_id}/tasks`, GET/PUT/PATCH/DELETE `/api/{user_id}/tasks/{task_id}`
- Existing AI Chatbot with natural language task CRUD via MCP tools
- Authentication via Better Auth JWT (unchanged)
- FastAPI backend with SQLModel ORM, Neon PostgreSQL
- Next.js frontend with existing task list and chat interfaces

---

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Task Priority Management (Priority: P1)

As a user, I want to assign priority levels to my tasks so that I can focus on the most important items first.

**Why this priority**: Priority is the most fundamental organizational feature. It transforms a flat task list into a structured work queue, providing immediate value for task triage.

**Independent Test**: Can be fully tested by creating a task with a priority level, viewing it in the task list sorted by priority, and changing the priority. Delivers immediate organizational value.

**Acceptance Scenarios**:

1. **Given** I am creating a new task, **When** I set the priority to "high", **Then** the task is created with priority "high" and displays a visual priority indicator
2. **Given** I have an existing task, **When** I update its priority from "medium" to "urgent", **Then** the priority changes and `updated_at` is refreshed
3. **Given** I have tasks with mixed priorities, **When** I view my task list sorted by priority, **Then** tasks appear in order: urgent > high > medium > low > none
4. **Given** I am creating a task without specifying priority, **When** the task is created, **Then** the priority defaults to "none"
5. **Given** I am in the AI chat, **When** I say "Add a high priority task to review the report", **Then** the chatbot creates a task with priority "high"
6. **Given** I am in the AI chat, **When** I say "Make my grocery task urgent", **Then** the chatbot updates the task's priority to "urgent"

---

### User Story 2 - Task Tagging (Priority: P1)

As a user, I want to add tags/labels to my tasks so that I can categorize and group related items across my list.

**Why this priority**: Tags enable cross-cutting categorization (e.g., "work", "personal", "errands") that priority alone cannot provide. Combined with filtering, tags become the primary organizational tool.

**Independent Test**: Can be fully tested by creating a task with tags, viewing tags on the task, and filtering by tag. Delivers categorization value independently.

**Acceptance Scenarios**:

1. **Given** I am creating a new task, **When** I add tags "work" and "urgent-review", **Then** the task is created with both tags displayed
2. **Given** I have an existing task, **When** I add a new tag "meeting", **Then** the tag is appended to the task's existing tags
3. **Given** I have an existing task with tag "work", **When** I remove the "work" tag, **Then** only remaining tags are displayed
4. **Given** I have multiple tasks with various tags, **When** I filter by tag "work", **Then** only tasks tagged "work" are shown
5. **Given** I type a tag name, **When** it matches existing tags, **Then** the system suggests auto-complete options from my previously used tags
6. **Given** I am in the AI chat, **When** I say "Add a task 'prepare slides' tagged with work and presentation", **Then** the chatbot creates the task with both tags
7. **Given** tags contain mixed case input, **When** saved, **Then** tags are normalized to lowercase (e.g., "Work" → "work")

---

### User Story 3 - Search Tasks (Priority: P2)

As a user, I want to search across my tasks by keyword so that I can quickly find specific items in a large task list.

**Why this priority**: Search becomes essential as the task list grows. It provides rapid access to specific tasks without manual scanning.

**Independent Test**: Can be fully tested by creating several tasks and searching for a keyword that matches one or more. Delivers discovery value independently.

**Acceptance Scenarios**:

1. **Given** I have tasks titled "Buy groceries", "Grocery list review", and "Send email", **When** I search for "grocery", **Then** the first two tasks are returned (case-insensitive match on title and description)
2. **Given** I search for a term that matches no tasks, **When** results load, **Then** the system displays "No tasks found" with the search term
3. **Given** I am in the AI chat, **When** I say "Find my tasks about groceries", **Then** the chatbot searches and returns matching tasks
4. **Given** I search while a filter is active, **When** results return, **Then** the search is applied within the active filter scope (AND logic)
5. **Given** I clear the search input, **When** the list refreshes, **Then** all tasks (respecting active filters) are shown again

---

### User Story 4 - Filter Tasks (Priority: P2)

As a user, I want to filter my task list by status, priority, tags, and due date so that I can focus on relevant subsets.

**Why this priority**: Filtering works alongside search and sort to provide a complete task management UX. Users with many tasks need this to reduce cognitive load.

**Independent Test**: Can be fully tested by creating tasks with different attributes and applying filters. Delivers focus value independently.

**Acceptance Scenarios**:

1. **Given** I have completed and incomplete tasks, **When** I filter by "incomplete only", **Then** only tasks with `completed: false` are shown
2. **Given** I have tasks with different priorities, **When** I filter by "high" priority, **Then** only tasks with priority "high" are shown
3. **Given** I have tasks with various tags, **When** I filter by tag "work", **Then** only tasks tagged "work" are shown
4. **Given** I apply multiple filters (priority = "high" AND tag = "work"), **When** results load, **Then** only tasks matching ALL active filters are shown (AND logic)
5. **Given** I have tasks with due dates, **When** I filter by "overdue", **Then** only tasks with due_date < today and completed = false are shown
6. **Given** I am in the AI chat, **When** I say "Show me my high priority work tasks", **Then** the chatbot filters and returns matching tasks
7. **Given** I clear all filters, **When** the list refreshes, **Then** all tasks are shown

---

### User Story 5 - Sort Tasks (Priority: P2)

As a user, I want to sort my task list by various criteria so that I can view tasks in the most useful order.

**Why this priority**: Sorting complements filtering and provides flexibility in how users consume their task list.

**Independent Test**: Can be fully tested by creating tasks and changing the sort order. Delivers ordering value independently.

**Acceptance Scenarios**:

1. **Given** I have multiple tasks, **When** I sort by "priority (highest first)", **Then** tasks are ordered urgent > high > medium > low > none
2. **Given** I have tasks with due dates, **When** I sort by "due date (earliest first)", **Then** tasks with the nearest due date appear first, and tasks without due dates appear last
3. **Given** I have tasks, **When** I sort by "created date (newest first)", **Then** most recently created tasks appear first
4. **Given** I have tasks, **When** I sort by "title (A-Z)", **Then** tasks are alphabetically sorted by title
5. **Given** I am in the AI chat, **When** I say "Show my tasks sorted by due date", **Then** the chatbot returns tasks sorted by due date
6. **Given** I apply a sort and a filter simultaneously, **When** results load, **Then** the filter is applied first and the sort is applied to the filtered result

---

### User Story 6 - Due Dates (Priority: P3)

As a user, I want to set due dates on tasks so that I can track deadlines and identify overdue items.

**Why this priority**: Due dates add temporal awareness to task management, enabling deadline tracking and overdue detection.

**Independent Test**: Can be fully tested by creating a task with a due date, viewing the date in the UI, and observing overdue styling when the date passes.

**Acceptance Scenarios**:

1. **Given** I am creating a task, **When** I set a due date of "2026-03-15", **Then** the task is created with the due date displayed
2. **Given** I have a task with a due date in the past and not completed, **When** I view the task list, **Then** the task is visually marked as overdue (e.g., red text/icon)
3. **Given** I have a task with a due date tomorrow, **When** I view the task list, **Then** the task shows a "due soon" indicator
4. **Given** I have a completed task with a past due date, **When** I view the task, **Then** it is NOT marked as overdue (completed tasks are not overdue)
5. **Given** I am in the AI chat, **When** I say "Add task 'submit report' due March 15th", **Then** the chatbot creates the task with due_date = 2026-03-15
6. **Given** I have a task, **When** I remove its due date, **Then** the task no longer shows any date or overdue indicators
7. **Given** I am in the AI chat, **When** I say "What tasks are overdue?", **Then** the chatbot returns only incomplete tasks with due_date < today

---

### User Story 7 - Reminders (Priority: P3)

As a user, I want to set reminders on tasks so that I am notified before a deadline approaches.

**Why this priority**: Reminders add proactive awareness. This spec covers only the reminder scheduling/data model — the actual notification delivery (email, push, in-app) is out of scope and will be handled by the notification infrastructure layer.

**Independent Test**: Can be fully tested by setting a reminder on a task and verifying the reminder record is created with the correct trigger time. Actual delivery is NOT tested here.

**Acceptance Scenarios**:

1. **Given** I have a task with due date "2026-03-15", **When** I set a reminder for "1 day before", **Then** a reminder record is created with trigger_at = 2026-03-14T09:00:00Z (default 9 AM UTC)
2. **Given** I have a task, **When** I set a custom reminder for "2026-03-10 14:00", **Then** a reminder record is created with trigger_at = 2026-03-10T14:00:00Z
3. **Given** I have a task with a reminder, **When** I delete the task, **Then** the associated reminder record is also deleted (cascade)
4. **Given** I have a task with a reminder, **When** I mark the task as complete, **Then** the reminder status changes to "cancelled"
5. **Given** I set a reminder in the past, **When** I save, **Then** the system rejects it with a validation error "Reminder time must be in the future"
6. **Given** I am in the AI chat, **When** I say "Remind me about the report task 2 days before it's due", **Then** the chatbot creates a reminder with trigger_at = due_date - 2 days
7. **Given** a reminder's trigger_at time arrives, **When** the system checks, **Then** the reminder status changes from "pending" to "triggered" (delivery is handled by a separate system)

---

### User Story 8 - Recurring Tasks (Priority: P4)

As a user, I want to create recurring tasks that automatically regenerate after completion so that I don't need to manually re-create repetitive items.

**Why this priority**: Recurring tasks are a power-user feature. This spec covers only the recurrence logic and data model — scheduling infrastructure (cron, Dapr Jobs API) is out of scope.

**Independent Test**: Can be fully tested by creating a recurring task, completing it, and verifying a new instance is generated per the recurrence rule.

**Acceptance Scenarios**:

1. **Given** I create a task with recurrence "every day", **When** I complete the task, **Then** a new task instance is created with the same title/description/priority/tags and due_date = next day
2. **Given** I create a task with recurrence "every week on Monday", **When** I complete the task, **Then** a new task is created with due_date = next Monday
3. **Given** I create a task with recurrence "every month on the 15th", **When** I complete the task, **Then** a new task is created with due_date = 15th of next month
4. **Given** I create a recurring task with an end date of "2026-06-01", **When** I complete an instance after 2026-06-01, **Then** no new instance is generated
5. **Given** I delete a recurring task, **When** prompted, **Then** I can choose to delete "this instance only" or "this and all future instances"
6. **Given** I am in the AI chat, **When** I say "Create a daily task to check email", **Then** the chatbot creates a task with recurrence_rule = "FREQ=DAILY"
7. **Given** I am in the AI chat, **When** I say "Stop the recurring email check task", **Then** the chatbot sets recurrence_rule to null, preventing future instances
8. **Given** a recurring task has no end date, **When** I keep completing instances, **Then** new instances continue to be generated indefinitely

---

### Edge Cases

- **What happens when a tag contains special characters (e.g., "#home", "work/life")?** Tags are normalized: lowercased, stripped of leading/trailing whitespace. Only alphanumeric characters, hyphens, and underscores are allowed. Invalid characters are stripped.
- **What happens when a user has 1000+ tasks and searches?** Search uses database-level `ILIKE` or `tsvector` for performance. Pagination is applied (default 50, max 100 per page).
- **What happens when a recurring task is edited after creation?** Edits apply to the current instance only. Future generated instances inherit the *original* recurrence template, not the edited instance.
- **What happens when a due date is set in the past?** The system allows it (useful for backdating) but immediately marks the task as overdue if incomplete.
- **What happens when multiple filters conflict (e.g., filter by "completed" AND "overdue")?** Overdue only applies to incomplete tasks, so this combination returns an empty result. The system applies all filters with AND logic without special conflict resolution.
- **What happens when a reminder is set on a task without a due date?** Allowed — the user specifies an absolute trigger_at time. Relative reminders ("1 day before due") require a due date and are rejected without one.
- **What happens when a recurring task has reminders?** Each new generated instance inherits the reminder rule (e.g., "1 day before due") and a new pending reminder is created relative to the new due date.
- **What happens when priority is changed via the AI chatbot with ambiguous language (e.g., "make it important")?** The chatbot maps "important" to "high". An explicit mapping table is used: urgent = "urgent/critical/ASAP", high = "important/high", medium = "medium/normal", low = "low/minor".

---

## Requirements *(mandatory)*

### Functional Requirements

**Priority Management**
- **FR-001**: System MUST support five priority levels: `none`, `low`, `medium`, `high`, `urgent` stored as an enum
- **FR-002**: System MUST default task priority to `none` when not specified
- **FR-003**: System MUST allow priority to be set at creation and updated at any time
- **FR-004**: System MUST expose priority in all task response payloads

**Tag Management**
- **FR-010**: System MUST support zero or more tags per task, stored as an array of strings
- **FR-011**: System MUST normalize tags to lowercase with only alphanumeric characters, hyphens, and underscores (max 50 chars per tag, max 20 tags per task)
- **FR-012**: System MUST validate tag format on creation and update, rejecting invalid tags with 422
- **FR-013**: System MUST provide a GET endpoint to retrieve the authenticated user's distinct tags for autocomplete: `GET /api/{user_id}/tags`
- **FR-014**: System MUST support adding and removing individual tags via PATCH without replacing the entire array

**Search**
- **FR-020**: System MUST support keyword search across task `title` and `description` fields via query parameter `?q=<term>`
- **FR-021**: System MUST perform case-insensitive search
- **FR-022**: System MUST return search results with the same response schema as the task list endpoint

**Filtering**
- **FR-030**: System MUST support filtering by `completed` status via query parameter `?completed=true|false`
- **FR-031**: System MUST support filtering by `priority` via query parameter `?priority=high` (comma-separated for multiple: `?priority=high,urgent`)
- **FR-032**: System MUST support filtering by `tag` via query parameter `?tag=work` (comma-separated for multiple: `?tag=work,meeting`)
- **FR-033**: System MUST support filtering by `overdue` via query parameter `?overdue=true` (incomplete tasks with due_date < current date)
- **FR-034**: System MUST support filtering by due date range via `?due_before=YYYY-MM-DD&due_after=YYYY-MM-DD`
- **FR-035**: System MUST apply all filters with AND logic when multiple are specified

**Sorting**
- **FR-040**: System MUST support sorting via query parameter `?sort_by=<field>&sort_order=asc|desc`
- **FR-041**: System MUST support sort fields: `priority`, `due_date`, `created_at`, `updated_at`, `title`
- **FR-042**: System MUST default sort to `created_at` descending when no sort is specified
- **FR-043**: For `priority` sort, system MUST use ordinal values: urgent=4, high=3, medium=2, low=1, none=0
- **FR-044**: For `due_date` sort, tasks without due dates MUST appear last when sorting ascending, first when sorting descending

**Pagination**
- **FR-050**: System MUST support pagination via `?limit=N&offset=N` query parameters
- **FR-051**: System MUST default to limit=50, offset=0
- **FR-052**: System MUST cap maximum limit at 100
- **FR-053**: System MUST return total count in response for pagination UI: `{ "tasks": [...], "total": N, "limit": N, "offset": N }`

**Due Dates**
- **FR-060**: System MUST support an optional `due_date` field on tasks as a date (YYYY-MM-DD format, no time component)
- **FR-061**: System MUST allow due_date to be set at creation and updated/removed at any time
- **FR-062**: System MUST expose `is_overdue` as a computed boolean in task responses (true when due_date < today AND completed = false)

**Reminders**
- **FR-070**: System MUST support creating reminder records associated with a task
- **FR-071**: Each reminder MUST have: `id` (UUID), `task_id` (FK), `user_id`, `trigger_at` (datetime), `status` (pending|triggered|cancelled), `created_at`
- **FR-072**: System MUST validate that `trigger_at` is in the future at creation time
- **FR-073**: System MUST cascade-delete reminders when the parent task is deleted
- **FR-074**: System MUST set reminder status to "cancelled" when the parent task is marked complete
- **FR-075**: System MUST support relative reminders from due date (e.g., "1 day before") — computed to absolute trigger_at at creation time
- **FR-076**: System MUST provide CRUD endpoints for reminders: `GET/POST /api/{user_id}/tasks/{task_id}/reminders`, `DELETE /api/{user_id}/tasks/{task_id}/reminders/{reminder_id}`

**Recurring Tasks**
- **FR-080**: System MUST support a recurrence rule on tasks using a simplified subset of RFC 5545 RRULE: `FREQ=DAILY|WEEKLY|MONTHLY`, optional `BYDAY=MO,TU,...`, optional `BYMONTHDAY=1-31`, optional `UNTIL=YYYY-MM-DD`
- **FR-081**: System MUST store recurrence as `recurrence_rule` (string|null) on the Task model
- **FR-082**: When a recurring task is completed, system MUST automatically generate the next instance with: same title, description, priority, tags; new UUID; new due_date computed from recurrence_rule; `completed = false`; recurrence_rule copied forward
- **FR-083**: System MUST NOT generate a new instance if `recurrence_rule` includes UNTIL and the next due_date exceeds UNTIL
- **FR-084**: System MUST support stopping recurrence by setting recurrence_rule to null (via PATCH)
- **FR-085**: System MUST link recurring task instances via a `recurrence_group_id` (UUID) shared across all instances in the chain

**AI Chatbot Integration**
- **FR-090**: Chatbot MUST understand natural language commands for setting/changing priority (e.g., "make it high priority", "this is urgent")
- **FR-091**: Chatbot MUST understand natural language commands for adding/removing tags (e.g., "tag it as work", "remove the meeting tag")
- **FR-092**: Chatbot MUST understand natural language commands for searching (e.g., "find tasks about groceries")
- **FR-093**: Chatbot MUST understand natural language commands for filtering (e.g., "show my overdue tasks", "show high priority work tasks")
- **FR-094**: Chatbot MUST understand natural language commands for due dates (e.g., "set due date to March 15th", "what's due this week")
- **FR-095**: Chatbot MUST understand natural language commands for reminders (e.g., "remind me 1 day before", "set a reminder for March 10th")
- **FR-096**: Chatbot MUST understand natural language commands for recurring tasks (e.g., "make it a daily task", "repeat every Monday")

### Key Entities

- **Task** (extended): Existing entity with new fields:
  - `priority`: Enum (none, low, medium, high, urgent) — default "none"
  - `tags`: Array of strings — default empty array
  - `due_date`: Date (nullable) — no time component
  - `recurrence_rule`: String (nullable) — simplified RRULE format
  - `recurrence_group_id`: UUID (nullable) — links instances of same recurring task

- **Reminder**: New entity representing a scheduled reminder:
  - `id`: UUID (primary key)
  - `task_id`: UUID (FK to tasks.id, cascade delete)
  - `user_id`: String (for user isolation)
  - `trigger_at`: DateTime (when the reminder should fire)
  - `status`: Enum (pending, triggered, cancelled)
  - `created_at`: DateTime

- **Priority Enum**: `none` (0), `low` (1), `medium` (2), `high` (3), `urgent` (4) — ordinal values for sorting

---

## API Endpoint Changes

### Modified Endpoints

**GET /api/{user_id}/tasks** — Add query parameters:
- `?q=<search_term>` — keyword search
- `?completed=true|false` — status filter
- `?priority=high,urgent` — priority filter (comma-separated)
- `?tag=work,meeting` — tag filter (comma-separated)
- `?overdue=true` — overdue filter
- `?due_before=YYYY-MM-DD&due_after=YYYY-MM-DD` — date range filter
- `?sort_by=priority|due_date|created_at|updated_at|title` — sort field
- `?sort_order=asc|desc` — sort direction (default: desc)
- `?limit=N&offset=N` — pagination

Response changes to paginated format:
```json
{
  "tasks": [{ "...task with new fields and is_overdue..." }],
  "total": 150,
  "limit": 50,
  "offset": 0
}
```

**POST /api/{user_id}/tasks** — Accept new optional fields:
- `priority` (string, default "none")
- `tags` (array of strings, default [])
- `due_date` (string YYYY-MM-DD, default null)
- `recurrence_rule` (string, default null)

**PUT/PATCH /api/{user_id}/tasks/{task_id}** — Accept new fields in update payloads

**PATCH /api/{user_id}/tasks/{task_id}** — Special behavior:
- `completed: true` on a recurring task triggers next instance generation
- `completed: true` cancels pending reminders for this task

### New Endpoints

**GET /api/{user_id}/tags** — Returns distinct tags for the user
```json
{ "tags": ["work", "personal", "meeting", "errands"] }
```

**GET /api/{user_id}/tasks/{task_id}/reminders** — List reminders for a task

**POST /api/{user_id}/tasks/{task_id}/reminders** — Create a reminder
```json
{ "trigger_at": "2026-03-14T09:00:00Z" }
```
OR relative:
```json
{ "relative_to_due": "-1d" }
```

**DELETE /api/{user_id}/tasks/{task_id}/reminders/{reminder_id}** — Delete a reminder

---

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Users can create tasks with priority, tags, and due date in a single operation (API roundtrip < 300ms)
- **SC-002**: Search returns results for keyword queries across 1000+ tasks in < 500ms
- **SC-003**: Filtered + sorted task list renders correctly for all valid filter/sort combinations
- **SC-004**: All 5 priority levels sort correctly in both ascending and descending order
- **SC-005**: Tag autocomplete returns suggestions within 200ms
- **SC-006**: Overdue tasks are correctly identified (is_overdue = true when due_date < today AND completed = false)
- **SC-007**: Completing a recurring task generates a new instance with correct next due date within the same API response
- **SC-008**: Reminder records are created with correct trigger_at times (both absolute and relative-to-due)
- **SC-009**: Cascade behaviors work correctly: deleting a task deletes its reminders; completing a task cancels its reminders
- **SC-010**: AI chatbot correctly interprets and executes priority, tag, search, filter, due date, reminder, and recurrence commands with > 85% accuracy on unambiguous inputs
- **SC-011**: All new features maintain strict user isolation — users cannot access other users' tasks, tags, or reminders (0% cross-user data leakage)
- **SC-012**: Pagination correctly reports total count and respects limit/offset bounds
- **SC-013**: Existing Phase II/III functionality (basic CRUD, chatbot conversation persistence) is unaffected by schema migration

### Database Index Requirements

- Index on `tasks.priority` for priority-based filtering and sorting
- Index on `tasks.due_date` for date-based filtering and sorting
- Index on `tasks.tags` using GIN index for array containment queries
- Index on `tasks.recurrence_group_id` for recurring task chain lookups
- Index on `reminders.task_id` for cascade operations
- Index on `reminders.user_id` for user-scoped queries
- Index on `reminders.trigger_at, reminders.status` for reminder scheduling queries (find pending reminders due to fire)
- Composite index on `tasks.user_id, tasks.due_date` for user-scoped overdue queries
- Composite index on `tasks.user_id, tasks.priority` for user-scoped priority queries
