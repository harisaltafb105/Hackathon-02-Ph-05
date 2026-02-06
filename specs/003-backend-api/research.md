# Research Findings: Backend API with Authentication

**Feature**: 003-backend-api
**Date**: 2026-01-07
**Phase**: Phase 0 - Research

## Overview

This document consolidates research findings for implementing a FastAPI backend with SQLModel, async PostgreSQL, and JWT authentication. All research tasks defined in plan.md have been completed with decisions, rationales, and implementation guidance.

---

## 1. FastAPI Project Structure Best Practices

### Decision: Router-based structure with dependency injection

**Findings**:
- **Application Instantiation**: Direct app instantiation is recommended for simple APIs. Factory pattern is overkill unless multiple app configurations are needed (e.g., testing vs production).
- **Router Organization**: Use `APIRouter` from `fastapi` to group related endpoints. For this project, a single `tasks.py` router is sufficient.
- **Dependency Injection**: FastAPI's `Depends()` is the idiomatic pattern for database sessions and authentication.
- **Middleware Ordering**:
  1. CORS middleware (first)
  2. Custom error handlers
  3. Route handlers with dependencies
- **Lifecycle Events**: Use `@app.on_event("startup")` and `@app.on_event("shutdown")` for database connection management.

**Implementation Pattern**:
```python
# main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routers import tasks
from .database import create_db_and_tables

app = FastAPI(title="Todo API", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3001"],  # Next.js dev server
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE"],
    allow_headers=["Authorization", "Content-Type"],
)

# Lifecycle events
@app.on_event("startup")
async def on_startup():
    await create_db_and_tables()

# Include routers
app.include_router(tasks.router, prefix="/api", tags=["tasks"])
```

**Rationale**: Direct app instantiation is simpler, router-based organization scales well, dependency injection is testable and explicit.

---

## 2. SQLModel with Async PostgreSQL

### Decision: AsyncEngine with asyncpg driver and async session factory

**Findings**:
- **Async Engine**: Use `create_async_engine` from SQLAlchemy with `postgresql+asyncpg://` connection string.
- **Session Factory**: Use `async_sessionmaker` with `expire_on_commit=False` for async context managers.
- **Connection Pooling**: Configure `pool_size=5`, `max_overflow=10`, `pool_pre_ping=True` for Neon serverless.
- **UUID Generation**: Use `uuid.uuid4()` as default factory in SQLModel field definition.
- **Auto-Update Timestamps**: Use `sa_column_kwargs={"onupdate": func.now()}` for `updated_at` field.
- **Async Session Dependency**: Yield session from async generator function.

**Implementation Pattern**:
```python
# database.py
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlmodel import SQLModel
from .config import settings

# Create async engine
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=True,  # Log SQL queries in development
    pool_size=5,
    max_overflow=10,
    pool_pre_ping=True,  # Verify connections before using
)

# Create session factory
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)

# Database session dependency
async def get_session() -> AsyncSession:
    async with AsyncSessionLocal() as session:
        yield session

# Create tables on startup
async def create_db_and_tables():
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)

# models.py
from sqlmodel import Field, SQLModel
from sqlalchemy import Column, DateTime, func
from datetime import datetime
from uuid import UUID, uuid4

class Task(SQLModel, table=True):
    __tablename__ = "tasks"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    title: str = Field(max_length=500, nullable=False)
    description: str | None = Field(default=None, max_length=5000)
    completed: bool = Field(default=False, nullable=False)
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column=Column(DateTime(timezone=True), nullable=False)
    )
    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column=Column(
            DateTime(timezone=True),
            nullable=False,
            onupdate=func.now()
        )
    )
    user_id: str = Field(nullable=False, index=True)
```

**Rationale**: asyncpg is the fastest async PostgreSQL driver, async session factory enables proper resource management, pool settings optimize for serverless database, UUID and timestamp defaults eliminate boilerplate.

---

## 3. PyJWT Verification with Better Auth

### Decision: HS256 verification with user_id extraction from `sub` claim

**Findings**:
- **Algorithm**: Better Auth typically uses HS256 (shared secret) for JWTs.
- **User ID Claim**: Standard JWT practice uses `sub` (subject) claim for user identifier. Fallback to `userId` if needed.
- **Expiry Validation**: PyJWT automatically validates `exp` claim when `verify_exp=True` (default).
- **Error Handling**:
  - `jwt.ExpiredSignatureError` → 401 "Token expired"
  - `jwt.InvalidTokenError` → 401 "Invalid token"
  - Missing token → 401 "Authentication required"
- **Dependency Pattern**: Create `get_current_user` dependency that returns user_id from verified token.

**Implementation Pattern**:
```python
# auth.py
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthCredentials
import jwt
from .config import settings

security = HTTPBearer()

async def get_current_user(credentials: HTTPAuthCredentials = Depends(security)) -> str:
    """
    Verify JWT token and extract user_id.

    Returns:
        user_id (str): User ID from token claims

    Raises:
        HTTPException 401: Invalid or expired token
    """
    token = credentials.credentials

    try:
        # Verify and decode token
        payload = jwt.decode(
            token,
            settings.BETTER_AUTH_SECRET,
            algorithms=["HS256"],
            options={"verify_exp": True}
        )

        # Extract user_id from sub claim (fallback to userId)
        user_id = payload.get("sub") or payload.get("userId")

        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User ID not found in token"
            )

        return user_id

    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token expired"
        )
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )

async def verify_user_access(
    user_id_path: str,
    current_user_id: str = Depends(get_current_user)
) -> str:
    """
    Verify that path user_id matches authenticated user_id.

    Args:
        user_id_path: User ID from URL path
        current_user_id: User ID from JWT token

    Returns:
        current_user_id (str): Verified user ID

    Raises:
        HTTPException 403: User ID mismatch
    """
    if user_id_path != current_user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot access other users' resources"
        )
    return current_user_id
```

**Rationale**: HS256 is standard for shared secret authentication, `sub` claim follows JWT standards, dependency injection makes auth testable and reusable, separate user_id verification enables defense-in-depth.

---

## 4. CORS Configuration for Next.js Frontend

### Decision: CORSMiddleware with explicit origins and credentials support

**Findings**:
- **Allowed Origins**: Development (`http://localhost:3001`), production (environment variable).
- **Allowed Methods**: All REST methods (GET, POST, PUT, PATCH, DELETE, OPTIONS).
- **Allowed Headers**: `Authorization`, `Content-Type` (minimum required).
- **Credentials**: Set `allow_credentials=True` if using cookies (not needed for Bearer tokens, but harmless).
- **Preflight Caching**: Browser handles OPTIONS preflight automatically.

**Implementation Pattern**:
```python
# main.py (CORS configuration)
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3001",  # Next.js dev server
        "http://localhost:3000",  # Alternative frontend port
        # Production origin from environment variable
        settings.FRONTEND_URL if hasattr(settings, 'FRONTEND_URL') else None
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type", "Accept"],
)
```

**Rationale**: Explicit origins prevent CSRF attacks, explicit methods follow principle of least privilege, explicit headers minimize attack surface.

---

## 5. Environment Variable Management with uv

### Decision: Pydantic Settings with python-dotenv for typed configuration

**Findings**:
- **Loading Strategy**: Use `python-dotenv` to load `.env` file, then Pydantic Settings for validation.
- **Validation**: Pydantic Settings validates types and required fields on application startup.
- **Fail Fast**: Application raises `ValidationError` if required variables missing.
- **File Location**: `.env` file in project root, loaded automatically by `python-dotenv`.
- **uv Compatibility**: `uv run` passes through environment variables without modification.

**Implementation Pattern**:
```python
# config.py
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field, validator

class Settings(BaseSettings):
    """Application configuration loaded from environment variables."""

    # Better Auth
    BETTER_AUTH_URL: str = Field(
        ...,  # Required field
        description="Better Auth service URL"
    )
    BETTER_AUTH_SECRET: str = Field(
        ...,
        description="Shared secret for JWT verification"
    )

    # Database
    DATABASE_URL: str = Field(
        ...,
        description="PostgreSQL connection string (postgresql+asyncpg://...)"
    )

    # Optional: Frontend URL for CORS
    FRONTEND_URL: str | None = Field(
        default=None,
        description="Production frontend URL for CORS"
    )

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore"  # Ignore extra environment variables
    )

    @validator("DATABASE_URL")
    def validate_database_url(cls, v):
        """Ensure asyncpg driver is specified."""
        if not v.startswith("postgresql+asyncpg://"):
            raise ValueError(
                "DATABASE_URL must use asyncpg driver: postgresql+asyncpg://..."
            )
        return v

# Create global settings instance
settings = Settings()
```

**`.env.example`**:
```env
# Better Auth Configuration
BETTER_AUTH_URL=http://localhost:3001/api/auth
BETTER_AUTH_SECRET=your-secret-key-here

# Database Configuration
DATABASE_URL=postgresql+asyncpg://user:password@host:5432/database

# Optional: Production Frontend URL
FRONTEND_URL=https://your-app.com
```

**Rationale**: Pydantic Settings provides type safety and validation, python-dotenv enables local development, fail-fast prevents runtime errors from misconfiguration.

---

## 6. Error Response Standardization

### Decision: Custom exception handlers with error + detail format

**Findings**:
- **Default FastAPI Format**: Uses `detail` field only (doesn't match FR-013).
- **Custom Handler**: Override HTTPException handler to add `error` field.
- **Validation Errors**: Override RequestValidationError handler for 422 responses.
- **Database Errors**: Catch asyncpg exceptions and return 503 with custom format.
- **Status Code Mapping**:
  - 400: Bad Request (malformed JSON)
  - 401: Unauthorized (auth failure)
  - 403: Forbidden (authorization failure)
  - 404: Not Found (resource doesn't exist)
  - 422: Unprocessable Entity (validation failure)
  - 500: Internal Server Error (unexpected errors)
  - 503: Service Unavailable (database unavailable)

**Implementation Pattern**:
```python
# main.py (error handlers)
from fastapi import FastAPI, HTTPException, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import ValidationError
import asyncpg

app = FastAPI()

# Custom error response schema
def error_response(error: str, detail: str) -> dict:
    """Standard error response format per FR-013."""
    return {"error": error, "detail": detail}

# HTTPException handler (401, 403, 404, etc.)
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Handle HTTP exceptions with custom error format."""
    error_map = {
        400: "Bad Request",
        401: "Unauthorized",
        403: "Forbidden",
        404: "Not Found",
        422: "Validation Error",
        500: "Internal Server Error",
        503: "Service Unavailable",
    }
    return JSONResponse(
        status_code=exc.status_code,
        content=error_response(
            error=error_map.get(exc.status_code, "Error"),
            detail=exc.detail
        )
    )

# Validation error handler (422)
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle Pydantic validation errors."""
    # Format validation errors into readable messages
    errors = []
    for error in exc.errors():
        field = ".".join(str(loc) for loc in error["loc"])
        message = error["msg"]
        errors.append(f"{field}: {message}")

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=error_response(
            error="Validation Error",
            detail="; ".join(errors)
        )
    )

# Database error handler (503)
@app.exception_handler(asyncpg.PostgresError)
async def database_exception_handler(request: Request, exc: asyncpg.PostgresError):
    """Handle database connection errors."""
    # Log the actual error for debugging (don't expose to client)
    import logging
    logging.error(f"Database error: {exc}")

    return JSONResponse(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        content=error_response(
            error="Service Unavailable",
            detail="Database temporarily unavailable"
        )
    )

# Catch-all for unexpected errors (500)
@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle unexpected errors without exposing stack traces."""
    import logging
    logging.error(f"Unexpected error: {exc}", exc_info=True)

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=error_response(
            error="Internal Server Error",
            detail="An unexpected error occurred"
        )
    )
```

**Rationale**: Custom handlers ensure consistent `error` + `detail` format per FR-013, validation errors are user-friendly, database errors don't expose internals, catch-all prevents stack trace leakage.

---

## Summary of Decisions

| Research Task | Decision | Key Technology/Pattern |
|---------------|----------|------------------------|
| 1. FastAPI Structure | Router-based with dependency injection | `APIRouter`, `Depends()`, lifecycle events |
| 2. SQLModel + PostgreSQL | Async engine with asyncpg driver | `create_async_engine`, `async_sessionmaker`, UUID defaults |
| 3. JWT Verification | HS256 with user_id from `sub` claim | `PyJWT`, `get_current_user` dependency |
| 4. CORS Configuration | Explicit origins with credentials support | `CORSMiddleware`, localhost + production origins |
| 5. Environment Variables | Pydantic Settings with python-dotenv | `BaseSettings`, fail-fast validation |
| 6. Error Responses | Custom handlers with error + detail format | Exception handlers, `error_response()` helper |

**All research tasks completed. Ready to proceed to Phase 1 (Data Model & Contracts).**
