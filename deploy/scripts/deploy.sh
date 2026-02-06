#!/bin/bash
# Deploy Todo App to Kubernetes using Helm
# Usage: ./deploy/scripts/deploy.sh
#
# Required environment variables:
#   DATABASE_URL       - PostgreSQL connection string
#   BETTER_AUTH_SECRET - JWT signing secret
#   OPENAI_API_KEY     - OpenAI API key
#
# Optional environment variables:
#   RELEASE_NAME       - Helm release name (default: todo-app)
#   NAMESPACE          - Kubernetes namespace (default: default)
#   VALUES_FILE        - Additional values file to use

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"
CHART_PATH="${REPO_ROOT}/deploy/helm/todo-app"

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

# Check prerequisites
check_prereqs() {
    log_info "Checking prerequisites..."

    # Check for helm
    if ! command -v helm &> /dev/null; then
        log_error "Helm is not installed"
        exit 1
    fi

    # Check for kubectl
    if ! command -v kubectl &> /dev/null; then
        log_error "kubectl is not installed"
        exit 1
    fi

    # Check kubectl context
    if ! kubectl cluster-info &> /dev/null; then
        log_error "Cannot connect to Kubernetes cluster. Is minikube running?"
        exit 1
    fi

    # Check required secrets
    if [[ -z "${DATABASE_URL}" ]]; then
        log_error "DATABASE_URL environment variable is not set"
        exit 1
    fi

    if [[ -z "${BETTER_AUTH_SECRET}" ]]; then
        log_error "BETTER_AUTH_SECRET environment variable is not set"
        exit 1
    fi

    if [[ -z "${OPENAI_API_KEY}" ]]; then
        log_error "OPENAI_API_KEY environment variable is not set"
        exit 1
    fi

    log_info "All prerequisites met!"
}

# Run helm lint
lint_chart() {
    log_info "Linting Helm chart..."
    helm lint "${CHART_PATH}"
}

# Deploy or upgrade
deploy() {
    log_info "Deploying ${RELEASE_NAME} to namespace ${NAMESPACE}..."

    # Build helm command
    HELM_CMD="helm upgrade --install ${RELEASE_NAME} ${CHART_PATH}"
    HELM_CMD="${HELM_CMD} --namespace ${NAMESPACE}"
    HELM_CMD="${HELM_CMD} --create-namespace"
    HELM_CMD="${HELM_CMD} --set secrets.databaseUrl=\"${DATABASE_URL}\""
    HELM_CMD="${HELM_CMD} --set secrets.betterAuthSecret=\"${BETTER_AUTH_SECRET}\""
    HELM_CMD="${HELM_CMD} --set secrets.openaiApiKey=\"${OPENAI_API_KEY}\""

    # Add optional values file
    if [[ -n "${VALUES_FILE}" && -f "${VALUES_FILE}" ]]; then
        HELM_CMD="${HELM_CMD} -f ${VALUES_FILE}"
    fi

    # Execute
    eval ${HELM_CMD}

    log_info "Deployment initiated!"
}

# Wait for pods to be ready
wait_for_pods() {
    log_info "Waiting for pods to be ready..."

    kubectl rollout status deployment/${RELEASE_NAME}-frontend -n ${NAMESPACE} --timeout=300s
    kubectl rollout status deployment/${RELEASE_NAME}-backend -n ${NAMESPACE} --timeout=300s
    kubectl rollout status deployment/${RELEASE_NAME}-mcp-server -n ${NAMESPACE} --timeout=300s
    kubectl rollout status deployment/${RELEASE_NAME}-ai-agent -n ${NAMESPACE} --timeout=300s

    log_info "All pods are ready!"
}

# Print access information
print_access_info() {
    echo ""
    log_info "Deployment complete!"
    echo ""
    echo "To access the application:"
    echo "  minikube service ${RELEASE_NAME}-frontend-svc -n ${NAMESPACE} --url"
    echo ""
    echo "To view pods:"
    echo "  kubectl get pods -n ${NAMESPACE} -l app=todo"
    echo ""
    echo "To view logs:"
    echo "  kubectl logs -n ${NAMESPACE} -l component=frontend -f"
    echo "  kubectl logs -n ${NAMESPACE} -l component=backend -f"
    echo ""
}

# Main execution
main() {
    check_prereqs
    lint_chart
    deploy
    wait_for_pods
    print_access_info
}

main "$@"
