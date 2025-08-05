#!/bin/bash

# MCP Memory Cloud - Deployment Script
# Handles complete cloud deployment with SSL, monitoring, and scaling

set -e

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
DOMAIN=${DOMAIN:-mcpmemory.cloud}
API_DOMAIN=${API_DOMAIN:-api.mcpmemory.cloud}
ENVIRONMENT=${ENVIRONMENT:-production}
COMPOSE_FILE=${COMPOSE_FILE:-docker-compose.yml}

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

check_dependencies() {
    log_info "Checking dependencies..."
    
    # Check Docker
    if ! command -v docker &> /dev/null; then
        log_error "Docker is not installed"
        exit 1
    fi
    
    # Check Docker Compose
    if ! command -v docker-compose &> /dev/null; then
        log_error "Docker Compose is not installed"
        exit 1
    fi
    
    # Check environment file
    if [ ! -f ".env.production" ]; then
        log_error ".env.production file not found"
        log_info "Please copy .env.production.example and configure it"
        exit 1
    fi
    
    log_success "Dependencies check passed"
}

setup_ssl() {
    log_info "Setting up SSL certificates..."
    
    # Create SSL directory
    mkdir -p deployment/ssl
    
    if [ "$ENVIRONMENT" = "production" ]; then
        # Check if certificates exist
        if [ ! -f "deployment/ssl/cert.pem" ] || [ ! -f "deployment/ssl/key.pem" ]; then
            log_warning "SSL certificates not found"
            log_info "Generating self-signed certificates for development..."
            
            # Generate self-signed certificate
            openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
                -keyout deployment/ssl/key.pem \
                -out deployment/ssl/cert.pem \
                -subj "/C=US/ST=State/L=City/O=Organization/CN=$DOMAIN"
            
            log_warning "Self-signed certificates generated. Replace with real certificates for production!"
        fi
    else
        log_info "Development mode: using self-signed certificates"
        
        # Generate development certificates
        openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
            -keyout deployment/ssl/key.pem \
            -out deployment/ssl/cert.pem \
            -subj "/C=US/ST=Development/L=Local/O=MCP Memory/CN=localhost"
    fi
    
    log_success "SSL certificates ready"
}

prepare_environment() {
    log_info "Preparing environment..."
    
    # Copy production environment
    cp .env.production .env
    
    # Create required directories
    mkdir -p logs
    mkdir -p data
    mkdir -p backups
    
    # Set permissions
    chmod 755 logs data backups
    
    log_success "Environment prepared"
}

build_images() {
    log_info "Building Docker images..."
    
    # Build main application image
    docker build -t mcp-memory-cloud:latest .
    
    # Build frontend image
    cd frontend
    docker build -t mcp-memory-frontend:latest .
    cd ..
    
    log_success "Docker images built"
}

deploy_services() {
    log_info "Deploying services..."
    
    # Pull required images
    docker-compose pull redis nginx
    
    # Deploy with Docker Compose
    docker-compose -f $COMPOSE_FILE up -d
    
    log_success "Services deployed"
}

wait_for_services() {
    log_info "Waiting for services to be ready..."
    
    # Wait for API Gateway
    timeout=60
    while [ $timeout -gt 0 ]; do
        if curl -f http://localhost:8000/health &> /dev/null; then
            break
        fi
        sleep 2
        timeout=$((timeout - 2))
    done
    
    if [ $timeout -le 0 ]; then
        log_error "API Gateway failed to start"
        exit 1
    fi
    
    # Wait for Frontend
    timeout=60
    while [ $timeout -gt 0 ]; do
        if curl -f http://localhost:3000 &> /dev/null; then
            break
        fi
        sleep 2
        timeout=$((timeout - 2))
    done
    
    if [ $timeout -le 0 ]; then
        log_error "Frontend failed to start"
        exit 1
    fi
    
    log_success "All services are ready"
}

setup_monitoring() {
    log_info "Setting up monitoring..."
    
    # Create monitoring configuration
    cat > prometheus.yml <<EOF
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'mcp-memory-api'
    static_configs:
      - targets: ['api-gateway:8000']
    metrics_path: '/metrics'
    
  - job_name: 'mcp-memory-billing'
    static_configs:
      - targets: ['billing-service:8001']
    metrics_path: '/metrics'
EOF
    
    log_success "Monitoring configured"
}

verify_deployment() {
    log_info "Verifying deployment..."
    
    # Check API Gateway
    if ! curl -f http://localhost:8000/health; then
        log_error "API Gateway health check failed"
        return 1
    fi
    
    # Check Frontend
    if ! curl -f http://localhost:3000; then
        log_error "Frontend check failed"
        return 1
    fi
    
    # Check database connectivity
    docker-compose exec api-gateway python -c "
import asyncio
from cloud.mongodb_provisioner import MongoDBCloudProvisioner

async def test():
    provisioner = MongoDBCloudProvisioner()
    await provisioner.initialize()
    print('Database connection successful')

asyncio.run(test())
" || {
        log_error "Database connection failed"
        return 1
    }
    
    log_success "Deployment verification passed"
}

show_status() {
    log_info "Deployment Status:"
    echo ""
    docker-compose ps
    echo ""
    log_info "URLs:"
    echo "  Frontend: https://$DOMAIN"
    echo "  API:      https://$API_DOMAIN"
    echo "  Health:   https://$DOMAIN/health"
    echo ""
    log_info "Logs:"
    echo "  docker-compose logs -f [service]"
    echo ""
}

cleanup() {
    log_info "Cleaning up..."
    docker-compose down
    docker system prune -f
}

# Main deployment flow
main() {
    echo ""
    log_info "🌩️ MCP Memory Cloud Deployment"
    echo "=================================="
    echo ""
    
    case "$1" in
        "deploy")
            check_dependencies
            setup_ssl
            prepare_environment
            build_images
            deploy_services
            wait_for_services
            setup_monitoring
            verify_deployment
            show_status
            ;;
        "update")
            log_info "Updating deployment..."
            build_images
            docker-compose up -d --force-recreate
            wait_for_services
            verify_deployment
            show_status
            ;;
        "stop")
            log_info "Stopping services..."
            docker-compose stop
            ;;
        "start")
            log_info "Starting services..."
            docker-compose start
            wait_for_services
            show_status
            ;;
        "restart")
            log_info "Restarting services..."
            docker-compose restart
            wait_for_services
            show_status
            ;;
        "status")
            show_status
            ;;
        "logs")
            docker-compose logs -f ${2:-}
            ;;
        "cleanup")
            cleanup
            ;;
        "ssl")
            setup_ssl
            ;;
        *)
            echo "Usage: $0 {deploy|update|start|stop|restart|status|logs|cleanup|ssl}"
            echo ""
            echo "Commands:"
            echo "  deploy   - Full deployment (first time)"
            echo "  update   - Update deployment with new code"
            echo "  start    - Start stopped services"
            echo "  stop     - Stop running services"
            echo "  restart  - Restart all services"
            echo "  status   - Show deployment status"
            echo "  logs     - Show logs (optional service name)"
            echo "  cleanup  - Clean up containers and images"
            echo "  ssl      - Setup/update SSL certificates"
            echo ""
            exit 1
            ;;
    esac
}

# Error handling
trap 'log_error "Deployment failed on line $LINENO"' ERR

# Run main function
main "$@" 