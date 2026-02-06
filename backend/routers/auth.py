"""
Authentication router.
Provides JWT-based authentication endpoints for user registration and login.
"""

from datetime import datetime, timedelta
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import select
from sqlalchemy.ext.asyncio import AsyncSession
import bcrypt
import jwt

from backend.database import get_session
from backend.models import User
from backend.schemas import UserRegister, UserLogin, AuthResponse, UserResponse
from backend.config import settings


router = APIRouter(prefix="/auth", tags=["authentication"])


def hash_password(password: str) -> str:
    """
    Hash password using bcrypt.

    Args:
        password: Plain text password

    Returns:
        Hashed password string
    """
    salt = bcrypt.gensalt()
    password_bytes = password.encode('utf-8')
    hashed = bcrypt.hashpw(password_bytes, salt)
    return hashed.decode('utf-8')


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify password against bcrypt hash.

    Args:
        plain_password: Plain text password to check
        hashed_password: Stored bcrypt hash

    Returns:
        True if password matches, False otherwise
    """
    password_bytes = plain_password.encode('utf-8')
    hashed_bytes = hashed_password.encode('utf-8')
    return bcrypt.checkpw(password_bytes, hashed_bytes)


def create_jwt_token(user_id: str) -> str:
    """
    Create JWT token for authenticated user.

    Args:
        user_id: User's UUID as string

    Returns:
        JWT token string
    """
    # Token expires in 24 hours
    exp = datetime.utcnow() + timedelta(hours=24)

    payload = {
        "sub": user_id,  # Standard JWT claim for user ID
        "userId": user_id,  # Alternative claim for compatibility
        "iat": datetime.utcnow(),  # Issued at
        "exp": exp,  # Expiration time
    }

    token = jwt.encode(
        payload,
        settings.better_auth_secret,
        algorithm="HS256"
    )

    return token


@router.post("/register", response_model=AuthResponse, status_code=status.HTTP_201_CREATED)
async def register(
    user_data: UserRegister,
    session: Annotated[AsyncSession, Depends(get_session)]
):
    """
    Register a new user.

    Creates a new user account, hashes the password, and returns a JWT token.

    Args:
        user_data: User registration data (email, password, name)
        session: Database session dependency

    Returns:
        AuthResponse with user data and JWT token

    Raises:
        HTTPException 409: If email already exists
    """
    # Check if user already exists
    statement = select(User).where(User.email == user_data.email)
    result = await session.execute(statement)
    existing_user = result.scalar_one_or_none()

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already registered"
        )

    # Hash password
    password_hash = hash_password(user_data.password)

    # Create user
    new_user = User(
        email=user_data.email,
        password_hash=password_hash,
        name=user_data.name
    )

    session.add(new_user)
    await session.commit()
    await session.refresh(new_user)

    # Generate JWT token
    token = create_jwt_token(str(new_user.id))

    # Return user and token
    return AuthResponse(
        user=UserResponse.model_validate(new_user),
        token=token
    )


@router.post("/login", response_model=AuthResponse)
async def login(
    credentials: UserLogin,
    session: Annotated[AsyncSession, Depends(get_session)]
):
    """
    Login existing user.

    Validates credentials and returns a JWT token.

    Args:
        credentials: User login credentials (email, password)
        session: Database session dependency

    Returns:
        AuthResponse with user data and JWT token

    Raises:
        HTTPException 401: If credentials are invalid
    """
    # Find user by email
    statement = select(User).where(User.email == credentials.email)
    result = await session.execute(statement)
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )

    # Verify password
    if not verify_password(credentials.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )

    # Generate JWT token
    token = create_jwt_token(str(user.id))

    # Return user and token
    return AuthResponse(
        user=UserResponse.model_validate(user),
        token=token
    )
