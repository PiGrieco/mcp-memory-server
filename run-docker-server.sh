#!/bin/bash

# =============================================================================
# Run Docker MCP Memory Server on Remote Instance
# =============================================================================

echo "🐳 Starting MCP Memory Server on Remote Instance"
echo "================================================"

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

print_info "Using: $DOCKER_COMPOSE"

# Step 1: Stop any existing containers
print_info "Step 1: Stopping existing containers..."
$DOCKER_COMPOSE down
print_success "Containers stopped"

# Step 2: Open firewall port
print_info "Step 2: Opening firewall port 8000..."
if command -v ufw >/dev/null 2>&1; then
    sudo ufw allow 8000
    print_success "UFW: Port 8000 opened"
elif command -v firewall-cmd >/dev/null 2>&1; then
    sudo firewall-cmd --permanent --add-port=8000/tcp
    sudo firewall-cmd --reload
    print_success "Firewalld: Port 8000 opened"
else
    print_warning "No firewall tool found - manually ensure port 8000 is open"
fi

# Step 3: Build Docker image
print_info "Step 3: Building Docker image (this may take a few minutes)..."
$DOCKER_COMPOSE build --no-cache mcp-memory-server-http
if [ $? -eq 0 ]; then
    print_success "Docker image built successfully"
else
    print_error "Failed to build Docker image"
    exit 1
fi

# Step 4: Start HTTP server
print_info "Step 4: Starting MCP Memory Server HTTP container..."
$DOCKER_COMPOSE up -d mcp-memory-server-http
if [ $? -eq 0 ]; then
    print_success "Container started"
else
    print_error "Failed to start container"
    exit 1
fi

# Step 5: Wait for server to initialize
print_info "Step 5: Waiting for server to initialize..."
sleep 15

# Step 6: Check container status
print_info "Step 6: Checking container status..."
$DOCKER_COMPOSE ps

# Step 7: Check container logs
print_info "Step 7: Checking container logs..."
$DOCKER_COMPOSE logs --tail=20 mcp-memory-server-http

# Step 8: Test local connectivity
print_info "Step 8: Testing local connectivity..."
for i in {1..10}; do
    if curl -s -f "http://localhost:8000/health" > /dev/null; then
        print_success "✅ Server responding on localhost:8000"
        curl -s "http://localhost:8000/health" | python3 -m json.tool 2>/dev/null || curl -s "http://localhost:8000/health"
        break
    else
        print_warning "Attempt $i/10: Server not ready, waiting 3 seconds..."
        sleep 3
    fi
    
    if [ $i -eq 10 ]; then
        print_error "Server failed to respond after 30 seconds"
        print_info "Container logs:"
        $DOCKER_COMPOSE logs mcp-memory-server-http
        exit 1
    fi
done

# Step 9: Test external connectivity
print_info "Step 9: Testing external connectivity..."
SERVER_IP=$(curl -s ifconfig.me 2>/dev/null || curl -s ipinfo.io/ip 2>/dev/null || echo "YOUR_SERVER_IP")

if curl -s -f "http://${SERVER_IP}:8000/health" > /dev/null; then
    print_success "✅ Server accessible externally at http://${SERVER_IP}:8000"
else
    print_warning "Server not accessible externally (may be firewall/network issue)"
fi

# Step 10: Test MCP functionality
print_info "Step 10: Testing MCP functionality..."
response=$(curl -s -X POST "http://localhost:8000/mcp" \
  -H 'Content-Type: application/json' \
  -d '{
    "jsonrpc": "2.0",
    "id": 1,
    "method": "tools/list",
    "params": {}
  }')

if echo "$response" | grep -q '"tools"'; then
    print_success "✅ MCP functionality working"
    echo "$response" | python3 -c "
import json, sys
try:
    data = json.load(sys.stdin)
    tools = data.get('result', {}).get('tools', [])
    print(f'Found {len(tools)} MCP tools:')
    for tool in tools:
        print(f'  - {tool[\"name\"]}: {tool[\"description\"]}')
except:
    print('Response received but could not parse JSON')
" 2>/dev/null || echo "MCP tools available"
else
    print_error "MCP functionality test failed"
    echo "Response: $response"
fi

echo ""
print_success "🎉 MCP Memory Server is running!"
echo ""
echo "📡 Server Information:"
echo "• Local Health: http://localhost:8000/health"
echo "• External Health: http://${SERVER_IP}:8000/health"
echo "• MCP Endpoint: http://${SERVER_IP}:8000/mcp"
echo ""
echo "🔧 Management Commands:"
echo "• View logs: $DOCKER_COMPOSE logs -f mcp-memory-server-http"
echo "• Stop server: $DOCKER_COMPOSE down"
echo "• Restart: $DOCKER_COMPOSE restart mcp-memory-server-http"
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
echo ""
print_success "🚀 Ready for Cursor IDE integration!"
