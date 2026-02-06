# Implementation Plan: Frontend Auth & API Readiness

**Branch**: `002-frontend-auth` | **Date**: 2026-01-07 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/002-frontend-auth/spec.md`

**Note**: This template is filled in by the `/sp.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

Create a complete frontend authentication experience with mocked state management and API client abstraction. This feature builds UI and client-side logic for user authentication (login, register, logout, route protection) while keeping all authentication logic mocked using localStorage. The implementation follows existing patterns (React Context + useReducer from task-context, React Hook Form + Zod validation) and creates a production-ready frontend architecture that can seamlessly integrate with Better Auth SDK + FastAPI backend in the future without requiring frontend refactoring.

**Key Deliverables**:
- Authentication pages: `/login` and `/register` with form validation
- AuthContext with mocked state management (matches task-context patterns)
- Route protection middleware for protected vs public routes
- API client abstraction with mocked network operations
- Layout system: public layout for auth pages, protected layout for dashboard
- Persistent session state via localStorage

## Technical Context

**Language/Version**: TypeScript 5.x (Next.js 16 App Router, React 19)
**Primary Dependencies**:
- Next.js 16+ (App Router, Server/Client Components)
- React 19 (Context API, useReducer, hooks)
- React Hook Form 7.x (form state management)
- Zod 3.x (schema validation)
- shadcn/ui components (Dialog, Button, Input, Card, Checkbox, Label)
- Framer Motion (animations, transitions)
- Tailwind CSS v4 (styling with OKLCH color space)
- Lucide React (icons)

**Storage**: localStorage for mocked session persistence (client-side only)
**Testing**: Manual testing against acceptance scenarios (automated testing in future phases)
**Target Platform**: Modern browsers (Chrome, Firefox, Safari, Edge) - ES2020+ support required
**Project Type**: Web application (frontend-only for this feature)
**Performance Goals**:
- Auth pages render in <500ms
- Form validation feedback in <100ms
- Auth action feedback in <1s
- API client simulated network delay: 300-800ms

**Constraints**:
- Frontend-only implementation (no backend changes)
- Must not install Better Auth SDK or any real auth libraries
- No environment variables or deployment configuration
- Must follow existing patterns from task-context.tsx and task-form.tsx
- All auth logic mocked using localStorage

**Scale/Scope**:
- 2 new pages (/login, /register)
- 1 context provider (AuthContext)
- 1 API client module (apiClient.ts)
- 6-8 new components (LoginForm, RegisterForm, ProtectedRoute, PublicLayout, etc.)
- Route protection for existing pages (/dashboard, /tasks)
- ~800-1200 lines of new TypeScript code

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### I. Spec-Driven Development ✅ PASS
- [x] Feature specification exists at `specs/002-frontend-auth/spec.md`
- [x] Implementation will follow spec-driven workflow via `/sp.plan` → `/sp.tasks` → `/sp.implement`
- [x] All changes will reference governing spec
- [x] Spec is single source of truth for requirements

**Status**: COMPLIANT - Full spec created with 6 user stories, 20 functional requirements, 15 success criteria.

### II. Multi-Tenant User Isolation ⚠️ DEFERRED
- [ ] Feature is frontend-only with mocked auth - no API endpoints to protect
- [ ] User isolation will be enforced when backend integration happens (future phase)
- [ ] Mocked auth state includes user ID structure ready for backend

**Status**: NOT APPLICABLE - This is frontend-only implementation. User isolation enforcement deferred to backend integration phase. Architecture prepared for future compliance (AuthState includes user object with id).

### III. JWT Authentication Bridge ⚠️ DEFERRED
- [ ] Feature explicitly excludes real JWT generation/verification
- [ ] Mocked token structure simulates JWT pattern
- [ ] API client abstraction includes Authorization header pattern
- [ ] Architecture ready for Better Auth SDK integration (no refactor needed)

**Status**: NOT APPLICABLE - This is mocked authentication only. Real JWT bridge implementation deferred to Better Auth SDK integration phase. Architecture designed for seamless future integration.

### IV. Monorepo with Clear Boundaries ✅ PASS
- [x] Changes confined to `frontend/` directory
- [x] No backend modifications required
- [x] Spec in `specs/002-frontend-auth/` provides clear contract
- [x] No cross-boundary code sharing (frontend self-contained)

**Status**: COMPLIANT - All changes in frontend directory, spec provides interface documentation.

### V. API-First Design ✅ PASS (with mocked implementation)
- [x] API client interface defined before implementation
- [x] Mocked API methods follow RESTful conventions
- [x] Response structure documented: `{ success, data, error, statusCode }`
- [x] Contract matches expected FastAPI backend patterns

**Status**: COMPLIANT - API client abstraction designed with clear interface matching future backend contract.

### VI. Database Schema Integrity ⚠️ NOT APPLICABLE
- [ ] No database access in this feature (frontend-only)
- [ ] User entity structure defined in spec for future backend alignment

**Status**: NOT APPLICABLE - Frontend-only feature has no database interaction. User entity structure documented for future backend implementation.

### Technology Stack Constraints ✅ PASS
**Frontend Requirements**:
- [x] Next.js 16+ with App Router ✅
- [x] TypeScript strict mode ✅
- [x] Tailwind CSS ✅
- [x] React Context API for state ✅
- [x] Native fetch with custom wrapper ✅ (apiClient.ts)

**Status**: COMPLIANT - All frontend technology choices match constitution requirements.

### Quality Gates ✅ PASS
**Before Implementation**:
- [x] Feature spec exists in `specs/002-frontend-auth/`
- [x] API contract defined (mocked API client interface)
- [x] User isolation verified in spec (prepared for future backend)
- [x] Authentication requirements explicit (mocked for now)

**Status**: COMPLIANT - All pre-implementation gates satisfied.

## Overall Constitution Compliance: ✅ PASS

**Justification**: This feature is frontend-only with mocked authentication, so backend-specific principles (II, III, VI) are not applicable. All applicable principles (I, IV, V) are fully compliant. Architecture explicitly designed to enable future compliance with deferred principles when backend integration occurs (Better Auth SDK + FastAPI + JWT verification).

## Project Structure

### Documentation (this feature)

```text
specs/[###-feature]/
├── plan.md              # This file (/sp.plan command output)
├── research.md          # Phase 0 output (/sp.plan command)
├── data-model.md        # Phase 1 output (/sp.plan command)
├── quickstart.md        # Phase 1 output (/sp.plan command)
├── contracts/           # Phase 1 output (/sp.plan command)
└── tasks.md             # Phase 2 output (/sp.tasks command - NOT created by /sp.plan)
```

### Source Code (repository root)

```text
frontend/
├── app/
│   ├── (auth)/                    # Route group for public auth pages
│   │   ├── login/
│   │   │   └── page.tsx           # Login page
│   │   ├── register/
│   │   │   └── page.tsx           # Register page
│   │   └── layout.tsx             # Public layout (minimal, no auth UI)
│   ├── (protected)/               # Route group for authenticated pages
│   │   ├── dashboard/
│   │   │   └── page.tsx           # Dashboard (existing, now protected)
│   │   ├── tasks/
│   │   │   └── page.tsx           # Tasks page (existing, now protected)
│   │   └── layout.tsx             # Protected layout (user menu, logout)
│   ├── layout.tsx                 # Root layout (providers)
│   └── page.tsx                   # Existing home page (UPDATE to check auth)
├── components/
│   ├── auth/
│   │   ├── login-form.tsx         # Login form with validation
│   │   ├── register-form.tsx      # Registration form with validation
│   │   └── protected-route.tsx    # HOC for route protection
│   ├── ui/                        # Existing shadcn/ui components (reuse)
│   └── [existing components]      # TaskCard, TaskList, etc.
├── context/
│   ├── auth-context.tsx           # NEW: Auth state management
│   └── task-context.tsx           # Existing task context
├── lib/
│   ├── api-client.ts              # NEW: Centralized API client with mocked methods
│   ├── auth-utils.ts              # NEW: Helper functions (token validation, etc.)
│   └── [existing utils]
├── types/
│   ├── auth.ts                    # NEW: User, AuthState, APIResponse types
│   └── task.ts                    # Existing task types
└── middleware.ts                  # NEW: Route protection middleware (Next.js 16)
```

**Structure Decision**: Web application (frontend-only changes). This feature adds authentication infrastructure to the existing Next.js frontend without modifying backend or shared specs. Uses Next.js 16 App Router route groups `(auth)` and `(protected)` to organize public vs authenticated pages with separate layouts. All new files follow existing patterns (context/, components/, lib/, types/).

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

No constitutional violations detected. All complexity is justified by feature requirements and follows existing patterns.

---

## Phase 0: Research & Unknowns Resolution ✅ COMPLETE

**Objective**: Resolve all NEEDS CLARIFICATION items and document architectural decisions.

**Output**: `research.md` (see [research.md](./research.md))

### Research Tasks Completed

1. ✅ **Existing Pattern Analysis**: Analyzed `task-context.tsx` pattern
   - Decision: Mirror Context + useReducer pattern for AuthContext
   - Rationale: Consistency with existing codebase

2. ✅ **Form Validation Pattern**: Analyzed `task-form.tsx` approach
   - Decision: Use React Hook Form + Zod (same as tasks)
   - Rationale: Leverage existing schemas, familiar UX

3. ✅ **Route Protection Strategies**: Researched Next.js 16 App Router patterns
   - Decision: Route groups with layout-based protection
   - Alternatives: Middleware (edge, no localStorage), HOC (repetitive)
   - Rationale: Best balance for App Router, access to client state

4. ✅ **API Client Abstraction**: Designed interface matching FastAPI backend
   - Decision: Singleton class with mocked methods
   - Rationale: Easy swap to real implementation, centralized config

5. ✅ **Mocked Authentication Logic**: Defined realistic simulation behavior
   - Decision: localStorage for user store and auth state
   - Rationale: Persists across refreshes, simple API

6. ✅ **Layout System Design**: Designed public vs protected layouts
   - Decision: Route groups `(auth)` and `(protected)` with separate layouts
   - Rationale: Clean separation, automatic layout switching

7. ✅ **Animation Patterns**: Determined animation approach
   - Decision: Reuse Framer Motion patterns from existing modals
   - Rationale: Consistency, proven smooth UX

8. ✅ **Error Handling Strategy**: Defined user feedback approach
   - Decision: Inline validation errors, card-based auth failures
   - Rationale: Security-conscious messaging, clear guidance

### Architectural Decisions (ADRs suggested but not required)

- **AD-001**: Auth State Management Pattern (Context + useReducer)
- **AD-002**: Route Protection Approach (Route groups + layouts)
- **AD-003**: API Client Architecture (Singleton class)
- **AD-004**: Mocked Storage (localStorage for state + users)
- **AD-005**: Form Validation Library (React Hook Form + Zod)

### Unknowns Resolution Status

All unknowns resolved. No blockers for Phase 1.

---

## Phase 1: Design & Contracts ✅ COMPLETE

**Objective**: Define data models, API contracts, and implementation guide.

**Outputs**:
- `data-model.md` (see [data-model.md](./data-model.md))
- `contracts/api-client.interface.ts` (see [contracts/api-client.interface.ts](./contracts/api-client.interface.ts))
- `quickstart.md` (see [quickstart.md](./quickstart.md))
- Updated `CLAUDE.md` with new patterns

### 1.1 Data Model Design ✅

**Entities Defined**:
1. **User**: Authenticated user entity (id, email, name, createdAt)
2. **AuthState**: Current auth context state (user, token, isLoading, error)
3. **AuthAction**: Discriminated union of all auth actions (9 action types)
4. **APIResponse<T>**: Generic response structure (success, data, error, statusCode)
5. **MockedUser**: Internal user storage structure (includes passwordHash)
6. **LoginFormData**: Login form validation shape
7. **RegisterFormData**: Registration form validation shape

**Key Design Decisions**:
- AuthState mirrors task-context pattern (state + actions separation)
- User entity matches expected backend structure (ready for SQLModel)
- APIResponse follows FastAPI conventions
- All entities TypeScript strict mode compliant

**Validation Rules**:
- Email: 1-320 chars, email regex
- Password: 8-128 chars (mocked, no complexity)
- All IDs: UUID v4 format

**Storage Strategy**:
- `auth-state` localStorage key: `{ user, token }`
- `mocked-users` localStorage key: `{ [email]: MockedUser }`
- Pre-populated test user: `test@example.com` / `password123`

### 1.2 API Contracts ✅

**Interface**: `IAPIClient` combining `AuthAPI` + `TaskAPI`

**Auth Methods**:
- `login(email, password)`: Returns `APIResponse<{ user, token }>`
- `register(email, password)`: Returns `APIResponse<{ user, token }>`
- `logout()`: Returns `APIResponse<void>`

**Task Methods** (with auth):
- `getTasks()`: Returns `APIResponse<Task[]>` (requires auth header)
- `createTask(data)`: Returns `APIResponse<Task>` (requires auth header)
- `updateTask(id, data)`: Returns `APIResponse<Task>` (requires auth header)
- `deleteTask(id)`: Returns `APIResponse<void>` (requires auth header)

**Response Structure** (all methods):
```typescript
{
  success: boolean
  data: T | null
  error: string | null
  statusCode: number
}
```

**Expected Backend Routes** (future):
- POST `/api/auth/login`
- POST `/api/auth/register`
- POST `/api/auth/logout`
- GET/POST/PATCH/DELETE `/api/tasks` (protected)

### 1.3 Implementation Guide ✅

**Quickstart Document**: Step-by-step implementation order

**Implementation Sequence**:
1. Types & Interfaces (15 min)
2. Auth Utilities (20 min)
3. API Client (30 min)
4. Auth Context (30 min)
5. Auth Components (60 min)
6. Auth Pages (30 min)
7. Route Protection (45 min)
8. Root Layout Integration (15 min)

**Total Estimated Time**: ~4 hours

**File Checklist**:
- 12 new files
- 1 modified file
- ~800-1200 lines of code

**Testing Checklist**: 6 user stories × 5 scenarios = 30 test cases

### 1.4 Agent Context Update ✅

Updated `CLAUDE.md` with:
- Language: TypeScript 5.x (Next.js 16 App Router, React 19)
- Database: localStorage for mocked session persistence

---

## Phase 2: Task Breakdown (Next Command)

**Status**: Ready for `/sp.tasks` command

**Objective**: Generate dependency-ordered, testable task list in `tasks.md`

**Expected Output**:
- Tasks organized by implementation sequence
- Each task with acceptance criteria
- Dependencies clearly marked
- Estimated effort per task

**Command**: Run `/sp.tasks` to proceed to task generation phase.

---

## Implementation Readiness Summary

### Constitution Compliance ✅
- All applicable principles satisfied
- Backend-specific principles deferred (frontend-only feature)
- Architecture prepared for future backend integration

### Research Complete ✅
- 8 research tasks completed
- 5 architectural decisions documented
- All unknowns resolved
- No blockers identified

### Design Artifacts ✅
- Data model: 7 entities defined
- API contracts: 8 methods specified
- Implementation guide: 8-step sequence documented
- Agent context: Updated with new patterns

### Quality Gates ✅
- Spec-driven workflow followed
- Existing patterns reused (task-context, task-form)
- Type safety enforced (TypeScript strict mode)
- Accessibility considered (keyboard nav, ARIA)
- Performance targets defined (<500ms render, <100ms validation)

### Risk Mitigation ✅
- localStorage fallback for private browsing
- Loading states prevent flash of unprotected content
- Error handling covers all failure modes
- Token expiry simulation (24 hours)

**Status**: ✅ READY FOR TASK GENERATION (`/sp.tasks`)

---

## Appendix: Key Files Reference

| File | Purpose | Lines | Complexity |
|------|---------|-------|-----------|
| `types/auth.ts` | Type definitions | ~80 | Low |
| `lib/auth-utils.ts` | Helper functions | ~150 | Medium |
| `lib/api-client.ts` | API client singleton | ~200 | Medium |
| `context/auth-context.tsx` | State management | ~120 | Medium |
| `components/auth/login-form.tsx` | Login UI | ~100 | Low |
| `components/auth/register-form.tsx` | Register UI | ~120 | Low |
| `app/(auth)/layout.tsx` | Public layout | ~30 | Low |
| `app/(protected)/layout.tsx` | Protected layout | ~60 | Medium |
| `app/(auth)/login/page.tsx` | Login page | ~40 | Low |
| `app/(auth)/register/page.tsx` | Register page | ~40 | Low |

**Total**: ~940 lines across 10 primary files + validation schemas + pages

**Complexity Distribution**:
- Low: 6 files (UI components, pages)
- Medium: 4 files (utilities, context, API client, protected layout)
- High: 0 files

**Testing Surface**:
- Unit tests: auth-utils, api-client (future)
- Integration tests: auth flows (manual for now)
- E2E tests: full registration → login → logout flow (future)
