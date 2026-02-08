"""
Reminder CRUD endpoints for Phase V.
Provides endpoints for creating, listing, and deleting task reminders.
"""

import re
from datetime import datetime, timedelta
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from backend.database import get_session
from backend.auth import get_current_user, verify_user_access
from backend.models import Task, Reminder, ReminderStatus
from backend.schemas import ReminderCreate, ReminderResponse


router = APIRouter(
    prefix="/api",
    tags=["reminders"]
)


async def _get_user_task(
    user_id: str,
    task_id: UUID,
    current_user_id: str,
    session: AsyncSession,
) -> Task:
    """Helper: verify user access and get task or raise 404."""
    await verify_user_access(user_id, current_user_id)

    query = select(Task).where(Task.id == task_id, Task.user_id == current_user_id)
    result = await session.execute(query)
    task = result.scalar_one_or_none()
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    return task


def _parse_relative_offset(relative: str, due_date) -> datetime:
    """Parse relative offset like '-1d', '-2d', '-1h' and compute absolute trigger_at."""
    if not due_date:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Relative reminder requires task to have a due_date",
        )

    match = re.match(r"^-(\d+)([dh])$", relative)
    if not match:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Invalid relative_to_due format. Use '-Nd' or '-Nh' (e.g., '-1d', '-2h')",
        )

    amount = int(match.group(1))
    unit = match.group(2)

    # Default trigger time: 9:00 AM UTC on the due date
    base = datetime(due_date.year, due_date.month, due_date.day, 9, 0, 0)

    if unit == "d":
        return base - timedelta(days=amount)
    elif unit == "h":
        return base - timedelta(hours=amount)

    raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Invalid unit")


@router.get("/{user_id}/tasks/{task_id}/reminders", response_model=dict)
async def list_reminders(
    user_id: str,
    task_id: UUID,
    session: Annotated[AsyncSession, Depends(get_session)],
    current_user_id: Annotated[str, Depends(get_current_user)],
):
    """List all reminders for a task."""
    await _get_user_task(user_id, task_id, current_user_id, session)

    query = select(Reminder).where(
        Reminder.task_id == task_id,
        Reminder.user_id == current_user_id,
    )
    result = await session.execute(query)
    reminders = result.scalars().all()

    return {
        "reminders": [ReminderResponse.model_validate(r) for r in reminders]
    }


@router.post(
    "/{user_id}/tasks/{task_id}/reminders",
    response_model=ReminderResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_reminder(
    user_id: str,
    task_id: UUID,
    reminder_data: ReminderCreate,
    session: Annotated[AsyncSession, Depends(get_session)],
    current_user_id: Annotated[str, Depends(get_current_user)],
):
    """Create a reminder for a task (absolute or relative to due date)."""
    task = await _get_user_task(user_id, task_id, current_user_id, session)

    if reminder_data.trigger_at:
        trigger_at = reminder_data.trigger_at
    else:
        trigger_at = _parse_relative_offset(reminder_data.relative_to_due, task.due_date)

    # Validate trigger_at is in the future
    if trigger_at <= datetime.utcnow():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Reminder time must be in the future",
        )

    reminder = Reminder(
        task_id=task_id,
        user_id=current_user_id,
        trigger_at=trigger_at,
        status=ReminderStatus.PENDING.value,
    )

    session.add(reminder)
    await session.commit()
    await session.refresh(reminder)

    return reminder


@router.delete(
    "/{user_id}/tasks/{task_id}/reminders/{reminder_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_reminder(
    user_id: str,
    task_id: UUID,
    reminder_id: UUID,
    session: Annotated[AsyncSession, Depends(get_session)],
    current_user_id: Annotated[str, Depends(get_current_user)],
):
    """Delete a reminder."""
    await verify_user_access(user_id, current_user_id)

    query = select(Reminder).where(
        Reminder.id == reminder_id,
        Reminder.task_id == task_id,
        Reminder.user_id == current_user_id,
    )
    result = await session.execute(query)
    reminder = result.scalar_one_or_none()

    if not reminder:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Reminder not found")

    await session.delete(reminder)
    await session.commit()
    return None
