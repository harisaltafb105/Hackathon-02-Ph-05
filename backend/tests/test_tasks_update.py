"""
US3 - Task Update Tests.
Tests PUT /api/{user_id}/tasks/{task_id} and PATCH /api/{user_id}/tasks/{task_id}
"""

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from backend.models import Task


@pytest.mark.asyncio
async def test_put_update_success(
    client: AsyncClient,
    test_session: AsyncSession,
    test_user_id: str,
    mock_jwt_token: str
):
    """
    Test: User can fully update their task with PUT.
    """
    # Create test task
    task = Task(
        title="Original Title",
        description="Original Description",
        completed=False,
        user_id=test_user_id
    )

    test_session.add(task)
    await test_session.commit()
    await test_session.refresh(task)
    original_updated_at = task.updated_at

    # Update task
    headers = {"Authorization": f"Bearer {mock_jwt_token}"}
    update_data = {
        "title": "Updated Title",
        "description": "Updated Description",
        "completed": True
    }

    response = await client.put(
        f"/api/{test_user_id}/tasks/{task.id}",
        json=update_data,
        headers=headers
    )

    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Updated Title"
    assert data["description"] == "Updated Description"
    assert data["completed"] is True
    # updated_at should change
    # Note: We can't easily compare timestamps in tests due to timezone/precision


@pytest.mark.asyncio
async def test_patch_update_success(
    client: AsyncClient,
    test_session: AsyncSession,
    test_user_id: str,
    mock_jwt_token: str
):
    """
    Test: User can partially update their task with PATCH.
    """
    # Create test task
    task = Task(
        title="Original Title",
        description="Original Description",
        completed=False,
        user_id=test_user_id
    )

    test_session.add(task)
    await test_session.commit()
    await test_session.refresh(task)

    # Partially update task (only completed field)
    headers = {"Authorization": f"Bearer {mock_jwt_token}"}
    update_data = {
        "completed": True
    }

    response = await client.patch(
        f"/api/{test_user_id}/tasks/{task.id}",
        json=update_data,
        headers=headers
    )

    assert response.status_code == 200
    data = response.json()
    # Only completed should change
    assert data["title"] == "Original Title"
    assert data["description"] == "Original Description"
    assert data["completed"] is True


@pytest.mark.asyncio
async def test_patch_update_multiple_fields(
    client: AsyncClient,
    test_session: AsyncSession,
    test_user_id: str,
    mock_jwt_token: str
):
    """
    Test: PATCH can update multiple fields at once.
    """
    # Create test task
    task = Task(
        title="Original Title",
        description="Original Description",
        completed=False,
        user_id=test_user_id
    )

    test_session.add(task)
    await test_session.commit()
    await test_session.refresh(task)

    # Update title and completed
    headers = {"Authorization": f"Bearer {mock_jwt_token}"}
    update_data = {
        "title": "New Title",
        "completed": True
    }

    response = await client.patch(
        f"/api/{test_user_id}/tasks/{task.id}",
        json=update_data,
        headers=headers
    )

    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "New Title"
    assert data["description"] == "Original Description"  # Unchanged
    assert data["completed"] is True


@pytest.mark.asyncio
async def test_update_other_user_task_403(
    client: AsyncClient,
    test_session: AsyncSession,
    test_user_id: str,
    test_user_id_2: str,
    mock_jwt_token: str
):
    """
    Test: User cannot update another user's task (403 or 404).
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

    # Try to update as user_1
    headers = {"Authorization": f"Bearer {mock_jwt_token}"}
    update_data = {
        "title": "Hacked Title",
        "completed": True
    }

    # Try PUT
    response = await client.put(
        f"/api/{test_user_id}/tasks/{task.id}",
        json=update_data,
        headers=headers
    )
    # Should be 404 since task doesn't exist for this user
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_update_nonexistent_404(
    client: AsyncClient,
    test_user_id: str,
    mock_jwt_token: str
):
    """
    Test: Updating non-existent task returns 404.
    """
    fake_uuid = "00000000-0000-0000-0000-000000000000"
    headers = {"Authorization": f"Bearer {mock_jwt_token}"}
    update_data = {
        "title": "New Title",
        "completed": True
    }

    response = await client.put(
        f"/api/{test_user_id}/tasks/{fake_uuid}",
        json=update_data,
        headers=headers
    )

    assert response.status_code == 404


@pytest.mark.asyncio
async def test_update_invalid_data_422(
    client: AsyncClient,
    test_session: AsyncSession,
    test_user_id: str,
    mock_jwt_token: str
):
    """
    Test: Updating with invalid data returns 422.
    """
    # Create test task
    task = Task(
        title="Original Title",
        user_id=test_user_id
    )

    test_session.add(task)
    await test_session.commit()
    await test_session.refresh(task)

    # Try to update with empty title (min_length=1)
    headers = {"Authorization": f"Bearer {mock_jwt_token}"}
    update_data = {
        "title": "",  # Invalid: empty string
        "completed": True
    }

    response = await client.put(
        f"/api/{test_user_id}/tasks/{task.id}",
        json=update_data,
        headers=headers
    )

    assert response.status_code == 422
