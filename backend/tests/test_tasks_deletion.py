"""
US4 - Task Deletion Tests.
Tests DELETE /api/{user_id}/tasks/{task_id}
"""

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select
from backend.models import Task


@pytest.mark.asyncio
async def test_delete_success_204(
    client: AsyncClient,
    test_session: AsyncSession,
    test_user_id: str,
    mock_jwt_token: str
):
    """
    Test: User can delete their own task (returns 204 No Content).
    """
    # Create test task
    task = Task(
        title="Task to Delete",
        description="Will be deleted",
        user_id=test_user_id
    )

    test_session.add(task)
    await test_session.commit()
    await test_session.refresh(task)
    task_id = task.id

    # Delete task
    headers = {"Authorization": f"Bearer {mock_jwt_token}"}
    response = await client.delete(
        f"/api/{test_user_id}/tasks/{task_id}",
        headers=headers
    )

    assert response.status_code == 204
    assert response.content == b""  # No content

    # Verify task is deleted
    statement = select(Task).where(Task.id == task_id)
    result = await test_session.execute(statement)
    deleted_task = result.scalar_one_or_none()
    assert deleted_task is None


@pytest.mark.asyncio
async def test_delete_other_user_task_403(
    client: AsyncClient,
    test_session: AsyncSession,
    test_user_id: str,
    test_user_id_2: str,
    mock_jwt_token: str
):
    """
    Test: User cannot delete another user's task (403 or 404).
    """
    # Create task for user_2
    task = Task(
        title="User 2 Task",
        description="Belongs to user 2",
        user_id=test_user_id_2
    )

    test_session.add(task)
    await test_session.commit()
    await test_session.refresh(task)

    # Try to delete as user_1
    headers = {"Authorization": f"Bearer {mock_jwt_token}"}
    response = await client.delete(
        f"/api/{test_user_id}/tasks/{task.id}",
        headers=headers
    )

    # Should be 404 since task doesn't exist for this user
    assert response.status_code == 404

    # Verify task still exists
    statement = select(Task).where(Task.id == task.id)
    result = await test_session.execute(statement)
    existing_task = result.scalar_one_or_none()
    assert existing_task is not None


@pytest.mark.asyncio
async def test_delete_nonexistent_404(
    client: AsyncClient,
    test_user_id: str,
    mock_jwt_token: str
):
    """
    Test: Deleting non-existent task returns 404.
    """
    fake_uuid = "00000000-0000-0000-0000-000000000000"
    headers = {"Authorization": f"Bearer {mock_jwt_token}"}
    response = await client.delete(
        f"/api/{test_user_id}/tasks/{fake_uuid}",
        headers=headers
    )

    assert response.status_code == 404


@pytest.mark.asyncio
async def test_delete_no_auth_401(
    client: AsyncClient,
    test_session: AsyncSession,
    test_user_id: str
):
    """
    Test: Deleting task without authentication returns 401.
    """
    # Create test task
    task = Task(
        title="Task requiring auth",
        user_id=test_user_id
    )

    test_session.add(task)
    await test_session.commit()
    await test_session.refresh(task)

    # Try to delete without auth
    response = await client.delete(
        f"/api/{test_user_id}/tasks/{task.id}"
    )

    assert response.status_code == 401

    # Verify task still exists
    statement = select(Task).where(Task.id == task.id)
    result = await test_session.execute(statement)
    existing_task = result.scalar_one_or_none()
    assert existing_task is not None
