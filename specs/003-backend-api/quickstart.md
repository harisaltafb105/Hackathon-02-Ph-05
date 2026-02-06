# Quickstart Guide: Backend API

**Feature**: 003-backend-api
**Date**: 2026-01-07

## Prerequisites

Before starting, ensure you have:

- **Python 3.13+** installed
- **uv** package manager installed (`pip install uv` or `brew install uv`)
- **Neon PostgreSQL database** created (https://neon.tech)
- **Better Auth** configured in frontend (already implemented)
- **Git** for version control

## Environment Setup

### 1. Clone Repository and Navigate to Backend

```bash
cd D:\Hackathon-02\Todo-Fullstack
git checkout 003-backend-api
```

### 2. Create Environment File

Copy the example environment file and fill in your configuration:

```bash
cp .env.example .env
```

Edit `.env` with your actual values:

```env
# Better Auth Configuration
# URL where Better Auth is hosted (frontend auth service)
BETTER_AUTH_URL=http://localhost:3001/api/auth

# Shared secret for JWT verification (MUST match frontend Better Auth secret)
BETTER_AUTH_SECRET=your-secret-key-here-must-match-frontend

# Database Configuration
# Neon PostgreSQL connection string (use asyncpg driver)
DATABASE_URL=postgresql+asyncpg://user:password@ep-your-endpoint.us-east-2.aws.neon.tech/neondb?sslmode=require

# Optional: Production Frontend URL for CORS
FRONTEND_URL=https://your-app.com
```

**⚠️ Important**:
- `BETTER_AUTH_SECRET` MUST match the secret configured in your frontend Better Auth setup
- Use `postgresql+asyncpg://` driver (not `postgresql://`)
- Add `?sslmode=require` for Neon database connections

### 3. Install Dependencies

Navigate to backend directory and install dependencies via uv:

```bash
cd backend
uv sync
```

This creates a virtual environment and installs:
- FastAPI
- SQLModel
- PyJWT
- asyncpg
- python-dotenv
- uvicorn
- pytest (for testing)

## Development Workflow

### Run Development Server

Start the FastAPI development server with auto-reload:

```bash
uv run uvicorn main:app --reload
```

**Output**:
```
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Started reloader process
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

**Server URLs**:
- API Base: http://localhost:8000/api
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### Run Tests

Execute test suite with pytest:

```bash
# Run all tests
uv run pytest

# Run with verbose output
uv run pytest -v

# Run specific test file
uv run pytest tests/test_tasks_crud.py

# Run with coverage report
uv run pytest --cov=. --cov-report=html
```

### Code Quality Checks

```bash
# Format code with black
uv run black .

# Lint with ruff
uv run ruff check .

# Type checking with mypy (optional)
uv run mypy .
```

## API Documentation

### Swagger UI (Interactive)

Navigate to http://localhost:8000/docs

**Features**:
- Try out endpoints directly from browser
- View request/response schemas
- See authentication requirements
- Test with real JWT tokens

### ReDoc (Reference)

Navigate to http://localhost:8000/redoc

**Features**:
- Clean, readable API reference
- Search functionality
- Download OpenAPI spec
- Code examples in multiple languages

## Testing Authentication

### 1. Obtain JWT Token from Frontend

**Method A: Browser DevTools**
1. Open frontend at http://localhost:3001/login
2. Login with test credentials (test@example.com / password123)
3. Open DevTools (F12) → Application/Storage → Local Storage
4. Find key `auth-state` → Copy the `token` value

**Method B: curl**
```bash
# Register new user (if Better Auth registration endpoint available)
curl -X POST http://localhost:3001/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"password123"}'

# Login (if Better Auth login endpoint available)
curl -X POST http://localhost:3001/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"password123"}'
```

### 2. Test Backend Endpoints

Replace `<YOUR_JWT_TOKEN>` and `<USER_ID>` with actual values:

**List Tasks**:
```bash
curl -X GET "http://localhost:8000/api/<USER_ID>/tasks" \
  -H "Authorization: Bearer <YOUR_JWT_TOKEN>"
```

**Create Task**:
```bash
curl -X POST "http://localhost:8000/api/<USER_ID>/tasks" \
  -H "Authorization: Bearer <YOUR_JWT_TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Test task from curl",
    "description": "Testing the API"
  }'
```

**Get Specific Task**:
```bash
curl -X GET "http://localhost:8000/api/<USER_ID>/tasks/<TASK_ID>" \
  -H "Authorization: Bearer <YOUR_JWT_TOKEN>"
```

**Update Task (PUT)**:
```bash
curl -X PUT "http://localhost:8000/api/<USER_ID>/tasks/<TASK_ID>" \
  -H "Authorization: Bearer <YOUR_JWT_TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Updated task title",
    "description": "Updated description",
    "completed": true
  }'
```

**Partial Update (PATCH)**:
```bash
curl -X PATCH "http://localhost:8000/api/<USER_ID>/tasks/<TASK_ID>" \
  -H "Authorization: Bearer <YOUR_JWT_TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{"completed": true}'
```

**Delete Task**:
```bash
curl -X DELETE "http://localhost:8000/api/<USER_ID>/tasks/<TASK_ID>" \
  -H "Authorization: Bearer <YOUR_JWT_TOKEN>"
```

### 3. Test Error Cases

**Missing Authorization (401)**:
```bash
curl -X GET "http://localhost:8000/api/<USER_ID>/tasks"
# Expected: {"error":"Unauthorized","detail":"Not authenticated"}
```

**Invalid Token (401)**:
```bash
curl -X GET "http://localhost:8000/api/<USER_ID>/tasks" \
  -H "Authorization: Bearer invalid-token-here"
# Expected: {"error":"Unauthorized","detail":"Invalid token"}
```

**User ID Mismatch (403)**:
```bash
curl -X GET "http://localhost:8000/api/other-user-id/tasks" \
  -H "Authorization: Bearer <YOUR_JWT_TOKEN>"
# Expected: {"error":"Forbidden","detail":"Cannot access other users' resources"}
```

**Validation Error (422)**:
```bash
curl -X POST "http://localhost:8000/api/<USER_ID>/tasks" \
  -H "Authorization: Bearer <YOUR_JWT_TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{"description":"Missing title field"}'
# Expected: {"error":"Validation Error","detail":"title: field required"}
```

## Frontend Integration

### Update Frontend API Client

The frontend API client is already implemented at `frontend/lib/api-client.ts`.

**Switch from mocks to live backend**:

1. Update `frontend/lib/api-client.ts`:
   ```typescript
   class APIClient {
     // Change baseURL from '/api' to backend URL
     private baseURL = 'http://localhost:8000/api'

     // Remove mock implementations
     // Keep token injection logic
   }
   ```

2. Restart Next.js dev server:
   ```bash
   cd frontend
   npm run dev
   ```

3. Test authentication flow:
   - Login → JWT token stored in localStorage
   - Token automatically included in all API requests
   - CRUD operations use live backend

**No frontend code changes required** beyond baseURL update (per FR-018).

## Docker Compose (Optional)

For local development with PostgreSQL instead of Neon:

### 1. Create docker-compose.yml

```yaml
version: '3.8'

services:
  postgres:
    image: postgres:16-alpine
    environment:
      POSTGRES_USER: todo_user
      POSTGRES_PASSWORD: todo_password
      POSTGRES_DB: todo_db
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data

  backend:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      DATABASE_URL: postgresql+asyncpg://todo_user:todo_password@postgres:5432/todo_db
      BETTER_AUTH_SECRET: ${BETTER_AUTH_SECRET}
      BETTER_AUTH_URL: ${BETTER_AUTH_URL}
    depends_on:
      - postgres
    command: uvicorn main:app --host 0.0.0.0 --port 8000 --reload

volumes:
  postgres_data:
```

### 2. Start Services

```bash
docker-compose up
```

### 3. Update DATABASE_URL

```env
DATABASE_URL=postgresql+asyncpg://todo_user:todo_password@localhost:5432/todo_db
```

## Troubleshooting

### Database Connection Errors

**Error**: `asyncpg.exceptions.InvalidCatalogNameError`
**Fix**: Database doesn't exist. Create it in Neon dashboard or PostgreSQL:
```sql
CREATE DATABASE todo_db;
```

**Error**: `asyncpg.exceptions.InvalidPasswordError`
**Fix**: Check DATABASE_URL credentials match Neon/PostgreSQL configuration.

### JWT Verification Errors

**Error**: `{"error":"Unauthorized","detail":"Invalid token"}`
**Fix**:
- Verify BETTER_AUTH_SECRET matches frontend configuration
- Check JWT token format (should be `Bearer <token>` in header)
- Ensure token hasn't expired

### CORS Errors in Browser

**Error**: `Access to fetch at 'http://localhost:8000/api/...' from origin 'http://localhost:3001' has been blocked by CORS policy`
**Fix**:
- Verify CORS middleware in `main.py` includes `http://localhost:3001` in allowed origins
- Restart backend server after configuration changes

### Import Errors

**Error**: `ModuleNotFoundError: No module named 'fastapi'`
**Fix**: Dependencies not installed. Run `uv sync` in backend directory.

## Next Steps

1. ✅ Backend running on http://localhost:8000
2. ✅ API documentation available at /docs
3. ⏳ Implement task CRUD endpoints (see tasks.md after running `/sp.tasks`)
4. ⏳ Write integration tests for user isolation
5. ⏳ Deploy to production (Docker container + Neon PostgreSQL)

## Resources

- **FastAPI Documentation**: https://fastapi.tiangolo.com
- **SQLModel Documentation**: https://sqlmodel.tiangolo.com
- **PyJWT Documentation**: https://pyjwt.readthedocs.io
- **Neon PostgreSQL**: https://neon.tech/docs
- **OpenAPI Spec**: `specs/003-backend-api/contracts/openapi.yaml`
- **Data Model**: `specs/003-backend-api/data-model.md`

## Support

For issues or questions:
1. Check API documentation at http://localhost:8000/docs
2. Review error logs in terminal
3. Verify environment variables in `.env`
4. Consult spec at `specs/003-backend-api/spec.md`
