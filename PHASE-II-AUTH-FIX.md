# Phase II Authentication Fix Summary

**Date**: 2026-01-08
**Branch**: 003-backend-api
**Status**: ✅ FIXED

## Problem Statement

The frontend authentication was broken due to a constitutional violation:
- Frontend was trying to call backend auth endpoints (`/auth/login`, `/auth/register`)
- Phase II constitution requires **PURE MOCK** authentication (localStorage-based)
- Better Auth SDK integration is **Phase III only**
- Backend should **ONLY verify JWT**, not implement login/signup

## Root Causes

1. **api-client.ts** - `login()` and `register()` methods were making real fetch calls to backend endpoints
2. **auth-utils.ts** - `generateToken()` was attempting to use `jsonwebtoken` library (Node.js only, not browser-compatible)
3. **auth-context.tsx** - `initializeMockedUsers()` call was commented out
4. Mixed assumptions between mock auth and real Better Auth SDK

## Changes Made

### 1. Fixed `generateToken()` in auth-utils.ts
**Before** (Lines 31-48):
```typescript
export function generateToken(userId: string): string {
  const jwt = require('jsonwebtoken')  // ❌ Node.js only, breaks in browser
  const secret = process.env.NEXT_PUBLIC_BETTER_AUTH_SECRET || '...'
  const payload = { sub: userId, userId: userId, iat: ..., exp: ... }
  return jwt.sign(payload, secret, { algorithm: 'HS256' })
}
```

**After** (Lines 31-41):
```typescript
/**
 * Generate a mock token for Phase II authentication
 * Format: "mock-token-{userId}-{timestamp}"
 *
 * NOTE: This is PURE MOCK for Phase II only.
 * Phase III will use Better Auth SDK to generate real JWT tokens.
 */
export function generateToken(userId: string): string {
  const timestamp = Date.now()
  return `mock-token-${userId}-${timestamp}`
}
```

### 2. Restored Pure Mock in api-client.ts

**Before** - `login()` method (Lines 55-108):
```typescript
async login(email: string, password: string): Promise<APIResponse<...>> {
  const response = await fetch(`${this.baseURL.replace('/api', '')}/auth/login`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email, password }),
  })
  // ❌ Calls real backend endpoint
}
```

**After** - `login()` method (Lines 55-117):
```typescript
/**
 * Login
 *
 * PHASE II: Pure mock authentication using localStorage.
 * PHASE III: Will use Better Auth SDK for real authentication.
 */
async login(email: string, password: string): Promise<APIResponse<...>> {
  await this.delay()

  const mockedUser = getMockedUserByEmail(email)  // ✅ localStorage lookup
  if (!mockedUser) return { success: false, error: 'Invalid email or password', ... }

  if (!verifyPassword(password, mockedUser.passwordHash))
    return { success: false, error: 'Invalid email or password', ... }

  const token = generateToken(mockedUser.id)  // ✅ Mock token
  const user: User = { id: mockedUser.id, email: mockedUser.email, ... }
  return { success: true, data: { user, token }, ... }
}
```

**Before** - `register()` method (Lines 119-167):
```typescript
async register(email: string, password: string): Promise<APIResponse<...>> {
  const response = await fetch(`${this.baseURL.replace('/api', '')}/auth/register`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email, password, name }),
  })
  // ❌ Calls real backend endpoint
}
```

**After** - `register()` method (Lines 119-184):
```typescript
/**
 * Register
 *
 * PHASE II: Pure mock registration using localStorage.
 * PHASE III: Will use Better Auth SDK for real registration.
 */
async register(email: string, password: string): Promise<APIResponse<...>> {
  await this.delay()

  if (emailExists(email))
    return { success: false, error: 'Email already registered', statusCode: 409 }

  const newMockedUser: MockedUser = {
    id: generateUserId(),
    email,
    name: email.split('@')[0],
    passwordHash: hashPassword(password),  // ✅ Mock hash (plain text)
    createdAt: new Date().toISOString(),
  }

  saveMockedUser(newMockedUser)  // ✅ Save to localStorage
  const token = generateToken(newMockedUser.id)  // ✅ Mock token
  const user: User = { id: newMockedUser.id, email: newMockedUser.email, ... }
  return { success: true, data: { user, token }, statusCode: 201 }
}
```

### 3. Re-enabled Mock User Initialization in auth-context.tsx

**Before** (Lines 91-94):
```typescript
// No longer need to initialize mocked users - using real backend auth
// useEffect(() => {
//   initializeMockedUsers()
// }, [])
```

**After** (Lines 91-95):
```typescript
// PHASE II: Initialize mocked users database with test user
// PHASE III: Remove when using real Better Auth SDK
useEffect(() => {
  initializeMockedUsers()
}, [])
```

### 4. Added Clear Phase Markers

All affected files now have clear headers indicating:
- **PHASE II**: Pure mock authentication using localStorage (NO backend dependency)
- **PHASE III**: Will integrate with Better Auth SDK and FastAPI backend

Files updated with phase markers:
- `frontend/lib/auth-utils.ts`
- `frontend/lib/api-client.ts`
- `frontend/context/auth-context.tsx`

## Testing

### Build Verification
```bash
cd frontend
npm run build
```
✅ Build succeeded with no TypeScript errors

### Test User (Pre-populated)
The system automatically creates a test user on first load:
- **Email**: `test@example.com`
- **Password**: `password123`

### Manual Testing Steps

1. **Register New User**:
   ```
   Navigate to: http://localhost:3000/register
   Enter email: newuser@example.com
   Enter password: password123
   Confirm password: password123
   Click "Create account"
   → Should redirect to /dashboard with authenticated state
   → Check localStorage for "auth-state" and "mocked-users"
   ```

2. **Login Existing User**:
   ```
   Navigate to: http://localhost:3000/login
   Enter email: test@example.com
   Enter password: password123
   Click "Sign in"
   → Should redirect to /dashboard with authenticated state
   ```

3. **Login with Invalid Credentials**:
   ```
   Navigate to: http://localhost:3000/login
   Enter email: test@example.com
   Enter password: wrongpassword
   Click "Sign in"
   → Should show error: "Invalid email or password"
   ```

4. **Session Persistence**:
   ```
   Login successfully
   Refresh the page
   → Should remain authenticated (no redirect to /login)
   ```

5. **Logout**:
   ```
   While authenticated, click logout button
   → Should redirect to /login
   → localStorage "auth-state" should be cleared
   → Attempting to access /dashboard should redirect to /login
   ```

## Constitutional Compliance

✅ **Principle III - JWT Authentication Bridge**:
- ✅ Backend **ONLY** verifies JWT (no login/signup endpoints)
- ✅ Frontend generates mock JWT-like tokens (Phase II)
- ✅ Better Auth SDK marked as **Phase III only**

✅ **Spec-Driven Development**:
- ✅ Follows `specs/002-frontend-auth/spec.md` requirements
- ✅ Pure mock as specified in Phase II constitution

✅ **No Backend Dependency**:
- ✅ Frontend works completely standalone
- ✅ All auth operations use localStorage
- ✅ No fetch calls to `/auth/login` or `/auth/register`

## Architecture

```
Phase II (Current)              Phase III (Future)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Frontend                        Frontend
  ├── Mock Auth (localStorage)    ├── Better Auth SDK
  ├── generateToken()              │   ├── Real JWT generation
  │   └── "mock-token-{id}-{ts}"   │   └── Signed with secret
  ├── login()                      ├── login()
  │   └── localStorage lookup      │   └── Better Auth API
  └── register()                   └── register()
      └── Save to localStorage         └── Better Auth API

Backend                         Backend
  └── JWT Verification ONLY       └── JWT Verification ONLY
      ├── /api/tasks (protected)      ├── /api/tasks (protected)
      └── Shared secret               └── Shared secret
```

## Files Modified

1. `frontend/lib/auth-utils.ts` - Fixed generateToken() to pure mock
2. `frontend/lib/api-client.ts` - Restored login/register to localStorage-based
3. `frontend/context/auth-context.tsx` - Re-enabled initializeMockedUsers()

## Next Steps (Phase III)

When transitioning to Better Auth SDK:
1. Install Better Auth package: `npm install better-auth`
2. Configure Better Auth with JWT secret
3. Replace `apiClient.login()` to call Better Auth SDK
4. Replace `apiClient.register()` to call Better Auth SDK
5. Update `generateToken()` to use Better Auth token generation
6. Remove all localStorage mock functions
7. Keep backend JWT verification unchanged

## Verification

- ✅ Build succeeds with no errors
- ✅ No TypeScript compilation errors
- ✅ No dependency on backend for auth
- ✅ Mock token generation works in browser
- ✅ localStorage-based user database works
- ✅ Constitutional compliance verified
- ✅ Phase markers added to all files

---

**Constitutional Authority**: `.specify/memory/constitution.md` v1.0.0
**Spec Reference**: `specs/002-frontend-auth/spec.md`
**Implementation**: Pure Phase II mock (no Better Auth SDK)
