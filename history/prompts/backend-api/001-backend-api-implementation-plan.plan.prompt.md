---
id: 001
title: Backend API Implementation Plan
stage: plan
date: 2026-01-07
surface: agent
model: claude-sonnet-4-5
feature: backend-api
branch: 003-backend-api
user: Developer
command: /sp.plan
labels: ["backend", "fastapi", "sqlmodel", "jwt-auth", "planning"]
links:
  spec: specs/003-backend-api/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - specs/003-backend-api/plan.md
  - specs/003-backend-api/research.md
  - specs/003-backend-api/data-model.md
  - specs/003-backend-api/quickstart.md
  - specs/003-backend-api/contracts/openapi.yaml
tests:
  - None (planning phase, no tests created yet)
---

## Prompt

User executed `/sp.plan` command with additional context:

```
Project: Phase II – Todo Full-Stack Web Application (Backend Integration)

Objective:
- Implement the backend for the Phase II Todo app, ensuring **full integration with the already implemented frontend-first UI**.
- Use FastAPI + SQLModel and persist data in Neon PostgreSQL.
- Authenticate all endpoints using Better Auth JWT integration.
- Backend must read `.env` variables for configuration: BETTER_AUTH_URL, BETTER_AUTH_SECRET, DATABASE_URL

2. **Database Setup**
   - Define PostgreSQL schema using SQLModel:
     - Users table: id (primary key), email, name
     - Tasks table: id, title, description, completed, user_id (foreign key)
   - Ensure **user_id** references authenticated user.
   - Prepare async DB session generator for dependency injection.

3. **Authentication**
   - Create dependency to validate JWT from frontend:
     - Read token from `Authorization: Bearer <token>` header.
     - Verify JWT using BETTER_AUTH_SECRET.
     - Extract user_id from token.
     - Raise 401 Unauthorized if invalid.
   - Ensure **all endpoints enforce user isolation**.

4. **API Endpoints (REST)**
   - GET `/api/{user_id}/tasks`: Return all tasks for the authenticated user.
   - POST `/api/{user_id}/tasks`: Create a new task (title, description)...
```

Command initiated the `/sp.plan` workflow to create a comprehensive implementation plan for the backend API with authentication.

## Response snapshot

Successfully completed `/sp.plan` workflow with the following outputs:

**Phase 0: Research** (research.md)
- Completed 6 research tasks covering FastAPI structure, SQLModel async setup, PyJWT verification, CORS configuration, environment management, and error response standardization
- Made key architectural decisions:
  1. Async PostgreSQL with SQLModel + asyncpg
  2. Dependency injection for authentication
  3. User ID validation strategy (URL + JWT claim matching)
  4. Custom error response format (error + detail fields)

**Phase 1: Design & Contracts** (data-model.md, contracts/openapi.yaml, quickstart.md)
- Defined Task entity with SQLModel schema (UUID, title, description, completed, timestamps, user_id)
- Created comprehensive OpenAPI 3.0 specification with 6 endpoints
- Documented indexes for performance (primary key, user_id, composite)
- Created request/response Pydantic schemas (TaskCreate, TaskUpdate, TaskPatch, TaskResponse)
- Generated quickstart guide with setup, testing, and troubleshooting instructions

**Constitution Check**: ✅ PASSED
- All 6 constitutional principles satisfied
- No violations or complexity tracking needed
- Technology stack compliance verified

**Project Structure**:
```
backend/
├── main.py (FastAPI app with CORS and error handlers)
├── models.py (SQLModel Task entity)
├── schemas.py (Pydantic request/response models)
├── database.py (Async engine and session factory)
├── auth.py (JWT verification dependencies)
├── config.py (Pydantic Settings for env vars)
├── routers/tasks.py (CRUD endpoints)
├── middleware/cors.py (CORS configuration)
└── tests/ (pytest test suite)
```

**Agent Context Updated**: Added Python 3.13+, FastAPI, SQLModel, PyJWT, asyncpg to CLAUDE.md

**Next Steps**: Run `/sp.tasks` to generate task breakdown for implementation phase.

## Outcome

- ✅ Impact: Complete implementation plan created for backend API with comprehensive research, design, and contracts. All constitutional gates passed. Zero frontend changes required per FR-018.
- 🧪 Tests: No tests created (planning phase). Test strategy defined: pytest with pytest-asyncio for async endpoints, httpx for API testing, coverage requirements documented in spec.
- 📁 Files: Created 5 new documentation files: plan.md (518 lines), research.md (381 lines), data-model.md (425 lines), quickstart.md (456 lines), contracts/openapi.yaml (435 lines). Updated CLAUDE.md with backend technology stack.
- 🔁 Next prompts: (1) Run `/sp.tasks` to generate actionable task breakdown; (2) Run `/sp.implement` to execute implementation; (3) Consider `/sp.adr` for architectural decisions if significant choices require documentation.
- 🧠 Reflection: Planning workflow successfully integrated user's detailed backend requirements with constitutional principles. All 6 research tasks yielded concrete implementation patterns. Design artifacts (data model, OpenAPI contract) are implementation-ready with no ambiguities or [NEEDS CLARIFICATION] markers.

## Evaluation notes (flywheel)

- Failure modes observed: None. Workflow executed without errors. Constitution check passed all gates. User requirements fully addressed.
- Graders run and results (PASS/FAIL):
  - Constitution Check: PASS (all 6 principles satisfied)
  - Success Criteria Validation: PASS (all 10 SC criteria addressed)
  - Quality Checklist: PASS (spec completeness verified)
- Prompt variant (if applicable): Standard /sp.plan workflow execution with user-provided context about Phase II integration and technology stack.
- Next experiment (smallest change to try): None needed - workflow successful. Consider automating research phase in future iterations by caching common technology research (FastAPI, SQLModel patterns).
