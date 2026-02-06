# Feature Specification: Backend API with Authentication

**Feature Branch**: `003-backend-api`
**Created**: 2026-01-07
**Status**: Ready
**Input**: User description: "Implement a production-quality FastAPI backend with SQLModel ORM, Neon PostgreSQL database, and Better Auth JWT authentication. The backend must provide RESTful CRUD endpoints for task management with strict user isolation (all operations scoped to authenticated user). Requirements: (1) Environment configuration via BETTER_AUTH_URL, BETTER_AUTH_SECRET, DATABASE_URL; (2) JWT verification from Authorization headers to extract user_id; (3) Task model with UUID id, title, description, completed (bool), created_at, updated_at, user_id (FK); (4) Endpoints: GET/POST /api/{user_id}/tasks, GET/PUT/DELETE/PATCH /api/{user_id}/tasks/{task_id}; (5) Proper HTTP status codes and JSON error responses; (6) Development via uv run backend.main:app --reload; (7) No frontend changes required - backend must match existing API client expectations."

## User Scenarios & Testing

### User Story 1 - Task Retrieval (Priority: P1)

As an authenticated user, I want to retrieve all my tasks from the backend so that I can see my task list in the frontend application.

**Why this priority**: This is the foundational read operation that enables users to view their data. Without this, the application cannot display any tasks, making it the most critical endpoint.

**Independent Test**: Can be fully tested by authenticating as a user, making a GET request to `/api/{user_id}/tasks`, and verifying that only tasks belonging to that user are returned. Delivers immediate value by enabling task viewing.

**Acceptance Scenarios**:

1. **Given** a user is authenticated with a valid JWT token, **When** they request GET `/api/{user_id}/tasks`, **Then** the system returns a 200 OK response with a JSON array of all tasks belonging to that user
2. **Given** a user is authenticated, **When** they request their tasks, **Then** the system returns only tasks where `user_id` matches the authenticated user's ID (strict user isolation)
3. **Given** a user has no tasks, **When** they request their tasks, **Then** the system returns a 200 OK response with an empty array
4. **Given** a user is not authenticated (no token), **When** they request tasks, **Then** the system returns a 401 Unauthorized response
5. **Given** a user is authenticated, **When** they request another user's tasks via `/api/{other_user_id}/tasks`, **Then** the system returns a 403 Forbidden response

---

### User Story 2 - Task Creation (Priority: P1)

As an authenticated user, I want to create new tasks via the backend so that I can add items to my task list.

**Why this priority**: Task creation is equally critical as retrieval, as it enables users to actually add data to the system. Together with retrieval (US1), it forms the minimum viable backend functionality.

**Independent Test**: Can be tested by authenticating as a user, POSTing a task with title and description to `/api/{user_id}/tasks`, and verifying the task is created with the authenticated user's ID.

**Acceptance Scenarios**:

1. **Given** a user is authenticated, **When** they POST to `/api/{user_id}/tasks` with valid JSON containing `title` and optional `description`, **Then** the system creates a new task with a generated UUID, sets `completed` to false, sets `created_at` and `updated_at` timestamps, associates it with the user's ID, and returns 201 Created with the task object
2. **Given** a user is authenticated, **When** they POST a task without a required `title` field, **Then** the system returns a 422 Unprocessable Entity response with validation error details
3. **Given** a user is authenticated, **When** they POST a task to another user's endpoint `/api/{other_user_id}/tasks`, **Then** the system returns a 403 Forbidden response
4. **Given** a user is not authenticated, **When** they attempt to create a task, **Then** the system returns a 401 Unauthorized response

---

### User Story 3 - Task Update (Priority: P2)

As an authenticated user, I want to update my existing tasks (toggle completion, edit title/description) so that I can manage my task list.

**Why this priority**: Update operations enable users to modify task state (mark complete/incomplete) and edit task content. This is essential for a functional task manager but can be tested independently after creation works.

**Independent Test**: Can be tested by creating a task, then updating it via PUT or PATCH to `/api/{user_id}/tasks/{task_id}`, and verifying the changes are persisted and returned correctly.

**Acceptance Scenarios**:

1. **Given** a user owns a task, **When** they PUT to `/api/{user_id}/tasks/{task_id}` with updated fields, **Then** the system updates the task, sets `updated_at` to current timestamp, and returns 200 OK with the updated task
2. **Given** a user owns a task, **When** they PATCH to `/api/{user_id}/tasks/{task_id}` with partial fields (e.g., only `completed: true`), **Then** the system updates only the specified fields and returns 200 OK
3. **Given** a user tries to update a task they don't own, **When** they PUT/PATCH to `/api/{user_id}/tasks/{other_users_task_id}`, **Then** the system returns a 403 Forbidden or 404 Not Found response
4. **Given** a user tries to update a non-existent task, **When** they PUT/PATCH to a non-existent task ID, **Then** the system returns a 404 Not Found response
5. **Given** a user provides invalid data, **When** they update a task, **Then** the system returns a 422 Unprocessable Entity response with validation errors

---

### User Story 4 - Task Deletion (Priority: P2)

As an authenticated user, I want to delete tasks from the backend so that I can remove items from my task list.

**Why this priority**: Deletion completes the CRUD operations. It's important for task management but lower priority than creation and retrieval since users can still manage tasks without it initially.

**Independent Test**: Can be tested by creating a task, then deleting it via DELETE to `/api/{user_id}/tasks/{task_id}`, and verifying it no longer appears in the task list.

**Acceptance Scenarios**:

1. **Given** a user owns a task, **When** they DELETE to `/api/{user_id}/tasks/{task_id}`, **Then** the system removes the task from the database and returns 204 No Content
2. **Given** a user tries to delete a task they don't own, **When** they DELETE to `/api/{user_id}/tasks/{other_users_task_id}`, **Then** the system returns a 403 Forbidden or 404 Not Found response
3. **Given** a user tries to delete a non-existent task, **When** they DELETE to a non-existent task ID, **Then** the system returns a 404 Not Found response
4. **Given** a user is not authenticated, **When** they attempt to delete a task, **Then** the system returns a 401 Unauthorized response

---

### User Story 5 - JWT Authentication Verification (Priority: P1)

As a system, I must verify JWT tokens from Better Auth on every request to ensure only authenticated users can access their data.

**Why this priority**: Authentication is the security foundation of the entire system. Without proper JWT verification, user isolation cannot be guaranteed, making this a P1 requirement that must work from day one.

**Independent Test**: Can be tested by making requests with valid tokens (should succeed), invalid tokens (should fail with 401), expired tokens (should fail with 401), and tokens with tampered claims (should fail with 401).

**Acceptance Scenarios**:

1. **Given** a request includes a valid JWT token in the Authorization header as `Bearer <token>`, **When** the system verifies the token using Better Auth secret, **Then** the system extracts the user_id claim and allows the request to proceed
2. **Given** a request has no Authorization header, **When** the system checks authentication, **Then** the system returns 401 Unauthorized with error message "Authentication required"
3. **Given** a request has an invalid JWT token (malformed, wrong signature, expired), **When** the system verifies the token, **Then** the system returns 401 Unauthorized with error message "Invalid or expired token"
4. **Given** a valid JWT token with user_id claim, **When** the user attempts to access another user's resources, **Then** the system returns 403 Forbidden (user_id in URL doesn't match token user_id)

---

### Edge Cases

- **What happens when the database connection is lost?** The system should return 503 Service Unavailable with a clear error message, and FastAPI should log the database error for monitoring.

- **What happens when a user sends extremely large payloads (e.g., 10MB task description)?** The system should enforce request body size limits (e.g., 1MB) and return 413 Payload Too Large if exceeded.

- **What happens when concurrent requests try to update the same task?** The database should handle this with transactions and optimistic locking. The system should return the latest state after the update.

- **What happens when the JWT token is valid but the user_id doesn't exist in the database?** The system should return 401 Unauthorized with message "User not found" since the token represents a non-existent user.

- **What happens when a task title exceeds reasonable length (e.g., 10,000 characters)?** The system should enforce validation limits (e.g., title max 500 chars, description max 5000 chars) and return 422 Unprocessable Entity.

- **What happens when the DATABASE_URL environment variable is missing or invalid?** The application should fail to start with a clear error message indicating missing configuration.

- **What happens when Better Auth service is unreachable?** JWT verification should be done locally using the shared secret (BETTER_AUTH_SECRET), not by calling Better Auth on every request, so this shouldn't block requests.

## Requirements

### Functional Requirements

- **FR-001**: System MUST authenticate all API requests by verifying JWT tokens from the Authorization header using Better Auth secret
- **FR-002**: System MUST extract user_id from verified JWT claims and use it for all database operations
- **FR-003**: System MUST enforce strict user isolation - users can only access, create, update, or delete their own tasks
- **FR-004**: System MUST validate that the user_id in the request URL matches the user_id from the JWT token, returning 403 Forbidden if they don't match
- **FR-005**: System MUST provide a GET endpoint at `/api/{user_id}/tasks` that returns all tasks for the authenticated user
- **FR-006**: System MUST provide a POST endpoint at `/api/{user_id}/tasks` that creates a new task with auto-generated UUID, timestamps, and user association
- **FR-007**: System MUST provide a GET endpoint at `/api/{user_id}/tasks/{task_id}` that returns a specific task if owned by the user
- **FR-008**: System MUST provide a PUT endpoint at `/api/{user_id}/tasks/{task_id}` that updates all fields of a task owned by the user
- **FR-009**: System MUST provide a PATCH endpoint at `/api/{user_id}/tasks/{task_id}` that updates partial fields of a task owned by the user
- **FR-010**: System MUST provide a DELETE endpoint at `/api/{user_id}/tasks/{task_id}` that removes a task owned by the user
- **FR-011**: System MUST validate all request payloads using Pydantic models and return 422 Unprocessable Entity with error details for invalid data
- **FR-012**: System MUST return proper HTTP status codes: 200 OK (success with body), 201 Created (task created), 204 No Content (deletion success), 400 Bad Request (client error), 401 Unauthorized (auth failure), 403 Forbidden (authorization failure), 404 Not Found (resource not found), 422 Unprocessable Entity (validation error), 500 Internal Server Error (server error), 503 Service Unavailable (database unavailable)
- **FR-013**: System MUST return all error responses in consistent JSON format with `error` and `detail` fields
- **FR-014**: System MUST persist all tasks to Neon PostgreSQL database using SQLModel ORM
- **FR-015**: System MUST set `created_at` timestamp when creating tasks and update `updated_at` timestamp when modifying tasks
- **FR-016**: System MUST read configuration from environment variables: BETTER_AUTH_URL, BETTER_AUTH_SECRET, DATABASE_URL
- **FR-017**: System MUST be runnable via `uv run backend.main:app --reload` for development
- **FR-018**: System MUST match the API client interface already implemented in the frontend (no frontend changes required)
- **FR-019**: System MUST use UUID type for task IDs (not integers)
- **FR-020**: System MUST use boolean type for `completed` field (not string or integer)

### Key Entities

- **Task**: Represents a user's todo item
  - `id`: UUID (primary key, auto-generated)
  - `title`: String (required, max 500 chars)
  - `description`: String (optional, max 5000 chars)
  - `completed`: Boolean (required, defaults to false)
  - `created_at`: DateTime (auto-set on creation)
  - `updated_at`: DateTime (auto-set on creation and updates)
  - `user_id`: String (foreign key to user, required)

- **User**: Represents an authenticated user (managed by Better Auth, not stored in backend database)
  - `id`: String (from JWT token)
  - Referenced in tasks via `user_id` field

### Non-Functional Requirements

- **NFR-001**: System MUST use FastAPI framework with async/await patterns for optimal performance
- **NFR-002**: System MUST use SQLModel ORM for type-safe database operations
- **NFR-003**: System MUST connect to Neon PostgreSQL using connection pooling
- **NFR-004**: System MUST handle database connection errors gracefully and return 503 Service Unavailable
- **NFR-005**: System MUST log all authentication failures for security monitoring
- **NFR-006**: System MUST enforce CORS policy to allow requests from the frontend domain
- **NFR-007**: System MUST validate environment variables on startup and fail fast with clear error messages if missing
- **NFR-008**: System MUST use uv for dependency management and execution
- **NFR-009**: System MUST follow FastAPI best practices for dependency injection (authentication as dependency)
- **NFR-010**: System MUST include appropriate database indexes on user_id and id for query performance

## Success Criteria

### Measurable Outcomes

- **SC-001**: All CRUD operations (GET, POST, PUT, PATCH, DELETE) can be completed successfully via API endpoints
- **SC-002**: JWT authentication correctly rejects 100% of invalid tokens (expired, malformed, wrong signature)
- **SC-003**: User isolation is enforced - users cannot access tasks belonging to other users (0% cross-user data leakage)
- **SC-004**: API responses include correct HTTP status codes matching RESTful conventions
- **SC-005**: Frontend application can switch from mocked API to live backend without any code changes (zero frontend modifications)
- **SC-006**: System can be started successfully via `uv run backend.main:app --reload` with valid environment variables
- **SC-007**: All database operations complete within reasonable time (< 200ms for simple CRUD under normal load)
- **SC-008**: System handles invalid requests gracefully with clear error messages (no stack traces exposed to clients)
- **SC-009**: Database schema matches Task entity specification with proper types and constraints
- **SC-010**: System can recover from temporary database disconnections without crashing

### Test Coverage

- **TC-001**: Unit tests for JWT verification logic (valid tokens, invalid tokens, expired tokens, missing tokens)
- **TC-002**: Integration tests for all CRUD endpoints with authentication
- **TC-003**: User isolation tests ensuring users cannot access other users' tasks
- **TC-004**: Edge case tests (missing fields, invalid UUIDs, concurrent updates, database errors)
- **TC-005**: Environment configuration tests (missing vars, invalid DATABASE_URL)
