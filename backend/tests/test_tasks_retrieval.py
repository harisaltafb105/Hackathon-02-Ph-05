"""
US1 - Task Retrieval Tests.
Tests GET /api/{user_id}/tasks and GET /api/{user_id}/tasks/{task_id}
"""

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from backend.models import Task


@pytest.mark.asyncio
async def test_list_own_tasks(
    client: AsyncClient,
    test_session: AsyncSession,
    test_user_id: str,
    mock_jwt_token: str
):
    """
    Test: Authenticated user can retrieve their own tasks.
    """
    # Create test tasks
    task1 = Task(
        title="Task 1",
        description="Description 1",
        user_id=test_user_id
    )
    task2 = Task(
        title="Task 2",
        description="Description 2",
        completed=True,
        user_id=test_user_id
    )

    test_session.add(task1)
    test_session.add(task2)
    await test_session.commit()

    # Request tasks with valid token
    headers = {"Authorization": f"Bearer {mock_jwt_token}"}
    response = await client.get(f"/api/{test_user_id}/tasks", headers=headers)

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert all(task["user_id"] == test_user_id for task in data)


@pytest.mark.asyncio
async def test_list_empty_tasks(
    client: AsyncClient,
    test_user_id: str,
    mock_jwt_token: str
):
    """
    Test: User with no tasks receives empty array.
    """
    headers = {"Authorization": f"Bearer {mock_jwt_token}"}
    response = await client.get(f"/api/{test_user_id}/tasks", headers=headers)

    assert response.status_code == 200
    data = response.json()
    assert data == []


@pytest.mark.asyncio
async def test_list_other_user_tasks_403(
    client: AsyncClient,
    test_user_id_2: str,
    mock_jwt_token: str
):
    """
    Test: User cannot access another user's tasks (403 Forbidden).
    """
    headers = {"Authorization": f"Bearer {mock_jwt_token}"}
    response = await client.get(f"/api/{test_user_id_2}/tasks", headers=headers)

    assert response.status_code == 403
    data = response.json()
    assert "error" in data


@pytest.mark.asyncio
async def test_list_no_auth_401(
    client: AsyncClient,
    test_user_id: str
):
    """
    Test: Request without authentication returns 401.
    """
    response = await client.get(f"/api/{test_user_id}/tasks")

    assert response.status_code == 401


@pytest.mark.asyncio
async def test_get_specific_task(
    client: AsyncClient,
    test_session: AsyncSession,
    test_user_id: str,
    mock_jwt_token: str
):
    """
    Test: User can retrieve a specific task by ID.
    """
    # Create test task
    task = Task(
        title="Specific Task",
        description="Test description",
        user_id=test_user_id
    )

    test_session.add(task)
    await test_session.commit()
    await test_session.refresh(task)

    # Request specific task
    headers = {"Authorization": f"Bearer {mock_jwt_token}"}
    response = await client.get(
        f"/api/{test_user_id}/tasks/{task.id}",
        headers=headers
    )

    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Specific Task"
    assert data["user_id"] == test_user_id


@pytest.mark.asyncio
async def test_get_nonexistent_task_404(
    client: AsyncClient,
    test_user_id: str,
    mock_jwt_token: str
):
    """
    Test: Getting non-existent task returns 404.
    """
    fake_uuid = "00000000-0000-0000-0000-000000000000"
    headers = {"Authorization": f"Bearer {mock_jwt_token}"}
    response = await client.get(
        f"/api/{test_user_id}/tasks/{fake_uuid}",
        headers=headers
    )

    assert response.status_code == 404
