#!/bin/bash

# =============================================================================
# Fix MCP Memory Server Permissions Issue
# =============================================================================

echo "🔧 Fixing MCP Memory Server Permissions"
echo "======================================="

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

print_info() { echo -e "${BLUE}ℹ️  $1${NC}"; }
print_success() { echo -e "${GREEN}✅ $1${NC}"; }
print_error() { echo -e "${RED}❌ $1${NC}"; }

# Detect Docker Compose
if docker-compose --version 2>/dev/null; then
    DOCKER_COMPOSE="docker-compose"
elif docker compose version 2>/dev/null; then
    DOCKER_COMPOSE="docker compose"
else
    print_error "Docker Compose not found"
    exit 1
fi

print_info "Step 1: Stopping containers"
$DOCKER_COMPOSE down

print_info "Step 2: Fixing logs directory permissions"
sudo chmod -R 777 logs/
print_success "Logs directory permissions fixed"

print_info "Step 3: Rebuilding Docker image with permission fixes"
$DOCKER_COMPOSE build --no-cache mcp-memory-server-http

print_info "Step 4: Starting container"
$DOCKER_COMPOSE up -d mcp-memory-server-http

print_info "Step 5: Waiting for server to start"
sleep 10

print_info "Step 6: Checking container status"
$DOCKER_COMPOSE ps

print_info "Step 7: Testing server"
for i in {1..5}; do
    if curl -s -f "http://localhost:8000/health" > /dev/null; then
        print_success "✅ Server is working!"
        curl -s "http://localhost:8000/health"
        break
    else
        echo "Attempt $i/5: Waiting for server..."
        sleep 3
    fi
    
    if [ $i -eq 5 ]; then
        print_error "Server still not responding. Checking logs..."
        $DOCKER_COMPOSE logs --tail=10 mcp-memory-server-http
    fi
done

# Get server IP
SERVER_IP=$(curl -s ifconfig.me 2>/dev/null || curl -s ipinfo.io/ip 2>/dev/null || echo "YOUR_SERVER_IP")

echo ""
print_success "🎉 Server should be working now!"
echo ""
echo "📡 Test URLs:"
echo "• Health: http://${SERVER_IP}:8000/health"
echo "• MCP: http://${SERVER_IP}:8000/mcp"
echo ""
echo "📁 Cursor Configuration:"
echo "{"
echo "  \"mcpServers\": {"
echo "    \"memory-server\": {"
echo "      \"transport\": \"http\","
echo "      \"url\": \"http://${SERVER_IP}:8000/mcp\""
echo "    }"
echo "  }"
echo "}"
