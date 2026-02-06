#!/bin/bash
# Validate Todo App deployment
# Usage: ./deploy/scripts/validate.sh
#
# Optional environment variables:
#   RELEASE_NAME - Helm release name (default: todo-app)
#   NAMESPACE    - Kubernetes namespace (default: default)

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Default values
RELEASE_NAME="${RELEASE_NAME:-todo-app}"
NAMESPACE="${NAMESPACE:-default}"

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

log_pass() {
    echo -e "${GREEN}[PASS]${NC} $1"
}

log_fail() {
    echo -e "${RED}[FAIL]${NC} $1"
}

TESTS_PASSED=0
TESTS_FAILED=0

# Check function that tracks results
check() {
    local description="$1"
    local command="$2"

    if eval "$command" &> /dev/null; then
        log_pass "$description"
        ((TESTS_PASSED++))
    else
        log_fail "$description"
        ((TESTS_FAILED++))
    fi
}

# Main validation
main() {
    echo ""
    log_info "Validating Todo App deployment"
    log_info "Release: ${RELEASE_NAME}, Namespace: ${NAMESPACE}"
    echo ""

    # 1. Check pods are running
    log_info "Checking pod status..."

    check "Frontend pod is Running" \
        "kubectl get pods -n ${NAMESPACE} -l component=frontend -o jsonpath='{.items[0].status.phase}' | grep -q Running"

    check "Backend pod is Running" \
        "kubectl get pods -n ${NAMESPACE} -l component=backend -o jsonpath='{.items[0].status.phase}' | grep -q Running"

    check "MCP Server pod is Running" \
        "kubectl get pods -n ${NAMESPACE} -l component=mcp-server -o jsonpath='{.items[0].status.phase}' | grep -q Running"

    check "AI Agent pod is Running" \
        "kubectl get pods -n ${NAMESPACE} -l component=ai-agent -o jsonpath='{.items[0].status.phase}' | grep -q Running"

    echo ""

    # 2. Check services have endpoints
    log_info "Checking service endpoints..."

    check "Frontend service has endpoints" \
        "kubectl get endpoints ${RELEASE_NAME}-frontend-svc -n ${NAMESPACE} -o jsonpath='{.subsets[0].addresses}' | grep -q ."

    check "Backend service has endpoints" \
        "kubectl get endpoints ${RELEASE_NAME}-backend-svc -n ${NAMESPACE} -o jsonpath='{.subsets[0].addresses}' | grep -q ."

    check "MCP Server service has endpoints" \
        "kubectl get endpoints ${RELEASE_NAME}-mcp-server-svc -n ${NAMESPACE} -o jsonpath='{.subsets[0].addresses}' | grep -q ."

    check "AI Agent service has endpoints" \
        "kubectl get endpoints ${RELEASE_NAME}-ai-agent-svc -n ${NAMESPACE} -o jsonpath='{.subsets[0].addresses}' | grep -q ."

    echo ""

    # 3. Check secrets and configmaps exist
    log_info "Checking configuration resources..."

    check "Secrets exist" \
        "kubectl get secret ${RELEASE_NAME}-secrets -n ${NAMESPACE}"

    check "ConfigMap exists" \
        "kubectl get configmap ${RELEASE_NAME}-config -n ${NAMESPACE}"

    echo ""

    # 4. Check pod restarts
    log_info "Checking for pod restarts..."

    FRONTEND_RESTARTS=$(kubectl get pods -n ${NAMESPACE} -l component=frontend -o jsonpath='{.items[0].status.containerStatuses[0].restartCount}' 2>/dev/null || echo "N/A")
    BACKEND_RESTARTS=$(kubectl get pods -n ${NAMESPACE} -l component=backend -o jsonpath='{.items[0].status.containerStatuses[0].restartCount}' 2>/dev/null || echo "N/A")
    MCP_RESTARTS=$(kubectl get pods -n ${NAMESPACE} -l component=mcp-server -o jsonpath='{.items[0].status.containerStatuses[0].restartCount}' 2>/dev/null || echo "N/A")
    AI_RESTARTS=$(kubectl get pods -n ${NAMESPACE} -l component=ai-agent -o jsonpath='{.items[0].status.containerStatuses[0].restartCount}' 2>/dev/null || echo "N/A")

    echo "  Frontend restarts: ${FRONTEND_RESTARTS}"
    echo "  Backend restarts: ${BACKEND_RESTARTS}"
    echo "  MCP Server restarts: ${MCP_RESTARTS}"
    echo "  AI Agent restarts: ${AI_RESTARTS}"

    echo ""

    # 5. Get access URL
    log_info "Getting access URL..."

    if command -v minikube &> /dev/null; then
        FRONTEND_URL=$(minikube service ${RELEASE_NAME}-frontend-svc -n ${NAMESPACE} --url 2>/dev/null || echo "Unable to determine")
        echo "  Frontend URL: ${FRONTEND_URL}"
    else
        NODE_PORT=$(kubectl get svc ${RELEASE_NAME}-frontend-svc -n ${NAMESPACE} -o jsonpath='{.spec.ports[0].nodePort}' 2>/dev/null || echo "Unknown")
        echo "  Frontend NodePort: ${NODE_PORT}"
    fi

    echo ""

    # Summary
    echo "=========================================="
    log_info "Validation Summary"
    echo "  Tests Passed: ${TESTS_PASSED}"
    echo "  Tests Failed: ${TESTS_FAILED}"
    echo "=========================================="

    if [[ ${TESTS_FAILED} -gt 0 ]]; then
        log_error "Some validation checks failed!"
        exit 1
    else
        log_info "All validation checks passed!"
        exit 0
    fi
}

main "$@"
