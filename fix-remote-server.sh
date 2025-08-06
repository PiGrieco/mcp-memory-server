#!/bin/bash

# =============================================================================
# Fix Remote MCP Memory Server Issues
# =============================================================================

echo "🔧 Fixing MCP Memory Server Remote Access"
echo "========================================="

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

print_info() { echo -e "${BLUE}ℹ️  $1${NC}"; }
print_success() { echo -e "${GREEN}✅ $1${NC}"; }
print_error() { echo -e "${RED}❌ $1${NC}"; }
print_warning() { echo -e "${YELLOW}⚠️  $1${NC}"; }

# Detect Docker Compose
if docker-compose --version 2>/dev/null; then
    DOCKER_COMPOSE="docker-compose"
elif docker compose version 2>/dev/null; then
    DOCKER_COMPOSE="docker compose"
else
    print_error "Docker Compose not found"
    exit 1
fi

print_info "Step 1: Opening firewall port 8000"
if command -v ufw >/dev/null 2>&1; then
    sudo ufw allow 8000
    print_success "UFW: Port 8000 opened"
elif command -v firewall-cmd >/dev/null 2>&1; then
    sudo firewall-cmd --permanent --add-port=8000/tcp
    sudo firewall-cmd --reload
    print_success "Firewalld: Port 8000 opened"
else
    print_warning "No firewall tool found - manually open port 8000"
fi

print_info "Step 2: Stopping existing containers"
$DOCKER_COMPOSE down

print_info "Step 3: Ensuring aiohttp is in requirements"
if ! grep -q "aiohttp" requirements.txt; then
    echo "aiohttp==3.12.15" >> requirements.txt
    echo "aiohttp-cors==0.8.0" >> requirements.txt
    print_success "Added aiohttp to requirements.txt"
fi

print_info "Step 4: Rebuilding Docker image"
$DOCKER_COMPOSE build --no-cache mcp-memory-server-http

print_info "Step 5: Starting HTTP server"
$DOCKER_COMPOSE up -d mcp-memory-server-http

print_info "Step 6: Waiting for server to start"
sleep 15

print_info "Step 7: Testing local connectivity"
for i in {1..5}; do
    if curl -s -f "http://localhost:8000/health" > /dev/null; then
        print_success "Server is responding locally"
        break
    else
        print_warning "Attempt $i: Server not ready, waiting..."
        sleep 5
    fi
done

print_info "Step 8: Testing external connectivity"
SERVER_IP=$(curl -s ifconfig.me 2>/dev/null || curl -s ipinfo.io/ip 2>/dev/null || echo "YOUR_SERVER_IP")

if curl -s -f "http://${SERVER_IP}:8000/health" > /dev/null; then
    print_success "Server is accessible externally!"
else
    print_error "Server not accessible externally"
    print_info "Checking container logs..."
    $DOCKER_COMPOSE logs --tail=20 mcp-memory-server-http
fi

echo ""
print_info "Server status:"
$DOCKER_COMPOSE ps

echo ""
print_success "🎉 Fix completed!"
echo ""
echo "📡 Test your server:"
echo "curl http://${SERVER_IP}:8000/health"
echo ""
echo "📁 Cursor IDE Configuration:"
echo "{"
echo "  \"mcpServers\": {"
echo "    \"memory-server\": {"
echo "      \"transport\": \"http\","
echo "      \"url\": \"http://${SERVER_IP}:8000/mcp\""
echo "    }"
echo "  }"
echo "}"
