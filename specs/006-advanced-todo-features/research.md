# Research: Intermediate & Advanced Todo Features

**Feature**: 006-advanced-todo-features
**Date**: 2026-02-07

## Research Questions & Findings

### R1: PostgreSQL Array Column with GIN Index via SQLModel

**Decision**: Use SQLAlchemy `ARRAY(String)` column type with `GIN` index for tags.

**Rationale**: PostgreSQL natively supports array types with efficient containment queries (`@>` operator). GIN indexes enable fast lookups. SQLModel/SQLAlchemy supports this via `sa_column=Column(ARRAY(String))`.

**Alternatives considered**:
- Separate `tags` junction table: More normalized but requires joins for every query, increases complexity. Rejected for MVP scope.
- JSON column: Flexible but no array-specific indexing/operators. Rejected.
- Comma-separated string: No indexing, requires parsing. Rejected.

**Implementation pattern**:
```python
from sqlalchemy import Column
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy import String

tags: list[str] = Field(
    default_factory=list,
    sa_column=Column(ARRAY(String), nullable=False, server_default="{}"),
)
```

**GIN index**:
```python
from sqlalchemy import Index
Index("idx_tasks_tags", "tags", postgresql_using="gin")
```

**Query for tag containment**:
```python
from sqlalchemy.dialects.postgresql import array
query = select(Task).where(Task.tags.contains(["work"]))
```

### R2: Enum Storage Strategy for Priority

**Decision**: Use Python `str` enum stored as VARCHAR in PostgreSQL, with ordinal values for sorting computed at query time via CASE WHEN.

**Rationale**: Storing as string keeps the database human-readable and avoids integer mapping confusion. Priority ordinals are needed only for sorting, which is rare enough to compute at query time without performance concern.

**Alternatives considered**:
- Integer enum in DB: Faster sorting but values meaningless without mapping. Rejected for readability.
- PostgreSQL native ENUM type: Requires explicit migration for new values. Rejected for flexibility.

**Implementation pattern**:
```python
class TaskPriority(str, Enum):
    NONE = "none"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"

PRIORITY_ORDER = {
    TaskPriority.NONE: 0,
    TaskPriority.LOW: 1,
    TaskPriority.MEDIUM: 2,
    TaskPriority.HIGH: 3,
    TaskPriority.URGENT: 4,
}
```

**Sort query** (SQLAlchemy CASE):
```python
from sqlalchemy import case
priority_order = case(
    (Task.priority == "urgent", 4),
    (Task.priority == "high", 3),
    (Task.priority == "medium", 2),
    (Task.priority == "low", 1),
    else_=0,
)
query = query.order_by(priority_order.desc())
```

### R3: Simplified RRULE Parsing for Recurrence

**Decision**: Parse a simplified RRULE string using manual parsing (no external library). Support only `FREQ`, `BYDAY`, `BYMONTHDAY`, `UNTIL`.

**Rationale**: The full RFC 5545 RRULE spec is extremely complex. Our needs are limited to daily/weekly/monthly patterns. A custom parser for this subset is 50-100 lines and avoids the `python-dateutil` dependency (which has a full rrule implementation but is heavy and introduces complexity).

**Alternatives considered**:
- `python-dateutil.rrule`: Full RFC 5545 support but overkill. Would need to convert between our string format and dateutil objects. Rejected for simplicity.
- Store as structured JSON: More complex to validate, harder for chatbot to construct. Rejected.

**Implementation pattern**:
```python
@dataclass
class RecurrenceConfig:
    freq: Literal["DAILY", "WEEKLY", "MONTHLY"]
    by_day: list[str] | None = None  # MO, TU, WE, TH, FR, SA, SU
    by_month_day: int | None = None  # 1-31
    until: date | None = None

def parse_recurrence_rule(rule: str) -> RecurrenceConfig:
    parts = dict(part.split("=", 1) for part in rule.split(";"))
    return RecurrenceConfig(
        freq=parts["FREQ"],
        by_day=parts.get("BYDAY", "").split(",") if "BYDAY" in parts else None,
        by_month_day=int(parts["BYMONTHDAY"]) if "BYMONTHDAY" in parts else None,
        until=date.fromisoformat(parts["UNTIL"]) if "UNTIL" in parts else None,
    )
```

### R4: Cascade Delete Strategy for Reminders

**Decision**: Use SQLAlchemy `ondelete="CASCADE"` on the `task_id` foreign key. For the "cancel on complete" behavior, handle it in application code (not DB trigger).

**Rationale**: Database-level cascade handles deletion cleanly. The "cancel on complete" logic requires checking the `status` field and only cancelling `pending` reminders, which is better as application logic than a DB trigger.

**Alternatives considered**:
- DB trigger for cancel-on-complete: More robust but harder to test and debug. Rejected for maintainability.
- Application-level cascade for both: Risk of orphaned records if delete logic has bugs. Rejected — use DB cascade for deletes.

### R5: ILIKE vs Full-Text Search for Task Search

**Decision**: Start with `ILIKE` for search. Add `tsvector` index if performance degrades at scale.

**Rationale**: `ILIKE '%term%'` is simple, works well for small-medium datasets (< 10k tasks per user), and requires no additional columns or triggers. If performance degrades, a `tsvector` column with GIN index can be added as an optimization without API changes.

**Alternatives considered**:
- PostgreSQL `tsvector` from day one: Better performance at scale but requires maintaining a generated column. Overkill for current scope.
- External search (Elasticsearch): Far too complex for current phase. Out of scope.

### R6: Paginated Response Breaking Change Mitigation

**Decision**: Change GET tasks response from `List[TaskResponse]` to `PaginatedTaskResponse` containing `{ tasks: [...], total, limit, offset }`. Update frontend API client simultaneously.

**Rationale**: The pagination wrapper is necessary for the frontend to display page controls and total counts. Since the frontend API client is under our control and currently mocked for task operations, the change is low-risk.

**Impact analysis**:
- `backend/routers/tasks.py` `list_tasks` return type changes
- `frontend/lib/api-client.ts` `getTasks()` response parsing changes
- `frontend/context/task-context.tsx` (if exists) must handle new shape
- `backend/chat/tools.py` `list_tasks` tool: **No change** — it already constructs its own response format
- Existing tests: Must be updated to expect new response shape

### R7: Due Date Overdue Computation

**Decision**: Compute `is_overdue` as a property in the Pydantic response model, not as a database column.

**Rationale**: `is_overdue` depends on the current date and changes without any database update. Computing it at response time keeps the data model clean and avoids stale values.

**Implementation pattern**:
```python
class TaskResponse(BaseModel):
    # ... existing fields ...
    due_date: date | None
    is_overdue: bool = False

    @model_validator(mode="after")
    def compute_overdue(self) -> "TaskResponse":
        if self.due_date and not self.completed and self.due_date < date.today():
            self.is_overdue = True
        return self
```
