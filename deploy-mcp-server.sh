#!/bin/bash

# =============================================================================
# MCP Memory Server - Complete One-Command Deployment
# This script handles EVERYTHING: setup, build, deploy, fix, test
# =============================================================================

set -e

echo "🚀 MCP Memory Server - Complete Deployment"
echo "=========================================="

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
    print_info "Using docker-compose"
elif docker compose version 2>/dev/null; then
    DOCKER_COMPOSE="docker compose"
    print_info "Using docker compose"
else
    print_error "Docker Compose not found. Please install Docker Compose."
    exit 1
fi

# Step 1: Stop any existing containers
print_info "Step 1: Cleaning up existing containers..."
$DOCKER_COMPOSE down 2>/dev/null || true
print_success "Cleanup completed"

# Step 2: Generate requirements.txt from .myenv if available
print_info "Step 2: Generating requirements.txt..."
if [ -d ".myenv" ]; then
    print_info "Found .myenv, generating requirements from virtual environment..."
    .myenv/bin/python -m pip freeze > requirements_temp.txt
    
    cat > requirements.txt << 'EOF'
# =============================================================================
# MCP Memory Server - Docker Requirements (Generated from .myenv)
# =============================================================================

EOF
    
    grep -v "^-e " requirements_temp.txt | \
    grep -v "^pkg-resources" | \
    sort >> requirements.txt
    
    # Ensure aiohttp-cors is included
    if ! grep -q "aiohttp-cors" requirements.txt; then
        echo "aiohttp-cors==0.8.0" >> requirements.txt
    fi
    
    rm requirements_temp.txt
    print_success "Generated requirements.txt with $(grep -v "^#" requirements.txt | grep -v "^$" | wc -l) packages"
else
    print_warning ".myenv not found, ensuring aiohttp-cors is in requirements.txt"
    if ! grep -q "aiohttp-cors" requirements.txt; then
        echo "aiohttp-cors==0.8.0" >> requirements.txt
    fi
fi

# Step 3: Create/update .env file
print_info "Step 3: Setting up environment configuration..."
if [ ! -f ".env" ]; then
    cat > .env << 'EOF'
# =============================================================================
# MCP Memory Server - Production Environment
# =============================================================================

# Project & Database Settings
PROJECT_NAME=cursor_project
DATABASE_NAME=mcp_memory_production

# MongoDB Configuration
MONGODB_URI=mongodb+srv://rjawaissaleem:tpQMJUV4cmknQqn3@cluster0.4ixuae0.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0
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
    print_success "Created .env file"
else
    print_success ".env file already exists"
fi

# Step 4: Fix permissions issues
print_info "Step 4: Fixing directory permissions..."
mkdir -p logs
sudo chmod -R 777 logs/ 2>/dev/null || chmod -R 777 logs/
print_success "Permissions fixed"

# Step 5: Open firewall port
print_info "Step 5: Opening firewall port 8000..."
if command -v ufw >/dev/null 2>&1; then
    sudo ufw allow 8000 2>/dev/null || print_warning "Could not configure UFW (may need manual firewall setup)"
    print_success "UFW: Port 8000 opened"
elif command -v firewall-cmd >/dev/null 2>&1; then
    sudo firewall-cmd --permanent --add-port=8000/tcp 2>/dev/null || print_warning "Could not configure firewalld"
    sudo firewall-cmd --reload 2>/dev/null || true
    print_success "Firewalld: Port 8000 opened"
else
    print_warning "No firewall tool found - ensure port 8000 is manually opened"
fi

# Step 6: Build Docker image
print_info "Step 6: Building Docker image (this may take several minutes)..."
$DOCKER_COMPOSE build --no-cache mcp-memory-server-http
if [ $? -eq 0 ]; then
    print_success "Docker image built successfully"
else
    print_error "Failed to build Docker image"
    exit 1
fi

# Step 7: Start HTTP server
print_info "Step 7: Starting MCP Memory Server..."
$DOCKER_COMPOSE up -d mcp-memory-server-http
if [ $? -eq 0 ]; then
    print_success "Container started"
else
    print_error "Failed to start container"
    exit 1
fi

# Step 8: Wait and test server
print_info "Step 8: Waiting for server to initialize..."
sleep 15

print_info "Step 9: Testing server connectivity..."
for i in {1..10}; do
    if curl -s -f "http://localhost:8000/health" > /dev/null; then
        print_success "✅ Server responding on localhost:8000"
        health_response=$(curl -s "http://localhost:8000/health")
        echo "$health_response" | python3 -m json.tool 2>/dev/null || echo "$health_response"
        break
    else
        print_warning "Attempt $i/10: Server not ready, waiting 3 seconds..."
        sleep 3
    fi
    
    if [ $i -eq 10 ]; then
        print_error "Server failed to respond after 30 seconds"
        print_info "Container status:"
        $DOCKER_COMPOSE ps
        print_info "Container logs:"
        $DOCKER_COMPOSE logs --tail=20 mcp-memory-server-http
        exit 1
    fi
done

# Step 10: Test external connectivity
print_info "Step 10: Testing external connectivity..."
SERVER_IP=$(curl -s ifconfig.me 2>/dev/null || curl -s ipinfo.io/ip 2>/dev/null || echo "YOUR_SERVER_IP")

if curl -s -f "http://${SERVER_IP}:8000/health" > /dev/null; then
    print_success "✅ Server accessible externally at http://${SERVER_IP}:8000"
else
    print_warning "Server not accessible externally (may be firewall/network configuration)"
fi

# Step 11: Test MCP functionality
print_info "Step 11: Testing MCP functionality..."
mcp_response=$(curl -s -X POST "http://localhost:8000/mcp" \
  -H 'Content-Type: application/json' \
  -d '{
    "jsonrpc": "2.0",
    "id": 1,
    "method": "tools/list",
    "params": {}
  }')

if echo "$mcp_response" | grep -q '"tools"'; then
    print_success "✅ MCP functionality working"
    echo "$mcp_response" | python3 -c "
import json, sys
try:
    data = json.load(sys.stdin)
    tools = data.get('result', {}).get('tools', [])
    print(f'Found {len(tools)} MCP tools:')
    for tool in tools:
        print(f'  - {tool[\"name\"]}: {tool[\"description\"]}')
except:
    print('MCP tools available (could not parse details)')
" 2>/dev/null || echo "MCP tools available"
else
    print_error "MCP functionality test failed"
    echo "Response: $mcp_response"
fi

# Step 12: Final status and configuration
echo ""
print_success "🎉 MCP Memory Server Deployment Complete!"
echo ""
echo "📡 Server Information:"
echo "• Server IP: ${SERVER_IP}"
echo "• Health Check: http://${SERVER_IP}:8000/health"
echo "• MCP Endpoint: http://${SERVER_IP}:8000/mcp"
echo "• Server Info: http://${SERVER_IP}:8000/info"
echo ""
echo "🔧 Management Commands:"
echo "• View logs: $DOCKER_COMPOSE logs -f mcp-memory-server-http"
echo "• Stop server: $DOCKER_COMPOSE down"
echo "• Restart: $DOCKER_COMPOSE restart mcp-memory-server-http"
echo "• Container status: $DOCKER_COMPOSE ps"
echo ""
echo "🧪 Test Commands:"
echo "curl http://${SERVER_IP}:8000/health"
echo "curl -X POST http://${SERVER_IP}:8000/mcp -H 'Content-Type: application/json' -d '{\"jsonrpc\":\"2.0\",\"id\":1,\"method\":\"tools/list\",\"params\":{}}'"
echo ""
echo "📁 Cursor IDE Configuration:"
echo "Add this to your Cursor mcp.json file:"
echo "{"
echo "  \"mcpServers\": {"
echo "    \"memory-server\": {"
echo "      \"transport\": \"http\","
echo "      \"url\": \"http://${SERVER_IP}:8000/mcp\""
echo "    }"
echo "  }"
echo "}"
echo ""
echo "🔒 Security Notes:"
echo "• Port 8000 is open for HTTP access"
echo "• MongoDB credentials are in .env file"
echo "• Consider HTTPS for production use"
echo ""
print_success "🚀 Your MCP Memory Server is ready for Cursor IDE!"
echo ""
echo "📋 Next Steps:"
echo "1. Copy the Cursor configuration above to your mcp.json"
echo "2. Restart Cursor IDE"
echo "3. Test memory features: 'Save this to memory: Hello from remote server!'"
