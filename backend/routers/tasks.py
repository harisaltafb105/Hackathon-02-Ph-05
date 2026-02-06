"""
Task CRUD endpoints.
Provides RESTful API for task management with strict user isolation.
"""

from typing import Annotated, List
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from backend.database import get_session
from backend.auth import get_current_user, verify_user_access
from backend.models import Task
from backend.schemas import TaskResponse, TaskCreate, TaskUpdate, TaskPatch


router = APIRouter(
    prefix="/api",
    tags=["tasks"]
)


# US1 - Task Retrieval
@router.get("/{user_id}/tasks", response_model=List[TaskResponse])
async def list_tasks(
    user_id: str,
    session: Annotated[AsyncSession, Depends(get_session)],
    current_user_id: Annotated[str, Depends(get_current_user)]
):
    """
    Get all tasks for the authenticated user.

    Strict user isolation: Only returns tasks where user_id matches the authenticated user.

    Returns:
        List of tasks (empty list if user has no tasks)

    Raises:
        401 Unauthorized: If token is missing or invalid
        403 Forbidden: If user_id in path doesn't match token user_id
    """
    # Verify user can only access their own tasks
    await verify_user_access(user_id, current_user_id)

    # Query tasks filtered by user_id
    statement = select(Task).where(Task.user_id == current_user_id)
    result = await session.execute(statement)
    tasks = result.scalars().all()

    return tasks


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
        user_id=current_user_id
    )

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
    if task_data.completed is not None:
        task.completed = task_data.completed

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

    # Delete task
    await session.delete(task)
    await session.commit()

    # Return None for 204 No Content
    return None
