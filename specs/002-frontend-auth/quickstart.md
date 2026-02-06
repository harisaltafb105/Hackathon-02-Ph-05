# Quickstart: Frontend Auth & API Readiness

**Feature**: 002-frontend-auth
**Branch**: 002-frontend-auth
**Date**: 2026-01-07

## Overview

This guide provides step-by-step instructions for implementing frontend authentication with mocked state management. Follow these steps to build login/register pages, auth context, route protection, and API client abstraction.

## Prerequisites

- Existing Next.js 16 Todo application running
- Familiarity with existing `task-context.tsx` pattern
- Familiarity with existing `task-form.tsx` validation pattern
- Node.js 20+ installed
- Git branch `002-frontend-auth` checked out

## Implementation Order

Follow this sequence to minimize integration issues:

1. **Types & Interfaces** (Foundation)
2. **Auth Utilities** (Helper functions)
3. **API Client** (Mocked network layer)
4. **Auth Context** (State management)
5. **Auth Components** (UI layer)
6. **Route Protection** (Layouts & middleware)
7. **Integration** (Connect to existing app)

---

## Step 1: Types & Interfaces (15 min)

### Create `frontend/types/auth.ts`

```typescript
export interface User {
  id: string
  email: string
  name: string
  createdAt: string
}

export interface AuthState {
  user: User | null
  isAuthenticated: boolean
  isLoading: boolean
  token: string | null
  error: string | null
}

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

export interface APIResponse<T = any> {
  success: boolean
  data: T | null
  error: string | null
  statusCode: number
}

export interface LoginFormData {
  email: string
  password: string
}

export interface RegisterFormData {
  email: string
  password: string
  confirmPassword: string
}
```

**Validation**: Run `npm run build` - should compile without errors.

---

## Step 2: Auth Utilities (20 min)

### Create `frontend/lib/auth-utils.ts`

Implement mocked authentication helper functions:
- `generateUserId()`: Create UUID for new users
- `hashPassword()`: Return plain text (mocked only)
- `verifyPassword()`: Simple string comparison (mocked only)
- `generateToken()`: Create mock token string
- `getMockedUsers()`: Read from localStorage
- `saveMockedUser()`: Write to localStorage
- `getAuthState()`: Read auth state from localStorage
- `saveAuthState()`: Write auth state to localStorage
- `clearAuthState()`: Remove auth state from localStorage
- `isTokenExpired()`: Check 24-hour expiry

**Pattern**: Follow existing localStorage patterns from `task-context.tsx`

**Storage Keys**:
- `mocked-users`: JSON object `{ [email]: MockedUser }`
- `auth-state`: JSON object `{ user, token }`

**Pre-populate test user**: `test@example.com` / `password123`

**Validation**: Import utils in a test file and verify localStorage operations work.

---

## Step 3: API Client (30 min)

### Create `frontend/lib/api-client.ts`

Implement singleton API client class:

```typescript
class APIClient {
  private baseURL = '/api'
  private token: string | null = null

  setToken(token: string | null) {
    this.token = token
  }

  getToken(): string | null {
    return this.token
  }

  private async delay(ms: number) {
    return new Promise(resolve => setTimeout(resolve, ms))
  }

  private async simulateNetwork() {
    await this.delay(300 + Math.random() * 500)
  }

  async login(email: string, password: string): Promise<APIResponse<{ user: User; token: string }>> {
    await this.simulateNetwork()
    // Check mocked-users, verify password, return user + token
  }

  async register(email: string, password: string): Promise<APIResponse<{ user: User; token: string }>> {
    await this.simulateNetwork()
    // Check if email exists, create user, return user + token
  }

  async logout(): Promise<APIResponse<void>> {
    await this.simulateNetwork()
    // Clear token, return success
  }

  // Task methods (existing functionality, now with auth headers)
  async getTasks(): Promise<APIResponse<Task[]>> { /* ... */ }
  async createTask(data: CreateTaskInput): Promise<APIResponse<Task>> { /* ... */ }
  async updateTask(id: string, data: UpdateTaskInput): Promise<APIResponse<Task>> { /* ... */ }
  async deleteTask(id: string): Promise<APIResponse<void>> { /* ... */ }
}

export const apiClient = new APIClient()
```

**Key Points**:
- Use helper functions from `auth-utils.ts`
- Return consistent `APIResponse<T>` structure
- Simulate realistic network delays
- Attach Authorization header when token present (for future backend)

**Validation**: Test each method in isolation, verify error cases.

---

## Step 4: Auth Context (30 min)

### Create `frontend/context/auth-context.tsx`

Pattern: **Exact mirror of `task-context.tsx`**

```typescript
'use client'

import { createContext, useContext, useReducer, useEffect } from 'react'
import { AuthState, AuthAction, User } from '@/types/auth'
import { getAuthState, saveAuthState, clearAuthState } from '@/lib/auth-utils'

// Initial state
const initialState: AuthState = {
  user: null,
  isAuthenticated: false,
  isLoading: false,
  token: null,
  error: null,
}

// Reducer function
function authReducer(state: AuthState, action: AuthAction): AuthState {
  switch (action.type) {
    case 'LOGIN_START':
    case 'REGISTER_START':
      return { ...state, isLoading: true, error: null }

    case 'LOGIN_SUCCESS':
    case 'REGISTER_SUCCESS':
    case 'RESTORE_SESSION':
      return {
        ...state,
        user: action.payload.user,
        token: action.payload.token,
        isAuthenticated: true,
        isLoading: false,
        error: null,
      }

    case 'LOGIN_FAILURE':
    case 'REGISTER_FAILURE':
      return {
        ...state,
        isLoading: false,
        error: action.payload.error,
      }

    case 'LOGOUT':
      return initialState

    case 'CLEAR_ERROR':
      return { ...state, error: null }

    default:
      return state
  }
}

// Context creation
const AuthStateContext = createContext<AuthState>(initialState)
const AuthActionsContext = createContext<React.Dispatch<AuthAction>>(() => {})

// Provider component
export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [state, dispatch] = useReducer(authReducer, initialState)

  // Restore session on mount
  useEffect(() => {
    const savedAuth = getAuthState()
    if (savedAuth && !isTokenExpired(savedAuth.token)) {
      dispatch({
        type: 'RESTORE_SESSION',
        payload: { user: savedAuth.user, token: savedAuth.token },
      })
    }
  }, [])

  // Persist to localStorage on auth changes
  useEffect(() => {
    if (state.isAuthenticated && state.user && state.token) {
      saveAuthState({ user: state.user, token: state.token })
    } else {
      clearAuthState()
    }
  }, [state.isAuthenticated, state.user, state.token])

  return (
    <AuthStateContext.Provider value={state}>
      <AuthActionsContext.Provider value={dispatch}>
        {children}
      </AuthActionsContext.Provider>
    </AuthStateContext.Provider>
  )
}

// Hooks
export function useAuth() {
  const context = useContext(AuthStateContext)
  if (!context) {
    throw new Error('useAuth must be used within AuthProvider')
  }
  return context
}

export function useAuthActions() {
  const context = useContext(AuthActionsContext)
  if (!context) {
    throw new Error('useAuthActions must be used within AuthProvider')
  }
  return context
}
```

**Validation**: Wrap a test component in `<AuthProvider>` and verify state updates work.

---

## Step 5: Auth Components (60 min)

### 5.1 Login Form

Create `frontend/components/auth/login-form.tsx`

Pattern: **Mirror `task-form.tsx`** structure

- Use React Hook Form + Zod validation
- Schema: email (required, format) + password (required, min 8 chars)
- Display inline errors below fields
- Loading state during submission
- Auto-focus email field on mount

```typescript
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { loginSchema } from '@/lib/validations/auth'
import { apiClient } from '@/lib/api-client'
import { useAuthActions } from '@/context/auth-context'

// ... implementation
```

### 5.2 Register Form

Create `frontend/components/auth/register-form.tsx`

Same pattern as LoginForm but with:
- Additional `confirmPassword` field
- Zod refine for password matching
- Error message "Passwords don't match"

### 5.3 Validation Schemas

Create `frontend/lib/validations/auth.ts`

```typescript
import { z } from 'zod'

export const loginSchema = z.object({
  email: z.string().min(1, 'Email is required').email('Please enter a valid email address'),
  password: z.string().min(1, 'Password is required').min(8, 'Password must be at least 8 characters'),
})

export const registerSchema = z.object({
  email: z.string().min(1, 'Email is required').email('Please enter a valid email address'),
  password: z.string().min(1, 'Password is required').min(8, 'Password must be at least 8 characters'),
  confirmPassword: z.string().min(1, 'Please confirm your password'),
}).refine((data) => data.password === data.confirmPassword, {
  message: "Passwords don't match",
  path: ['confirmPassword'],
})
```

**Validation**: Test forms with invalid inputs, verify errors appear correctly.

---

## Step 6: Auth Pages (30 min)

### 6.1 Login Page

Create `frontend/app/(auth)/login/page.tsx`

```typescript
'use client'

import { LoginForm } from '@/components/auth/login-form'
import { Card } from '@/components/ui/card'

export default function LoginPage() {
  return (
    <div className="min-h-screen flex items-center justify-center bg-background p-4">
      <Card className="w-full max-w-md p-8">
        <h1 className="text-3xl font-bold mb-2">Welcome Back</h1>
        <p className="text-muted-foreground mb-6">Sign in to your account</p>
        <LoginForm />
        <p className="text-sm text-center mt-4">
          Don't have an account?{' '}
          <a href="/register" className="text-primary hover:underline">
            Sign up
          </a>
        </p>
      </Card>
    </div>
  )
}
```

### 6.2 Register Page

Create `frontend/app/(auth)/register/page.tsx`

Similar structure to login page, but with RegisterForm.

**Validation**: Navigate to `/login` and `/register`, verify pages render.

---

## Step 7: Route Protection (45 min)

### 7.1 Public Layout (Auth Pages)

Create `frontend/app/(auth)/layout.tsx`

```typescript
'use client'

import { useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { useAuth } from '@/context/auth-context'

export default function AuthLayout({ children }: { children: React.ReactNode }) {
  const { isAuthenticated } = useAuth()
  const router = useRouter()

  useEffect(() => {
    if (isAuthenticated) {
      router.push('/dashboard')
    }
  }, [isAuthenticated, router])

  if (isAuthenticated) {
    return null // Don't render while redirecting
  }

  return <>{children}</>
}
```

### 7.2 Protected Layout (Dashboard/Tasks)

Create `frontend/app/(protected)/layout.tsx`

```typescript
'use client'

import { useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { useAuth, useAuthActions } from '@/context/auth-context'
import { Button } from '@/components/ui/button'
import { LogOut } from 'lucide-react'

export default function ProtectedLayout({ children }: { children: React.ReactNode }) {
  const { isAuthenticated, user, isLoading } = useAuth()
  const dispatch = useAuthActions()
  const router = useRouter()

  useEffect(() => {
    if (!isLoading && !isAuthenticated) {
      router.push('/login')
    }
  }, [isAuthenticated, isLoading, router])

  const handleLogout = async () => {
    dispatch({ type: 'LOGOUT' })
    await apiClient.logout()
    router.push('/login')
  }

  if (isLoading) {
    return <div>Loading...</div>
  }

  if (!isAuthenticated) {
    return null // Don't render while redirecting
  }

  return (
    <div>
      <header className="border-b border-border bg-card p-4">
        <div className="container mx-auto flex items-center justify-between">
          <h1 className="text-xl font-bold">Todo App</h1>
          <div className="flex items-center gap-4">
            <span className="text-sm text-muted-foreground">{user?.email}</span>
            <Button variant="outline" size="sm" onClick={handleLogout}>
              <LogOut className="h-4 w-4 mr-2" />
              Logout
            </Button>
          </div>
        </div>
      </header>
      <main>{children}</main>
    </div>
  )
}
```

### 7.3 Move Existing Pages

Move `frontend/app/page.tsx` → `frontend/app/(protected)/dashboard/page.tsx`

Update imports if necessary.

**Validation**: Test route protection - unauthenticated users redirect to `/login`, authenticated users redirect away from `/login`.

---

## Step 8: Root Layout Integration (15 min)

Update `frontend/app/layout.tsx` to wrap children in AuthProvider:

```typescript
import { AuthProvider } from '@/context/auth-context'
import { TaskProvider } from '@/context/task-context'

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>
        <AuthProvider>
          <TaskProvider>
            {children}
          </TaskProvider>
        </AuthProvider>
      </body>
    </html>
  )
}
```

**Validation**: Full integration test - register → login → view tasks → logout.

---

## Testing Checklist

### User Story 1: Registration
- [ ] Navigate to `/register`
- [ ] Fill email and password (valid)
- [ ] Submit form
- [ ] Redirected to `/dashboard`
- [ ] User email shown in header
- [ ] Try invalid email → see error message
- [ ] Try short password → see error message
- [ ] Try mismatched passwords → see error message
- [ ] Try existing email → see "Email already registered"

### User Story 2: Login
- [ ] Navigate to `/login`
- [ ] Enter `test@example.com` / `password123`
- [ ] Redirected to `/dashboard`
- [ ] Refresh page → remain authenticated
- [ ] Enter wrong password → see error "Invalid email or password"
- [ ] Try non-existent email → see error "Invalid email or password"

### User Story 3: Route Protection
- [ ] While logged out, try `/dashboard` → redirect to `/login`
- [ ] While logged in, try `/login` → redirect to `/dashboard`
- [ ] After login, can access `/dashboard` and `/tasks`

### User Story 4: Logout
- [ ] Click logout button
- [ ] Redirected to `/login`
- [ ] Try accessing `/dashboard` → redirect to `/login`
- [ ] localStorage cleared (check DevTools)

### User Story 5: API Client
- [ ] All API methods return `APIResponse<T>` format
- [ ] Network delays visible (300-800ms)
- [ ] Authorization header included when authenticated (check Network tab)

### User Story 6: Form Validation
- [ ] Email validation works (format check)
- [ ] Password length validation (min 8 chars)
- [ ] Inline errors appear below fields
- [ ] Errors clear on re-submit
- [ ] Loading state disables form

---

## Common Issues & Solutions

### Issue: "useAuth must be used within AuthProvider"
**Solution**: Ensure AuthProvider wraps the component tree in root layout.

### Issue: Infinite redirect loop
**Solution**: Check that layouts properly handle loading state before redirecting.

### Issue: Auth state not persisting
**Solution**: Verify localStorage keys match between save/load functions.

### Issue: Forms not validating
**Solution**: Ensure Zod schemas are properly defined and resolver is passed to useForm.

### Issue: Can't access protected routes after login
**Solution**: Check that RESTORE_SESSION action dispatches correctly on app mount.

---

## Performance Optimization

- [ ] Memoize auth context value to prevent unnecessary re-renders
- [ ] Use `useCallback` for dispatch functions
- [ ] Lazy load auth forms (already handled by route-based code splitting)
- [ ] Debounce validation on input fields (optional enhancement)

---

## Next Steps After Implementation

1. Run `/sp.tasks` to generate actionable task breakdown
2. Use `/sp.implement` to execute tasks via Claude Code agents
3. Manual QA against all acceptance scenarios
4. Document any deviations in ADR if needed
5. Commit changes with conventional commit message

---

## File Checklist

Created files:
- [ ] `frontend/types/auth.ts`
- [ ] `frontend/lib/auth-utils.ts`
- [ ] `frontend/lib/api-client.ts`
- [ ] `frontend/lib/validations/auth.ts`
- [ ] `frontend/context/auth-context.tsx`
- [ ] `frontend/components/auth/login-form.tsx`
- [ ] `frontend/components/auth/register-form.tsx`
- [ ] `frontend/app/(auth)/layout.tsx`
- [ ] `frontend/app/(auth)/login/page.tsx`
- [ ] `frontend/app/(auth)/register/page.tsx`
- [ ] `frontend/app/(protected)/layout.tsx`
- [ ] `frontend/app/(protected)/dashboard/page.tsx` (moved from root)

Modified files:
- [ ] `frontend/app/layout.tsx` (add AuthProvider)

Total: 12 new files, 1 modified file, ~800-1200 lines of code
