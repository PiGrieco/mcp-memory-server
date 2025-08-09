#!/bin/bash

# =============================================================================
# MCP Memory Server - Remote Server Deployment Script
# Deploy MCP Memory Server on remote instance with HTTP access
# =============================================================================

set -e

echo "🌐 MCP Memory Server - Remote Deployment"
echo "========================================"

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

print_status() { echo -e "${GREEN}✅ $1${NC}"; }
print_warning() { echo -e "${YELLOW}⚠️  $1${NC}"; }
print_error() { echo -e "${RED}❌ $1${NC}"; }
print_info() { echo -e "${BLUE}ℹ️  $1${NC}"; }

# Check Docker
if ! docker --version; then
    print_error "Docker not found. Please install Docker first."
    exit 1
fi

# Detect Docker Compose
if docker-compose --version 2>/dev/null; then
    DOCKER_COMPOSE="docker-compose"
elif docker compose version 2>/dev/null; then
    DOCKER_COMPOSE="docker compose"
else
    print_error "Docker Compose not found"
    exit 1
fi

print_status "Docker and Docker Compose detected"

# Generate requirements.txt if .myenv exists
if [ -d ".myenv" ]; then
    print_info "Generating requirements.txt from .myenv..."
    .myenv/bin/python -m pip freeze > requirements_temp.txt
    
    cat > requirements.txt << 'EOF'
# =============================================================================
# MCP Memory Server - Docker Requirements (Generated from .myenv)
# =============================================================================

EOF
    
    grep -v "^-e " requirements_temp.txt | \
    grep -v "^pkg-resources" | \
    sort >> requirements.txt
    
    rm requirements_temp.txt
    print_status "Generated requirements.txt"
fi

# Create .env if not exists
if [ ! -f ".env" ]; then
    print_info "Creating .env file..."
    cat > .env << 'EOF'
# =============================================================================
# MCP Memory Server - Remote Server Configuration
# =============================================================================

# Project & Database Settings
PROJECT_NAME=cursor_project
DATABASE_NAME=mcp_memory_production

# MongoDB Configuration
MONGODB_URI=mongodb://localhost:27017
MONGODB_DATABASE=mcp_memory_production
MONGODB_COLLECTION=memories

# Environment
ENVIRONMENT=production

# Embedding Model
EMBEDDING_MODEL=all-MiniLM-L6-v2

# HTTP Server Settings
HOST=0.0.0.0
PORT=8000
EOF
    print_status "Created .env file"
fi

# Create logs directory
mkdir -p logs

# Stop any existing containers
print_info "Stopping existing containers..."
$DOCKER_COMPOSE down 2>/dev/null || true

# Build the image
print_info "Building Docker image..."
$DOCKER_COMPOSE build --no-cache

# Start HTTP server
print_info "Starting MCP Memory Server in HTTP mode..."
$DOCKER_COMPOSE up -d mcp-memory-server-http

# Wait for server to start
print_info "Waiting for server to start..."
sleep 10

# Check if server is running
if $DOCKER_COMPOSE ps | grep -q "mcp-memory-server-http.*Up"; then
    print_status "HTTP server is running"
else
    print_error "Failed to start HTTP server"
    $DOCKER_COMPOSE logs mcp-memory-server-http
    exit 1
fi

# Get server IP
SERVER_IP=$(curl -s ifconfig.me 2>/dev/null || curl -s ipinfo.io/ip 2>/dev/null || echo "YOUR_SERVER_IP")

echo ""
print_status "🎉 MCP Memory Server deployed successfully!"
echo ""
echo "📡 Server Information:"
echo "• HTTP Endpoint: http://${SERVER_IP}:8000/mcp"
echo "• Health Check: http://${SERVER_IP}:8000/health"
echo "• Server Info: http://${SERVER_IP}:8000/info"
echo ""
echo "🔧 Management Commands:"
echo "• View logs: $DOCKER_COMPOSE logs -f mcp-memory-server-http"
echo "• Stop server: $DOCKER_COMPOSE down"
echo "• Restart: $DOCKER_COMPOSE restart mcp-memory-server-http"
echo ""
echo "🧪 Test the server:"
echo "curl -X POST http://${SERVER_IP}:8000/mcp \\"
echo "  -H 'Content-Type: application/json' \\"
echo "  -d '{\"jsonrpc\":\"2.0\",\"id\":1,\"method\":\"tools/list\",\"params\":{}}'"
echo ""
echo "📁 Cursor IDE Configuration:"
echo "{"
echo "  \"mcpServers\": {"
echo "    \"memory-server\": {"
echo "      \"command\": \"curl\","
echo "      \"args\": [\"-X\", \"POST\", \"http://${SERVER_IP}:8000/mcp\", \"-H\", \"Content-Type: application/json\", \"-d\"],"
echo "      \"transport\": \"http\","
echo "      \"url\": \"http://${SERVER_IP}:8000/mcp\""
echo "    }"
echo "  }"
echo "}"
echo ""
echo "🔒 Security Notes:"
echo "• Server is running on port 8000"
echo "• Make sure firewall allows port 8000"
echo "• Consider using HTTPS in production"
echo "• MongoDB credentials are in .env file"
echo ""
print_status "🚀 Your remote MCP Memory Server is ready!"

# Test the server
print_info "Testing server connectivity..."
if curl -s -f "http://localhost:8000/health" > /dev/null; then
    print_status "Server health check passed"
else
    print_warning "Health check failed - server may still be starting"
fi
