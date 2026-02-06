# Todo Backend API

FastAPI backend with SQLModel ORM, PostgreSQL database, and Better Auth JWT authentication.

## Features

- RESTful CRUD API for task management
- JWT authentication with Better Auth integration
- Strict user isolation (users can only access their own data)
- PostgreSQL database with SQLModel ORM
- Async/await for high performance
- Comprehensive test suite with pytest
- Docker support for deployment

## Prerequisites

- Python 3.13+
- uv package manager
- Neon PostgreSQL database (or local PostgreSQL)
- Better Auth configured in frontend

## Quick Start

### 1. Install Dependencies

```bash
# Install uv if not already installed
pip install uv

# Install project dependencies
uv sync
```

### 2. Configure Environment

```bash
# Copy example environment file
cp .env.example .env

# Edit .env and add your configuration:
# - BETTER_AUTH_SECRET: Must match frontend Better Auth secret
# - DATABASE_URL: Your Neon PostgreSQL connection string
```

### 3. Run Development Server

```bash
# Run with auto-reload
uv run uvicorn backend.main:app --reload

# Server will start at http://localhost:8000
```

### 4. Access API Documentation

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## API Endpoints

All endpoints require Bearer token authentication.

### Tasks

- `GET /api/{user_id}/tasks` - List all tasks for user
- `POST /api/{user_id}/tasks` - Create new task
- `GET /api/{user_id}/tasks/{task_id}` - Get specific task
- `PUT /api/{user_id}/tasks/{task_id}` - Update task (full)
- `PATCH /api/{user_id}/tasks/{task_id}` - Update task (partial)
- `DELETE /api/{user_id}/tasks/{task_id}` - Delete task

### Health Check

- `GET /health` - Health check endpoint (no auth required)

## Testing

```bash
# Run all tests
uv run pytest

# Run with coverage
uv run pytest --cov=backend --cov-report=html

# Run specific test file
uv run pytest backend/tests/test_auth.py

# Run with verbose output
uv run pytest -v
```

## Docker Deployment

### Build and Run

```bash
# Build Docker image
docker build -t todo-backend .

# Run container
docker run -p 8000:8000 \
  -e BETTER_AUTH_SECRET=your-secret \
  -e DATABASE_URL=your-database-url \
  todo-backend
```

### Using Docker Compose

```bash
# Start all services (backend + postgres)
docker-compose up -d

# View logs
docker-compose logs -f backend

# Stop services
docker-compose down
```

## Project Structure

```
backend/
├── __init__.py
├── main.py              # FastAPI application
├── config.py            # Environment configuration
├── database.py          # Database connection
├── auth.py              # JWT authentication
├── models.py            # SQLModel database models
├── schemas.py           # Pydantic request/response schemas
├── routers/
│   ├── __init__.py
│   └── tasks.py         # Task CRUD endpoints
├── middleware/
│   └── __init__.py
└── tests/
    ├── __init__.py
    ├── conftest.py      # Test fixtures
    ├── test_auth.py
    ├── test_tasks_retrieval.py
    ├── test_tasks_creation.py
    ├── test_tasks_update.py
    ├── test_tasks_deletion.py
    └── test_user_isolation.py
```

## Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `BETTER_AUTH_URL` | Better Auth service URL | Yes |
| `BETTER_AUTH_SECRET` | JWT signing secret (must match frontend) | Yes |
| `DATABASE_URL` | PostgreSQL connection string | Yes |

## Authentication

All API endpoints (except `/health`) require a valid JWT token in the Authorization header:

```
Authorization: Bearer <token>
```

The token must be obtained from the Better Auth service (frontend authentication).

## User Isolation

The API enforces strict user isolation:

- Users can only access their own tasks
- All queries filter by authenticated user's ID
- Attempting to access another user's resources returns 403 Forbidden
- User ID from JWT token must match user ID in URL path

## Error Responses

All errors return consistent JSON format:

```json
{
  "error": "Error type",
  "detail": "Detailed error message"
}
```

HTTP Status Codes:
- `200` - Success
- `201` - Created
- `204` - No Content (success, no body)
- `400` - Bad Request
- `401` - Unauthorized (authentication failed)
- `403` - Forbidden (access denied)
- `404` - Not Found
- `422` - Validation Error
- `500` - Internal Server Error
- `503` - Service Unavailable (database error)

## Development

### Code Quality

```bash
# Run type checking
uv run mypy backend/

# Format code
uv run black backend/

# Lint code
uv run ruff backend/
```

### Database Migrations

The application auto-creates tables on startup using SQLModel metadata. For production, consider using Alembic for migrations:

```bash
# Install Alembic
uv pip install alembic

# Initialize Alembic
alembic init migrations

# Create migration
alembic revision --autogenerate -m "description"

# Apply migration
alembic upgrade head
```

## Production Considerations

1. **Database Connection Pooling**: Already configured with `pool_size=5` and `max_overflow=10`

2. **CORS**: Update `allow_origins` in `main.py` to include your production frontend domain

3. **Logging**: Add structured logging (e.g., using `python-json-logger`)

4. **Monitoring**: Add application monitoring (e.g., Sentry, DataDog)

5. **Rate Limiting**: Consider adding rate limiting middleware

6. **Database Migrations**: Use Alembic instead of auto-create tables

7. **Environment Validation**: Already validates required env vars on startup

## Troubleshooting

### Database Connection Errors

- Verify `DATABASE_URL` is correct
- Check Neon database is accessible
- Ensure SSL mode is configured (`?sslmode=require` for Neon)

### Authentication Errors

- Verify `BETTER_AUTH_SECRET` matches frontend
- Check JWT token is not expired
- Ensure Authorization header format is correct

### Import Errors

- Verify virtual environment is activated
- Run `uv sync` to install dependencies
- Check Python version is 3.13+

## License

MIT
