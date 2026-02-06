#!/bin/bash
# Build all Docker images for the Todo App
# Usage: ./deploy/scripts/build-images.sh [--push]
#
# Prerequisites:
#   - Docker Desktop running
#   - For Minikube: eval $(minikube docker-env)

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"

# Default tag
TAG="${TAG:-latest}"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if Docker is available
if ! command -v docker &> /dev/null; then
    log_error "Docker is not installed or not in PATH"
    exit 1
fi

# Check if Docker daemon is running
if ! docker info &> /dev/null; then
    log_error "Docker daemon is not running"
    exit 1
fi

log_info "Building Docker images with tag: ${TAG}"
log_info "Repository root: ${REPO_ROOT}"

# Build Frontend
log_info "Building todo-frontend..."
docker build \
    -t "todo-frontend:${TAG}" \
    -f "${REPO_ROOT}/deploy/docker/frontend/Dockerfile" \
    "${REPO_ROOT}/frontend"

# Build Backend
log_info "Building todo-backend..."
docker build \
    -t "todo-backend:${TAG}" \
    -f "${REPO_ROOT}/deploy/docker/backend/Dockerfile" \
    "${REPO_ROOT}"

# Build MCP Server
log_info "Building todo-mcp-server..."
docker build \
    -t "todo-mcp-server:${TAG}" \
    -f "${REPO_ROOT}/deploy/docker/mcp-server/Dockerfile" \
    "${REPO_ROOT}"

# Build AI Agent
log_info "Building todo-ai-agent..."
docker build \
    -t "todo-ai-agent:${TAG}" \
    -f "${REPO_ROOT}/deploy/docker/ai-agent/Dockerfile" \
    "${REPO_ROOT}"

log_info "All images built successfully!"

# List built images
echo ""
log_info "Built images:"
docker images | grep -E "todo-(frontend|backend|mcp-server|ai-agent)" | head -8

# Optional: Push to registry
if [[ "$1" == "--push" ]]; then
    if [[ -z "${REGISTRY}" ]]; then
        log_error "REGISTRY environment variable not set. Cannot push."
        exit 1
    fi

    log_info "Pushing images to ${REGISTRY}..."

    for img in frontend backend mcp-server ai-agent; do
        docker tag "todo-${img}:${TAG}" "${REGISTRY}/todo-${img}:${TAG}"
        docker push "${REGISTRY}/todo-${img}:${TAG}"
    done

    log_info "All images pushed successfully!"
fi
