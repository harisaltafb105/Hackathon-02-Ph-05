"""
US2 - Task Creation Tests.
Tests POST /api/{user_id}/tasks
"""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_create_task_success(
    client: AsyncClient,
    test_user_id: str,
    mock_jwt_token: str
):
    """
    Test: Authenticated user can create a task.
    """
    headers = {"Authorization": f"Bearer {mock_jwt_token}"}
    task_data = {
        "title": "New Task",
        "description": "Task description"
    }

    response = await client.post(
        f"/api/{test_user_id}/tasks",
        json=task_data,
        headers=headers
    )

    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "New Task"
    assert data["description"] == "Task description"
    assert data["completed"] is False
    assert data["user_id"] == test_user_id
    assert "id" in data
    assert "created_at" in data
    assert "updated_at" in data


@pytest.mark.asyncio
async def test_create_task_without_description(
    client: AsyncClient,
    test_user_id: str,
    mock_jwt_token: str
):
    """
    Test: Task can be created with only title (description is optional).
    """
    headers = {"Authorization": f"Bearer {mock_jwt_token}"}
    task_data = {
        "title": "Task without description"
    }

    response = await client.post(
        f"/api/{test_user_id}/tasks",
        json=task_data,
        headers=headers
    )

    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Task without description"
    assert data["description"] is None


@pytest.mark.asyncio
async def test_create_without_title_422(
    client: AsyncClient,
    test_user_id: str,
    mock_jwt_token: str
):
    """
    Test: Creating task without title returns 422 Validation Error.
    """
    headers = {"Authorization": f"Bearer {mock_jwt_token}"}
    task_data = {
        "description": "Description only, no title"
    }

    response = await client.post(
        f"/api/{test_user_id}/tasks",
        json=task_data,
        headers=headers
    )

    assert response.status_code == 422
    data = response.json()
    assert "error" in data


@pytest.mark.asyncio
async def test_create_title_too_long_422(
    client: AsyncClient,
    test_user_id: str,
    mock_jwt_token: str
):
    """
    Test: Creating task with title > 500 chars returns 422.
    """
    headers = {"Authorization": f"Bearer {mock_jwt_token}"}
    task_data = {
        "title": "x" * 501  # 501 characters
    }

    response = await client.post(
        f"/api/{test_user_id}/tasks",
        json=task_data,
        headers=headers
    )

    assert response.status_code == 422


@pytest.mark.asyncio
async def test_create_for_other_user_403(
    client: AsyncClient,
    test_user_id_2: str,
    mock_jwt_token: str
):
    """
    Test: User cannot create tasks for another user (403 Forbidden).
    """
    headers = {"Authorization": f"Bearer {mock_jwt_token}"}
    task_data = {
        "title": "Task for another user"
    }

    response = await client.post(
        f"/api/{test_user_id_2}/tasks",
        json=task_data,
        headers=headers
    )

    assert response.status_code == 403


@pytest.mark.asyncio
async def test_create_no_auth_401(
    client: AsyncClient,
    test_user_id: str
):
    """
    Test: Creating task without authentication returns 401.
    """
    task_data = {
        "title": "Unauthenticated task"
    }

    response = await client.post(
        f"/api/{test_user_id}/tasks",
        json=task_data
    )

    assert response.status_code == 401
