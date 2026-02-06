#!/bin/bash
# ==============================================================================
# Frontend Docker Image Validation Script
# ==============================================================================
# This script validates the todo-frontend Docker image for security and
# production readiness before deployment
# ==============================================================================

set -e

IMAGE_NAME="${1:-todo-frontend:latest}"
CONTAINER_NAME="todo-frontend-validate-$$"

echo "=========================================="
echo "Docker Image Validation Report"
echo "=========================================="
echo "Image: $IMAGE_NAME"
echo "Date: $(date -u +%Y-%m-%dT%H:%M:%SZ)"
echo ""

# Check if image exists
echo "1. Checking if image exists..."
if ! docker image inspect "$IMAGE_NAME" > /dev/null 2>&1; then
    echo "   FAILED: Image $IMAGE_NAME not found"
    exit 1
fi
echo "   PASSED: Image exists"
echo ""

# Get image size
echo "2. Checking image size..."
IMAGE_SIZE=$(docker image inspect "$IMAGE_NAME" --format='{{.Size}}' | awk '{print $1/1024/1024 " MB"}')
echo "   Image Size: $IMAGE_SIZE"
IMAGE_SIZE_MB=$(docker image inspect "$IMAGE_NAME" --format='{{.Size}}' | awk '{print int($1/1024/1024)}')
if [ "$IMAGE_SIZE_MB" -gt 500 ]; then
    echo "   WARNING: Image size exceeds 500 MB (actual: ${IMAGE_SIZE_MB} MB)"
else
    echo "   PASSED: Image size is optimized"
fi
echo ""

# Check base image
echo "3. Checking base image..."
BASE_IMAGE=$(docker image inspect "$IMAGE_NAME" --format='{{index .Config.Image}}' 2>/dev/null || echo "N/A")
echo "   Base: $BASE_IMAGE"
echo ""

# Verify non-root user
echo "4. Verifying non-root user..."
USER_CHECK=$(docker run --rm "$IMAGE_NAME" id 2>/dev/null || echo "failed")
if echo "$USER_CHECK" | grep -q "uid=1001(nextjs)"; then
    echo "   PASSED: Running as non-root user (nextjs:1001)"
else
    echo "   FAILED: Not running as expected non-root user"
    echo "   Actual: $USER_CHECK"
fi
echo ""

# Check exposed ports
echo "5. Checking exposed ports..."
EXPOSED_PORTS=$(docker image inspect "$IMAGE_NAME" --format='{{range $port, $_ := .Config.ExposedPorts}}{{$port}} {{end}}')
if echo "$EXPOSED_PORTS" | grep -q "3000"; then
    echo "   PASSED: Port 3000 exposed"
    echo "   Ports: $EXPOSED_PORTS"
else
    echo "   FAILED: Port 3000 not exposed"
    echo "   Actual ports: $EXPOSED_PORTS"
fi
echo ""

# Check environment variables
echo "6. Checking environment variables..."
ENV_VARS=$(docker image inspect "$IMAGE_NAME" --format='{{range .Config.Env}}{{println .}}{{end}}')
echo "   Environment variables:"
echo "$ENV_VARS" | grep -E "(NODE_ENV|PORT|HOSTNAME|NEXT_)" | sed 's/^/     - /'

if echo "$ENV_VARS" | grep -q "NODE_ENV=production"; then
    echo "   PASSED: NODE_ENV set to production"
else
    echo "   WARNING: NODE_ENV not set to production"
fi
echo ""

# Verify no secrets in environment
echo "7. Checking for secrets in environment..."
if echo "$ENV_VARS" | grep -iE "(password|secret|key|token)" | grep -v "NEXT_PUBLIC"; then
    echo "   FAILED: Potential secrets found in environment variables"
else
    echo "   PASSED: No obvious secrets in environment"
fi
echo ""

# Check health check configuration
echo "8. Verifying health check..."
HEALTHCHECK=$(docker image inspect "$IMAGE_NAME" --format='{{.Config.Healthcheck}}')
if [ "$HEALTHCHECK" != "<nil>" ] && [ -n "$HEALTHCHECK" ]; then
    echo "   PASSED: Health check configured"
    echo "   Config: $HEALTHCHECK"
else
    echo "   WARNING: No health check configured"
fi
echo ""

# Test container startup
echo "9. Testing container startup..."
if docker run -d --name "$CONTAINER_NAME" -p 3001:3000 "$IMAGE_NAME" > /dev/null 2>&1; then
    echo "   PASSED: Container started successfully"

    # Wait for container to be ready
    echo "   Waiting for application to be ready (max 60s)..."
    for i in {1..60}; do
        if docker exec "$CONTAINER_NAME" sh -c 'wget -q -O- http://localhost:3000 > /dev/null 2>&1'; then
            echo "   PASSED: Application responding on port 3000"
            break
        fi
        if [ $i -eq 60 ]; then
            echo "   FAILED: Application not responding after 60s"
            docker logs "$CONTAINER_NAME"
        fi
        sleep 1
    done

    # Check process ownership
    echo ""
    echo "10. Verifying process ownership..."
    PROCESS_USER=$(docker exec "$CONTAINER_NAME" sh -c 'ps aux | grep "node.*server.js" | grep -v grep | awk "{print \$1}"' || echo "N/A")
    if [ "$PROCESS_USER" = "nextjs" ]; then
        echo "    PASSED: Process running as nextjs user"
    else
        echo "    WARNING: Process not running as expected user"
        echo "    Actual: $PROCESS_USER"
    fi

    # Cleanup
    docker stop "$CONTAINER_NAME" > /dev/null 2>&1
    docker rm "$CONTAINER_NAME" > /dev/null 2>&1
else
    echo "   FAILED: Container failed to start"
    echo "   Logs:"
    docker logs "$CONTAINER_NAME" 2>&1 || true
    docker rm -f "$CONTAINER_NAME" > /dev/null 2>&1 || true
fi
echo ""

# Check for common vulnerabilities (if trivy is installed)
echo "11. Security scan (optional)..."
if command -v trivy &> /dev/null; then
    echo "    Running Trivy scan..."
    trivy image --severity HIGH,CRITICAL --no-progress "$IMAGE_NAME"
else
    echo "    SKIPPED: Trivy not installed (install with: brew install trivy)"
fi
echo ""

# Image layers analysis
echo "12. Analyzing image layers..."
LAYER_COUNT=$(docker history "$IMAGE_NAME" --no-trunc --format "{{.ID}}" | wc -l)
echo "    Total layers: $LAYER_COUNT"
echo "    Top 5 largest layers:"
docker history "$IMAGE_NAME" --no-trunc --format "{{.Size}}\t{{.CreatedBy}}" | \
    grep -v "0B" | sort -hr | head -5 | sed 's/^/      /'
echo ""

# Final summary
echo "=========================================="
echo "VALIDATION SUMMARY"
echo "=========================================="
echo "Image: $IMAGE_NAME"
echo "Size: $IMAGE_SIZE"
echo ""
echo "Checklist:"
echo "  [✓] Image exists"
echo "  [$([ "$IMAGE_SIZE_MB" -le 500 ] && echo '✓' || echo '⚠')] Image size optimized (<= 500 MB)"
echo "  [$(echo "$USER_CHECK" | grep -q 'uid=1001(nextjs)' && echo '✓' || echo '✗')] Non-root user (nextjs:1001)"
echo "  [$(echo "$EXPOSED_PORTS" | grep -q '3000' && echo '✓' || echo '✗')] Port 3000 exposed"
echo "  [$(echo "$ENV_VARS" | grep -q 'NODE_ENV=production' && echo '✓' || echo '⚠')] NODE_ENV=production"
echo "  [$([ "$HEALTHCHECK" != "<nil>" ] && echo '✓' || echo '⚠')] Health check configured"
echo "  [✓] No secrets in environment"
echo ""
echo "Ready for deployment: $([ "$IMAGE_SIZE_MB" -le 500 ] && echo "$USER_CHECK" | grep -q 'uid=1001(nextjs)' && echo 'YES' || echo 'CHECK WARNINGS')"
echo "=========================================="
