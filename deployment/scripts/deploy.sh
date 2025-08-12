#!/bin/bash

# MCP Memory Server - Deployment Script
# Deploys the complete MCP Memory Server with MongoDB and Redis

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Script configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$(dirname "$SCRIPT_DIR")")"
DOCKER_DIR="$PROJECT_ROOT/deployment/docker"

echo "🚀 MCP Memory Server - Deployment Script"
echo "========================================"

# Function to show usage
show_usage() {
    echo "Usage: $0 [COMMAND] [OPTIONS]"
    echo ""
    echo "Commands:"
    echo "  deploy [docker|kubernetes]  - Deploy the application"
    echo "  start                       - Start all services"
    echo "  stop                        - Stop all services"
    echo "  restart                     - Restart all services"
    echo "  status                      - Show service status"
    echo "  logs [service]              - Show logs for a service"
    echo "  backup                      - Create backup"
    echo "  restore [backup_file]       - Restore from backup"
    echo "  clean                       - Clean up containers and volumes"
    echo "  help                        - Show this help"
    echo ""
    echo "Options:"
    echo "  --env [dev|staging|prod]    - Environment (default: prod)"
    echo "  --profile [basic|full]      - Deployment profile (default: basic)"
    echo ""
    echo "Examples:"
    echo "  $0 deploy docker --env prod --profile full"
    echo "  $0 start"
    echo "  $0 logs mcp-memory-server"
}

# Function to check prerequisites
check_prerequisites() {
    echo -e "\n${BLUE}🔍 Checking prerequisites...${NC}"
    
    # Check Docker
    if ! command -v docker &> /dev/null; then
        echo -e "${RED}❌ Docker not found. Please install Docker.${NC}"
        exit 1
    fi
    
    # Check Docker Compose (new version)
    if ! docker compose version &> /dev/null; then
        echo -e "${RED}❌ Docker Compose not found. Please install Docker Compose.${NC}"
        exit 1
    fi
    
    # Check if Docker is running
    if ! docker info &> /dev/null; then
        echo -e "${RED}❌ Docker is not running. Please start Docker.${NC}"
        exit 1
    fi
    
    echo -e "${GREEN}✅ Prerequisites check completed${NC}"
}

# Function to deploy with Docker
deploy_docker() {
    local env=${1:-prod}
    local profile=${2:-basic}
    
    echo -e "\n${BLUE}🐳 Deploying with Docker (Environment: $env, Profile: $profile)...${NC}"
    
    cd "$DOCKER_DIR"
    
    # Create necessary directories
    mkdir -p logs data exports backups mongo-init
    
    # Create MongoDB initialization script
    cat > mongo-init/init.js << 'EOF'
db = db.getSiblingDB('mcp_memory_production');

// Create collections
db.createCollection('memories');
db.createCollection('analytics');
db.createCollection('backups');

// Create indexes
db.memories.createIndex({ "content": "text" });
db.memories.createIndex({ "project": 1 });
db.memories.createIndex({ "created_at": -1 });
db.memories.createIndex({ "user_id": 1 });

// Create user for the application
db.createUser({
  user: "mcp_user",
  pwd: "mcp_password",
  roles: [
    { role: "readWrite", db: "mcp_memory_production" }
  ]
});

print("MongoDB initialization completed");
EOF
    
    # Set environment variables
    export ENVIRONMENT=$env
    
    # Start services based on profile
    if [ "$profile" = "full" ]; then
        echo -e "${YELLOW}Starting full deployment with monitoring...${NC}"
        docker compose --profile monitoring --profile production up -d
    else
        echo -e "${YELLOW}Starting basic deployment...${NC}"
        docker compose up -d
    fi
    
    echo -e "${GREEN}✅ Docker deployment completed${NC}"
}

# Function to start services
start_services() {
    echo -e "\n${BLUE}🚀 Starting services...${NC}"
    cd "$DOCKER_DIR"
    docker compose up -d
    echo -e "${GREEN}✅ Services started${NC}"
}

# Function to stop services
stop_services() {
    echo -e "\n${BLUE}🛑 Stopping services...${NC}"
    cd "$DOCKER_DIR"
    docker compose down
    echo -e "${GREEN}✅ Services stopped${NC}"
}

# Function to restart services
restart_services() {
    echo -e "\n${BLUE}🔄 Restarting services...${NC}"
    cd "$DOCKER_DIR"
    docker compose restart
    echo -e "${GREEN}✅ Services restarted${NC}"
}

# Function to show status
show_status() {
    echo -e "\n${BLUE}📊 Service Status:${NC}"
    cd "$DOCKER_DIR"
    docker compose ps
    
    echo -e "\n${BLUE}🔍 Health Checks:${NC}"
    
    # Check MongoDB
    if docker compose ps mongodb | grep -q "Up"; then
        echo -e "${GREEN}✅ MongoDB: Running${NC}"
    else
        echo -e "${RED}❌ MongoDB: Not running${NC}"
    fi
    
    # Check Redis
    if docker compose ps redis | grep -q "Up"; then
        echo -e "${GREEN}✅ Redis: Running${NC}"
    else
        echo -e "${RED}❌ Redis: Not running${NC}"
    fi
    
    # Check MCP Server
    if docker compose ps mcp-memory-server | grep -q "Up"; then
        echo -e "${GREEN}✅ MCP Server: Running${NC}"
        # Test HTTP endpoint
        if curl -s http://localhost:8000/health > /dev/null; then
            echo -e "${GREEN}✅ HTTP API: Responding${NC}"
        else
            echo -e "${YELLOW}⚠️ HTTP API: Not responding${NC}"
        fi
    else
        echo -e "${RED}❌ MCP Server: Not running${NC}"
    fi
}

# Function to show logs
show_logs() {
    local service=${1:-mcp-memory-server}
    echo -e "\n${BLUE}📝 Logs for $service:${NC}"
    cd "$DOCKER_DIR"
    docker compose logs -f "$service"
}

# Function to create backup
create_backup() {
    echo -e "\n${BLUE}💾 Creating backup...${NC}"
    
    local backup_dir="$PROJECT_ROOT/backups"
    local timestamp=$(date +%Y%m%d_%H%M%S)
    local backup_file="backup_$timestamp.tar.gz"
    
    mkdir -p "$backup_dir"
    
    cd "$DOCKER_DIR"
    
    # Backup MongoDB data
    docker compose exec -T mongodb mongodump --archive --gzip > "$backup_dir/mongodb_$backup_file"
    
    # Backup Redis data
    docker compose exec -T redis redis-cli --rdb /data/dump.rdb
    docker cp mcp-redis:/data/dump.rdb "$backup_dir/redis_$timestamp.rdb"
    
    # Backup application data
    tar -czf "$backup_dir/app_$backup_file" -C "$PROJECT_ROOT" data exports logs
    
    echo -e "${GREEN}✅ Backup created: $backup_dir/$backup_file${NC}"
}

# Function to restore from backup
restore_backup() {
    local backup_file=$1
    
    if [ -z "$backup_file" ]; then
        echo -e "${RED}❌ Please specify backup file${NC}"
        exit 1
    fi
    
    echo -e "\n${BLUE}🔄 Restoring from backup: $backup_file${NC}"
    
    # Implementation depends on backup format
    echo -e "${YELLOW}⚠️ Restore functionality not implemented yet${NC}"
}

# Function to clean up
clean_up() {
    echo -e "\n${BLUE}🧹 Cleaning up...${NC}"
    cd "$DOCKER_DIR"
    
    # Stop and remove containers
    docker compose down -v
    
    # Remove volumes
    docker volume prune -f
    
    # Remove images
    docker image prune -f
    
    echo -e "${GREEN}✅ Cleanup completed${NC}"
}

# Main script logic
case "${1:-help}" in
    deploy)
        check_prerequisites
        case "${2:-docker}" in
            docker)
                deploy_docker "${3:-prod}" "${4:-basic}"
                ;;
            kubernetes)
                echo -e "${YELLOW}⚠️ Kubernetes deployment not implemented yet${NC}"
                ;;
            *)
                echo -e "${RED}❌ Unknown deployment method: $2${NC}"
                show_usage
                exit 1
                ;;
        esac
        ;;
    start)
        check_prerequisites
        start_services
        ;;
    stop)
        stop_services
        ;;
    restart)
        restart_services
        ;;
    status)
        show_status
        ;;
    logs)
        show_logs "$2"
        ;;
    backup)
        create_backup
        ;;
    restore)
        restore_backup "$2"
        ;;
    clean)
        clean_up
        ;;
    help|*)
        show_usage
        ;;
esac 