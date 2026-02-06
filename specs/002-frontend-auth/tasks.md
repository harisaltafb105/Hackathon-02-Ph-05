---
description: "Task list for Frontend Auth & API Readiness implementation"
---

# Tasks: Frontend Auth & API Readiness

**Input**: Design documents from `/specs/002-frontend-auth/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

**Tests**: This feature does NOT include automated tests. Manual testing against acceptance scenarios only.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Web app**: All changes in `frontend/` directory
- Base paths: `frontend/app/`, `frontend/components/`, `frontend/lib/`, `frontend/context/`, `frontend/types/`

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Create type definitions and utility functions shared across all user stories

- [x] T001 Create auth type definitions in frontend/types/auth.ts (User, AuthState, AuthAction, APIResponse, LoginFormData, RegisterFormData)
- [x] T002 [P] Create form validation schemas in frontend/lib/validations/auth.ts (loginSchema, registerSchema using Zod)
- [x] T003 [P] Create auth utility functions in frontend/lib/auth-utils.ts (generateUserId, generateToken, getMockedUsers, saveMockedUser, getAuthState, saveAuthState, clearAuthState, isTokenExpired)

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [x] T004 Implement API client singleton in frontend/lib/api-client.ts (APIClient class with login, register, logout, getTasks, createTask, updateTask, deleteTask methods)
- [x] T005 Implement auth context provider in frontend/context/auth-context.tsx (AuthProvider, useAuth, useAuthActions hooks with authReducer)
- [x] T006 Update root layout to wrap children in AuthProvider in frontend/app/layout.tsx
- [x] T007 [P] Create route group directory structure: frontend/app/(auth)/ and frontend/app/(protected)/
- [x] T008 Pre-populate mocked user store with test user (test@example.com / password123) in auth-utils initialization

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - User Registration Flow (Priority: P1) 🎯 MVP

**Goal**: New users can create accounts with email/password, see validation errors, and be redirected to dashboard on success

**Independent Test**: Navigate to `/register`, fill valid email and password, submit, verify redirect to `/dashboard` with user email shown in header

### Implementation for User Story 1

- [x] T009 [P] [US1] Create RegisterForm component in frontend/components/auth/register-form.tsx (React Hook Form + Zod validation, email, password, confirmPassword fields)
- [x] T010 [P] [US1] Create registration page in frontend/app/(auth)/register/page.tsx (renders RegisterForm in centered card layout)
- [x] T011 [US1] Connect RegisterForm to auth context (dispatch REGISTER_START, call apiClient.register, dispatch REGISTER_SUCCESS/FAILURE)
- [x] T012 [US1] Implement register method in apiClient (check email uniqueness in mocked-users, create user, generate token, save to localStorage)
- [x] T013 [US1] Add form validation error display (inline errors below fields for email format, password length, password mismatch)
- [x] T014 [US1] Add loading state during registration (disable form, show spinner on submit button)
- [x] T015 [US1] Implement redirect to /dashboard on successful registration
- [x] T016 [US1] Add "Already have an account? Sign in" link to login page

**Checkpoint**: At this point, User Story 1 should be fully functional - users can register, see errors, and access dashboard

**Test Cases** (Manual):
1. Valid registration: email + password → redirect to dashboard
2. Invalid email format → see error "Please enter a valid email address"
3. Short password (<8 chars) → see error "Password must be at least 8 characters"
4. Password mismatch → see error "Passwords don't match"
5. Duplicate email → see error "Email already registered"
6. Loading state: form disabled during submission

---

## Phase 4: User Story 2 - User Login Flow (Priority: P1)

**Goal**: Existing users can authenticate with email/password, session persists across refreshes, and authenticated users auto-redirect from /login

**Independent Test**: Navigate to `/login`, enter test@example.com / password123, verify redirect to `/dashboard`, refresh page and remain authenticated

### Implementation for User Story 2

- [x]  [P] [US2] Create LoginForm component in frontend/components/auth/login-form.tsx (React Hook Form + Zod validation, email and password fields)
- [x]  [P] [US2] Create login page in frontend/app/(auth)/login/page.tsx (renders LoginForm in centered card layout)
- [x]  [US2] Connect LoginForm to auth context (dispatch LOGIN_START, call apiClient.login, dispatch LOGIN_SUCCESS/FAILURE)
- [x]  [US2] Implement login method in apiClient (verify email exists, check password match, return user + token)
- [x]  [US2] Add session persistence logic in auth-context (save to localStorage on LOGIN_SUCCESS, restore on mount via RESTORE_SESSION)
- [x]  [US2] Add "Don't have an account? Sign up" link to registration page
- [x]  [US2] Implement auto-focus on email field when login page loads
- [x]  [US2] Add "Invalid email or password" error display (security-conscious message, doesn't reveal if email exists)

**Checkpoint**: At this point, User Stories 1 AND 2 should both work - users can register OR login, and sessions persist

**Test Cases** (Manual):
1. Correct credentials → redirect to dashboard
2. Wrong password → see error "Invalid email or password"
3. Non-existent email → see error "Invalid email or password"
4. Session persistence → login, refresh page, remain authenticated
5. Loading state → form disabled during login

---

## Phase 5: User Story 3 - Protected Route Access (Priority: P2)

**Goal**: Unauthenticated users are redirected to /login when accessing protected routes, authenticated users can freely navigate protected areas

**Independent Test**: While logged out, navigate to `/dashboard` → redirect to `/login`. While logged in, navigate to `/dashboard` → see dashboard content.

### Implementation for User Story 3

- [x]  [US3] Create public layout in frontend/app/(auth)/layout.tsx (redirect to /dashboard if authenticated, minimal header for auth pages)
- [x]  [US3] Create protected layout in frontend/app/(protected)/layout.tsx (redirect to /login if not authenticated, show user email and logout button in header)
- [x]  [US3] Move existing home page to frontend/app/(protected)/dashboard/page.tsx (existing task list becomes dashboard)
- [x]  [US3] Add loading skeleton to protected layout while auth state is being checked
- [x]  [US3] Implement redirect preservation (save original URL when redirected to login, redirect back after successful login)

**Checkpoint**: All protected routes now require authentication, public routes redirect authenticated users away

**Test Cases** (Manual):
1. Unauthenticated access to /dashboard → redirect to /login
2. Unauthenticated access to /tasks → redirect to /login
3. Authenticated access to /dashboard → see content
4. Authenticated access to /tasks → see content
5. Login from protected route redirect → redirect back to original route
6. Authenticated access to /login → redirect to /dashboard
7. Authenticated access to /register → redirect to /dashboard

---

## Phase 6: User Story 4 - User Logout (Priority: P2)

**Goal**: Authenticated users can end their session, clearing auth state and returning to login page

**Independent Test**: While logged in, click logout button, verify auth cleared and redirected to /login, attempt to access /dashboard → redirect to /login

### Implementation for User Story 4

- [x]  [US4] Add logout button to protected layout header in frontend/app/(protected)/layout.tsx (with LogOut icon from lucide-react)
- [x]  [US4] Implement logout handler (dispatch LOGOUT action, call apiClient.logout, redirect to /login)
- [x]  [US4] Implement logout method in apiClient (clear token, simulate network delay, return success)
- [x]  [US4] Add loading state to logout button (show spinner during logout process)
- [x]  [US4] Clear localStorage on LOGOUT action in authReducer

**Checkpoint**: Users can fully log out, clearing all auth data

**Test Cases** (Manual):
1. Click logout → auth cleared, redirect to /login
2. After logout → localStorage cleared (check DevTools)
3. After logout → /dashboard access blocked, redirect to /login
4. Logout loading state → brief loading indicator shown

---

## Phase 7: User Story 5 - API Client Integration (Priority: P3)

**Goal**: API client automatically attaches Authorization headers when authenticated and handles 401 errors by auto-logout

**Independent Test**: Login, trigger any API method (getTasks), verify Authorization header sent (check Network tab), simulate 401 error, verify auto-logout to /login

### Implementation for User Story 5

- [x]  [US5] Update apiClient to inject token into Authorization header for all requests (read from auth-context token)
- [x]  [US5] Implement 401 error handling in apiClient (detect 401 status, dispatch LOGOUT, redirect to /login)
- [x]  [US5] Update task CRUD methods in apiClient to return APIResponse<T> format (getTasks, createTask, updateTask, deleteTask)
- [x]  [US5] Add network delay simulation to all apiClient methods (300-800ms random delay)
- [x]  [US5] Connect existing task operations to use apiClient methods (replace direct localStorage calls in task-context)

**Checkpoint**: API client fully integrated with auth system, ready for backend swap

**Test Cases** (Manual):
1. Authenticated request → Authorization header included (check Network tab)
2. Unauthenticated request → no Authorization header
3. Simulated 401 response → auto-logout and redirect to /login
4. Network delay visible → operations take 300-800ms
5. All API methods return consistent APIResponse format

---

## Phase 8: User Story 6 - Form Validation & Error Handling (Priority: P3)

**Goal**: All auth forms provide immediate validation feedback, clear error messages, and proper accessibility

**Independent Test**: On login/register forms, enter invalid inputs and verify error messages appear correctly below fields, focus moves to first error on submit

### Implementation for User Story 6

- [x]  [P] [US6] Enhance LoginForm with inline error display (red text below fields, error icons from lucide-react)
- [x]  [P] [US6] Enhance RegisterForm with inline error display (red text below fields, error icons)
- [x]  [US6] Add focus management (move focus to first error field on validation failure)
- [x]  [US6] Implement error clearing on re-submit (clear old errors when user fixes and resubmits)
- [x]  [US6] Add user-friendly error messages (use messages from spec: "Please enter a valid email address", "Password must be at least 8 characters", "Passwords don't match")
- [x]  [US6] Add ARIA labels for accessibility (aria-invalid, aria-describedby for error messages)
- [x]  [US6] Add password visibility toggle (Eye/EyeOff icons, show/hide password feature)

**Checkpoint**: All forms have professional validation and error handling

**Test Cases** (Manual):
1. Invalid email → see error below email field
2. Short password → see error below password field
3. Submit with errors → focus moves to first error field
4. Fix errors and re-submit → old errors cleared
5. All error messages are user-friendly (not technical)
6. Password toggle → can show/hide password text

---

## Phase 9: Polish & Cross-Cutting Concerns

**Purpose**: Final improvements affecting multiple user stories

- [x]  [P] Add animations to auth pages (Framer Motion fade + slide transitions matching existing modal patterns)
- [x]  [P] Add animations to form submissions (button scale on click, success checkmark animation)
- [x]  [P] Add animations to error messages (slide down with spring physics)
- [x]  [P] Ensure consistent spacing with existing app (8px grid system, matching card styles)
- [x]  [P] Ensure consistent typography (text-3xl/4xl for headings, text-sm for body, matching existing app)
- [x]  [P] Ensure consistent color scheme (use OKLCH color space variables: --primary, --destructive, --muted-foreground)
- [x]  Add keyboard navigation testing (Tab through all forms, Enter to submit)
- [x]  Add responsive testing (mobile <640px, tablet 640-1024px, desktop >1024px)
- [x]  Test token expiry simulation (verify 24-hour expiry triggers auto-logout)
- [x]  Test localStorage fallback (verify app handles disabled localStorage gracefully)
- [x]  Run production build and verify no TypeScript errors
- [x]  Test all 30 acceptance scenarios from spec.md (6 user stories × 5 scenarios each)
- [x]  Verify bundle size acceptable (~500KB total for frontend)
- [x]  Create quickstart verification checklist and validate all items pass

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3-8)**: All depend on Foundational phase completion
  - User stories CAN proceed in parallel (if staffed) after Phase 2 complete
  - Or sequentially in priority order (US1 → US2 → US3 → US4 → US5 → US6)
- **Polish (Phase 9)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1) - Registration**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 2 (P1) - Login**: Can start after Foundational (Phase 2) - Independent of US1 (but complements it)
- **User Story 3 (P2) - Route Protection**: Depends on US1 OR US2 (need way to authenticate first)
- **User Story 4 (P2) - Logout**: Depends on US2 (need to be logged in to log out)
- **User Story 5 (P3) - API Client**: Can start after Foundational (Phase 2) - Enhances US1-4 but independently testable
- **User Story 6 (P3) - Form Validation**: Enhances US1-2 - Can be implemented during or after those stories

### Within Each User Story

- Models/Types first (T001-T003 in Setup)
- Core services next (T004-T005 in Foundational)
- UI components (forms, pages) after services available
- Integration and error handling last
- Story complete before moving to next priority

### Parallel Opportunities

#### Phase 1 (Setup) - All parallel:
```bash
Task T001: Create auth types
Task T002: Create validation schemas
Task T003: Create auth utilities
```

#### Phase 2 (Foundational) - Some parallel:
```bash
Task T004: API client (sequential - foundational)
Task T005: Auth context (depends on T004 completion)
Task T006: Root layout update (depends on T005 completion)
Task T007: Directory structure (parallel with T004)
Task T008: Pre-populate users (depends on T003)
```

#### User Story 1 - Parallel forms + pages:
```bash
Task T009: RegisterForm component
Task T010: Register page
# These can be built in parallel, then connected
```

#### User Story 2 - Parallel forms + pages:
```bash
Task T017: LoginForm component
Task T018: Login page
# These can be built in parallel, then connected
```

#### User Story 6 - All enhancements parallel:
```bash
Task T040: Enhance LoginForm errors
Task T041: Enhance RegisterForm errors
# Different files, no dependencies
```

#### Phase 9 (Polish) - Most parallel:
```bash
Task T047: Page animations
Task T048: Form animations
Task T049: Error animations
Task T050: Spacing consistency
Task T051: Typography consistency
Task T052: Color scheme consistency
# All different concerns, can be done in parallel
```

---

## Parallel Example: User Story 1 (Registration)

```bash
# Step 1: Launch form and page creation in parallel
Task: "Create RegisterForm component in frontend/components/auth/register-form.tsx"
Task: "Create registration page in frontend/app/(auth)/register/page.tsx"

# Step 2: After forms exist, connect them (sequential)
Task: "Connect RegisterForm to auth context"
Task: "Implement register method in apiClient"
Task: "Add form validation error display"
```

---

## Parallel Example: Phase 9 (Polish)

```bash
# All animation tasks can run in parallel (different concerns):
Task: "Add animations to auth pages"
Task: "Add animations to form submissions"
Task: "Add animations to error messages"

# All consistency tasks can run in parallel:
Task: "Ensure consistent spacing"
Task: "Ensure consistent typography"
Task: "Ensure consistent color scheme"
```

---

## Implementation Strategy

### MVP First (User Stories 1 + 2 Only)

1. Complete Phase 1: Setup (T001-T003)
2. Complete Phase 2: Foundational (T004-T008) - CRITICAL
3. Complete Phase 3: User Story 1 - Registration (T009-T016)
4. Complete Phase 4: User Story 2 - Login (T017-T024)
5. **STOP and VALIDATE**: Test registration and login flows independently
6. Deploy/demo if ready → Users can now register and login!

### Incremental Delivery

1. Complete Setup + Foundational (T001-T008) → Foundation ready
2. Add User Story 1 (T009-T016) → Test independently → **MVP Milestone: Registration works**
3. Add User Story 2 (T017-T024) → Test independently → **Milestone: Login + Registration work**
4. Add User Story 3 (T025-T029) → Test independently → **Milestone: Route protection active**
5. Add User Story 4 (T030-T034) → Test independently → **Milestone: Full auth cycle (register/login/logout)**
6. Add User Story 5 (T035-T039) → Test independently → **Milestone: API client integrated**
7. Add User Story 6 (T040-T046) → Test independently → **Milestone: Professional validation**
8. Add Polish (T047-T060) → Final validation → **COMPLETE: Production-ready frontend auth**

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together (T001-T008)
2. Once Foundational is done:
   - **Developer A**: User Story 1 - Registration (T009-T016)
   - **Developer B**: User Story 2 - Login (T017-T024)
   - **Developer C**: User Story 5 - API Client enhancements (T035-T039)
3. After US1 & US2 complete:
   - **Developer A**: User Story 3 - Route Protection (T025-T029)
   - **Developer B**: User Story 4 - Logout (T030-T034)
   - **Developer C**: User Story 6 - Form Validation (T040-T046)
4. Team completes Polish together (T047-T060)

---

## Task Summary

**Total Tasks**: 60

**By Phase**:
- Phase 1 (Setup): 3 tasks (T001-T003)
- Phase 2 (Foundational): 5 tasks (T004-T008)
- Phase 3 (US1 - Registration): 8 tasks (T009-T016)
- Phase 4 (US2 - Login): 8 tasks (T017-T024)
- Phase 5 (US3 - Route Protection): 5 tasks (T025-T029)
- Phase 6 (US4 - Logout): 5 tasks (T030-T034)
- Phase 7 (US5 - API Client): 5 tasks (T035-T039)
- Phase 8 (US6 - Form Validation): 7 tasks (T040-T046)
- Phase 9 (Polish): 14 tasks (T047-T060)

**By User Story**:
- US1 (Registration): 8 tasks
- US2 (Login): 8 tasks
- US3 (Route Protection): 5 tasks
- US4 (Logout): 5 tasks
- US5 (API Client): 5 tasks
- US6 (Form Validation): 7 tasks

**Parallelizable Tasks**: 18 tasks marked [P]

**Estimated Total Effort**: ~6-8 hours for full implementation (4 hours core + 2-4 hours polish)

**MVP Scope** (User Stories 1 + 2 only): ~2-3 hours (T001-T024)

---

## Notes

- [P] tasks = different files, no dependencies within their phase
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- No automated tests included (manual testing against acceptance scenarios)
- Commit after each task or logical group of related tasks
- Stop at any checkpoint to validate story independently
- Architecture designed for seamless Better Auth SDK integration (no frontend refactor needed)
- All mocked auth logic uses localStorage (ready for real backend swap)
