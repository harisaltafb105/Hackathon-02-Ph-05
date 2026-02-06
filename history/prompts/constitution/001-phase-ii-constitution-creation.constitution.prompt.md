---
id: 001
title: Phase II Constitution Creation
stage: constitution
date: 2026-01-05
surface: agent
model: claude-sonnet-4-5-20250929
feature: none
branch: master
user: harisaltafb105
command: /sp.constitution
labels: ["constitution", "phase-ii", "initial-setup", "full-stack-architecture"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
  - .specify/memory/constitution.md
tests:
  - N/A (documentation only)
---

## Prompt

Phase II: Todo Full-Stack Web Application - Spec Constitution

Mission:
----------
Transform the Phase I console todo app into a modern multi-user full-stack web application using Claude Code and Spec-Kit Plus.
Ensure persistent storage, secure authentication, and responsive UI. No manual coding is allowed; all implementation is via Claude Code following spec-driven development.

Basic Level Features (Core Essentials):
---------------------------------------
1. Add Task – Create new todo ----------------------------
Frontend         | Next.js 16+ (App Router), TypeScript, Tailwind CSS
Backend          | Python FastAPI, SQLModel ORM
Database         | Neon Serverless PostgreSQL
Spec-Driven      | Claude Code + Spec-Kit Plus
Authentication   | Better Auth (JWT integration)

API Endpoints:
---------------
Method  | Endpoint                         | Description
--------|---------------------------------|------------------------------------------
GET     | /api/{user_id}/tasks             | List all tasks
POST    | /api/{user_id}/tasks             | Create a new task
GET     | /api/{user_id}/tasks/{id}        | Get task details
PUT     | /api/{user_id}/tasks/{id}        | Update a task
DELETE  | /api/{user_id}/tasks/{id}        | Delete a task
PATCH   | /api/{user_id}/tasks/{id}/complete | Toggle completion

Authentication & Security:
---------------------------
- Better Auth issues JWT tokens on frontend login.
- Frontend includes JWT in Authorization: Bearer <token> header for API requests.
- Backend verifies JWT and extracts user ID using shared secret (BETTER_AUTH_SECRET environment variable).
- Every endpoint enforces user isolation:
  - Only returns data for authenticated user
  - 401 Unauthorized if token is missing/invalid
- Benefits:
  - Stateless authentication
  - Automatic token expiry
  - No shared DB session required
  - Complete user isolation

Monorepo Structure:
-------------------
hackathon-todo/
├── .spec-kit/                      # Spec-Kit configuration
│   └── config.yaml
├── specs/                          # Spec-Kit managed specifications
│   ├── overview.md
│   ├── architecture.md
│   ├── features/
│   │   ├── task-crud.md
│   │   ├── authentication.md
│   │   └── chatbot.md
│   ├── api/
│   │   ├── rest-endpoints.md
│   │   └── mcp-tools.md
│   ├── database/
│   │   └── schema.md
│   └── ui/
│       ├── components.md
│       └── pages.md
├── CLAUDE.md                       # Root Claude Code instructions
├── frontend/
│   ├── CLAUDE.md                   # Frontend guidelines for Claude Code
│   └── ... (Next.js app)
├── backend/
│   ├── CLAUDE.md                   # Backend guidelines for Claude Code
│   └── ... (FastAPI app)
├── docker-compose.yml
└── README.md

Key Rules for Phase II:
-----------------------
1. Always read the relevant spec before implementation.
2. Reference specs using: @specs/features/task-crud.md
3. No manual coding; all work via Claude Code.
4. Implement all Basic Level features first.
5. Verify JWT authentication on all API endpoints.
6. Use structured CLAUDE.md files for both frontend and backend guidance.
7. Use MCP server docs for dependency installation and environment setup.

Workflow with Spec-Kit Plus + Claude Code:
------------------------------------------
- Write/Update Spec → @specs/features/[feature].md
- Ask Claude Code to implement:
    "Implement @specs/features/task-crud.md"
- Claude Code reads:
    - Root CLAUDE.md
    - Feature spec
    - API spec
    - Database spec
    - Relevant frontend/backend CLAUDE.md
- Claude Code implements both frontend and backend.
- Test and iterate on spec if needed.

Skills & Dependencies:
-----------------------
- Frontend: Next.js 16+, TypeScript, Tailwind CSS
- Backend: FastAPI, SQLModel, Python 3.13+
- DB: Neon Serverless PostgreSQL
- Authentication: Better Auth (JWT)
- Deployment: Docker / Docker Compose
- Tools: Claude Code, Spec-Kit Plus, MCP server documentation for all installations

Bottom Line:
-------------
Phase II transforms the console todo app into a fully functional, multi-user, secure web application with persistent storage.
All Basic Level tasks must be implemented with proper authentication, API endpoints, and frontend UI.
Spec-Kit Plus + Claude Code ensures spec-driven development with structured agents handling all tasks.

## Response snapshot

Created the initial constitution (v1.0.0) for the Todo Full-Stack Web Application with six core non-negotiable principles:

1. **Spec-Driven Development** - All implementation via specs in specs/ directory, no manual coding
2. **Multi-Tenant User Isolation** - Strict user data isolation enforced at API and database levels
3. **JWT Authentication Bridge** - Better Auth frontend + FastAPI backend with shared secret verification
4. **Monorepo with Clear Boundaries** - Separate frontend/, backend/, specs/ with explicit contracts
5. **API-First Design** - RESTful endpoints documented before implementation
6. **Database Schema Integrity** - SQLModel ORM with migrations and user scoping

Also defined:
- **Technology Stack Constraints**: Next.js 16+ (App Router), FastAPI, SQLModel, Neon PostgreSQL, Better Auth
- **Development Workflow**: Phase-based implementation with Spec-Kit Plus commands and agent roles
- **Security Standards**: JWT expiry, input validation, data privacy, HTTPS requirements
- **Quality Gates**: Pre-implementation, during implementation, and pre-deployment checklists
- **Governance**: Amendment process, semantic versioning, compliance requirements

Constitution stored at: `.specify/memory/constitution.md`

## Outcome

- ✅ Impact: Established foundational governance document for Phase II full-stack development. All agents and developers must follow these principles. Constitution defines tech stack, security requirements, and development workflow.
- 🧪 Tests: N/A (documentation artifact, not executable code)
- 📁 Files: Created `.specify/memory/constitution.md` (262 lines)
- 🔁 Next prompts:
  - Create specs: `/sp.specify` for task-crud, authentication features
  - Generate plans: `/sp.plan` for each feature spec
  - Create tasks: `/sp.tasks` to break down implementation
  - Begin implementation: `/sp.implement` to execute via agents
- 🧠 Reflection: Constitution provides strong guardrails for multi-user security (user isolation, JWT auth) and clear tech stack boundaries. The six principles are testable and enforceable by agents. Quality gates ensure specs exist before implementation. Monorepo structure enables parallel frontend/backend development while maintaining clear separation.

## Evaluation notes (flywheel)

- Failure modes observed: None (initial creation)
- Graders run and results (PASS/FAIL): N/A (awaiting implementation to validate principles)
- Prompt variant (if applicable): N/A (standard constitution creation)
- Next experiment (smallest change to try): Validate that agents correctly enforce user isolation principle during first API endpoint implementation
