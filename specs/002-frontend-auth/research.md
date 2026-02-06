# Research: Frontend Auth & API Readiness

**Feature**: 002-frontend-auth
**Date**: 2026-01-07
**Phase**: 0 (Research & Decision Documentation)

## Overview

This document captures research findings and architectural decisions for implementing frontend authentication with mocked state management. All decisions prioritize alignment with existing patterns and prepare for seamless Better Auth SDK integration.

## Research Tasks Completed

### 1. Existing Pattern Analysis

**Task**: Analyze existing `task-context.tsx` pattern for state management consistency

**Findings**:
- Uses React Context + useReducer pattern
- Separates state (`useTasks()`) from actions (`useTaskActions()`)
- Actions defined as discriminated union types
- State includes both data and UI state (`{ tasks, ui }`)
- Persistent state via localStorage (loaded on mount)

**Decision**: AuthContext will mirror this exact pattern
- `useAuth()` for reading state
- `useAuthActions()` for dispatching actions
- AuthState = `{ user, isAuthenticated, isLoading, token }`
- Persist to localStorage with key `auth-state`

**Rationale**: Consistency with existing codebase, familiar to developers working on tasks, proven pattern.

---

### 2. Form Validation Pattern

**Task**: Analyze existing `task-form.tsx` for form validation approach

**Findings**:
- Uses React Hook Form with Zod schema validation
- Form component receives `mode` prop ('add' | 'edit')
- Validation runs on blur and submit
- Error messages displayed inline below fields
- Loading state disables form during async operations

**Decision**: Auth forms will use identical pattern
- LoginForm: email + password fields with Zod validation
- RegisterForm: email + password + confirmPassword with Zod validation
- Same error display approach (inline below fields)
- Same loading state handling (disabled form + spinner)

**Rationale**: Consistency, leverage existing Zod schemas, familiar UX patterns.

---

### 3. Route Protection Strategies (Next.js 16 App Router)

**Task**: Research best practices for route protection in Next.js 16 App Router

**Options Considered**:

**Option A: Middleware-based protection**
- Pros: Centralized logic, runs before page render, can redirect early
- Cons: Middleware runs on edge, localStorage not available

**Option B: Layout-based protection**
- Pros: Access to React Context, can read localStorage, flexible per-route-group
- Cons: Client-side only, flash of unprotected content possible

**Option C: Component-based HOC**
- Pros: Granular control, reusable
- Cons: Repetitive, boilerplate in every protected page

**Decision**: Hybrid approach using Route Groups + Layout protection
- Route groups: `(auth)` for public, `(protected)` for authenticated
- Each route group has its own layout
- Protected layout checks auth state, redirects if unauthenticated
- Public layout checks auth state, redirects if authenticated

**Rationale**: Best balance of simplicity and App Router patterns. Avoids middleware complexity while maintaining centralized protection per route group.

---

### 4. API Client Abstraction Design

**Task**: Design API client interface matching expected FastAPI backend

**Requirements from Spec**:
- Methods: `login()`, `register()`, `logout()`, `getTasks()`, `createTask()`, `updateTask()`, `deleteTask()`
- Auto-attach Authorization header when authenticated
- Handle 401 errors (auto-logout)
- Simulate network delay (300-800ms)
- Return consistent structure: `{ success, data, error, statusCode }`

**Decision**: Singleton class-based API client
```typescript
class APIClient {
  private baseURL = '/api' // Future backend endpoint

  private async request<T>(endpoint: string, options?: RequestInit): Promise<APIResponse<T>> {
    // Simulate network delay
    await delay(300 + Math.random() * 500)

    // Attach auth header if token exists
    const token = getToken()
    if (token) {
      options.headers = { ...options.headers, Authorization: `Bearer ${token}` }
    }

    // Mocked fetch (will be replaced with real fetch)
    return mockResponse()
  }

  // Auth methods
  async login(email: string, password: string): Promise<APIResponse<User>>
  async register(email: string, password: string): Promise<APIResponse<User>>
  async logout(): Promise<APIResponse<void>>

  // Task methods (mocked)
  async getTasks(): Promise<APIResponse<Task[]>>
  async createTask(data: CreateTaskInput): Promise<APIResponse<Task>>
  async updateTask(id: string, data: UpdateTaskInput): Promise<APIResponse<Task>>
  async deleteTask(id: string): Promise<APIResponse<void>>
}

export const apiClient = new APIClient()
```

**Rationale**:
- Singleton pattern provides single point of configuration
- Class structure easy to extend
- Method signatures match expected FastAPI endpoints
- Header injection centralized in `request()` method
- Easy to swap mocked implementation for real fetch

---

### 5. Mocked Authentication Logic

**Task**: Define mocked authentication behavior for realistic simulation

**Mocked User Store**:
- Stored in localStorage under key `mocked-users`
- Structure: `{ [email]: { id, email, name, passwordHash, createdAt } }`
- Pre-populate with test user: `test@example.com` / `password123`

**Registration Logic**:
1. Validate email format
2. Check if email already exists in mocked store
3. If exists, return error "Email already registered"
4. Generate mocked user ID (UUID)
5. Store user in mocked store (password stored as plain text for mocking)
6. Generate mocked token (simple string: `mock-token-${userId}`)
7. Return success with user data

**Login Logic**:
1. Validate email format
2. Check if email exists in mocked store
3. If not exists, return error "Invalid email or password"
4. Check if password matches (simple string comparison for mocking)
5. If mismatch, return error "Invalid email or password"
6. Generate mocked token
7. Return success with user data and token

**Logout Logic**:
1. Clear token from localStorage
2. Clear auth state
3. Redirect to /login

**Token Expiry Simulation**:
- Tokens include timestamp in localStorage
- On app load, check if token is older than 24 hours
- If expired, auto-logout

**Decision**: Implement above mocked logic in `lib/auth-utils.ts`

**Rationale**: Provides realistic UX without real authentication complexity, allows testing all error cases, prepares structure for real auth replacement.

---

### 6. Layout System Design

**Task**: Design public vs protected layout structure

**Public Layout** (`app/(auth)/layout.tsx`):
- Minimal header (app name/logo only)
- No user menu, no logout button
- Centered form container with card styling
- Redirect to /dashboard if already authenticated

**Protected Layout** (`app/(protected)/layout.tsx`):
- Full header with user name display
- Logout button in header
- Same sidebar/navigation as existing app
- Redirect to /login if not authenticated

**Root Layout** (`app/layout.tsx`):
- Wrap children in AuthProvider
- Existing TaskProvider remains
- Providers composition: `<AuthProvider><TaskProvider>{children}</TaskProvider></AuthProvider>`

**Decision**: Implement above structure using Next.js route groups

**Rationale**: Clean separation of concerns, automatic layout switching based on route, no conditional logic in individual pages.

---

### 7. Animation and Transition Patterns

**Task**: Determine animation approach for auth pages

**Existing Patterns**:
- Modal animations use Framer Motion with `initial`, `animate`, `exit`
- Scale + opacity transitions (0.95 → 1 scale, 0 → 1 opacity)
- Spring physics (stiffness: 300, damping: 20)
- Duration: 200ms

**Decision**: Apply same animation patterns to auth pages
- Page transitions: fade + slide (opacity 0→1, y 20→0)
- Form submission: button scale down slightly on click
- Error messages: slide down with red color
- Success feedback: green checkmark with scale animation

**Rationale**: Consistency with existing app feel, smooth professional UX.

---

### 8. Error Handling Strategy

**Task**: Define error handling and user feedback approach

**Error Types**:
1. **Validation Errors**: Inline below form fields (red text, icon)
2. **Authentication Errors**: Display above form (card with destructive styling)
3. **Network Errors**: Toast notification or inline error
4. **401 Auto-logout**: Silent redirect to /login with message

**User-Friendly Messages**:
- "Invalid email or password" (not "User not found" - security best practice)
- "Email already registered" (registration collision)
- "Please enter a valid email address" (format validation)
- "Password must be at least 8 characters" (length validation)
- "Passwords do not match" (confirmation mismatch)

**Decision**: Use inline errors for validation, card-based alerts for auth failures

**Rationale**: Clear user guidance, security-conscious messaging, consistent with existing form patterns.

---

## Architectural Decisions Summary

### AD-001: Auth State Management Pattern
**Decision**: Use React Context + useReducer matching task-context pattern
**Alternatives**: Redux, Zustand, custom hooks
**Rationale**: Consistency with existing codebase, no new dependencies, familiar pattern

### AD-002: Route Protection Approach
**Decision**: Route groups with layout-based protection
**Alternatives**: Middleware-based, HOC per page, server components
**Rationale**: Best fit for Next.js 16 App Router, access to client-side storage, centralized per group

### AD-003: API Client Architecture
**Decision**: Singleton class with mocked methods
**Alternatives**: Functional API, React Query, SWR
**Rationale**: Simple swap to real implementation, centralized header injection, no new dependencies

### AD-004: Mocked Authentication Storage
**Decision**: localStorage for both auth state and mocked user database
**Alternatives**: In-memory only, sessionStorage, IndexedDB
**Rationale**: Persists across refreshes, simple API, matches existing task storage pattern

### AD-005: Form Validation Library
**Decision**: React Hook Form + Zod (existing pattern)
**Alternatives**: Formik, native HTML5 validation, custom validation
**Rationale**: Already in use for task forms, type-safe schemas, excellent DX

## Unknowns and Risks

### Resolved During Research
- ✅ How to protect routes in Next.js 16 App Router → Route groups + layout protection
- ✅ How to persist auth state → localStorage with same pattern as tasks
- ✅ How to structure API client → Singleton class ready for backend swap
- ✅ Form validation approach → Reuse existing React Hook Form + Zod

### Remaining Risks
- **Risk**: localStorage disabled in private browsing
  - **Mitigation**: Detect and show friendly error message, app still functional but won't persist
- **Risk**: Race condition between auth check and page render
  - **Mitigation**: Use loading state in layout, show skeleton until auth resolved
- **Risk**: Flash of unauthenticated content
  - **Mitigation**: Layout protection runs early, redirect before children render

## Next Steps

Proceed to Phase 1: Design & Contracts
- Generate data-model.md with User, AuthState, APIResponse entities
- Generate contracts/ with API client interface
- Generate quickstart.md with setup instructions
- Update agent context with new patterns
