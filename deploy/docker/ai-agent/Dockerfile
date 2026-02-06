# ============================================
# Stage 1: Builder - Install dependencies
# ============================================
FROM python:3.13-slim AS builder

# Set working directory
WORKDIR /app

# Install uv for fast dependency management
RUN pip install --no-cache-dir uv

# Copy dependency files
COPY pyproject.toml ./

# Install dependencies to a virtual environment
# Using --system flag with uv for system-wide installation in builder
RUN uv pip install --system --no-cache -r pyproject.toml

# ============================================
# Stage 2: Production - Minimal runtime image
# ============================================
FROM python:3.13-slim AS production

# Set working directory
WORKDIR /app

# Create non-root user for security
# Group ID 1001, User ID 1001
RUN groupadd -g 1001 appuser && \
    useradd -r -u 1001 -g appuser appuser

# Copy Python packages from builder stage
COPY --from=builder /usr/local/lib/python3.13/site-packages /usr/local/lib/python3.13/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy application code with proper ownership
# AI agent uses the same backend code, just with different configuration
COPY --chown=appuser:appuser backend/ ./backend/

# Environment variables for Python optimization
# Prevent Python from writing .pyc files
ENV PYTHONDONTWRITEBYTECODE=1
# Force stdout/stderr to be unbuffered for better logging
ENV PYTHONUNBUFFERED=1
# Disable pip version check
ENV PIP_DISABLE_PIP_VERSION_CHECK=1

# AI Agent specific configuration
# This environment variable indicates this instance runs as AI agent
ENV AI_AGENT_MODE=true

# Environment variables placeholders (override at runtime)
# These will be injected by Kubernetes secrets/configmaps
ENV OPENAI_API_KEY=""
ENV MCP_SERVER_URL=""
ENV DATABASE_URL=""
ENV BETTER_AUTH_URL=""
ENV BETTER_AUTH_SECRET=""

# Switch to non-root user
USER appuser

# Expose AI agent port (8002 as per data-model.md)
EXPOSE 8002

# Health check configuration
# Checks /health endpoint every 30 seconds
# 3 second timeout, 3 retries before marking unhealthy
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8002/health').read()" || exit 1

# Run uvicorn server on port 8002
# AI agent runs the same FastAPI app but on a different port
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8002"]
