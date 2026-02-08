# Implementation Plan: Intermediate & Advanced Todo Features

**Branch**: `006-advanced-todo-features` | **Date**: 2026-02-07 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/006-advanced-todo-features/spec.md`

## Summary

Extend the existing Phase II/III Full-Stack Todo Application with intermediate features (priority, tags, search, filter, sort, pagination) and advanced features (due dates, reminders logic, recurring tasks logic). All changes are additive — extending the existing Task model, API endpoints, MCP tools, and frontend components. No infrastructure changes (Kafka, Dapr, K8s) are introduced. The plan follows a backend-first approach: domain model → validation → API → MCP tools → frontend UI → integration testing.

## Technical Context

**Language/Version**: Python 3.13+ (backend), TypeScript (frontend)
**Primary Dependencies**: FastAPI, SQLModel, SQLAlchemy, Pydantic (backend); Next.js 16+, React, Tailwind CSS (frontend); OpenAI Agents SDK, MCP SDK (chatbot)
**Storage**: Neon Serverless PostgreSQL via SQLModel/SQLAlchemy async
**Testing**: pytest with async fixtures (backend); manual integration (frontend)
**Target Platform**: Web application (local development, future K8s deployment)
**Project Type**: Web (monorepo with `backend/` and `frontend/` directories)
**Performance Goals**: API roundtrip < 300ms, search < 500ms across 1000+ tasks, tag autocomplete < 200ms
**Constraints**: No infrastructure changes, no Kafka/Dapr/K8s code, backward compatible with existing data, strict user isolation on all new endpoints
**Scale/Scope**: 5 new Task fields, 1 new Reminder model, 4 new API endpoints, modifications to 4 existing endpoints, 6 new MCP tool parameters, frontend enhancements to task list/form/card components

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Notes |
|-----------|--------|-------|
| I. Spec-Driven Development | PASS | Spec exists at `specs/006-advanced-todo-features/spec.md` |
| II. Multi-Tenant User Isolation | PASS | All new endpoints/queries include user_id. Reminder model includes user_id. |
| III. JWT Authentication Bridge | PASS | All endpoints use existing `get_current_user` dependency. No auth changes. |
| IV. Monorepo with Clear Boundaries | PASS | Backend changes in `backend/`, frontend in `frontend/`, specs in `specs/`. |
| V. API-First Design | PASS | API contracts defined in spec before implementation. |
| VI. Database Schema Integrity | PASS | Schema extensions via SQLModel. Migration strategy documented. |
| VII. Phase III Additive Extension | PASS | Chatbot logic extended, not replaced. Existing MCP tools preserved. |
| VIII. Architectural Authority | PASS | All mutations flow through FastAPI → Database. MCP tools wrap API logic. |
| IX. Stateless Server Law | PASS | No in-memory state introduced. |
| X. MCP Tool Sovereignty | PASS | Existing tools extended with new parameters. New tools for reminders. |
| XI. Agent Behavior Constraints | PASS | Chatbot confirms actions, handles ambiguity via mapping tables. |
| XII. Data Integrity & Safety | PASS | Cascade deletes, transactional writes, validation. |
| XIII. Final Constitutional Law | PASS | Backend remains authority. Database remains memory. |
| XIV. Infrastructure-Only Phase | N/A | This is a feature phase, not Phase IV infrastructure. |
| XX. Event-Driven First | DEFERRED | Feature logic first. Event emission hooks will be added in a separate event-driven spec. |
| XXII. Feature Event Governance | DEFERRED | Same as XX — feature logic is infrastructure-agnostic per spec scope. |

**Gate Result**: PASS — All applicable principles satisfied. Principles XX and XXII are explicitly deferred per the spec's infrastructure-agnostic scope boundary. Event hooks will be added in a subsequent spec.

## Project Structure

### Documentation (this feature)

```text
specs/006-advanced-todo-features/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/           # Phase 1 output
│   ├── task-api.yaml    # Extended task endpoints
│   ├── reminder-api.yaml # New reminder endpoints
│   └── tags-api.yaml    # New tags endpoint
├── checklists/
│   └── requirements.md  # Quality checklist
└── tasks.md             # Phase 2 output (via /sp.tasks)
```

### Source Code (repository root)

```text
backend/
├── models.py            # MODIFY: Extend Task model, add Reminder model, add Priority enum
├── schemas.py           # MODIFY: Add new request/response schemas
├── routers/
│   ├── tasks.py         # MODIFY: Add query params, pagination, new fields
│   └── reminders.py     # NEW: Reminder CRUD endpoints
├── services/
│   └── recurrence.py    # NEW: Recurring task generation logic
├── chat/
│   └── tools.py         # MODIFY: Extend tool definitions and handlers
└── tests/
    ├── test_priority.py        # NEW
    ├── test_tags.py            # NEW
    ├── test_search_filter.py   # NEW
    ├── test_due_dates.py       # NEW
    ├── test_reminders.py       # NEW
    ├── test_recurring.py       # NEW
    └── test_pagination.py      # NEW

frontend/
├── types/
│   └── task.ts          # MODIFY: Extend Task interface with new fields
├── lib/
│   └── api-client.ts    # MODIFY: Add query params, new endpoints
├── components/
│   ├── task-form.tsx     # MODIFY: Add priority, tags, due date, recurrence fields
│   ├── task-card.tsx     # MODIFY: Display priority, tags, due date, overdue indicator
│   ├── task-list.tsx     # MODIFY: Add search bar, filter controls, sort selector
│   ├── filter-tabs.tsx   # MODIFY: Extend with priority/tag/overdue filters
│   ├── search-bar.tsx    # NEW: Search input component
│   ├── sort-selector.tsx # NEW: Sort field/direction selector
│   ├── priority-badge.tsx # NEW: Priority level indicator
│   ├── tag-input.tsx     # NEW: Tag input with autocomplete
│   ├── date-picker.tsx   # NEW: Due date selector
│   └── edit-task-modal.tsx # MODIFY: Add new fields
└── hooks/
    └── use-task-filters.ts # NEW: Filter/sort/search state management hook
```

**Structure Decision**: Extending existing web application structure. No new top-level directories. Backend services directory added for isolated business logic (recurrence computation). Frontend gains 5 new components and 1 new hook.

## Complexity Tracking

> No constitution violations requiring justification. All changes within existing patterns.

## Implementation Phases

### Phase 1: Backend Domain Model Extension (Steps 1-2)

**Goal**: Extend Task model and add Reminder model with all new fields, enums, and indexes.

**Step 1: Extend Task Model**
- Add `TaskPriority` enum to `backend/models.py` (none, low, medium, high, urgent)
- Add `ReminderStatus` enum to `backend/models.py` (pending, triggered, cancelled)
- Extend `Task` class with new fields:
  - `priority: TaskPriority` (default=none, index)
  - `tags: list[str]` (default=[], PostgreSQL ARRAY with GIN index)
  - `due_date: date | None` (default=None, index)
  - `recurrence_rule: str | None` (default=None)
  - `recurrence_group_id: UUID | None` (default=None, index)
- Add composite indexes: `(user_id, priority)`, `(user_id, due_date)`
- Files: `backend/models.py`
- Acceptance: Existing tasks retain defaults. New fields nullable/defaulted.

**Step 2: Add Reminder Model**
- Create `Reminder` model in `backend/models.py`:
  - `id`, `task_id` (FK cascade), `user_id`, `trigger_at`, `status`, `created_at`
- Add indexes: `(task_id)`, `(user_id)`, `(trigger_at, status)`
- Files: `backend/models.py`
- Acceptance: Model creates table. FK cascade verified.

**Step 3: Update Pydantic Schemas**
- Extend `TaskCreate` with optional: `priority`, `tags`, `due_date`, `recurrence_rule`
- Extend `TaskUpdate` and `TaskPatch` with new fields
- Extend `TaskResponse` with new fields + computed `is_overdue`
- Add `PaginatedTaskResponse` with `tasks`, `total`, `limit`, `offset`
- Add `ReminderCreate`, `ReminderResponse`, `TagListResponse` schemas
- Add tag validation (lowercase, alphanumeric/hyphens/underscores, max 50 chars, max 20 tags)
- Files: `backend/schemas.py`
- Acceptance: Validation rules enforced. Old request payloads still valid (new fields optional).

### Phase 2: Backend Query & Filtering (Steps 4-5)

**Step 4: Extend Task List Endpoint with Search/Filter/Sort/Pagination**
- Modify `GET /{user_id}/tasks` in `backend/routers/tasks.py`:
  - Add query parameters: `q`, `completed`, `priority`, `tag`, `overdue`, `due_before`, `due_after`, `sort_by`, `sort_order`, `limit`, `offset`
  - Build composable SQLAlchemy query with all filters (AND logic)
  - Implement ILIKE search on `title` and `description`
  - Implement priority sorting with ordinal mapping (CASE WHEN)
  - Handle null `due_date` positioning in sort
  - Return `PaginatedTaskResponse` with total count
- Files: `backend/routers/tasks.py`
- Acceptance: All filter/sort combos work. Pagination returns correct total. Backward compatible (no params = all tasks, default sort).

**Step 5: Add Tags Endpoint**
- Add `GET /{user_id}/tags` to `backend/routers/tasks.py`:
  - Query distinct tags across user's tasks using `unnest` + `DISTINCT`
  - Return `TagListResponse`
- Files: `backend/routers/tasks.py`
- Acceptance: Returns deduplicated, sorted tag list for the user.

### Phase 3: Backend Advanced Logic (Steps 6-8)

**Step 6: Update Task Create/Update with New Fields**
- Modify `POST /{user_id}/tasks` to accept and persist new fields
- Modify `PUT/PATCH /{user_id}/tasks/{task_id}` to accept new fields
- Add tag normalization in create/update (lowercase, strip invalid chars)
- For PATCH: support adding/removing individual tags
- Files: `backend/routers/tasks.py`, `backend/schemas.py`
- Acceptance: Tasks created/updated with priority, tags, due_date, recurrence_rule.

**Step 7: Implement Recurring Task Logic**
- Create `backend/services/recurrence.py` with:
  - `parse_recurrence_rule(rule: str) -> RecurrenceConfig` — parse simplified RRULE
  - `compute_next_due_date(current_due: date, rule: str) -> date | None` — calculate next instance date
  - `generate_next_instance(task: Task, session: AsyncSession) -> Task | None` — create next recurring task
- Modify PATCH endpoint: when `completed: true` on a recurring task:
  1. Mark current instance complete
  2. Call `generate_next_instance()` to create next instance
  3. Return both the completed task and the new instance info
- Handle UNTIL clause (no generation if past end date)
- Copy `recurrence_group_id` to new instance
- Files: `backend/services/recurrence.py`, `backend/routers/tasks.py`
- Acceptance: Completing a daily/weekly/monthly task generates correct next instance.

**Step 8: Implement Reminder CRUD**
- Create `backend/routers/reminders.py` with:
  - `GET /{user_id}/tasks/{task_id}/reminders` — list reminders for task
  - `POST /{user_id}/tasks/{task_id}/reminders` — create reminder (absolute or relative-to-due)
  - `DELETE /{user_id}/tasks/{task_id}/reminders/{reminder_id}` — delete reminder
- Validate: `trigger_at` must be in the future, task must belong to user
- For relative reminders: compute `trigger_at` from task's `due_date`
- Add cascade behavior in PATCH/complete: cancel pending reminders when task completed
- Add cascade behavior in DELETE: reminders deleted when task deleted
- Register router in `backend/main.py`
- Files: `backend/routers/reminders.py`, `backend/main.py`, `backend/routers/tasks.py`
- Acceptance: Reminder CRUD works. Cascade on complete/delete verified.

### Phase 4: AI Chatbot Integration (Step 9)

**Step 9: Extend MCP Tool Definitions and Handlers**
- Update `add_task` tool to accept: `priority`, `tags`, `due_date`, `recurrence_rule`
- Update `list_tasks` tool to accept: `q` (search), `priority`, `tag`, `sort_by`, `overdue`
- Update `update_task` tool to accept: `priority`, `tags`, `due_date`
- Add `set_reminder` tool: create reminder for a task
- Update `complete_task` to handle recurring task completion (return new instance info)
- Update tool definitions in `get_tool_definitions()` with new parameters
- Update `TOOL_REGISTRY` with new tool entries
- Files: `backend/chat/tools.py`
- Acceptance: Chatbot can set priority, add tags, search, filter, set due dates, create reminders, handle recurring tasks via natural language.

### Phase 5: Frontend Extensions (Steps 10-14)

**Step 10: Extend TypeScript Types and API Client**
- Extend `Task` interface in `frontend/types/task.ts`:
  - Add: `priority`, `tags`, `dueDate`, `isOverdue`, `recurrenceRule`, `recurrenceGroupId`
- Extend `TaskFormData` with new optional fields
- Add new types: `PaginatedTaskResponse`, `ReminderResponse`, `TaskFilters`
- Update `api-client.ts`:
  - Modify `getTasks()` to accept filter/sort/pagination query params
  - Add `getTags()` method
  - Add `createReminder()`, `deleteReminder()`, `getReminders()` methods
  - Update `createTask()` and `updateTask()` to send new fields
- Files: `frontend/types/task.ts`, `frontend/lib/api-client.ts`
- Acceptance: TypeScript types match backend response shapes. API client methods cover all new endpoints.

**Step 11: Create New UI Components**
- `frontend/components/priority-badge.tsx` — Color-coded priority indicator (urgent=red, high=orange, medium=yellow, low=blue, none=gray)
- `frontend/components/tag-input.tsx` — Tag input with autocomplete from `GET /tags` endpoint
- `frontend/components/search-bar.tsx` — Search input with debounce
- `frontend/components/sort-selector.tsx` — Dropdown for sort field + direction toggle
- `frontend/components/date-picker.tsx` — Due date input (native HTML date or lightweight picker)
- `frontend/hooks/use-task-filters.ts` — Hook managing search, filter, sort, pagination state; syncs with URL query params
- Files: 5 new component files, 1 new hook file
- Acceptance: Each component renders independently. Hook manages state correctly.

**Step 12: Extend Task Form and Card**
- Modify `frontend/components/task-form.tsx`:
  - Add priority selector dropdown
  - Add tag input component
  - Add due date picker
  - Add recurrence rule selector (daily/weekly/monthly + optional end date)
- Modify `frontend/components/task-card.tsx`:
  - Display priority badge
  - Display tags as chips
  - Display due date with overdue styling (red for overdue, orange for due soon)
  - Display recurrence indicator icon
- Modify `frontend/components/edit-task-modal.tsx` and `frontend/components/add-task-modal.tsx`:
  - Include new form fields
- Files: `task-form.tsx`, `task-card.tsx`, `edit-task-modal.tsx`, `add-task-modal.tsx`
- Acceptance: New fields visible in create/edit forms. Task cards show all metadata.

**Step 13: Extend Task List with Controls**
- Modify `frontend/components/task-list.tsx`:
  - Add search bar at top
  - Add filter controls (priority, tag, overdue, completion status)
  - Add sort selector
  - Implement pagination (load more or page navigation)
  - Connect to `use-task-filters` hook
- Modify `frontend/components/filter-tabs.tsx`:
  - Extend beyond all/active/completed to include priority/tag/overdue filters
- Files: `task-list.tsx`, `filter-tabs.tsx`
- Acceptance: Search/filter/sort/pagination works end-to-end from UI to API.

**Step 14: Update Dashboard Page**
- Modify `frontend/app/(protected)/dashboard/page.tsx` to use the enhanced task list
- Ensure context providers supply filter state
- Files: `dashboard/page.tsx`
- Acceptance: Dashboard displays enhanced task list with all controls.

### Phase 6: Integration & Regression (Steps 15-16)

**Step 15: Integration Validation**
- Test full flow: create task with priority/tags/due date → view in list → filter/sort → search → update → complete recurring → verify next instance
- Test AI chatbot: "Add high priority task 'review report' tagged work due March 15th" → verify task created with all fields
- Test reminder flow: create reminder → verify record → complete task → verify reminder cancelled
- Test pagination: create 60+ tasks → verify pagination returns correct pages and total
- Files: `backend/tests/test_*.py`
- Acceptance: All 50 FRs verified. All 13 success criteria met.

**Step 16: Regression Safety**
- Verify existing CRUD still works (no regressions from schema changes)
- Verify chatbot conversation persistence still works
- Verify old tasks without new fields display correctly (defaults applied)
- Verify user isolation on all new endpoints
- Files: Existing test suite
- Acceptance: All existing tests pass. No breaking changes to Phase II/III.

## Risk Analysis

1. **Schema migration on existing data**: New fields have defaults (priority=none, tags=[], due_date=null, etc.). `SQLModel.metadata.create_all()` will add columns. Risk: existing rows need defaults. Mitigation: All new fields are nullable or have defaults.

2. **GET tasks response format change**: Changing from `List[TaskResponse]` to `PaginatedTaskResponse` is a breaking change for the frontend. Mitigation: Update frontend API client simultaneously. AI chatbot `list_tasks` tool already uses its own response format.

3. **Recurring task infinite loop**: If completion logic has a bug, it could generate unlimited tasks. Mitigation: `generate_next_instance()` only runs once per completion call, is transactional, and validates UNTIL clause.

## Follow-ups

- Event emission hooks for Kafka integration (separate spec, per Phase V constitution)
- Alembic migration scripts for production deployment (currently using `create_all()`)
- Frontend tests with React Testing Library
