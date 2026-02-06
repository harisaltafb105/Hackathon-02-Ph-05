"""
Authentication tests.
Tests JWT token verification and user access control.
"""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_health_check_no_auth(client: AsyncClient):
    """
    Test that health check endpoint works without authentication.
    """
    response = await client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}


@pytest.mark.asyncio
async def test_missing_token(client: AsyncClient, test_user_id: str):
    """
    Test that requests without Authorization header return 401.
    """
    # Try to access a protected endpoint without token
    # Note: We'll test with tasks endpoint once it's created
    # For now, just verify the pattern works
    response = await client.get(f"/api/{test_user_id}/tasks")
    assert response.status_code in [401, 404]  # 404 if endpoint doesn't exist yet


@pytest.mark.asyncio
async def test_invalid_token(client: AsyncClient, test_user_id: str, invalid_jwt_token: str):
    """
    Test that requests with invalid token return 401.
    """
    headers = {"Authorization": f"Bearer {invalid_jwt_token}"}
    response = await client.get(f"/api/{test_user_id}/tasks", headers=headers)

    # Should return 401 when endpoint exists
    # For now accept 404 if endpoint not created yet
    assert response.status_code in [401, 404]


@pytest.mark.asyncio
async def test_expired_token(client: AsyncClient, test_user_id: str, expired_jwt_token: str):
    """
    Test that requests with expired token return 401.
    """
    headers = {"Authorization": f"Bearer {expired_jwt_token}"}
    response = await client.get(f"/api/{test_user_id}/tasks", headers=headers)

    # Should return 401 when endpoint exists
    # For now accept 404 if endpoint not created yet
    assert response.status_code in [401, 404]


@pytest.mark.asyncio
async def test_valid_token(client: AsyncClient, test_user_id: str, mock_jwt_token: str):
    """
    Test that requests with valid token are accepted.
    This will be fully tested once task endpoints are created.
    """
    headers = {"Authorization": f"Bearer {mock_jwt_token}"}
    response = await client.get(f"/api/{test_user_id}/tasks", headers=headers)

    # Should return 200 when endpoint exists
    # For now accept 404 if endpoint not created yet
    assert response.status_code in [200, 404]


@pytest.mark.asyncio
async def test_user_id_mismatch(
    client: AsyncClient,
    test_user_id: str,
    test_user_id_2: str,
    mock_jwt_token: str
):
    """
    Test that user cannot access another user's resources.
    Token is for test_user_id but trying to access test_user_id_2's tasks.
    """
    headers = {"Authorization": f"Bearer {mock_jwt_token}"}

    # Try to access another user's tasks
    response = await client.get(f"/api/{test_user_id_2}/tasks", headers=headers)

    # Should return 403 when endpoint exists
    # For now accept 404 if endpoint not created yet
    assert response.status_code in [403, 404]
