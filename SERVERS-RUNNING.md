# Servers Running ✅

**Date**: 2026-01-08
**Status**: Both servers are UP and RUNNING

## Backend Server

**URL**: http://localhost:8000
**Status**: ✅ RUNNING
**Framework**: FastAPI (Python)
**Database**: Neon PostgreSQL (CONNECTED)

**Available Endpoints**:
- `GET /health` - Health check
- `POST /auth/register` - User registration
- `POST /auth/login` - User login
- `GET /api/{user_id}/tasks` - List tasks
- `POST /api/{user_id}/tasks` - Create task
- `GET /api/{user_id}/tasks/{id}` - Get task
- `PUT /api/{user_id}/tasks/{id}` - Update task
- `DELETE /api/{user_id}/tasks/{id}` - Delete task
- `PATCH /api/{user_id}/tasks/{id}/complete` - Toggle completion

**Documentation**: http://localhost:8000/docs (Swagger UI)

## Frontend Server

**URL**: http://localhost:3000
**Status**: ✅ RUNNING
**Framework**: Next.js 16 (App Router)
**UI**: React 19 + Tailwind CSS

**Available Routes**:
- `/` - Home page
- `/login` - Login page
- `/register` - Registration page
- `/dashboard` - Task dashboard (protected)

## Quick Test

### Test Authentication Flow:

1. **Open your browser**: http://localhost:3000

2. **Register a new user**:
   - Click "Get Started" or navigate to http://localhost:3000/register
   - Enter email: yourname@example.com
   - Enter password: password123 (minimum 8 characters)
   - Confirm password
   - Click "Create account"
   - Should redirect to /dashboard

3. **Verify JWT Token**:
   - Open DevTools (F12)
   - Go to Network tab
   - Make any action on dashboard
   - Check request headers for: `Authorization: Bearer eyJ...`
   - Check localStorage for "auth-state" with user and token

4. **Test Login**:
   - Logout (if logged in)
   - Go to http://localhost:3000/login
   - Enter same credentials
   - Should successfully authenticate and redirect to /dashboard

5. **Test Session Persistence**:
   - While logged in, refresh the page
   - Should remain authenticated (no redirect to /login)

### Direct Backend Test:

```bash
# Register user
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"password123","name":"Test User"}'

# Login user
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"password123"}'
```

## Server Process IDs

To stop the servers, use these background task IDs:
- Backend: `b93e5bd`
- Frontend: `b8de736`

Or manually stop with:
```bash
# Stop backend
netstat -ano | findstr :8000
# Kill the process with PID shown

# Stop frontend
netstat -ano | findstr :3000
# Kill the process with PID shown
```

## Environment Configuration

**Backend** (`.env`):
```env
BETTER_AUTH_SECRET=8d6FQlFZM6jyDmYmCEBVC9rNSlq6lGNo
DATABASE_URL=postgresql+asyncpg://neondb_owner:npg_8KYmFA7OcQJH@ep-odd-queen-a77a8hbk-pooler.ap-southeast-2.aws.neon.tech/neondb?ssl=require
BETTER_AUTH_URL=http://localhost:3000
```

**Frontend** (`frontend/.env`):
```env
BETTER_AUTH_SECRET=8d6FQlFZM6jyDmYmCEBVC9rNSlq6lGNo
NEXT_PUBLIC_BETTER_AUTH_SECRET=8d6FQlFZM6jyDmYmCEBVC9rNSlq6lGNo
BETTER_AUTH_URL=http://127.0.0.1:8000
```

## Constitution Compliance ✅

- [x] Backend issues real JWT tokens
- [x] Frontend calls real backend endpoints
- [x] JWT verification with BETTER_AUTH_SECRET
- [x] bcrypt password hashing
- [x] Neon PostgreSQL database
- [x] User isolation on all queries
- [x] No mock authentication
- [x] Proper error handling (401, 409, 500)

---

**Status**: ✅ ALL SYSTEMS OPERATIONAL
**Authentication**: CONSTITUTION-COMPLIANT
**Ready for**: End-to-end testing
