#!/bin/bash

# =============================================================================
# Quick Fix for Environment Variables Issue
# =============================================================================

echo "🔧 Quick Fix: Environment Variables"
echo "==================================="

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

print_info "Step 1: Stopping container"
$DOCKER_COMPOSE down

print_info "Step 2: Rebuilding with environment fix"
$DOCKER_COMPOSE build --no-cache mcp-memory-server-http

print_info "Step 3: Starting with explicit environment variables"
$DOCKER_COMPOSE up -d mcp-memory-server-http

print_info "Step 4: Waiting for server..."
sleep 10

print_info "Step 5: Testing server"
for i in {1..5}; do
    if curl -s -f "http://localhost:8000/health" > /dev/null; then
        print_success "✅ Server is working!"
        curl -s "http://localhost:8000/health"
        break
    else
        echo "Attempt $i/5: Waiting..."
        sleep 3
    fi
    
    if [ $i -eq 5 ]; then
        print_error "Still not working. Checking logs..."
        $DOCKER_COMPOSE logs --tail=10 mcp-memory-server-http
        
        print_info "Testing environment variables inside container..."
        $DOCKER_COMPOSE exec -T mcp-memory-server-http python -c "
import os
print('Environment check:')
env_vars = ['MONGODB_URI', 'PROJECT_NAME', 'DATABASE_NAME', 'ENVIRONMENT']
for var in env_vars:
    value = os.getenv(var, 'NOT SET')
    if 'MONGODB' in var and len(value) > 20:
        value = value[:20] + '...' + value[-10:]
    print(f'{var}: {value}')
"
    fi
done

# Get server IP
SERVER_IP=$(curl -s ifconfig.me 2>/dev/null || curl -s ipinfo.io/ip 2>/dev/null || echo "YOUR_SERVER_IP")

echo ""
print_success "🎉 Environment fix applied!"
echo ""
echo "📡 Test your server:"
echo "curl http://${SERVER_IP}:8000/health"
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
