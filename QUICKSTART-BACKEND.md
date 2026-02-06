# Backend API Quickstart Guide

Get the FastAPI backend running in 5 minutes!

## Prerequisites

- Python 3.13+ installed
- Access to a Neon PostgreSQL database
- Better Auth secret from frontend configuration

## Setup Steps

### 1. Install uv (Package Manager)

```bash
# Windows (PowerShell)
pip install uv

# macOS/Linux
pip3 install uv
```

### 2. Create Environment File

```bash
# Copy the example file
cp .env.example .env

# Edit .env with your values
# Required variables:
# - BETTER_AUTH_SECRET: Must match your frontend Better Auth secret
# - DATABASE_URL: Your Neon PostgreSQL connection string
```

Example `.env`:
```env
BETTER_AUTH_URL=http://localhost:3001
BETTER_AUTH_SECRET=your-secret-key-minimum-32-characters-long
DATABASE_URL=postgresql+asyncpg://username:password@ep-example.us-east-2.aws.neon.tech/neondb?sslmode=require
```

### 3. Install Dependencies

```bash
# Install all backend dependencies
uv sync
```

### 4. Run Development Server

```bash
# Start the backend with auto-reload
uv run uvicorn backend.main:app --reload

# Server will be available at:
# - API: http://localhost:8000
# - Swagger UI: http://localhost:8000/docs
# - ReDoc: http://localhost:8000/redoc
```

### 5. Verify Installation

Open http://localhost:8000/docs in your browser. You should see the Swagger UI with all API endpoints.

Test the health check endpoint:
```bash
curl http://localhost:8000/health
```

Expected response:
```json
{"status": "healthy"}
```

## Testing the API

### Get a JWT Token

1. Run your frontend application (Next.js at http://localhost:3001)
2. Login using Better Auth
3. Open browser DevTools > Application/Storage > Local Storage
4. Copy the JWT token value

### Test Authentication

```bash
# Set your token
TOKEN="your-jwt-token-here"

# List tasks (should return empty array for new user)
curl -H "Authorization: Bearer $TOKEN" http://localhost:8000/api/{your-user-id}/tasks

# Create a task
curl -X POST \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"title": "Test Task", "description": "My first task"}' \
  http://localhost:8000/api/{your-user-id}/tasks
```

## Running Tests

```bash
# Run all tests
uv run pytest

# Run with coverage report
uv run pytest --cov=backend --cov-report=html

# Run specific test file
uv run pytest backend/tests/test_auth.py -v

# Open coverage report
open htmlcov/index.html  # macOS
start htmlcov/index.html  # Windows
```

## Docker Deployment (Optional)

### Using Docker Compose

```bash
# Start all services (backend + postgres)
docker-compose up -d

# View logs
docker-compose logs -f backend

# Stop services
docker-compose down
```

### Build Custom Docker Image

```bash
# Build the image
docker build -t todo-backend .

# Run the container
docker run -p 8000:8000 \
  -e BETTER_AUTH_SECRET=your-secret \
  -e DATABASE_URL=your-database-url \
  todo-backend
```

## Project Structure

```
backend/
├── __init__.py
├── main.py              # FastAPI app entry point
├── config.py            # Environment variables
├── database.py          # Database connection
├── auth.py              # JWT authentication
├── models.py            # SQLModel database models
├── schemas.py           # Pydantic request/response schemas
├── routers/
│   └── tasks.py         # Task CRUD endpoints
└── tests/
    ├── conftest.py      # Test fixtures
    ├── test_auth.py
    ├── test_tasks_*.py
    └── test_user_isolation.py
```

## API Endpoints

All endpoints require Bearer token authentication (except `/health`).

### Tasks
- `GET /api/{user_id}/tasks` - List all tasks
- `POST /api/{user_id}/tasks` - Create task
- `GET /api/{user_id}/tasks/{task_id}` - Get specific task
- `PUT /api/{user_id}/tasks/{task_id}` - Update task (full)
- `PATCH /api/{user_id}/tasks/{task_id}` - Update task (partial)
- `DELETE /api/{user_id}/tasks/{task_id}` - Delete task

### Health Check
- `GET /health` - Health check (no auth required)

## Common Issues

### Issue: Module not found errors

**Solution**: Ensure you're running commands with `uv run` prefix:
```bash
uv run uvicorn backend.main:app --reload
uv run pytest
```

### Issue: Database connection errors

**Solution**:
1. Verify `DATABASE_URL` in `.env` is correct
2. Check Neon database is accessible
3. Ensure SSL mode is included: `?sslmode=require`

### Issue: Authentication failures

**Solution**:
1. Verify `BETTER_AUTH_SECRET` matches frontend configuration
2. Check JWT token is not expired
3. Ensure Authorization header format: `Bearer <token>`

### Issue: CORS errors from frontend

**Solution**: Update `allow_origins` in `backend/main.py` to include your frontend URL.

## Development Tips

### Watch for file changes
The `--reload` flag automatically restarts the server when code changes.

### View SQL queries
Set `echo=True` in `backend/database.py` engine configuration to see all SQL queries.

### Debug mode
Set breakpoints and run with debugger:
```bash
uv run python -m debugpy --listen 5678 -m uvicorn backend.main:app --reload
```

## Next Steps

1. Read the full documentation in `backend/README.md`
2. Review API contracts in `specs/003-backend-api/contracts/openapi.yaml`
3. Check implementation plan in `specs/003-backend-api/plan.md`
4. Integrate with your frontend application

## Getting Help

- API Documentation: http://localhost:8000/docs
- FastAPI Docs: https://fastapi.tiangolo.com
- SQLModel Docs: https://sqlmodel.tiangolo.com
- Neon Docs: https://neon.tech/docs

---

**Status**: All 45 tasks completed
**Last Updated**: 2026-01-07
