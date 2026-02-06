# Data Model: Frontend Auth & API Readiness

**Feature**: 002-frontend-auth
**Date**: 2026-01-07
**Phase**: 1 (Design & Contracts)

## Overview

This document defines the data structures for frontend authentication with mocked state management. All entities are designed to match expected backend structures for seamless future integration.

## Core Entities

### User

Represents an authenticated user in the system.

**TypeScript Definition**:
```typescript
export interface User {
  id: string              // Unique user identifier (UUID format)
  email: string           // User email (unique, validated format)
  name: string            // Display name
  createdAt: string       // ISO 8601 timestamp (e.g., "2026-01-07T10:30:00Z")
}
```

**Validation Rules**:
- `id`: Must be valid UUID format (generated on registration)
- `email`: Must match email regex pattern `/^[^\s@]+@[^\s@]+\.[^\s@]+$/`
- `name`: Derived from email (part before @) on registration, 1-100 characters
- `createdAt`: ISO 8601 format, automatically set on user creation

**Example**:
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "email": "alice@example.com",
  "name": "alice",
  "createdAt": "2026-01-07T10:30:00Z"
}
```

**Storage**:
- Mocked user database: localStorage key `mocked-users`
- Current user: Stored in AuthState

---

### AuthState

Represents the current authentication state of the application.

**TypeScript Definition**:
```typescript
export interface AuthState {
  user: User | null       // Currently authenticated user (null if not authenticated)
  isAuthenticated: boolean // Derived: true if user !== null
  isLoading: boolean      // True during async auth operations (login, register, logout)
  token: string | null    // Mocked JWT token (format: "mock-token-{userId}")
  error: string | null    // Last authentication error message
}
```

**State Transitions**:
```
INITIAL → LOADING → AUTHENTICATED
                  ↘ ERROR (retry from INITIAL)

AUTHENTICATED → LOADING → INITIAL (logout)
```

**Derived Values**:
- `isAuthenticated`: Computed as `user !== null && token !== null`

**Example (authenticated)**:
```json
{
  "user": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "email": "alice@example.com",
    "name": "alice",
    "createdAt": "2026-01-07T10:30:00Z"
  },
  "isAuthenticated": true,
  "isLoading": false,
  "token": "mock-token-550e8400-e29b-41d4-a716-446655440000",
  "error": null
}
```

**Example (unauthenticated)**:
```json
{
  "user": null,
  "isAuthenticated": false,
  "isLoading": false,
  "token": null,
  "error": null
}
```

**Storage**:
- localStorage key: `auth-state`
- Persisted fields: `user`, `token`
- Not persisted: `isLoading`, `error` (reset on app load)

---

### AuthAction

Defines all possible authentication actions (discriminated union).

**TypeScript Definition**:
```typescript
export type AuthAction =
  | { type: 'LOGIN_START' }
  | { type: 'LOGIN_SUCCESS'; payload: { user: User; token: string } }
  | { type: 'LOGIN_FAILURE'; payload: { error: string } }
  | { type: 'REGISTER_START' }
  | { type: 'REGISTER_SUCCESS'; payload: { user: User; token: string } }
  | { type: 'REGISTER_FAILURE'; payload: { error: string } }
  | { type: 'LOGOUT' }
  | { type: 'CLEAR_ERROR' }
  | { type: 'RESTORE_SESSION'; payload: { user: User; token: string } }
```

**Action Descriptions**:
- `LOGIN_START`: Begin login process (set isLoading=true)
- `LOGIN_SUCCESS`: Login succeeded (set user, token, isAuthenticated=true, isLoading=false)
- `LOGIN_FAILURE`: Login failed (set error, isLoading=false)
- `REGISTER_START`: Begin registration (set isLoading=true)
- `REGISTER_SUCCESS`: Registration succeeded (set user, token, isAuthenticated=true, isLoading=false)
- `REGISTER_FAILURE`: Registration failed (set error, isLoading=false)
- `LOGOUT`: Clear auth state (set user=null, token=null, isAuthenticated=false)
- `CLEAR_ERROR`: Clear error message
- `RESTORE_SESSION`: Restore auth from localStorage on app load

---

### APIResponse<T>

Generic response structure for all API operations (mocked and future real API).

**TypeScript Definition**:
```typescript
export interface APIResponse<T = any> {
  success: boolean        // True if operation succeeded
  data: T | null          // Response payload (type varies by endpoint)
  error: string | null    // Error message if failed (null if success)
  statusCode: number      // HTTP status code (200, 401, 403, 500, etc.)
}
```

**Example (successful login)**:
```json
{
  "success": true,
  "data": {
    "user": {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "email": "alice@example.com",
      "name": "alice",
      "createdAt": "2026-01-07T10:30:00Z"
    },
    "token": "mock-token-550e8400-e29b-41d4-a716-446655440000"
  },
  "error": null,
  "statusCode": 200
}
```

**Example (failed login)**:
```json
{
  "success": false,
  "data": null,
  "error": "Invalid email or password",
  "statusCode": 401
}
```

**Status Code Mapping**:
- `200`: Success (login, register, logout, CRUD operations)
- `400`: Bad request (validation failure)
- `401`: Unauthorized (invalid credentials, missing token)
- `403`: Forbidden (access denied)
- `404`: Not found (resource doesn't exist)
- `500`: Server error (unexpected failure)

---

### MockedUser

Internal structure for mocked user database (not exposed to frontend components).

**TypeScript Definition**:
```typescript
interface MockedUser {
  id: string              // UUID
  email: string           // Unique email
  name: string            // Display name
  passwordHash: string    // Plain text password (mocked only - real app uses bcrypt)
  createdAt: string       // ISO 8601 timestamp
}
```

**Storage**:
- localStorage key: `mocked-users`
- Structure: `{ [email]: MockedUser }`

**Example**:
```json
{
  "alice@example.com": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "email": "alice@example.com",
    "name": "alice",
    "passwordHash": "password123",
    "createdAt": "2026-01-07T10:30:00Z"
  },
  "test@example.com": {
    "id": "660e8400-e29b-41d4-a716-446655440111",
    "email": "test@example.com",
    "name": "test",
    "passwordHash": "password123",
    "createdAt": "2026-01-05T08:00:00Z"
  }
}
```

**Note**: Pre-populated with test user on first app load.

---

### LoginFormData

Form data structure for login page validation.

**TypeScript Definition**:
```typescript
export interface LoginFormData {
  email: string
  password: string
}
```

**Zod Schema**:
```typescript
export const loginSchema = z.object({
  email: z.string()
    .min(1, 'Email is required')
    .email('Please enter a valid email address'),
  password: z.string()
    .min(1, 'Password is required')
    .min(8, 'Password must be at least 8 characters'),
})
```

---

### RegisterFormData

Form data structure for registration page validation.

**TypeScript Definition**:
```typescript
export interface RegisterFormData {
  email: string
  password: string
  confirmPassword: string
}
```

**Zod Schema**:
```typescript
export const registerSchema = z.object({
  email: z.string()
    .min(1, 'Email is required')
    .email('Please enter a valid email address'),
  password: z.string()
    .min(1, 'Password is required')
    .min(8, 'Password must be at least 8 characters'),
  confirmPassword: z.string()
    .min(1, 'Please confirm your password'),
}).refine((data) => data.password === data.confirmPassword, {
  message: "Passwords don't match",
  path: ['confirmPassword'],
})
```

---

## Entity Relationships

```
┌─────────────────┐
│   AuthState     │
│  (Context)      │
│                 │
│  - user ────────┼──────> User
│  - token        │
│  - isLoading    │
│  - error        │
└─────────────────┘

┌─────────────────┐
│  MockedUsers    │
│ (localStorage)  │
│                 │
│ [email] ────────┼──────> MockedUser
│                 │
└─────────────────┘

┌─────────────────┐
│   APIClient     │
│   (Singleton)   │
│                 │
│  Methods return │
│  APIResponse<T> │
└─────────────────┘
```

## Data Flow

### Login Flow
```
1. User submits LoginForm
   ↓
2. LoginForm validates with Zod schema
   ↓
3. Dispatch LOGIN_START action (isLoading=true)
   ↓
4. Call apiClient.login(email, password)
   ↓
5. API client checks mocked-users in localStorage
   ↓
6a. Success: Dispatch LOGIN_SUCCESS with user + token
    ↓
    Save to auth-state in localStorage
    ↓
    Redirect to /dashboard

6b. Failure: Dispatch LOGIN_FAILURE with error message
    ↓
    Display error above form
```

### Registration Flow
```
1. User submits RegisterForm
   ↓
2. RegisterForm validates with Zod schema (including password match)
   ↓
3. Dispatch REGISTER_START action (isLoading=true)
   ↓
4. Call apiClient.register(email, password)
   ↓
5. API client checks if email exists in mocked-users
   ↓
6a. Email exists: Return error "Email already registered"
    ↓
    Dispatch REGISTER_FAILURE with error

6b. New email: Create MockedUser, generate token
    ↓
    Save to mocked-users in localStorage
    ↓
    Dispatch REGISTER_SUCCESS with user + token
    ↓
    Save to auth-state in localStorage
    ↓
    Redirect to /dashboard
```

### Session Restore Flow
```
1. App loads (root layout mounts)
   ↓
2. AuthProvider reads auth-state from localStorage
   ↓
3a. Valid auth-state found:
    ↓
    Check token expiry (24 hour limit)
    ↓
    If not expired: Dispatch RESTORE_SESSION
    ↓
    User remains authenticated

3b. No auth-state or expired:
    ↓
    User starts unauthenticated
    ↓
    Redirect to /login if on protected route
```

## Validation Rules Summary

| Field | Min Length | Max Length | Format | Required |
|-------|-----------|-----------|---------|----------|
| email | 1 | 320 | Email regex | Yes |
| password | 8 | 128 | Any chars | Yes |
| confirmPassword | 8 | 128 | Must match password | Yes (register only) |
| name | 1 | 100 | Any chars | Auto-generated |
| id | 36 | 36 | UUID v4 | Auto-generated |

## Storage Keys Reference

| Key | Type | Contents | Persistence |
|-----|------|----------|-------------|
| `auth-state` | JSON | `{ user, token }` | Persists across sessions |
| `mocked-users` | JSON | `{ [email]: MockedUser }` | Persists across sessions |
| `tasks` | JSON | Task array | Existing, unrelated to auth |

## Future Backend Alignment

All entities designed to match expected FastAPI backend structures:

- **User**: Matches SQLModel User table structure
- **AuthState**: Token field ready for real JWT
- **APIResponse**: Matches FastAPI response format
- **MockedUser**: Password field ready for bcrypt hash replacement

When integrating Better Auth SDK + FastAPI:
1. Replace `apiClient` mocked methods with real fetch calls
2. Swap `passwordHash` plain text with bcrypt verification
3. Replace mocked token generation with real JWT from Better Auth
4. No changes needed to User, AuthState, or APIResponse structures
