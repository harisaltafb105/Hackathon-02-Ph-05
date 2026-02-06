"""
JWT authentication module.
Verifies Better Auth JWT tokens and enforces user isolation.
"""

from typing import Annotated
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt
from jwt.exceptions import ExpiredSignatureError, InvalidTokenError

from backend.config import settings


# HTTP Bearer security scheme
security = HTTPBearer()


async def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)]
) -> str:
    """
    Verify JWT token and extract user_id.

    This dependency should be used on all protected endpoints to ensure
    the request is authenticated.

    Args:
        credentials: Bearer token from Authorization header

    Returns:
        user_id: The authenticated user's ID from JWT claims

    Raises:
        HTTPException 401: If token is missing, invalid, or expired
    """
    token = credentials.credentials

    try:
        # Decode JWT token using Better Auth secret
        # algorithm="HS256" is the default for Better Auth
        payload = jwt.decode(
            token,
            settings.better_auth_secret,
            algorithms=["HS256"]
        )

        # Extract user_id from claims
        # Better Auth typically uses 'sub' claim, but also check 'userId'
        user_id = payload.get("sub") or payload.get("userId")

        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token: missing user identifier"
            )

        return str(user_id)

    except ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token"
        )
    except InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token"
        )
    except Exception as e:
        # Catch any other unexpected errors during token verification
        print(f"Token verification error: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token"
        )


async def verify_user_access(
    user_id_path: str,
    current_user_id: Annotated[str, Depends(get_current_user)]
) -> str:
    """
    Verify that the user_id in the URL path matches the authenticated user's ID.

    This enforces strict user isolation - users can only access their own resources.

    Args:
        user_id_path: The user_id from the URL path parameter
        current_user_id: The authenticated user's ID from JWT token

    Returns:
        current_user_id: The verified user ID

    Raises:
        HTTPException 403: If user_id in path doesn't match token user_id
    """
    if user_id_path != current_user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied: cannot access other users' resources"
        )

    return current_user_id
