"""
Pytest fixtures for testing.
Provides test database, session, and authentication tokens.
"""

import pytest
import jwt
from datetime import datetime, timedelta
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlmodel import SQLModel
from httpx import AsyncClient, ASGITransport
from backend.config import settings
from backend.database import get_session
from backend.main import app


# Test database URL (in-memory SQLite for testing)
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"


@pytest.fixture(scope="function")
async def test_engine():
    """
    Create a test database engine.
    Uses in-memory SQLite for fast, isolated tests.
    """
    engine = create_async_engine(
        TEST_DATABASE_URL,
        echo=False,
        connect_args={"check_same_thread": False}
    )

    # Create all tables
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)

    yield engine

    # Drop all tables after test
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.drop_all)

    await engine.dispose()


@pytest.fixture(scope="function")
async def test_session(test_engine) -> AsyncGenerator[AsyncSession, None]:
    """
    Create a test database session.
    """
    async_session_maker = async_sessionmaker(
        test_engine,
        class_=AsyncSession,
        expire_on_commit=False
    )

    async with async_session_maker() as session:
        yield session


@pytest.fixture(scope="function")
async def client(test_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    """
    Create a test client with overridden database dependency.
    """
    async def override_get_session():
        yield test_session

    app.dependency_overrides[get_session] = override_get_session

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

    app.dependency_overrides.clear()


@pytest.fixture
def test_user_id() -> str:
    """
    Test user ID for authentication tests.
    """
    return "test-user-123"


@pytest.fixture
def test_user_id_2() -> str:
    """
    Second test user ID for user isolation tests.
    """
    return "test-user-456"


@pytest.fixture
def mock_jwt_token(test_user_id: str) -> str:
    """
    Create a valid JWT token for testing.

    Args:
        test_user_id: The user ID to encode in the token

    Returns:
        A valid JWT token string
    """
    payload = {
        "sub": test_user_id,
        "userId": test_user_id,
        "exp": datetime.utcnow() + timedelta(hours=1)
    }

    token = jwt.encode(payload, settings.better_auth_secret, algorithm="HS256")
    return token


@pytest.fixture
def mock_jwt_token_user2(test_user_id_2: str) -> str:
    """
    Create a valid JWT token for second test user.
    """
    payload = {
        "sub": test_user_id_2,
        "userId": test_user_id_2,
        "exp": datetime.utcnow() + timedelta(hours=1)
    }

    token = jwt.encode(payload, settings.better_auth_secret, algorithm="HS256")
    return token


@pytest.fixture
def expired_jwt_token(test_user_id: str) -> str:
    """
    Create an expired JWT token for testing.
    """
    payload = {
        "sub": test_user_id,
        "userId": test_user_id,
        "exp": datetime.utcnow() - timedelta(hours=1)  # Expired 1 hour ago
    }

    token = jwt.encode(payload, settings.better_auth_secret, algorithm="HS256")
    return token


@pytest.fixture
def invalid_jwt_token() -> str:
    """
    Create an invalid JWT token (wrong signature).
    """
    payload = {
        "sub": "test-user-123",
        "exp": datetime.utcnow() + timedelta(hours=1)
    }

    # Use wrong secret to create invalid signature
    token = jwt.encode(payload, "wrong-secret", algorithm="HS256")
    return token
