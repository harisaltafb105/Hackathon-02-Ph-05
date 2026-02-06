#!/bin/bash
# ============================================
# AI Agent Docker Build Script
# ============================================
# Builds the AI Agent container image for local Kubernetes deployment
#
# Usage:
#   ./build.sh [version]
#
# Example:
#   ./build.sh 1.0.0
#   ./build.sh        # Uses default version 1.0.0

set -e

# Configuration
IMAGE_NAME="todo-ai-agent"
VERSION="${1:-1.0.0}"
TAG_LOCAL="${VERSION}-local"
BUILD_CONTEXT="../../../"  # Project root
DOCKERFILE="./Dockerfile"

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${BLUE}============================================${NC}"
echo -e "${BLUE}Building AI Agent Docker Image${NC}"
echo -e "${BLUE}============================================${NC}"
echo ""
echo -e "${YELLOW}Configuration:${NC}"
echo -e "  Image Name: ${GREEN}${IMAGE_NAME}${NC}"
echo -e "  Version: ${GREEN}${VERSION}${NC}"
echo -e "  Tags: ${GREEN}${IMAGE_NAME}:${TAG_LOCAL}, ${IMAGE_NAME}:latest${NC}"
echo -e "  Dockerfile: ${GREEN}${DOCKERFILE}${NC}"
echo -e "  Build Context: ${GREEN}${BUILD_CONTEXT}${NC}"
echo ""

# Check if Dockerfile exists
if [ ! -f "${DOCKERFILE}" ]; then
    echo -e "${YELLOW}Error: Dockerfile not found at ${DOCKERFILE}${NC}"
    exit 1
fi

# Build the image
echo -e "${BLUE}Building Docker image...${NC}"
docker build \
    --file "${DOCKERFILE}" \
    --tag "${IMAGE_NAME}:${TAG_LOCAL}" \
    --tag "${IMAGE_NAME}:latest" \
    "${BUILD_CONTEXT}"

# Verify build success
if [ $? -eq 0 ]; then
    echo ""
    echo -e "${GREEN}============================================${NC}"
    echo -e "${GREEN}Build Successful!${NC}"
    echo -e "${GREEN}============================================${NC}"
    echo ""

    # Display image information
    echo -e "${BLUE}Image Information:${NC}"
    docker images "${IMAGE_NAME}" | head -2
    echo ""

    # Display image size
    SIZE=$(docker inspect "${IMAGE_NAME}:latest" --format='{{.Size}}' | awk '{printf "%.2f MB", $1/1024/1024}')
    echo -e "  Image Size: ${GREEN}${SIZE}${NC}"
    echo -e "  Exposed Port: ${GREEN}8002${NC}"
    echo -e "  User: ${GREEN}appuser (non-root)${NC}"
    echo -e "  Health Check: ${GREEN}Enabled${NC}"
    echo ""

    echo -e "${BLUE}Available tags:${NC}"
    echo -e "  - ${GREEN}${IMAGE_NAME}:${TAG_LOCAL}${NC}"
    echo -e "  - ${GREEN}${IMAGE_NAME}:latest${NC}"
    echo ""

    echo -e "${BLUE}Next steps:${NC}"
    echo -e "  1. Test locally: ${YELLOW}docker run -p 8002:8002 -e OPENAI_API_KEY=<key> ${IMAGE_NAME}:latest${NC}"
    echo -e "  2. Deploy to K8s: ${YELLOW}kubectl apply -f ../../helm/todo-app/templates/ai-agent-deployment.yaml${NC}"
    echo ""
else
    echo ""
    echo -e "${YELLOW}============================================${NC}"
    echo -e "${YELLOW}Build Failed!${NC}"
    echo -e "${YELLOW}============================================${NC}"
    exit 1
fi
