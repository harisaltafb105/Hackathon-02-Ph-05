# Quickstart: 006-advanced-todo-features

## Prerequisites

- Python 3.13+ with `uv` package manager
- Node.js 18+ with npm
- Running Neon PostgreSQL instance (DATABASE_URL configured)
- Existing Phase II/III application operational

## Backend Changes

### 1. Schema Migration (if create_all() doesn't add columns)

If existing tasks table doesn't get new columns via `SQLModel.metadata.create_all()`, run manually:

```sql
-- Add new columns to tasks table
ALTER TABLE tasks ADD COLUMN IF NOT EXISTS priority VARCHAR(10) NOT NULL DEFAULT 'none';
ALTER TABLE tasks ADD COLUMN IF NOT EXISTS tags TEXT[] NOT NULL DEFAULT '{}';
ALTER TABLE tasks ADD COLUMN IF NOT EXISTS due_date DATE;
ALTER TABLE tasks ADD COLUMN IF NOT EXISTS recurrence_rule VARCHAR(200);
ALTER TABLE tasks ADD COLUMN IF NOT EXISTS recurrence_group_id UUID;

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_tasks_priority ON tasks (priority);
CREATE INDEX IF NOT EXISTS idx_tasks_tags ON tasks USING gin (tags);
CREATE INDEX IF NOT EXISTS idx_tasks_due_date ON tasks (due_date);
CREATE INDEX IF NOT EXISTS idx_tasks_recurrence_group ON tasks (recurrence_group_id);
CREATE INDEX IF NOT EXISTS idx_tasks_user_priority ON tasks (user_id, priority);
CREATE INDEX IF NOT EXISTS idx_tasks_user_due_date ON tasks (user_id, due_date);

-- Create reminders table
CREATE TABLE IF NOT EXISTS reminders (
    id UUID PRIMARY KEY,
    task_id UUID NOT NULL REFERENCES tasks(id) ON DELETE CASCADE,
    user_id VARCHAR NOT NULL,
    trigger_at TIMESTAMP NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'pending',
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_reminders_task_id ON reminders (task_id);
CREATE INDEX IF NOT EXISTS idx_reminders_user_id ON reminders (user_id);
CREATE INDEX IF NOT EXISTS idx_reminders_trigger_status ON reminders (trigger_at, status);
```

### 2. Run Backend

```bash
cd backend
uv run uvicorn backend.main:app --reload
```

### 3. Test New Endpoints

```bash
# Create task with new fields
curl -X POST http://localhost:8000/api/{user_id}/tasks \
  -H "Authorization: Bearer {token}" \
  -H "Content-Type: application/json" \
  -d '{"title": "Review report", "priority": "high", "tags": ["work"], "due_date": "2026-03-15"}'

# Search tasks
curl "http://localhost:8000/api/{user_id}/tasks?q=report" \
  -H "Authorization: Bearer {token}"

# Filter by priority + tag
curl "http://localhost:8000/api/{user_id}/tasks?priority=high,urgent&tag=work" \
  -H "Authorization: Bearer {token}"

# Sort by priority descending
curl "http://localhost:8000/api/{user_id}/tasks?sort_by=priority&sort_order=desc" \
  -H "Authorization: Bearer {token}"

# Paginate
curl "http://localhost:8000/api/{user_id}/tasks?limit=10&offset=20" \
  -H "Authorization: Bearer {token}"

# Get overdue tasks
curl "http://localhost:8000/api/{user_id}/tasks?overdue=true" \
  -H "Authorization: Bearer {token}"

# Get user's tags
curl "http://localhost:8000/api/{user_id}/tags" \
  -H "Authorization: Bearer {token}"

# Create reminder
curl -X POST "http://localhost:8000/api/{user_id}/tasks/{task_id}/reminders" \
  -H "Authorization: Bearer {token}" \
  -H "Content-Type: application/json" \
  -d '{"trigger_at": "2026-03-14T09:00:00Z"}'

# Create relative reminder
curl -X POST "http://localhost:8000/api/{user_id}/tasks/{task_id}/reminders" \
  -H "Authorization: Bearer {token}" \
  -H "Content-Type: application/json" \
  -d '{"relative_to_due": "-1d"}'
```

### 4. Run Tests

```bash
cd backend
uv run pytest tests/ -v
```

## Frontend Changes

### 1. Install Dependencies (if any new)

No new npm dependencies required. Using native HTML date input and existing Tailwind components.

### 2. Run Frontend

```bash
cd frontend
npm run dev
```

### 3. Verify

- Open http://localhost:3000
- Create a task with priority, tags, and due date
- Search for tasks using the search bar
- Filter by priority, tag, overdue status
- Sort by different fields
- Complete a recurring task and verify new instance

## Key Files Changed

| File | Change Type | Description |
|------|-------------|-------------|
| `backend/models.py` | MODIFY | Add Priority enum, extend Task, add Reminder |
| `backend/schemas.py` | MODIFY | Add new schemas, extend existing |
| `backend/routers/tasks.py` | MODIFY | Search/filter/sort/pagination, new fields |
| `backend/routers/reminders.py` | NEW | Reminder CRUD |
| `backend/services/recurrence.py` | NEW | Recurring task logic |
| `backend/chat/tools.py` | MODIFY | Extended MCP tool definitions |
| `backend/main.py` | MODIFY | Register reminder router |
| `frontend/types/task.ts` | MODIFY | Extended Task interface |
| `frontend/lib/api-client.ts` | MODIFY | New API methods |
| `frontend/components/*.tsx` | MODIFY/NEW | UI extensions |
| `frontend/hooks/use-task-filters.ts` | NEW | Filter state management |
