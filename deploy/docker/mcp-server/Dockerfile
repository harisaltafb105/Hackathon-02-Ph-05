# Dockerfile for MCP (Model Context Protocol) Server
# Multi-stage build for optimized production image
# Base: python:3.13-slim for minimal attack surface

# ============================================================
# Stage 1: Builder - Install dependencies
# ============================================================
FROM python:3.13-slim AS builder

# Set working directory for build
WORKDIR /build

# Install uv for fast dependency resolution
# Using --no-cache-dir to minimize layer size
RUN pip install --no-cache-dir uv

# Copy dependency manifest
COPY pyproject.toml uv.lock* ./

# Install dependencies to a virtual environment
# This isolates dependencies and makes the final stage cleaner
RUN python -m venv /opt/venv && \
    . /opt/venv/bin/activate && \
    uv pip install --no-cache -r pyproject.toml

# ============================================================
# Stage 2: Production - Minimal runtime image
# ============================================================
FROM python:3.13-slim AS production

# Security: Create non-root user for running the application
# UID/GID 1001 to avoid conflicts with common system users
RUN groupadd -g 1001 mcpuser && \
    useradd -r -u 1001 -g mcpuser -s /sbin/nologin -c "MCP Server User" mcpuser

# Set working directory
WORKDIR /app

# Copy virtual environment from builder stage
COPY --from=builder --chown=mcpuser:mcpuser /opt/venv /opt/venv

# Copy application code (backend only, as it contains the MCP functionality)
COPY --chown=mcpuser:mcpuser backend/ ./backend/

# Environment variables for Python optimization and runtime configuration
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PATH="/opt/venv/bin:$PATH" \
    # MCP Server specific configuration
    MCP_MODE=true \
    MCP_SERVER_HOST=0.0.0.0 \
    MCP_SERVER_PORT=8001

# Expose MCP server port
EXPOSE 8001

# Switch to non-root user for security
USER mcpuser

# Health check endpoint (assumes /health or /ready exists)
# Adjust path if your MCP server uses a different health endpoint
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8001/health').read()" || exit 1

# Run MCP server using uvicorn
# Note: This assumes the backend.main:app can be configured via MCP_MODE env var
# If a dedicated MCP entry point exists (e.g., backend.mcp.server:app), update accordingly
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8001", "--workers", "1"]
