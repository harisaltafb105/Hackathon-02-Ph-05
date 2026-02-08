"""
Task CRUD endpoints.
Provides RESTful API for task management with strict user isolation.

Phase V: Extended with search, filter, sort, pagination, priority, tags,
         due dates, recurring tasks, reminders, and tags endpoint.
"""

from datetime import date
from typing import Annotated, Optional
from uuid import UUID, uuid4
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import case, func, text
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.dialects.postgresql import array as pg_array
from sqlmodel import select

from backend.database import get_session
from backend.auth import get_current_user, verify_user_access
from backend.models import Task, Reminder, ReminderStatus
from backend.schemas import (
    TaskResponse, TaskCreate, TaskUpdate, TaskPatch,
    PaginatedTaskResponse, TagListResponse, normalize_tags,
)


router = APIRouter(
    prefix="/api",
    tags=["tasks"]
)


# Priority ordinal mapping for sorting
PRIORITY_ORDER = case(
    (Task.priority == "urgent", 4),
    (Task.priority == "high", 3),
    (Task.priority == "medium", 2),
    (Task.priority == "low", 1),
    else_=0,
)


# US1 - Task Retrieval (Phase V: search, filter, sort, pagination)
@router.get("/{user_id}/tasks", response_model=PaginatedTaskResponse)
async def list_tasks(
    user_id: str,
    session: Annotated[AsyncSession, Depends(get_session)],
    current_user_id: Annotated[str, Depends(get_current_user)],
    q: Optional[str] = Query(default=None, description="Keyword search on title and description"),
    completed: Optional[bool] = Query(default=None, description="Filter by completion status"),
    priority: Optional[str] = Query(default=None, description="Filter by priority (comma-separated)"),
    tag: Optional[str] = Query(default=None, description="Filter by tag (comma-separated)"),
    overdue: Optional[bool] = Query(default=None, description="Filter overdue tasks"),
    due_before: Optional[date] = Query(default=None, description="Tasks due before this date"),
    due_after: Optional[date] = Query(default=None, description="Tasks due after this date"),
    sort_by: Optional[str] = Query(default="created_at", description="Sort field"),
    sort_order: Optional[str] = Query(default="desc", description="Sort direction (asc/desc)"),
    limit: int = Query(default=50, ge=1, le=100, description="Page size"),
    offset: int = Query(default=0, ge=0, description="Page offset"),
):
    """
    Get tasks for the authenticated user with search, filter, sort, and pagination.

    Returns:
        PaginatedTaskResponse with tasks array, total count, limit, offset
    """
    await verify_user_access(user_id, current_user_id)

    # Base query with user isolation
    query = select(Task).where(Task.user_id == current_user_id)

    # Search: ILIKE on title and description
    if q:
        search_pattern = f"%{q}%"
        query = query.where(
            (Task.title.ilike(search_pattern)) | (Task.description.ilike(search_pattern))
        )

    # Filter: completed status
    if completed is not None:
        query = query.where(Task.completed == completed)

    # Filter: priority (comma-separated)
    if priority:
        priorities = [p.strip() for p in priority.split(",") if p.strip()]
        if priorities:
            query = query.where(Task.priority.in_(priorities))

    # Filter: tag containment (comma-separated, AND logic — task must have ALL tags)
    if tag:
        tags = [t.strip().lower() for t in tag.split(",") if t.strip()]
        for t in tags:
            query = query.where(Task.tags.contains([t]))

    # Filter: overdue (incomplete + due_date < today)
    if overdue:
        query = query.where(
            Task.completed == False,
            Task.due_date < date.today(),
            Task.due_date.isnot(None),
        )

    # Filter: due date range
    if due_before:
        query = query.where(Task.due_date <= due_before)
    if due_after:
        query = query.where(Task.due_date >= due_after)

    # Count total before pagination
    count_query = select(func.count()).select_from(query.subquery())
    total_result = await session.execute(count_query)
    total = total_result.scalar_one()

    # Sort
    if sort_by == "priority":
        order_expr = PRIORITY_ORDER.desc() if sort_order == "desc" else PRIORITY_ORDER.asc()
    elif sort_by == "due_date":
        if sort_order == "asc":
            order_expr = Task.due_date.asc().nulls_last()
        else:
            order_expr = Task.due_date.desc().nulls_first()
    elif sort_by == "title":
        order_expr = Task.title.desc() if sort_order == "desc" else Task.title.asc()
    elif sort_by == "updated_at":
        order_expr = Task.updated_at.desc() if sort_order == "desc" else Task.updated_at.asc()
    else:  # default: created_at
        order_expr = Task.created_at.desc() if sort_order == "desc" else Task.created_at.asc()

    query = query.order_by(order_expr)

    # Pagination
    query = query.offset(offset).limit(limit)

    result = await session.execute(query)
    tasks = result.scalars().all()

    return PaginatedTaskResponse(
        tasks=[TaskResponse.model_validate(t) for t in tasks],
        total=total,
        limit=limit,
        offset=offset,
    )


@router.get("/{user_id}/tasks/{task_id}", response_model=TaskResponse)
async def get_task(
    user_id: str,
    task_id: UUID,
    session: Annotated[AsyncSession, Depends(get_session)],
    current_user_id: Annotated[str, Depends(get_current_user)]
):
    """
    Get a specific task by ID.

    Returns:
        Task object

    Raises:
        401 Unauthorized: If token is missing or invalid
        403 Forbidden: If user_id in path doesn't match token user_id
        404 Not Found: If task doesn't exist or doesn't belong to user
    """
    # Verify user can only access their own tasks
    await verify_user_access(user_id, current_user_id)

    # Query task by ID and user_id (ensures user owns the task)
    statement = select(Task).where(
        Task.id == task_id,
        Task.user_id == current_user_id
    )
    result = await session.execute(statement)
    task = result.scalar_one_or_none()

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )

    return task


# US2 - Task Creation
@router.post("/{user_id}/tasks", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
async def create_task(
    user_id: str,
    task_data: TaskCreate,
    session: Annotated[AsyncSession, Depends(get_session)],
    current_user_id: Annotated[str, Depends(get_current_user)]
):
    """
    Create a new task.

    Request body must include:
        - title (required, 1-500 characters)
        - description (optional, max 5000 characters)

    Returns:
        201 Created with the created task object

    Raises:
        401 Unauthorized: If token is missing or invalid
        403 Forbidden: If user_id in path doesn't match token user_id
        422 Validation Error: If title is missing or validation fails
    """
    # Verify user can only create tasks for themselves
    await verify_user_access(user_id, current_user_id)

    # Create new task with user_id from JWT token
    new_task = Task(
        title=task_data.title,
        description=task_data.description,
        user_id=current_user_id,
        priority=task_data.priority,
        tags=task_data.tags,
        due_date=task_data.due_date,
        recurrence_rule=task_data.recurrence_rule,
    )

    # If recurring, assign a recurrence_group_id
    if task_data.recurrence_rule:
        new_task.recurrence_group_id = uuid4()

    session.add(new_task)
    await session.commit()
    await session.refresh(new_task)

    return new_task


# US3 - Task Update (Full)
@router.put("/{user_id}/tasks/{task_id}", response_model=TaskResponse)
async def update_task_full(
    user_id: str,
    task_id: UUID,
    task_data: TaskUpdate,
    session: Annotated[AsyncSession, Depends(get_session)],
    current_user_id: Annotated[str, Depends(get_current_user)]
):
    """
    Update all fields of a task (full replacement).

    Request body must include all fields:
        - title (required)
        - description (optional)
        - completed (required)

    Returns:
        200 OK with updated task object

    Raises:
        401 Unauthorized: If token is missing or invalid
        403 Forbidden: If user_id in path doesn't match token user_id
        404 Not Found: If task doesn't exist or doesn't belong to user
        422 Validation Error: If validation fails
    """
    # Verify user can only update their own tasks
    await verify_user_access(user_id, current_user_id)

    # Get task by ID and user_id
    statement = select(Task).where(
        Task.id == task_id,
        Task.user_id == current_user_id
    )
    result = await session.execute(statement)
    task = result.scalar_one_or_none()

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )

    # Update all fields
    task.title = task_data.title
    task.description = task_data.description
    task.completed = task_data.completed
    task.priority = task_data.priority
    task.tags = task_data.tags
    task.due_date = task_data.due_date
    task.recurrence_rule = task_data.recurrence_rule
    task.update_timestamp()

    session.add(task)
    await session.commit()
    await session.refresh(task)

    return task


# US3 - Task Update (Partial)
@router.patch("/{user_id}/tasks/{task_id}", response_model=TaskResponse)
async def update_task_partial(
    user_id: str,
    task_id: UUID,
    task_data: TaskPatch,
    session: Annotated[AsyncSession, Depends(get_session)],
    current_user_id: Annotated[str, Depends(get_current_user)]
):
    """
    Update specific fields of a task (partial update).

    Request body can include any combination of:
        - title (optional)
        - description (optional)
        - completed (optional)

    Returns:
        200 OK with updated task object

    Raises:
        401 Unauthorized: If token is missing or invalid
        403 Forbidden: If user_id in path doesn't match token user_id
        404 Not Found: If task doesn't exist or doesn't belong to user
        422 Validation Error: If validation fails
    """
    # Verify user can only update their own tasks
    await verify_user_access(user_id, current_user_id)

    # Get task by ID and user_id
    statement = select(Task).where(
        Task.id == task_id,
        Task.user_id == current_user_id
    )
    result = await session.execute(statement)
    task = result.scalar_one_or_none()

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )

    # Update only provided fields
    if task_data.title is not None:
        task.title = task_data.title
    if task_data.description is not None:
        task.description = task_data.description
    if task_data.priority is not None:
        task.priority = task_data.priority
    if task_data.tags is not None:
        task.tags = task_data.tags
    if task_data.due_date is not None:
        task.due_date = task_data.due_date
    if task_data.recurrence_rule is not None:
        task.recurrence_rule = task_data.recurrence_rule

    # Handle completion with side effects
    if task_data.completed is not None:
        task.completed = task_data.completed

        if task_data.completed:
            # Cancel pending reminders when task is completed
            reminder_query = select(Reminder).where(
                Reminder.task_id == task.id,
                Reminder.status == ReminderStatus.PENDING.value,
            )
            reminder_result = await session.execute(reminder_query)
            pending_reminders = reminder_result.scalars().all()
            for reminder in pending_reminders:
                reminder.status = ReminderStatus.CANCELLED.value
                session.add(reminder)

            # Generate next recurring task instance if applicable
            if task.recurrence_rule:
                from backend.services.recurrence import generate_next_instance
                new_instance = await generate_next_instance(task, session)
                # new_instance is already added to session inside generate_next_instance

    task.update_timestamp()

    session.add(task)
    await session.commit()
    await session.refresh(task)

    return task


# US4 - Task Deletion
@router.delete("/{user_id}/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(
    user_id: str,
    task_id: UUID,
    session: Annotated[AsyncSession, Depends(get_session)],
    current_user_id: Annotated[str, Depends(get_current_user)]
):
    """
    Delete a task.

    Returns:
        204 No Content (success, no body)

    Raises:
        401 Unauthorized: If token is missing or invalid
        403 Forbidden: If user_id in path doesn't match token user_id
        404 Not Found: If task doesn't exist or doesn't belong to user
    """
    # Verify user can only delete their own tasks
    await verify_user_access(user_id, current_user_id)

    # Get task by ID and user_id
    statement = select(Task).where(
        Task.id == task_id,
        Task.user_id == current_user_id
    )
    result = await session.execute(statement)
    task = result.scalar_one_or_none()

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )

    # Delete task (reminders cascade-deleted by DB FK)
    await session.delete(task)
    await session.commit()

    # Return None for 204 No Content
    return None


# Phase V: Tags endpoint
@router.get("/{user_id}/tags", response_model=TagListResponse)
async def list_user_tags(
    user_id: str,
    session: Annotated[AsyncSession, Depends(get_session)],
    current_user_id: Annotated[str, Depends(get_current_user)]
):
    """
    Get all distinct tags used by the authenticated user.
    Returns a sorted, deduplicated list for tag autocomplete.
    """
    await verify_user_access(user_id, current_user_id)

    result = await session.execute(
        text(
            "SELECT DISTINCT unnest(tags) AS tag FROM tasks WHERE user_id = :uid ORDER BY tag"
        ),
        {"uid": current_user_id},
    )
    tags = [row[0] for row in result.fetchall()]

    return TagListResponse(tags=tags)
