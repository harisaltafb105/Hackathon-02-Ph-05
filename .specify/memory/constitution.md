<!--
Sync Impact Report:
Version change: 2.0.0 → 3.0.0
Modified principles:
  - Development Workflow - expanded to include Phase IV
Added sections:
  - Principle XIV: Infrastructure-Only Phase (NON-NEGOTIABLE)
  - Principle XV: Spec-Driven Infrastructure (NON-NEGOTIABLE)
  - Principle XVI: Local-First Cloud-Native (NON-NEGOTIABLE)
  - Principle XVII: Reproducible Deployment (NON-NEGOTIABLE)
  - Principle XVIII: AI-Assisted DevOps Sovereignty (NON-NEGOTIABLE)
  - Principle XIX: Failure Diagnosis Protocol (NON-NEGOTIABLE)
  - Phase IV Technology Stack
  - Phase IV Agent Roles
  - Phase IV Success Definition
  - Phase IV Explicit Out-of-Scope
Removed sections: None
Templates requiring updates:
  ✅ plan-template.md - Constitution Check references remain valid
  ✅ spec-template.md - Requirements alignment verified
  ✅ tasks-template.md - Task categorization includes infrastructure tasks
Follow-up TODOs: None
-->

# Todo Full-Stack Web Application Constitution

## Core Principles

### I. Spec-Driven Development (NON-NEGOTIABLE)

All implementation MUST be driven by specifications created in the `specs/` directory. No manual coding is permitted outside of Claude Code execution following spec-driven workflows.

**Rules**:
- Every feature begins with a specification document in `specs/features/[feature-name].md`
- Implementation follows the workflow: Write Spec → Claude Code reads spec → Claude Code implements
- All changes reference their governing spec using `@specs/` notation
- Specs are the single source of truth for requirements, API contracts, and data models
- Claude Code MUST read relevant specs before any implementation work
- Specs are append-only; updates MUST be done via new spec revisions
- No retroactive spec rewriting

**Rationale**: Eliminates ambiguity, ensures traceability from requirement to implementation, enables autonomous agent execution with clear boundaries.

### II. Multi-Tenant User Isolation (NON-NEGOTIABLE)

Every API endpoint and database query MUST enforce strict user isolation. No user can access or modify another user's data under any circumstances.

**Rules**:
- All API endpoints extract user ID from verified JWT tokens
- All database queries include user_id filtering in WHERE clauses
- User ID comes exclusively from JWT claims, never from request parameters
- 401 Unauthorized returned for missing/invalid tokens
- 403 Forbidden returned when attempting to access other users' resources
- Database models include user_id foreign key with NOT NULL constraint
- Integration tests MUST verify cross-user isolation
- User identity MUST never be inferred from chat text (Phase III)

**Rationale**: Security-first design prevents data leakage, satisfies multi-user requirements, provides defense-in-depth through stateless authentication.

### III. JWT Authentication Bridge (NON-NEGOTIABLE)

Authentication uses Better Auth on frontend issuing JWTs, verified by FastAPI backend using shared secret. No session storage, no shared authentication database.

**Rules**:
- Better Auth frontend generates JWT tokens on successful login
- All API requests include `Authorization: Bearer <token>` header
- Backend verifies JWT signature using `BETTER_AUTH_SECRET` environment variable
- Backend extracts user ID from JWT payload (`sub` or `userId` claim)
- Tokens are stateless with embedded expiry (no server-side revocation for MVP)
- Failed verification returns 401 with descriptive error message
- Environment variable `BETTER_AUTH_SECRET` MUST match between frontend and backend
- AI receives user_id only from backend context, never from user input (Phase III)

**Rationale**: Stateless authentication enables horizontal scaling, eliminates database round-trips for auth, simplifies frontend-backend contract, standard JWT ecosystem compatibility.

### IV. Monorepo with Clear Boundaries

Project structure separates frontend, backend, and shared specifications with explicit interface contracts.

**Rules**:
- Root `CLAUDE.md` provides high-level project guidance
- `specs/` directory contains all feature specifications, API contracts, database schemas
- `frontend/` contains Next.js application with own `CLAUDE.md` for frontend-specific guidance
- `backend/` contains FastAPI application with own `CLAUDE.md` for backend-specific guidance
- `docker-compose.yml` orchestrates local development environment
- No code sharing between frontend and backend except via API contracts in specs
- Each subdirectory is independently deployable
- Phase III chatbot logic MUST remain isolated, modular, and detachable
- Phase IV infrastructure code MUST be separate from application code

**Rationale**: Clear separation of concerns, enables parallel frontend/backend development, explicit contracts prevent implicit coupling, supports independent scaling and deployment.

### V. API-First Design

All backend functionality exposed through well-defined REST API endpoints documented in specs before implementation.

**Rules**:
- API contracts defined in `specs/api/rest-endpoints.md` before implementation
- Endpoints follow RESTful conventions: GET (read), POST (create), PUT (update), DELETE (delete), PATCH (partial update)
- All endpoints include user_id in path: `/api/{user_id}/tasks`
- Request/response schemas defined with TypeScript/Python types
- Error responses use standard HTTP status codes with descriptive messages
- API documentation auto-generated from code annotations where possible

**Rationale**: Contract-first approach enables parallel development, facilitates testing, provides clear interface for frontend, enables API versioning strategy.

### VI. Database Schema Integrity

Database schema managed through SQLModel ORM with explicit migrations, type safety, and user scoping.

**Rules**:
- All models defined using SQLModel (Pydantic + SQLAlchemy)
- Every user-specific table includes `user_id` foreign key
- Migrations managed explicitly (Alembic or similar) before deployment
- Database constraints enforce data integrity (NOT NULL, UNIQUE, FOREIGN KEY)
- No raw SQL queries except for complex analytical queries
- Connection pooling configured for production workloads
- Schema documented in `specs/database/schema.md`

**Rationale**: Type-safe ORM prevents runtime errors, migrations enable safe schema evolution, constraints provide database-level validation, documentation ensures schema visibility.

### VII. Phase III Additive Extension (NON-NEGOTIABLE)

Phase III (AI-Powered Todo Chatbot) is a strict extension of the Phase II Full-Stack Todo Application. The chatbot is an additive layer, not a replacement.

**Rules**:
- Existing frontend, backend, APIs, database schema, and authentication MUST NOT be broken
- No refactor of Phase II unless explicitly required for chatbot integration
- Chatbot logic MUST remain isolated, modular, and detachable
- Phase II MUST continue to work even if chatbot is disabled
- Chat UI is an additive feature; existing Todo UI remains unchanged
- Chatbot UI MUST degrade gracefully if backend is unavailable
- No frontend logic duplication of backend rules

**Rationale**: Ensures existing functionality remains stable, enables incremental rollout, allows chatbot removal without core app impact, maintains separation of concerns.

### VIII. Architectural Authority (NON-NEGOTIABLE)

Backend remains the single source of truth. AI has no direct database access. All task mutations flow through the defined chain.

**Rules**:
- All task mutations MUST go through: Agent → MCP Tool → FastAPI → Database
- Chatbot MUST NOT bypass authentication, authorization, or business rules
- AI agent receives user context only from backend, never from user input
- MCP tools are the only interface between AI and backend
- Tool outputs MUST be deterministic and auditable

**Rationale**: Maintains security boundaries, ensures consistent business logic enforcement, provides audit trail, prevents unauthorized data access.

### IX. Stateless Server Law (NON-NEGOTIABLE)

FastAPI server MUST remain fully stateless. No in-memory session or conversation state.

**Rules**:
- No in-memory session or conversation state on server
- Conversation continuity MUST be restored only from database
- Any server restart MUST NOT affect chatbot continuity
- All required state persisted to database or external store
- Horizontal scaling MUST be supported without session affinity

**Rationale**: Enables horizontal scaling, improves reliability, simplifies deployment, eliminates single points of failure.

### X. MCP Tool Sovereignty (NON-NEGOTIABLE)

MCP server exposes only task-related tools. Each tool has a single responsibility and validates user ownership.

**Rules**:
- Each MCP tool is stateless
- Each MCP tool performs exactly one responsibility
- Each MCP tool validates user_id ownership before execution
- AI agent MUST NOT invent tools
- Tool outputs MUST be deterministic and auditable
- Tools exposed: add_task, list_tasks, update_task, delete_task, complete_task

**Rationale**: Constrains AI capabilities to defined operations, ensures security validation at tool level, provides predictable behavior.

### XI. Agent Behavior Constraints (NON-NEGOTIABLE)

AI agents MUST act only through MCP tools with explicit user confirmation and safe handling of ambiguity.

**AI Agents MUST**:
- Act only through MCP tools
- Confirm actions in natural language before and after execution
- Handle ambiguity by requesting clarification
- Provide user-friendly error messages

**AI Agents MUST NEVER**:
- Execute destructive actions silently
- Guess task IDs without verification
- Leak internal system details to users
- Modify tasks of another user
- Bypass authentication or authorization

**Rationale**: Ensures safe AI behavior, prevents unintended data modification, maintains user trust, provides audit trail.

### XII. Data Integrity & Safety (NON-NEGOTIABLE)

All data operations MUST be transactional, safe, and non-destructive by default.

**Rules**:
- All writes MUST be transactional
- Partial failures MUST rollback safely
- Duplicate tasks MUST be handled gracefully
- Deleted tasks MUST NOT reappear in chat context
- Errors MUST be logged, user-friendly, and non-destructive
- AI hallucinations prevented via tool-only execution
- If unsure, AI MUST respond with clarification, not action

**Rationale**: Protects data integrity, prevents data loss, ensures consistent state, maintains user confidence.

### XIII. Final Constitutional Law (NON-NEGOTIABLE)

**The AI chatbot is a controlled assistant, not an authority.**
**The backend is the authority.**
**The database is the memory.**

This principle supersedes all other guidance. No agent, tool, or process may violate this hierarchy.

### XIV. Infrastructure-Only Phase (NON-NEGOTIABLE)

Phase IV is exclusively a deployment and infrastructure phase. No application logic changes are permitted.

**Rules**:
- Phase IV MUST NOT introduce new features
- No frontend or backend business logic changes
- No database schema or API redesign
- Existing Phase II functionality MUST remain fully operational
- Existing Phase III chatbot MUST remain fully operational
- Infrastructure code MUST be separate from application code
- All containerization and orchestration is additive only

**Rationale**: Ensures deployment work cannot inadvertently break working application code, maintains separation between application development and infrastructure concerns.

### XV. Spec-Driven Infrastructure (NON-NEGOTIABLE)

All infrastructure decisions MUST follow the spec-driven workflow. No ad-hoc CLI experimentation without specification backing.

**Rules**:
- All infrastructure follows: spec → plan → tasks → implement
- Dockerfiles, Helm charts, and K8s manifests MUST be specified before creation
- No ad-hoc kubectl or docker commands without spec backing
- Infrastructure changes require spec updates first
- All deployment configurations MUST be version-controlled
- Rollback procedures MUST be documented in specs

**Rationale**: Maintains traceability and reproducibility for infrastructure, prevents configuration drift, enables infrastructure as code best practices.

### XVI. Local-First Cloud-Native (NON-NEGOTIABLE)

Phase IV deployment target is local Minikube only. No cloud provider configurations.

**Rules**:
- Deployment target is Minikube (local Kubernetes)
- No AWS, GCP, or Azure provider configurations
- No production deployment assumptions
- No cloud-specific services (managed databases, load balancers, etc.)
- All services MUST work with local resources only
- Ingress configurations MUST be Minikube-compatible

**Rationale**: Ensures consistent local development environment, eliminates cloud vendor lock-in for development, enables offline development and testing.

### XVII. Reproducible Deployment (NON-NEGOTIABLE)

A fresh machine MUST be able to reproduce the deployment using specifications alone. No hidden steps, no manual tweaks.

**Rules**:
- All deployment steps MUST be documented in specs
- No manual configuration tweaks allowed
- Environment setup MUST be fully automated
- All dependencies MUST be explicitly declared
- Helm values MUST be sufficient for complete deployment
- Secrets handling MUST be documented (without exposing actual secrets)

**Rationale**: Ensures any developer can reproduce the deployment, eliminates tribal knowledge, enables CI/CD readiness for future phases.

### XVIII. AI-Assisted DevOps Sovereignty (NON-NEGOTIABLE)

AI DevOps tools (Docker AI, kubectl-ai, kagent) are preferred for infrastructure operations. Manual CLI is fallback only.

**Rules**:
- Docker AI Agent (Gordon) MUST be preferred for Dockerfile generation and optimization
- kubectl-ai MUST be used for deployments, scaling, and pod debugging
- kagent MUST be used for cluster health analysis and resource optimization
- Manual CLI fallback MUST be explicitly documented when AI tools unavailable
- All AI tool outputs MUST be validated against specifications
- AI tools MUST NOT modify application behavior

**Rationale**: Leverages AI assistance for infrastructure optimization, maintains consistency in operations, provides intelligent troubleshooting.

### XIX. Failure Diagnosis Protocol (NON-NEGOTIABLE)

All deployment failures MUST be diagnosed, explained, and fixed with minimal changes. Silent retries and destructive resets are forbidden.

**Rules**:
- Any failure MUST be diagnosed via kubectl-ai or kagent
- Root cause MUST be explained before fix is applied
- Fixes MUST use the smallest possible change
- Silent retries without explanation are forbidden
- Destructive resets (delete all, recreate) require explicit justification
- All failures and resolutions MUST be logged

**Rationale**: Ensures learning from failures, prevents recurring issues, maintains system stability, provides audit trail for troubleshooting.

## Technology Stack Constraints

### Frontend Requirements (Phase II)

**Framework**: Next.js 16+ with App Router (NOT Pages Router)
**Language**: TypeScript (strict mode enabled)
**Styling**: Tailwind CSS
**State Management**: React hooks, Context API for global state
**Authentication**: Better Auth library for JWT generation
**API Client**: Native fetch with custom wrapper for token injection

**Justification**: Next.js App Router provides server components for performance, TypeScript eliminates entire classes of bugs, Tailwind enables rapid UI development, Better Auth simplifies JWT flows.

### Backend Requirements (Phase II)

**Framework**: FastAPI (Python 3.13+)
**ORM**: SQLModel (SQLAlchemy + Pydantic)
**Database**: Neon Serverless PostgreSQL
**Authentication**: PyJWT for token verification
**Deployment**: Docker container with Python 3.13-slim base
**Development**: uv for dependency management

**Justification**: FastAPI provides automatic OpenAPI docs and high performance, SQLModel combines ORM with validation, Neon offers serverless PostgreSQL with zero-downtime scaling, PyJWT is industry standard for JWT verification.

### Phase III Technology Stack (STRICT - NO ALTERNATIVES)

**AI Layer**: OpenAI Agents SDK
**Tool Interface**: Official MCP SDK
**AI Provider**: OpenAI API (via OPENAI_API_KEY)
**Frontend Chat UI**: OpenAI ChatKit

**Required Environment Variables**:
- `OPENAI_API_KEY` - OpenAI API authentication
- `BETTER_AUTH_URL` - Better Auth service URL
- `BETTER_AUTH_SECRET` - JWT signing secret (shared)
- `DATABASE_URL` - Neon PostgreSQL connection string

**Constraints**:
- No alternative frameworks, SDKs, or shortcuts allowed
- All secrets loaded via `.env` files
- No secrets hardcoded in specs, code, or prompts
- Frontend uses only public-safe environment variables
- Backend owns all privileged credentials

**Justification**: Standardized stack ensures consistent behavior, official SDKs provide stability and support, environment-based secrets enable secure deployment.

### Phase IV Technology Stack (STRICT - NO ALTERNATIVES)

**Containerization**:
- Docker (Docker Desktop)
- Docker AI Agent (Gordon) — preferred for Dockerfile generation and optimization
- Standard Docker CLI — fallback when Gordon unavailable

**Orchestration**:
- Kubernetes via Minikube (local only)
- No cloud-managed Kubernetes (EKS, GKE, AKS)

**Packaging**:
- Helm Charts (required for all deployments)
- No raw kubectl apply for production-like deployments

**AI-Assisted DevOps**:
- kubectl-ai (required for deployments, scaling, debugging)
- kagent (required for cluster health and resource optimization)

**Applications Deployed**:
- Phase II Backend (FastAPI)
- Phase II Frontend (Next.js)
- Phase III MCP Server
- Phase III AI Agent Service

**Required Environment Variables** (injected via Helm/K8s Secrets):
- `OPENAI_API_KEY` - OpenAI API authentication
- `BETTER_AUTH_URL` - Better Auth service URL
- `BETTER_AUTH_SECRET` - JWT signing secret (shared)
- `DATABASE_URL` - Neon PostgreSQL connection string

**Constraints**:
- All documentation and commands MUST reference MCP Server Context 7 documentation
- No guessing or outdated instructions
- .env files are NOT committed to version control
- Secrets MUST be passed via Helm values or Kubernetes secrets
- Absence of secrets during spec/plan stages MUST NOT break implementation

**Justification**: Local-first approach enables consistent development environments, Helm provides declarative configuration management, AI-assisted tooling optimizes operations.

### Shared Standards

**Version Control**: Git with conventional commits
**Environment Variables**: `.env.local` files (never committed)
**Secrets Management**: Environment variables for all secrets
**API Documentation**: OpenAPI 3.0 auto-generated from FastAPI
**Logging**: Structured JSON logs for production

## Development Workflow

### Phase-Based Implementation

**Phase I: Specifications** (Complete)
- Console todo app specifications created
- Project structure defined
- Agent roles established

**Phase II: Full-Stack Implementation** (Complete)
1. Database schema implementation in backend
2. FastAPI endpoints with JWT verification
3. Next.js frontend with Better Auth integration
4. End-to-end testing of authentication flow
5. Task CRUD operations frontend + backend

**Phase III: AI-Powered Chatbot** (Complete)
1. MCP server setup with task-related tools
2. OpenAI Agent integration via Agents SDK
3. Chat UI implementation with ChatKit
4. Conversation persistence and continuity
5. End-to-end testing of chatbot flows

**Phase IV: Local Kubernetes Deployment** (Current)
1. Dockerfile creation for all services (via Docker AI/Gordon)
2. Helm chart generation for Kubernetes packaging
3. Minikube cluster setup and configuration
4. Service deployment via kubectl-ai
5. Cluster health validation via kagent
6. End-to-end deployment verification

**Workflow Steps**:
1. Review spec in `specs/features/[feature].md`
2. Invoke Claude Code: "Implement @specs/features/[feature].md"
3. Claude Code reads root `CLAUDE.md` + feature spec + API spec + database schema + relevant frontend/backend guidance
4. Claude Code implements frontend and backend in parallel
5. Run integration tests to verify behavior
6. Iterate on spec if requirements change

### Spec-Kit Plus Integration

**Commands**:
- `/sp.specify` - Create or update feature specification
- `/sp.plan` - Generate implementation plan from spec
- `/sp.tasks` - Break down plan into actionable tasks
- `/sp.implement` - Execute tasks via Claude Code agents
- `/sp.adr` - Document architectural decisions

**Agent Roles (Phase II)**:
- `spec-intelligence` - Validates and clarifies specifications
- `frontend-app-builder` - Implements Next.js UI and API integration
- `backend-api-builder` - Implements FastAPI endpoints and database operations
- `auth-bridge-verifier` - Ensures JWT authentication correctness
- `database-guardian` - Validates schema integrity and user scoping
- `phase-ii-orchestrator` - Coordinates multi-agent implementation

**Agent Roles (Phase III)**:
- `mcp-tool-validator` - Validates MCP tool calls before execution
- `intent-resolver` - Translates natural language to actionable intents
- `user-context-guardian` - Validates user context for all operations
- `tool-chain-orchestrator` - Manages multi-tool operation sequences
- `conversation-context-manager` - Handles conversation continuity
- `error-translator` - Converts system errors to user-friendly messages

**Agent Roles (Phase IV)**:
- `phase4-deployment-orchestrator` - Coordinates Phase IV deployment workflow
- `containerization-docker` - Generates and optimizes Dockerfiles via Docker AI
- `helm-chart-generator` - Creates Helm charts for Kubernetes packaging
- `kubectl-ops` - Executes Kubernetes operations via kubectl-ai
- `kagent` - Analyzes cluster health and provides optimization insights
- `dev-environment-validator` - Validates local development environment setup

### Git Workflow

**Branch Strategy**: Feature branches from master
**Commit Messages**: Conventional commits (feat, fix, docs, refactor, test)
**PR Requirements**: All tests pass, spec references included in description
**Code Review**: Automated via Claude Code review agent before merge

## Deployment Architecture (Phase IV)

### Service Topology

Each major component MUST be deployed as a separate Kubernetes Deployment:
- `frontend` - Next.js application
- `backend` - FastAPI application
- `mcp-server` - MCP tool server
- `ai-agent` - AI agent service

### Service Exposure

- Services MUST be exposed via Kubernetes Services (ClusterIP or NodePort)
- Ingress MAY be enabled if required (Minikube-compatible)
- Frontend MUST communicate with backend via internal service DNS

### Environment Configuration

- Environment variables MUST be injected via Helm values
- Secrets MUST be managed via Kubernetes Secrets
- No hardcoded configuration in container images
- ConfigMaps for non-sensitive configuration

## Security Standards

### Authentication Security

- JWTs include expiry (`exp` claim) with reasonable lifetime (1-24 hours)
- Secrets stored in environment variables, never in code
- HTTPS required for all production API traffic
- Token refresh strategy defined before production deployment
- AI receives user context only from authenticated backend

### Input Validation

- All user inputs validated on backend (never trust frontend)
- SQL injection prevention via ORM parameterized queries
- XSS prevention via React's automatic escaping
- CSRF protection via SameSite cookies for auth tokens (if cookie-based)
- AI agent inputs validated through MCP tool layer

### Data Privacy

- User passwords never stored (Better Auth handles hashing)
- User data isolated per principle II
- No logging of sensitive data (passwords, full tokens)
- Database connections use SSL in production
- AI does not retain user data beyond conversation scope

### Infrastructure Security (Phase IV)

- Kubernetes Secrets for all sensitive values
- No secrets in Helm values files committed to version control
- Container images MUST use non-root users where possible
- Network policies MAY be applied for service isolation

## Quality Gates

### Before Implementation

- [ ] Feature spec exists in `specs/features/`
- [ ] API contract defined in `specs/api/`
- [ ] Database schema impact assessed in `specs/database/`
- [ ] User isolation verified in spec
- [ ] Authentication requirements explicit
- [ ] Phase III: MCP tool requirements defined (if AI-related)
- [ ] Phase IV: Deployment architecture specified (if infrastructure-related)

### During Implementation

- [ ] Claude Code reads relevant specs before coding
- [ ] JWT verification included in all protected endpoints
- [ ] User ID filtering applied to all database queries
- [ ] TypeScript types match API contracts
- [ ] Error handling returns appropriate status codes
- [ ] Phase III: AI agent uses only defined MCP tools
- [ ] Phase IV: Dockerfiles and Helm charts follow specifications

### Before Deployment

- [ ] All Basic Level features implemented
- [ ] Authentication flow tested end-to-end
- [ ] User isolation verified via integration tests
- [ ] Environment variables documented
- [ ] Docker Compose setup tested locally
- [ ] Phase III: Chatbot degradation tested (backend unavailable scenario)
- [ ] Phase IV: All pods healthy and restart-safe
- [ ] Phase IV: Deployment reproducible from specs alone

## Phase III Success Definition

Phase III is successful if:
- Users can manage todos via natural language
- All actions are correctly persisted to database
- Conversation resumes correctly after server restart
- Phase II functionality remains fully operational
- AI acts as an assistant, not a system owner
- Cross-user data isolation is maintained
- System supports horizontal scaling and multiple concurrent users

## Phase IV Success Definition

Phase IV is successful if:
- All services run on Minikube without errors
- Pods are healthy and restart-safe
- Frontend communicates with backend and AI chatbot
- MCP tools function correctly via deployed services
- Deployment is reproducible from specs alone
- No manual steps are required post-implementation
- Phase II and Phase III functionality remain fully operational

## Phase IV Explicit Out-of-Scope

The following are explicitly NOT part of Phase IV:
- Cloud hosting (AWS, GCP, Azure)
- CI/CD pipelines
- Production hardening
- Monitoring stacks (Prometheus, Grafana)
- Log aggregation systems
- Service mesh implementations
- Multi-cluster deployments

## Governance

This constitution is the supreme authority for all development practices. Any deviation requires explicit justification documented in an ADR (Architecture Decision Record).

**Amendment Process**:
1. Propose change with rationale
2. Document impact on existing code/specs
3. Update constitution version (semantic versioning)
4. Update dependent templates and specs
5. Create migration plan if breaking changes

**Versioning**:
- MAJOR: Breaking changes to principles (e.g., removing JWT auth, changing monorepo structure, adding non-negotiable principles)
- MINOR: New principles or significant expansions (e.g., adding new security requirement)
- PATCH: Clarifications, typo fixes, non-semantic refinements

**Compliance**:
- All PRs must verify compliance with constitution
- Agents refuse implementation requests violating principles
- Complexity must be justified if adding beyond defined stack
- Use `CLAUDE.md` at root and subdirectories for runtime guidance

**Constitutional Authority**:
- Constitution overrides conflicting guidance in individual `CLAUDE.md` files
- Agents cite constitution section when rejecting non-compliant requests
- User can override principles only by amending constitution first

**Version**: 3.0.0 | **Ratified**: 2026-01-05 | **Last Amended**: 2026-02-03
