#!/bin/bash

# MCP Memory Server Deployment Script
# This script automates the deployment process

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
PROJECT_NAME="mcp-memory-server"
DOCKER_IMAGE="mcp-memory-server:latest"
DOCKER_COMPOSE_FILE="deployment/docker/docker-compose.yml"
KUBERNETES_DIR="deployment/kubernetes"

# Functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

check_prerequisites() {
    log_info "Checking prerequisites..."
    
    # Check if Docker is installed
    if ! command -v docker &> /dev/null; then
        log_error "Docker is not installed. Please install Docker first."
        exit 1
    fi
    
    # Check if Docker Compose is installed
    if ! command -v docker-compose &> /dev/null; then
        log_error "Docker Compose is not installed. Please install Docker Compose first."
        exit 1
    fi
    
    # Check if kubectl is installed (for Kubernetes deployment)
    if ! command -v kubectl &> /dev/null; then
        log_warning "kubectl is not installed. Kubernetes deployment will be skipped."
    fi
    
    log_success "Prerequisites check completed"
}

build_docker_image() {
    log_info "Building Docker image..."
    
    # Build the Docker image
    docker build -t $DOCKER_IMAGE -f deployment/docker/Dockerfile .
    
    if [ $? -eq 0 ]; then
        log_success "Docker image built successfully"
    else
        log_error "Failed to build Docker image"
        exit 1
    fi
}

deploy_docker() {
    log_info "Deploying with Docker Compose..."
    
    # Stop existing containers
    docker-compose -f $DOCKER_COMPOSE_FILE down
    
    # Start services
    docker-compose -f $DOCKER_COMPOSE_FILE up -d
    
    # Wait for services to be ready
    log_info "Waiting for services to be ready..."
    sleep 30
    
    # Check service health
    check_service_health
    
    log_success "Docker deployment completed"
}

deploy_kubernetes() {
    log_info "Deploying to Kubernetes..."
    
    # Check if kubectl is available
    if ! command -v kubectl &> /dev/null; then
        log_error "kubectl is not available. Skipping Kubernetes deployment."
        return
    fi
    
    # Apply Kubernetes manifests
    kubectl apply -f $KUBERNETES_DIR/
    
    # Wait for deployment to be ready
    log_info "Waiting for Kubernetes deployment to be ready..."
    kubectl wait --for=condition=available --timeout=300s deployment/mcp-memory-server
    
    # Check service health
    check_kubernetes_health
    
    log_success "Kubernetes deployment completed"
}

check_service_health() {
    log_info "Checking service health..."
    
    # Check if the service is responding
    for i in {1..10}; do
        if curl -f http://localhost:8000/health &> /dev/null; then
            log_success "Service is healthy"
            return 0
        fi
        log_info "Waiting for service to be ready... (attempt $i/10)"
        sleep 5
    done
    
    log_error "Service health check failed"
    return 1
}

check_kubernetes_health() {
    log_info "Checking Kubernetes service health..."
    
    # Get service URL
    SERVICE_URL=$(kubectl get service mcp-memory-service -o jsonpath='{.status.loadBalancer.ingress[0].ip}')
    
    if [ -z "$SERVICE_URL" ]; then
        log_warning "Could not determine service URL. Using port-forward..."
        kubectl port-forward service/mcp-memory-service 8000:80 &
        SERVICE_URL="localhost:8000"
        sleep 5
    fi
    
    # Check health endpoint
    if curl -f http://$SERVICE_URL/health &> /dev/null; then
        log_success "Kubernetes service is healthy"
    else
        log_error "Kubernetes service health check failed"
    fi
}

run_tests() {
    log_info "Running deployment tests..."
    
    # Run integration tests
    python test_complete_services.py
    
    if [ $? -eq 0 ]; then
        log_success "Deployment tests passed"
    else
        log_error "Deployment tests failed"
        exit 1
    fi
}

show_status() {
    log_info "Deployment Status:"
    
    echo "=== Docker Services ==="
    docker-compose -f $DOCKER_COMPOSE_FILE ps
    
    echo ""
    echo "=== Service Health ==="
    curl -s http://localhost:8000/health | jq . 2>/dev/null || echo "Health check not available"
    
    echo ""
    echo "=== Logs ==="
    docker-compose -f $DOCKER_COMPOSE_FILE logs --tail=10
}

cleanup() {
    log_info "Cleaning up..."
    
    # Stop Docker services
    docker-compose -f $DOCKER_COMPOSE_FILE down
    
    # Remove Docker images
    docker rmi $DOCKER_IMAGE 2>/dev/null || true
    
    log_success "Cleanup completed"
}

# Main deployment function
deploy() {
    local deployment_type=$1
    
    log_info "Starting deployment of $PROJECT_NAME..."
    
    # Check prerequisites
    check_prerequisites
    
    # Build Docker image
    build_docker_image
    
    # Deploy based on type
    case $deployment_type in
        "docker")
            deploy_docker
            ;;
        "kubernetes")
            deploy_kubernetes
            ;;
        "both")
            deploy_docker
            deploy_kubernetes
            ;;
        *)
            log_error "Invalid deployment type. Use: docker, kubernetes, or both"
            exit 1
            ;;
    esac
    
    # Run tests
    run_tests
    
    # Show status
    show_status
    
    log_success "Deployment completed successfully!"
}

# Parse command line arguments
case "${1:-}" in
    "deploy")
        deploy "${2:-docker}"
        ;;
    "test")
        run_tests
        ;;
    "status")
        show_status
        ;;
    "cleanup")
        cleanup
        ;;
    "help"|"--help"|"-h")
        echo "Usage: $0 {deploy|test|status|cleanup} [docker|kubernetes|both]"
        echo ""
        echo "Commands:"
        echo "  deploy [type]  - Deploy the application (docker|kubernetes|both)"
        echo "  test          - Run deployment tests"
        echo "  status        - Show deployment status"
        echo "  cleanup       - Clean up deployment"
        echo "  help          - Show this help message"
        echo ""
        echo "Examples:"
        echo "  $0 deploy docker"
        echo "  $0 deploy kubernetes"
        echo "  $0 deploy both"
        echo "  $0 test"
        echo "  $0 status"
        ;;
    *)
        echo "Usage: $0 {deploy|test|status|cleanup} [docker|kubernetes|both]"
        echo "Use '$0 help' for more information"
        exit 1
        ;;
esac 