"""
Recurring task logic for Phase V.

Parses simplified RRULE strings and generates next task instances
when a recurring task is completed.

Supported RRULE subset:
  FREQ=DAILY|WEEKLY|MONTHLY
  BYDAY=MO,TU,...  (optional, WEEKLY only)
  BYMONTHDAY=1-31  (optional, MONTHLY only)
  UNTIL=YYYY-MM-DD (optional)
"""

import calendar
from dataclasses import dataclass
from datetime import date, timedelta
from typing import Optional
from uuid import uuid4

from sqlalchemy.ext.asyncio import AsyncSession

from backend.models import Task, Reminder, ReminderStatus


DAY_MAP = {
    "MO": 0, "TU": 1, "WE": 2, "TH": 3, "FR": 4, "SA": 5, "SU": 6,
}


@dataclass
class RecurrenceConfig:
    freq: str  # DAILY, WEEKLY, MONTHLY
    by_day: Optional[list[str]] = None
    by_month_day: Optional[int] = None
    until: Optional[date] = None


def parse_recurrence_rule(rule: str) -> RecurrenceConfig:
    """Parse a simplified RRULE string into a RecurrenceConfig."""
    parts = {}
    for segment in rule.split(";"):
        if "=" in segment:
            key, value = segment.split("=", 1)
            parts[key.strip().upper()] = value.strip()

    freq = parts.get("FREQ", "DAILY")
    by_day = None
    if "BYDAY" in parts:
        by_day = [d.strip() for d in parts["BYDAY"].split(",") if d.strip()]

    by_month_day = None
    if "BYMONTHDAY" in parts:
        by_month_day = int(parts["BYMONTHDAY"])

    until = None
    if "UNTIL" in parts:
        until = date.fromisoformat(parts["UNTIL"])

    return RecurrenceConfig(
        freq=freq,
        by_day=by_day,
        by_month_day=by_month_day,
        until=until,
    )


def compute_next_due_date(current_due: Optional[date], rule: str) -> Optional[date]:
    """
    Compute the next due date based on the recurrence rule.
    Returns None if the UNTIL date has been exceeded.
    """
    config = parse_recurrence_rule(rule)
    base = current_due or date.today()

    if config.freq == "DAILY":
        next_date = base + timedelta(days=1)

    elif config.freq == "WEEKLY":
        if config.by_day:
            # Find the next matching weekday
            target_days = sorted(DAY_MAP[d] for d in config.by_day if d in DAY_MAP)
            current_weekday = base.weekday()
            next_date = None
            for target in target_days:
                if target > current_weekday:
                    next_date = base + timedelta(days=target - current_weekday)
                    break
            if next_date is None:
                # Wrap to next week
                days_until = 7 - current_weekday + target_days[0]
                next_date = base + timedelta(days=days_until)
        else:
            next_date = base + timedelta(weeks=1)

    elif config.freq == "MONTHLY":
        if config.by_month_day:
            target_day = config.by_month_day
        else:
            target_day = base.day

        # Move to next month
        if base.month == 12:
            next_month, next_year = 1, base.year + 1
        else:
            next_month, next_year = base.month + 1, base.year

        # Clamp day to month's max
        max_day = calendar.monthrange(next_year, next_month)[1]
        actual_day = min(target_day, max_day)
        next_date = date(next_year, next_month, actual_day)

    else:
        return None

    # Check UNTIL clause
    if config.until and next_date > config.until:
        return None

    return next_date


async def generate_next_instance(task: Task, session: AsyncSession) -> Optional[Task]:
    """
    Generate the next recurring task instance.
    Returns the new Task or None if recurrence has ended.
    """
    if not task.recurrence_rule:
        return None

    next_due = compute_next_due_date(task.due_date, task.recurrence_rule)
    if next_due is None:
        return None

    new_task = Task(
        title=task.title,
        description=task.description,
        user_id=task.user_id,
        priority=task.priority,
        tags=list(task.tags) if task.tags else [],
        due_date=next_due,
        recurrence_rule=task.recurrence_rule,
        recurrence_group_id=task.recurrence_group_id or uuid4(),
        completed=False,
    )

    session.add(new_task)

    # Inherit relative reminders from parent task
    from sqlmodel import select
    reminder_query = select(Reminder).where(
        Reminder.task_id == task.id,
    )
    reminder_result = await session.execute(reminder_query)
    parent_reminders = reminder_result.scalars().all()

    for r in parent_reminders:
        # If the parent reminder was relative (trigger_at was before due_date),
        # compute the same offset for the new instance
        if task.due_date and r.trigger_at:
            from datetime import datetime, timezone
            due_dt = datetime(task.due_date.year, task.due_date.month, task.due_date.day)
            offset = due_dt - r.trigger_at.replace(tzinfo=None)
            new_trigger = datetime(next_due.year, next_due.month, next_due.day) - offset
            if new_trigger > datetime.utcnow():
                new_reminder = Reminder(
                    task_id=new_task.id,
                    user_id=task.user_id,
                    trigger_at=new_trigger,
                    status=ReminderStatus.PENDING.value,
                )
                session.add(new_reminder)

    return new_task
