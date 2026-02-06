# Implementation Plan: Backend API with Authentication

**Branch**: `003-backend-api` | **Date**: 2026-01-07 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/003-backend-api/spec.md`

## Summary

Implement a production-quality FastAPI backend with SQLModel ORM and Neon PostgreSQL database to serve the already-implemented Next.js frontend. The backend provides RESTful CRUD endpoints for task management with strict user isolation enforced through Better Auth JWT authentication. All endpoints verify JWT tokens, extract user_id from claims, and ensure users can only access their own data. The system reads configuration from environment variables (BETTER_AUTH_URL, BETTER_AUTH_SECRET, DATABASE_URL) and runs via `uv run backend.main:app --reload` for development. No frontend changes are required - the backend matches the existing API client interface.

## Technical Context

**Language/Version**: Python 3.13+
**Primary Dependencies**: FastAPI, SQLModel, PyJWT, asyncpg, python-dotenv, uvicorn
**Storage**: Neon Serverless PostgreSQL (via DATABASE_URL environment variable)
**Testing**: pytest with pytest-asyncio for async endpoint tests, httpx for API testing
**Target Platform**: Linux server (Docker container with Python 3.13-slim base)
**Project Type**: Web backend (API service)
**Performance Goals**: < 200ms p95 latency for simple CRUD operations, handle concurrent requests with async/await
**Constraints**: Stateless authentication (no session storage), strict user isolation (0% cross-user data leakage), matches existing frontend API client interface
**Scale/Scope**: Multi-tenant task management API with 5 core endpoints (list, create, get, update, delete tasks)

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### Principle I: Spec-Driven Development ✅ PASS
- [x] Feature spec exists at `specs/003-backend-api/spec.md`
- [x] Implementation follows /sp.specify → /sp.plan → /sp.tasks → /sp.implement workflow
- [x] All requirements documented in spec with acceptance criteria
- [x] Plan references spec as source of truth

### Principle II: Multi-Tenant User Isolation ✅ PASS
- [x] FR-003 requires strict user isolation - users can only access own tasks
- [x] FR-004 validates user_id in URL matches JWT token user_id
- [x] All endpoints extract user_id from verified JWT (FR-002)
- [x] Database queries filtered by user_id (Task model includes user_id FK)
- [x] 403 Forbidden returned when accessing other users' resources
- [x] Integration tests required for cross-user isolation (TC-003)

### Principle III: JWT Authentication Bridge ✅ PASS
- [x] Frontend uses Better Auth to generate JWT tokens (already implemented)
- [x] Backend verifies JWT using BETTER_AUTH_SECRET (FR-001)
- [x] Authorization header format: `Bearer <token>` (FR-001)
- [x] User ID extracted from JWT claims (FR-002)
- [x] Stateless authentication with embedded expiry (NFR-005)
- [x] 401 Unauthorized for invalid/missing tokens (FR-012)
- [x] BETTER_AUTH_SECRET environment variable required (FR-016)

### Principle IV: Monorepo with Clear Boundaries ✅ PASS
- [x] Backend code in `backend/` directory with own CLAUDE.md
- [x] Specs in `specs/003-backend-api/` define API contracts
- [x] Frontend in `frontend/` directory (already implemented)
- [x] No code sharing except via API contracts
- [x] Backend independently deployable via Docker

### Principle V: API-First Design ✅ PASS
- [x] RESTful endpoints defined in spec (FR-005 through FR-010)
- [x] Standard HTTP methods: GET, POST, PUT, PATCH, DELETE
- [x] User_id in path: `/api/{user_id}/tasks` (FR-005)
- [x] Request/response schemas defined (Task entity in spec)
- [x] HTTP status codes documented (FR-012)
- [x] FastAPI auto-generates OpenAPI documentation

### Principle VI: Database Schema Integrity ✅ PASS
- [x] SQLModel ORM for type-safe models (NFR-002)
- [x] Task model includes user_id foreign key (Task entity spec)
- [x] Database constraints: NOT NULL, UUID primary key
- [x] Timestamps managed automatically (FR-015)
- [x] Connection pooling configured (NFR-003)
- [x] Schema documented in spec (Key Entities section)

### Technology Stack Compliance ✅ PASS
- [x] FastAPI framework (per constitution backend requirements)
- [x] SQLModel ORM (per constitution)
- [x] Neon Serverless PostgreSQL (per constitution)
- [x] PyJWT for token verification (per constitution)
- [x] uv for dependency management (NFR-008)
- [x] Docker deployment ready (per constitution)

**Constitution Check Result**: ✅ ALL GATES PASSED - No violations, proceed to Phase 0

## Project Structure

### Documentation (this feature)

```text
specs/003-backend-api/
├── spec.md              # Feature specification (COMPLETE)
├── checklist.md         # Quality validation (COMPLETE)
├── plan.md              # This file (IN PROGRESS)
├── research.md          # Phase 0 output (PENDING)
├── data-model.md        # Phase 1 output (PENDING)
├── quickstart.md        # Phase 1 output (PENDING)
├── contracts/           # Phase 1 output (PENDING)
│   └── openapi.yaml     # API contract (auto-generated from FastAPI)
└── tasks.md             # Phase 2 output (/sp.tasks command - NOT created by /sp.plan)
```

### Source Code (repository root)

```text
backend/                           # New directory for FastAPI backend
├── __init__.py
├── main.py                        # FastAPI application entry point
├── models.py                      # SQLModel database models (Task, User reference)
├── schemas.py                     # Pydantic request/response schemas
├── database.py                    # Database connection and session management
├── auth.py                        # JWT verification dependency
├── config.py                      # Environment variable configuration
├── routers/
│   ├── __init__.py
│   └── tasks.py                   # Task CRUD endpoints
├── middleware/
│   ├── __init__.py
│   └── cors.py                    # CORS configuration
└── tests/
    ├── __init__.py
    ├── conftest.py                # pytest fixtures (test DB, auth tokens)
    ├── test_auth.py               # JWT verification tests
    ├── test_tasks_crud.py         # CRUD endpoint tests
    └── test_user_isolation.py     # Cross-user isolation tests

pyproject.toml                     # uv project configuration (dependencies)
.env.example                       # Example environment variables
docker-compose.yml                 # Local development (PostgreSQL + backend)
Dockerfile                         # Backend container definition
```

**Structure Decision**: Web application structure with backend directory containing FastAPI service. Frontend already exists in `frontend/` directory. Backend is independently deployable and matches existing monorepo structure defined in constitution Principle IV.

## Complexity Tracking

> **No violations - this section left empty per template instructions**

All constitutional principles are satisfied without requiring additional complexity or deviations.

---

## Phase 0: Outline & Research

### Research Tasks

#### 1. FastAPI Project Structure Best Practices
**Research Question**: What is the recommended FastAPI project structure for a multi-router API with authentication middleware?

**Findings Required**:
- Application factory pattern vs direct app instantiation
- Router organization (single vs multiple routers)
- Dependency injection patterns for database sessions and auth
- Middleware ordering (CORS, authentication, error handling)
- Startup/shutdown event handlers for database connections

#### 2. SQLModel with Async PostgreSQL
**Research Question**: How to configure SQLModel with asyncpg for Neon PostgreSQL serverless database?

**Findings Required**:
- Async engine configuration with asyncpg driver
- Session factory with async context manager
- Connection pooling settings for serverless database
- UUID primary key generation with SQLModel
- DateTime auto-update for `updated_at` field
- Proper async session dependency injection in FastAPI

#### 3. PyJWT Verification with Better Auth
**Research Question**: What is the correct PyJWT verification pattern for Better Auth tokens?

**Findings Required**:
- JWT decoding with HS256 algorithm (shared secret)
- Claim extraction (user_id location: `sub`, `userId`, or custom)
- Expiry validation (`exp` claim)
- Error handling (expired, invalid signature, malformed)
- FastAPI dependency pattern for auth injection
- HTTPException status codes for auth failures

#### 4. CORS Configuration for Next.js Frontend
**Research Question**: What CORS settings allow Next.js frontend (localhost:3001) to call FastAPI backend?

**Findings Required**:
- FastAPI CORSMiddleware configuration
- Allowed origins for development (localhost:3001) and production
- Allowed methods (GET, POST, PUT, PATCH, DELETE)
- Allowed headers (Authorization, Content-Type)
- Credentials support if needed

#### 5. Environment Variable Management with uv
**Research Question**: How to load environment variables in FastAPI when running via `uv run`?

**Findings Required**:
- python-dotenv integration
- Environment variable validation on startup (fail fast)
- Pydantic Settings pattern for typed configuration
- `.env` file location and loading precedence
- Required variables: BETTER_AUTH_URL, BETTER_AUTH_SECRET, DATABASE_URL

#### 6. Error Response Standardization
**Research Question**: What is the FastAPI best practice for consistent error response format?

**Findings Required**:
- Custom exception handlers for HTTPException
- Error response schema (error + detail fields per FR-013)
- Status code mapping (400, 401, 403, 404, 422, 500, 503)
- Validation error formatting (Pydantic validation failures)
- Database error handling (503 for connection failures)

**Output**: `research.md` with consolidated findings and decisions

---

## Phase 1: Design & Contracts

### Data Model Design (`data-model.md`)

#### Entity: Task

**Purpose**: Represents a user's todo item with title, description, completion status, and timestamps.

**Fields**:
- `id`: UUID (primary key, auto-generated on insert)
- `title`: String (required, max 500 chars, not null)
- `description`: String (optional, max 5000 chars, nullable)
- `completed`: Boolean (required, default False, not null)
- `created_at`: DateTime (auto-set on insert, not null)
- `updated_at`: DateTime (auto-set on insert and update, not null)
- `user_id`: String (foreign key, not null, indexed)

**Relationships**:
- `user_id` references User (managed by Better Auth, not stored in backend DB)

**Validation Rules** (from FR-011):
- Title: 1-500 characters
- Description: 0-5000 characters
- Completed: boolean only (not string/int)
- User_id: must match JWT token user_id

**Indexes** (from NFR-010):
- Primary index on `id` (UUID)
- Index on `user_id` for query performance
- Composite index on `(user_id, created_at)` for sorted listings

**State Transitions**:
- New task: `completed = False`, timestamps auto-set
- Update task: `updated_at` auto-updated
- Toggle completion: `completed` toggled, `updated_at` updated

#### Entity: User (Reference Only)

**Purpose**: Represents authenticated user (managed by Better Auth, not stored in backend database).

**Fields**:
- `id`: String (from JWT token `sub` or `userId` claim)

**Note**: No User table in backend database. User ID is extracted from JWT token and used as foreign key in Task table.

### API Contracts (`contracts/openapi.yaml`)

**Base URL**: `/api`

#### Endpoints

1. **GET /api/{user_id}/tasks**
   - **Description**: List all tasks for authenticated user
   - **Auth**: Required (JWT Bearer token)
   - **Path Params**: `user_id` (string, must match JWT user_id)
   - **Response 200**: Array of Task objects
   - **Response 401**: Unauthorized (missing/invalid token)
   - **Response 403**: Forbidden (user_id mismatch)

2. **POST /api/{user_id}/tasks**
   - **Description**: Create new task
   - **Auth**: Required (JWT Bearer token)
   - **Path Params**: `user_id` (string, must match JWT user_id)
   - **Request Body**: `{ title: string, description?: string }`
   - **Response 201**: Created Task object
   - **Response 400**: Bad Request (invalid JSON)
   - **Response 401**: Unauthorized
   - **Response 403**: Forbidden
   - **Response 422**: Validation Error (missing title, length exceeded)

3. **GET /api/{user_id}/tasks/{task_id}**
   - **Description**: Get specific task
   - **Auth**: Required (JWT Bearer token)
   - **Path Params**: `user_id`, `task_id` (UUID)
   - **Response 200**: Task object
   - **Response 401**: Unauthorized
   - **Response 403**: Forbidden (not owner)
   - **Response 404**: Not Found

4. **PUT /api/{user_id}/tasks/{task_id}**
   - **Description**: Update entire task
   - **Auth**: Required (JWT Bearer token)
   - **Path Params**: `user_id`, `task_id` (UUID)
   - **Request Body**: `{ title: string, description?: string, completed: boolean }`
   - **Response 200**: Updated Task object
   - **Response 401**: Unauthorized
   - **Response 403**: Forbidden
   - **Response 404**: Not Found
   - **Response 422**: Validation Error

5. **PATCH /api/{user_id}/tasks/{task_id}**
   - **Description**: Partial task update
   - **Auth**: Required (JWT Bearer token)
   - **Path Params**: `user_id`, `task_id` (UUID)
   - **Request Body**: `{ title?: string, description?: string, completed?: boolean }`
   - **Response 200**: Updated Task object
   - **Response 401**: Unauthorized
   - **Response 403**: Forbidden
   - **Response 404**: Not Found
   - **Response 422**: Validation Error

6. **DELETE /api/{user_id}/tasks/{task_id}**
   - **Description**: Delete task
   - **Auth**: Required (JWT Bearer token)
   - **Path Params**: `user_id`, `task_id` (UUID)
   - **Response 204**: No Content (success)
   - **Response 401**: Unauthorized
   - **Response 403**: Forbidden
   - **Response 404**: Not Found

**Error Response Format** (FR-013):
```json
{
  "error": "Error category",
  "detail": "Specific error message"
}
```

### Quickstart Guide (`quickstart.md`)

**Prerequisites**:
- Python 3.13+
- uv installed (`pip install uv`)
- Neon PostgreSQL database created
- Better Auth configured in frontend

**Environment Setup**:
1. Copy `.env.example` to `.env`
2. Fill in required variables:
   ```
   BETTER_AUTH_URL=<frontend-better-auth-url>
   BETTER_AUTH_SECRET=<shared-secret-with-frontend>
   DATABASE_URL=postgresql+asyncpg://user:pass@host/db
   ```

**Development**:
```bash
# Install dependencies
cd backend
uv sync

# Run development server
uv run uvicorn main:app --reload

# Run tests
uv run pytest
```

**Docker Compose** (local development):
```bash
docker-compose up
```

**API Documentation**:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

**Testing Authentication**:
1. Login via frontend (http://localhost:3001/login)
2. Copy JWT token from browser DevTools (localStorage)
3. Use token in API requests:
   ```bash
   curl -H "Authorization: Bearer <token>" http://localhost:8000/api/{user_id}/tasks
   ```

### Agent Context Update

After Phase 1 design completion, run:
```bash
.specify/scripts/powershell/update-agent-context.ps1 -AgentType claude
```

This updates `.claude/` configuration with backend technology stack:
- FastAPI framework
- SQLModel ORM
- PyJWT authentication
- asyncpg PostgreSQL driver
- pytest testing

---

## Phase 2: Implementation Tasks

**Note**: Task breakdown is generated by `/sp.tasks` command, NOT `/sp.plan`. This section is intentionally left empty.

Tasks will be created in `specs/003-backend-api/tasks.md` after this plan is approved.

---

## Architecture Decisions

### Decision 1: Async PostgreSQL with SQLModel + asyncpg

**Context**: Need type-safe ORM with async support for Neon PostgreSQL serverless database.

**Options Considered**:
1. SQLModel with asyncpg (async engine)
2. SQLAlchemy 2.0 with async support
3. Tortoise ORM (fully async)

**Decision**: SQLModel with asyncpg

**Rationale**:
- Combines SQLAlchemy ORM with Pydantic validation (single source of truth for schemas)
- Type-safe models eliminate runtime errors
- Async support via asyncpg driver for optimal performance
- FastAPI integration via Pydantic models
- Smaller learning curve than raw SQLAlchemy 2.0
- Preferred by constitution (Principle VI)

**Trade-offs**:
- Slightly less mature than pure SQLAlchemy
- Async session management requires careful handling

### Decision 2: Dependency Injection for Auth

**Context**: Need to verify JWT on every endpoint without code duplication.

**Options Considered**:
1. Middleware (verify all requests)
2. Dependency injection (verify per endpoint)
3. Decorator pattern

**Decision**: Dependency injection with FastAPI `Depends()`

**Rationale**:
- FastAPI idiomatic pattern
- Explicit authentication requirement per endpoint
- Automatic 401 error handling
- Testable (mock dependencies in tests)
- Flexible (can have public endpoints if needed)

**Trade-offs**:
- Requires adding `user_id: str = Depends(get_current_user)` to every protected endpoint
- More verbose than middleware

### Decision 3: User ID Validation Strategy

**Context**: Must prevent user from accessing other users' resources via URL manipulation.

**Options Considered**:
1. Validate `user_id` in URL matches JWT claim (fail with 403)
2. Ignore URL `user_id` and use JWT claim only
3. Remove `user_id` from URL entirely

**Decision**: Validate URL `user_id` matches JWT claim (Option 1)

**Rationale**:
- Matches existing frontend API client expectations (FR-018)
- Explicit user context in URL aids debugging and logging
- Defense in depth (URL + token validation)
- Clear 403 Forbidden response when mismatch occurs
- Required by FR-004

**Trade-offs**:
- Additional validation code in each endpoint
- URL `user_id` is technically redundant (JWT already has it)

### Decision 4: Error Response Standardization

**Context**: Need consistent error format across all endpoints.

**Options Considered**:
1. FastAPI default error format
2. Custom error handler with `error` + `detail` fields (FR-013)
3. RFC 7807 Problem Details format

**Decision**: Custom error handler with `error` + `detail` fields

**Rationale**:
- Matches spec requirement (FR-013)
- Simple format easy for frontend to parse
- Consistent with existing frontend error handling
- Less complex than RFC 7807

**Trade-offs**:
- Not a standard format (but matches spec requirement)

---

## Success Criteria Validation

From spec.md Success Criteria section:

- [x] **SC-001**: Plan defines all CRUD endpoints (GET, POST, PUT, PATCH, DELETE)
- [x] **SC-002**: JWT authentication strategy documented (PyJWT verification dependency)
- [x] **SC-003**: User isolation enforced (URL validation + database filtering)
- [x] **SC-004**: HTTP status codes documented in API contracts
- [x] **SC-005**: Backend matches frontend API client (no breaking changes)
- [x] **SC-006**: Development workflow defined (`uv run` command)
- [x] **SC-007**: Performance goal set (< 200ms async operations)
- [x] **SC-008**: Error handling strategy defined (custom handlers, no stack traces)
- [x] **SC-009**: Database schema defined (Task entity with proper types)
- [x] **SC-010**: Error recovery strategy (503 for DB failures, reconnection)

**Plan Status**: ✅ All success criteria addressed in design

---

## Next Steps

1. ✅ **Constitution Check**: PASSED - All principles satisfied
2. ⏳ **Phase 0**: Generate `research.md` with findings for 6 research tasks
3. ⏳ **Phase 1**: Generate `data-model.md`, `contracts/openapi.yaml`, `quickstart.md`
4. ⏳ **Phase 1**: Run agent context update script
5. ⏳ **Constitution Re-check**: Verify design doesn't violate principles
6. ⏳ **Phase 2**: Run `/sp.tasks` to generate task breakdown

**Plan Complete**: Ready for Phase 0 research execution.
