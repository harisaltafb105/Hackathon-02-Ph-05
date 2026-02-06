"""
Comprehensive User Isolation Tests.
Verifies that users cannot access, modify, or delete other users' tasks.
"""

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from backend.models import Task


@pytest.mark.asyncio
async def test_user1_cannot_list_user2_tasks(
    client: AsyncClient,
    test_session: AsyncSession,
    test_user_id: str,
    test_user_id_2: str,
    mock_jwt_token: str
):
    """
    Test: User 1 cannot list User 2's tasks.
    """
    # Create tasks for both users
    task_user1 = Task(title="User 1 Task", user_id=test_user_id)
    task_user2_1 = Task(title="User 2 Task 1", user_id=test_user_id_2)
    task_user2_2 = Task(title="User 2 Task 2", user_id=test_user_id_2)

    test_session.add_all([task_user1, task_user2_1, task_user2_2])
    await test_session.commit()

    # User 1 tries to list User 2's tasks
    headers = {"Authorization": f"Bearer {mock_jwt_token}"}
    response = await client.get(f"/api/{test_user_id_2}/tasks", headers=headers)

    # Should return 403 Forbidden
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_user_only_sees_own_tasks(
    client: AsyncClient,
    test_session: AsyncSession,
    test_user_id: str,
    test_user_id_2: str,
    mock_jwt_token: str
):
    """
    Test: User only sees their own tasks in list, never other users' tasks.
    """
    # Create tasks for both users
    task_user1_1 = Task(title="User 1 Task 1", user_id=test_user_id)
    task_user1_2 = Task(title="User 1 Task 2", user_id=test_user_id)
    task_user2_1 = Task(title="User 2 Task 1", user_id=test_user_id_2)
    task_user2_2 = Task(title="User 2 Task 2", user_id=test_user_id_2)

    test_session.add_all([task_user1_1, task_user1_2, task_user2_1, task_user2_2])
    await test_session.commit()

    # User 1 lists their tasks
    headers = {"Authorization": f"Bearer {mock_jwt_token}"}
    response = await client.get(f"/api/{test_user_id}/tasks", headers=headers)

    assert response.status_code == 200
    data = response.json()

    # Should only see 2 tasks (their own)
    assert len(data) == 2

    # All tasks should belong to user 1
    assert all(task["user_id"] == test_user_id for task in data)

    # None should belong to user 2
    assert not any(task["user_id"] == test_user_id_2 for task in data)


@pytest.mark.asyncio
async def test_user1_cannot_get_user2_task_by_id(
    client: AsyncClient,
    test_session: AsyncSession,
    test_user_id: str,
    test_user_id_2: str,
    mock_jwt_token: str
):
    """
    Test: User 1 cannot retrieve User 2's task by ID.
    """
    # Create task for user 2
    task_user2 = Task(
        title="User 2 Private Task",
        description="Should not be accessible to User 1",
        user_id=test_user_id_2
    )

    test_session.add(task_user2)
    await test_session.commit()
    await test_session.refresh(task_user2)

    # User 1 tries to get User 2's task
    headers = {"Authorization": f"Bearer {mock_jwt_token}"}
    response = await client.get(
        f"/api/{test_user_id}/tasks/{task_user2.id}",
        headers=headers
    )

    # Should return 404 (task not found for this user)
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_user1_cannot_update_user2_task(
    client: AsyncClient,
    test_session: AsyncSession,
    test_user_id: str,
    test_user_id_2: str,
    mock_jwt_token: str
):
    """
    Test: User 1 cannot update User 2's task.
    """
    # Create task for user 2
    task_user2 = Task(
        title="User 2 Task",
        description="Original description",
        completed=False,
        user_id=test_user_id_2
    )

    test_session.add(task_user2)
    await test_session.commit()
    await test_session.refresh(task_user2)

    # User 1 tries to update User 2's task
    headers = {"Authorization": f"Bearer {mock_jwt_token}"}
    update_data = {
        "title": "Hacked Title",
        "description": "Hacked description",
        "completed": True
    }

    response = await client.put(
        f"/api/{test_user_id}/tasks/{task_user2.id}",
        json=update_data,
        headers=headers
    )

    # Should return 404
    assert response.status_code == 404

    # Verify task was not modified
    await test_session.refresh(task_user2)
    assert task_user2.title == "User 2 Task"
    assert task_user2.description == "Original description"
    assert task_user2.completed is False


@pytest.mark.asyncio
async def test_user1_cannot_delete_user2_task(
    client: AsyncClient,
    test_session: AsyncSession,
    test_user_id: str,
    test_user_id_2: str,
    mock_jwt_token: str
):
    """
    Test: User 1 cannot delete User 2's task.
    """
    # Create task for user 2
    task_user2 = Task(
        title="User 2 Task to Protect",
        user_id=test_user_id_2
    )

    test_session.add(task_user2)
    await test_session.commit()
    await test_session.refresh(task_user2)
    task_id = task_user2.id

    # User 1 tries to delete User 2's task
    headers = {"Authorization": f"Bearer {mock_jwt_token}"}
    response = await client.delete(
        f"/api/{test_user_id}/tasks/{task_id}",
        headers=headers
    )

    # Should return 404
    assert response.status_code == 404

    # Verify task still exists
    await test_session.refresh(task_user2)
    assert task_user2.id == task_id


@pytest.mark.asyncio
async def test_user1_cannot_create_task_for_user2(
    client: AsyncClient,
    test_user_id: str,
    test_user_id_2: str,
    mock_jwt_token: str
):
    """
    Test: User 1 cannot create a task for User 2.
    """
    headers = {"Authorization": f"Bearer {mock_jwt_token}"}
    task_data = {
        "title": "Task for User 2",
        "description": "Trying to create for another user"
    }

    # User 1 tries to create task at User 2's endpoint
    response = await client.post(
        f"/api/{test_user_id_2}/tasks",
        json=task_data,
        headers=headers
    )

    # Should return 403 Forbidden
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_complete_isolation_workflow(
    client: AsyncClient,
    test_session: AsyncSession,
    test_user_id: str,
    test_user_id_2: str,
    mock_jwt_token: str,
    mock_jwt_token_user2: str
):
    """
    Test: Complete workflow showing both users can work independently.
    """
    # User 1 creates a task
    headers_user1 = {"Authorization": f"Bearer {mock_jwt_token}"}
    task_data_user1 = {"title": "User 1 Task", "description": "Private to User 1"}

    response = await client.post(
        f"/api/{test_user_id}/tasks",
        json=task_data_user1,
        headers=headers_user1
    )
    assert response.status_code == 201
    task_user1 = response.json()

    # User 2 creates a task
    headers_user2 = {"Authorization": f"Bearer {mock_jwt_token_user2}"}
    task_data_user2 = {"title": "User 2 Task", "description": "Private to User 2"}

    response = await client.post(
        f"/api/{test_user_id_2}/tasks",
        json=task_data_user2,
        headers=headers_user2
    )
    assert response.status_code == 201
    task_user2 = response.json()

    # User 1 lists tasks - should only see their own
    response = await client.get(f"/api/{test_user_id}/tasks", headers=headers_user1)
    assert response.status_code == 200
    user1_tasks = response.json()
    assert len(user1_tasks) == 1
    assert user1_tasks[0]["id"] == task_user1["id"]

    # User 2 lists tasks - should only see their own
    response = await client.get(f"/api/{test_user_id_2}/tasks", headers=headers_user2)
    assert response.status_code == 200
    user2_tasks = response.json()
    assert len(user2_tasks) == 1
    assert user2_tasks[0]["id"] == task_user2["id"]

    # User 1 tries to access User 2's task - should fail
    response = await client.get(
        f"/api/{test_user_id}/tasks/{task_user2['id']}",
        headers=headers_user1
    )
    assert response.status_code == 404

    # User 2 tries to access User 1's task - should fail
    response = await client.get(
        f"/api/{test_user_id_2}/tasks/{task_user1['id']}",
        headers=headers_user2
    )
    assert response.status_code == 404
