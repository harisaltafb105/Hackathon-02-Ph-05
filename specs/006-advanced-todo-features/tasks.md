# Tasks: Intermediate & Advanced Todo Features

**Input**: Design documents from `/specs/006-advanced-todo-features/`
**Prerequisites**: plan.md (required), spec.md (required), research.md, data-model.md, contracts/

**Tests**: Test tasks included per spec requirement (50 FRs, 13 success criteria).

**Organization**: Tasks grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2)
- Include exact file paths in descriptions

---

## Phase 1: Setup (Shared Domain Model Extension)

**Purpose**: Extend the existing Task model and add new models/schemas that ALL user stories depend on. No new files yet — only extending `backend/models.py` and `backend/schemas.py`.

- [x] T001 [SETUP] Add `TaskPriority` enum (none/low/medium/high/urgent) and `ReminderStatus` enum (pending/triggered/cancelled) to `backend/models.py`
- [x] T002 [SETUP] Extend `Task` model with 5 new fields: `priority` (VARCHAR default "none"), `tags` (ARRAY(String) default []), `due_date` (DATE nullable), `recurrence_rule` (VARCHAR(200) nullable), `recurrence_group_id` (UUID nullable) in `backend/models.py`
- [x] T003 [SETUP] Add indexes to `Task` model `__table_args__`: `idx_tasks_priority`, `idx_tasks_tags` (GIN), `idx_tasks_due_date`, `idx_tasks_recurrence_group`, `idx_tasks_user_priority` (composite), `idx_tasks_user_due_date` (composite) in `backend/models.py`
- [x] T004 [SETUP] Add `Reminder` model with fields: `id` (UUID PK), `task_id` (UUID FK cascade), `user_id` (VARCHAR), `trigger_at` (TIMESTAMP), `status` (VARCHAR default "pending"), `created_at` (TIMESTAMP) with indexes `idx_reminders_task_id`, `idx_reminders_user_id`, `idx_reminders_trigger_status` (composite) in `backend/models.py`
- [x] T005 [SETUP] Extend `TaskCreate` schema with optional fields: `priority` (default "none"), `tags` (default []), `due_date` (nullable), `recurrence_rule` (nullable) in `backend/schemas.py`
- [x] T006 [SETUP] Extend `TaskUpdate` schema with new fields: `priority`, `tags`, `due_date`, `recurrence_rule` in `backend/schemas.py`
- [x] T007 [SETUP] Extend `TaskPatch` schema with optional new fields: `priority`, `tags`, `due_date`, `recurrence_rule` in `backend/schemas.py`
- [x] T008 [SETUP] Extend `TaskResponse` schema with new fields: `priority`, `tags`, `due_date`, `is_overdue` (computed), `recurrence_rule`, `recurrence_group_id` in `backend/schemas.py`
- [x] T009 [SETUP] Add `PaginatedTaskResponse` schema with `tasks: list[TaskResponse]`, `total: int`, `limit: int`, `offset: int` in `backend/schemas.py`
- [x] T010 [SETUP] Add `ReminderCreate` schema (trigger_at OR relative_to_due), `ReminderResponse` schema, `TagListResponse` schema in `backend/schemas.py`
- [x] T011 [SETUP] Add tag validation logic: lowercase normalization, regex `[a-z0-9_-]`, max 50 chars per tag, max 20 tags per task in `backend/schemas.py`
- [x] T012 [SETUP] Add `is_overdue` computed field via `@model_validator(mode="after")` on `TaskResponse`: true when `due_date < today AND completed = false` in `backend/schemas.py`

**Checkpoint**: Models and schemas ready. Database schema will auto-extend on next startup. All user story implementations can now begin.

---

## Phase 2: Foundational (Pagination Breaking Change)

**Purpose**: Change GET tasks response format from `List[TaskResponse]` to `PaginatedTaskResponse`. This is a breaking change that MUST be done before any filter/sort/search work.

**CRITICAL**: This phase changes the task list API contract. Frontend must be updated simultaneously.

- [x] T013 [FOUND] Modify `list_tasks` endpoint in `backend/routers/tasks.py` to return `PaginatedTaskResponse` with `limit` (default 50, max 100) and `offset` (default 0) query parameters, including `total` count via `SELECT COUNT(*)` before pagination
- [x] T014 [FOUND] Update `frontend/types/task.ts`: add `PaginatedTaskResponse` type, extend `Task` interface with `priority`, `tags`, `dueDate`, `isOverdue`, `recurrenceRule`, `recurrenceGroupId`
- [x] T015 [FOUND] Update `frontend/lib/api-client.ts`: modify `getTasks()` to accept filter/sort/pagination params and parse `PaginatedTaskResponse` wrapper (extract `.tasks` array)
- [x] T016 [FOUND] Update frontend components consuming task list data to handle the new paginated response shape (task-list.tsx and any context/state that stores task arrays)

**Checkpoint**: Pagination contract live. Frontend and backend in sync. Old task list behavior preserved (default params = all tasks, page 1).

---

## Phase 3: User Story 1 - Task Priority Management (Priority: P1)

**Goal**: Users can assign, update, and sort by priority levels (none/low/medium/high/urgent)

**Independent Test**: Create a task with priority "high", sort task list by priority descending, verify urgent > high > medium > low > none ordering.

**FRs**: FR-001, FR-002, FR-003, FR-004

### Backend

- [x] T017 [US1] Modify `POST /{user_id}/tasks` in `backend/routers/tasks.py` to accept and persist `priority` field (default "none")
- [x] T018 [US1] Modify `PUT/PATCH /{user_id}/tasks/{task_id}` in `backend/routers/tasks.py` to accept and persist `priority` updates
- [x] T019 [US1] Implement priority sorting via CASE WHEN ordinal mapping (urgent=4, high=3, medium=2, low=1, none=0) in `backend/routers/tasks.py` for `?sort_by=priority&sort_order=asc|desc`

### Frontend

- [x] T020 [P] [US1] Create `frontend/components/priority-badge.tsx`: color-coded priority indicator (urgent=red, high=orange, medium=yellow, low=blue, none=gray)
- [x] T021 [US1] Modify `frontend/components/task-form.tsx` (or add-task-modal.tsx): add priority selector dropdown with 5 levels
- [x] T022 [US1] Modify `frontend/components/task-card.tsx`: display `PriorityBadge` component on each task card
- [x] T023 [US1] Modify `frontend/components/edit-task-modal.tsx`: add priority selector to edit form

### AI Chatbot

- [x] T024 [US1] Update `add_task` tool definition in `backend/chat/tools.py` to accept optional `priority` parameter
- [x] T025 [US1] Update `update_task` tool definition in `backend/chat/tools.py` to accept optional `priority` parameter

**Checkpoint**: Priority CRUD works end-to-end. Tasks can be created/updated with priority. Priority badge visible on task cards. Chatbot can set priority.

---

## Phase 4: User Story 2 - Task Tagging (Priority: P1)

**Goal**: Users can add/remove tags on tasks, view tags as chips, and get tag autocomplete suggestions.

**Independent Test**: Create a task with tags ["work", "meeting"], view tags on the card, call GET /tags and verify autocomplete list.

**FRs**: FR-010, FR-011, FR-012, FR-013, FR-014

### Backend

- [x] T026 [US2] Modify `POST /{user_id}/tasks` in `backend/routers/tasks.py` to accept and persist `tags` array with tag normalization (lowercase, strip invalid chars)
- [x] T027 [US2] Modify `PUT/PATCH /{user_id}/tasks/{task_id}` in `backend/routers/tasks.py` to accept and persist `tags` updates with normalization
- [x] T028 [US2] Add `GET /{user_id}/tags` endpoint in `backend/routers/tasks.py`: query `SELECT DISTINCT unnest(tags) FROM tasks WHERE user_id = :uid ORDER BY 1` and return `TagListResponse`

### Frontend

- [x] T029 [P] [US2] Create `frontend/components/tag-input.tsx`: tag input component with autocomplete from `GET /tags` endpoint, chip display, add/remove
- [x] T030 [US2] Modify `frontend/components/task-form.tsx` (or add-task-modal.tsx): integrate `TagInput` component for tag entry
- [x] T031 [US2] Modify `frontend/components/task-card.tsx`: display tags as styled chips/badges
- [x] T032 [US2] Modify `frontend/components/edit-task-modal.tsx`: integrate `TagInput` for editing tags
- [x] T033 [US2] Add `getTags()` method to `frontend/lib/api-client.ts`

### AI Chatbot

- [x] T034 [US2] Update `add_task` tool definition in `backend/chat/tools.py` to accept optional `tags` array parameter
- [x] T035 [US2] Update `update_task` tool definition in `backend/chat/tools.py` to accept optional `tags` array parameter

**Checkpoint**: Tags CRUD works end-to-end. Tag autocomplete populated. Chatbot can add/remove tags.

---

## Phase 5: User Story 3 - Search Tasks (Priority: P2)

**Goal**: Users can search tasks by keyword across title and description fields.

**Independent Test**: Create tasks "Buy groceries" and "Send email", search for "grocery", verify only the first task matches.

**FRs**: FR-020, FR-021, FR-022

### Backend

- [x] T036 [US3] Add `q` query parameter to `GET /{user_id}/tasks` in `backend/routers/tasks.py`: implement ILIKE search on `title` and `description` fields with `%{q}%` pattern

### Frontend

- [x] T037 [P] [US3] Create `frontend/components/search-bar.tsx`: search input with debounce (300ms), clear button, search icon
- [x] T038 [US3] Integrate `SearchBar` into `frontend/components/task-list.tsx` at the top of the list
- [x] T039 [US3] Update `frontend/lib/api-client.ts` `getTasks()` to pass `q` query parameter when search term is provided

### AI Chatbot

- [x] T040 [US3] Update `list_tasks` tool definition in `backend/chat/tools.py` to accept optional `q` (search) parameter

**Checkpoint**: Search works end-to-end. Keyword search filters results in real-time. Chatbot can search tasks.

---

## Phase 6: User Story 4 - Filter Tasks (Priority: P2)

**Goal**: Users can filter tasks by completion status, priority, tags, overdue status, and due date range.

**Independent Test**: Create tasks with mixed priorities and tags, filter by "priority=high" + "tag=work", verify only matching tasks shown.

**FRs**: FR-030, FR-031, FR-032, FR-033, FR-034, FR-035

### Backend

- [x] T041 [US4] Add `completed` (bool), `priority` (comma-separated string), `tag` (comma-separated string) query parameters to `GET /{user_id}/tasks` in `backend/routers/tasks.py` with AND logic composition
- [x] T042 [US4] Add `overdue` (bool) query parameter: filter where `due_date < date.today() AND completed = false` in `backend/routers/tasks.py`
- [x] T043 [US4] Add `due_before` and `due_after` (date string) query parameters for date range filtering in `backend/routers/tasks.py`
- [x] T044 [US4] Implement tag containment filter using PostgreSQL `@>` (contains) operator with ARRAY cast in `backend/routers/tasks.py`

### Frontend

- [x] T045 [US4] Modify `frontend/components/filter-tabs.tsx`: extend beyond all/active/completed to include priority filter dropdown, tag filter dropdown, overdue toggle
- [x] T046 [P] [US4] Create `frontend/hooks/use-task-filters.ts`: hook managing filter/sort/search/pagination state, constructs query params for API calls
- [x] T047 [US4] Connect `filter-tabs.tsx` and `task-list.tsx` to `use-task-filters` hook; trigger API refetch on filter change

### AI Chatbot

- [x] T048 [US4] Update `list_tasks` tool definition in `backend/chat/tools.py` to accept optional `priority`, `tag`, `overdue` filter parameters

**Checkpoint**: All filter combinations work. AND logic applied. Chatbot can filter tasks by priority/tag/overdue.

---

## Phase 7: User Story 5 - Sort Tasks (Priority: P2)

**Goal**: Users can sort task list by priority, due date, created date, updated date, and title in ascending or descending order.

**Independent Test**: Create tasks with different priorities, sort by "priority desc", verify urgent appears first.

**FRs**: FR-040, FR-041, FR-042, FR-043, FR-044

### Backend

- [x] T049 [US5] Add `sort_by` (enum: priority/due_date/created_at/updated_at/title, default created_at) and `sort_order` (asc/desc, default desc) query parameters to `GET /{user_id}/tasks` in `backend/routers/tasks.py`
- [x] T050 [US5] Implement null handling for `due_date` sort: tasks without due dates appear LAST when ascending, FIRST when descending using `NULLS LAST` / `NULLS FIRST` in `backend/routers/tasks.py`

### Frontend

- [x] T051 [P] [US5] Create `frontend/components/sort-selector.tsx`: dropdown for sort field selection + ascending/descending toggle button
- [x] T052 [US5] Integrate `SortSelector` into `frontend/components/task-list.tsx` alongside search bar and filters
- [x] T053 [US5] Connect sort selector to `use-task-filters` hook; trigger API refetch on sort change

### AI Chatbot

- [x] T054 [US5] Update `list_tasks` tool definition in `backend/chat/tools.py` to accept optional `sort_by` parameter

**Checkpoint**: Sort works end-to-end for all 5 fields in both directions. Null due_date positioned correctly. Chatbot can sort.

---

## Phase 8: User Story 6 - Due Dates (Priority: P3)

**Goal**: Users can set due dates on tasks and see overdue indicators.

**Independent Test**: Create a task with due date in the past, verify `is_overdue = true` in response and red styling in UI.

**FRs**: FR-060, FR-061, FR-062

### Backend

- [x] T055 [US6] Modify `POST /{user_id}/tasks` in `backend/routers/tasks.py` to accept and persist `due_date` field (date, nullable)
- [x] T056 [US6] Modify `PUT/PATCH /{user_id}/tasks/{task_id}` in `backend/routers/tasks.py` to accept `due_date` updates (including setting to null to remove)

### Frontend

- [x] T057 [P] [US6] Create `frontend/components/date-picker.tsx`: due date input component using native HTML date input, with clear button
- [x] T058 [US6] Modify `frontend/components/task-form.tsx` (or add-task-modal.tsx): integrate `DatePicker` for due date entry
- [x] T059 [US6] Modify `frontend/components/task-card.tsx`: display due date with conditional styling — red text for overdue, orange for due within 2 days, gray for future dates
- [x] T060 [US6] Modify `frontend/components/edit-task-modal.tsx`: integrate `DatePicker` for editing due dates

### AI Chatbot

- [x] T061 [US6] Update `add_task` tool definition in `backend/chat/tools.py` to accept optional `due_date` parameter (YYYY-MM-DD format)
- [x] T062 [US6] Update `update_task` tool definition in `backend/chat/tools.py` to accept optional `due_date` parameter

**Checkpoint**: Due dates work end-to-end. Overdue indicator computed correctly. Chatbot can set/query due dates.

---

## Phase 9: User Story 7 - Reminders (Priority: P3)

**Goal**: Users can create, list, and delete reminders on tasks. Reminders auto-cancel when task is completed.

**Independent Test**: Create a reminder on a task, list reminders, complete the task, verify reminder status changed to "cancelled".

**FRs**: FR-070, FR-071, FR-072, FR-073, FR-074, FR-075, FR-076

### Backend

- [x] T063 [US7] Create `backend/routers/reminders.py` with `GET /{user_id}/tasks/{task_id}/reminders` endpoint: list reminders for a task (user-scoped)
- [x] T064 [US7] Add `POST /{user_id}/tasks/{task_id}/reminders` endpoint in `backend/routers/reminders.py`: create reminder with absolute `trigger_at` OR relative `relative_to_due` (computed from task's due_date). Validate trigger_at is in the future. Validate task belongs to user.
- [x] T065 [US7] Add `DELETE /{user_id}/tasks/{task_id}/reminders/{reminder_id}` endpoint in `backend/routers/reminders.py`
- [x] T066 [US7] Register reminder router in `backend/main.py`
- [x] T067 [US7] Modify PATCH endpoint in `backend/routers/tasks.py`: when `completed: true`, cancel all `pending` reminders for the task (set status = "cancelled")

### Frontend

- [x] T068 [US7] Add `createReminder()`, `getReminders()`, `deleteReminder()` methods to `frontend/lib/api-client.ts`
- [x] T069 [US7] Add reminder UI to task detail/edit view: display existing reminders, button to add reminder (absolute datetime or relative-to-due), delete button per reminder

### AI Chatbot

- [x] T070 [US7] Add `set_reminder` tool definition to `backend/chat/tools.py`: create a reminder for a task (accepts task_id, trigger_at or relative_to_due). Update `get_tool_definitions()` and `TOOL_REGISTRY`.

**Checkpoint**: Reminder CRUD works end-to-end. Cascade cancel on task completion works. Chatbot can set reminders.

---

## Phase 10: User Story 8 - Recurring Tasks (Priority: P4)

**Goal**: Users can create recurring tasks that auto-generate the next instance upon completion.

**Independent Test**: Create a task with `recurrence_rule = "FREQ=DAILY"` and due date today, complete it, verify new task created with due date = tomorrow and same recurrence_group_id.

**FRs**: FR-080, FR-081, FR-082, FR-083, FR-084, FR-085

### Backend

- [x] T071 [P] [US8] Create `backend/services/recurrence.py` with: `parse_recurrence_rule(rule: str) -> RecurrenceConfig` (parse simplified RRULE), `compute_next_due_date(current_due: date, rule: str) -> date | None` (calculate next instance date), `generate_next_instance(task: Task, session: AsyncSession) -> Task | None` (create next recurring task with same title/description/priority/tags, new UUID, new due_date, copied recurrence_rule and recurrence_group_id)
- [x] T072 [US8] Modify `POST /{user_id}/tasks` in `backend/routers/tasks.py`: when `recurrence_rule` is provided, generate a `recurrence_group_id` (uuid4) and assign it to the new task
- [x] T073 [US8] Modify PATCH endpoint in `backend/routers/tasks.py`: when `completed: true` on a task with `recurrence_rule`, call `generate_next_instance()` to create the next recurring task. Handle UNTIL clause (skip generation if past end date).
- [x] T074 [US8] Handle recurring task reminder inheritance: when generating next instance, if parent task had reminder rules (relative reminders), create corresponding pending reminders on the new instance in `backend/services/recurrence.py`

### Frontend

- [x] T075 [US8] Modify `frontend/components/task-form.tsx` (or add-task-modal.tsx): add recurrence rule selector (dropdown: None/Daily/Weekly/Monthly + optional end date input)
- [x] T076 [US8] Modify `frontend/components/task-card.tsx`: display recurrence indicator icon (e.g., refresh/repeat icon) for tasks with `recurrence_rule`
- [x] T077 [US8] Modify `frontend/components/edit-task-modal.tsx`: add recurrence editing (change rule or set to null to stop)

### AI Chatbot

- [x] T078 [US8] Update `add_task` tool definition in `backend/chat/tools.py` to accept optional `recurrence_rule` parameter
- [x] T079 [US8] Update `complete_task` tool handler in `backend/chat/tools.py`: when completing a recurring task, include info about the newly generated instance in the response

**Checkpoint**: Recurring tasks work end-to-end. Completing a recurring task generates the next instance. UNTIL clause respected. Chatbot can create and stop recurring tasks.

---

## Phase 11: Integration & Regression

**Purpose**: Validate all features work together and no regressions from schema changes.

- [ ] T080 [INT] Full integration test: create task with priority "high", tags ["work"], due date "2026-03-15", recurrence "FREQ=WEEKLY;BYDAY=MO" → verify all fields persisted and returned correctly
- [ ] T081 [INT] Filter + sort combo test: create 10+ tasks with varied attributes → filter by priority=high + tag=work → sort by due_date asc → verify correct filtered, sorted result
- [ ] T082 [INT] Search + filter combo test: search "grocery" with priority filter "high" → verify AND logic between search and filter
- [ ] T083 [INT] Pagination test: create 60+ tasks → request limit=10, offset=0 → verify 10 tasks returned with total=60+ → request offset=50 → verify remaining tasks
- [ ] T084 [INT] Recurring task completion flow: complete a FREQ=DAILY recurring task → verify new instance with next day's due date → verify recurrence_group_id matches → verify pending reminders created on new instance
- [ ] T085 [INT] Cascade test: create task with reminders → delete task → verify reminders deleted. Create task with reminders → complete task → verify reminders cancelled.
- [ ] T086 [INT] AI chatbot integration test: "Add high priority task 'review report' tagged work due March 15th" → verify task created with all fields correct
- [x] T087 [REG] Regression: verify existing CRUD operations (create/read/update/delete basic tasks) still work with old payload format (no new fields specified)
- [x] T088 [REG] Regression: verify old tasks without new fields display correctly in frontend (defaults applied: priority="none", tags=[], no due date, no recurrence)
- [ ] T089 [REG] Regression: verify chatbot conversation persistence still works (no schema conflicts)
- [ ] T090 [REG] Regression: verify user isolation on ALL new endpoints — user A cannot access user B's tasks, tags, or reminders

**Checkpoint**: All 50 FRs verified. All 13 success criteria met. No regressions from Phase II/III.

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1 (Setup)**: No dependencies — start immediately. BLOCKS all subsequent phases.
- **Phase 2 (Foundational)**: Depends on Phase 1. BLOCKS all user story phases (pagination contract change).
- **Phases 3-10 (User Stories)**: All depend on Phase 1 + 2 completion.
  - US1 (Priority) and US2 (Tags) are P1 — implement first.
  - US3 (Search), US4 (Filter), US5 (Sort) are P2 — implement second.
  - US6 (Due Dates) and US7 (Reminders) are P3 — implement third.
  - US8 (Recurring) is P4 — implement last.
- **Phase 11 (Integration)**: Depends on all user stories being complete.

### User Story Dependencies

- **US1 (Priority)**: Independent. Can start after Phase 2.
- **US2 (Tags)**: Independent. Can start after Phase 2. Can run in parallel with US1.
- **US3 (Search)**: Independent. Can start after Phase 2.
- **US4 (Filter)**: Depends on US1 (priority filter) and US2 (tag filter) for full filter coverage. Can start backend work after Phase 2, but frontend filter UI benefits from priority badge and tag chips existing.
- **US5 (Sort)**: Depends on US1 (priority sort) for full sort coverage. Can start after Phase 2.
- **US6 (Due Dates)**: Independent. Can start after Phase 2.
- **US7 (Reminders)**: Weakly depends on US6 (relative reminders need due_date). Can start independently for absolute reminders.
- **US8 (Recurring)**: Weakly depends on US6 (due_date computation) and US7 (reminder inheritance). Can start independently for core recurrence.

### Parallel Opportunities

**Within Phase 1**:
- T001-T004 (models) can run sequentially (same file)
- T005-T012 (schemas) can run sequentially (same file)
- Model work and schema work are in different files and can run in parallel

**Within User Story Phases**:
- Frontend component creation tasks marked [P] can run in parallel (different files)
- Backend route changes within the same file must be sequential
- Chatbot tool updates (same file) must be sequential

**Across User Stories** (after Phase 2):
- US1 and US2 can run fully in parallel (P1 pair)
- US3, US5, US6 can run fully in parallel with each other
- US4 frontend benefits from US1 + US2 being complete first
- US7 backend benefits from US6 being complete first (relative reminders)
- US8 benefits from US6 + US7 being complete first (recurrence with due dates and reminder inheritance)

---

## Implementation Strategy

### Recommended Sequence (Single Developer)

1. Phase 1: Setup (T001-T012) — ~12 tasks, same 2 files
2. Phase 2: Foundational (T013-T016) — pagination breaking change
3. Phase 3: US1 Priority (T017-T025) — P1, immediate user value
4. Phase 4: US2 Tags (T026-T035) — P1, completes categorization
5. Phase 6: US4 Filters (T041-T048) — P2, uses priority + tags
6. Phase 5: US3 Search (T036-T040) — P2, lightweight addition
7. Phase 7: US5 Sort (T049-T054) — P2, completes list controls
8. Phase 8: US6 Due Dates (T055-T062) — P3, enables reminders
9. Phase 9: US7 Reminders (T063-T070) — P3, uses due dates
10. Phase 10: US8 Recurring (T071-T079) — P4, power-user feature
11. Phase 11: Integration (T080-T090) — validation sweep

### MVP Delivery Point

After Phase 4 (US1 + US2 complete): users can create tasks with priorities and tags. Provides immediate organizational value.

---

## Summary

| Metric | Count |
|--------|-------|
| **Total tasks** | **90** |
| Phase 1 (Setup) | 12 |
| Phase 2 (Foundational) | 4 |
| US1 (Priority) | 9 |
| US2 (Tags) | 10 |
| US3 (Search) | 5 |
| US4 (Filter) | 8 |
| US5 (Sort) | 6 |
| US6 (Due Dates) | 8 |
| US7 (Reminders) | 8 |
| US8 (Recurring) | 9 |
| Integration & Regression | 11 |
| **Parallel opportunities** | 8 tasks marked [P] + cross-story parallelism |
| **Files modified** | 9 existing files |
| **Files created** | 7 new files |
