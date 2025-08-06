#!/bin/bash

# =============================================================================
# Debug Remote MCP Memory Server
# =============================================================================

echo "🔍 Debugging MCP Memory Server Deployment"
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

print_info "Step 1: Check container status"
$DOCKER_COMPOSE ps

echo ""
print_info "Step 2: Check container logs"
$DOCKER_COMPOSE logs mcp-memory-server-http

echo ""
print_info "Step 3: Check if port 8000 is listening"
netstat -tlnp | grep :8000 || ss -tlnp | grep :8000

echo ""
print_info "Step 4: Check firewall status"
if command -v ufw >/dev/null 2>&1; then
    echo "UFW Status:"
    ufw status
elif command -v firewall-cmd >/dev/null 2>&1; then
    echo "Firewalld Status:"
    firewall-cmd --list-ports
else
    echo "No common firewall tool found"
fi

echo ""
print_info "Step 5: Test local connectivity"
if curl -s -f "http://localhost:8000/health" > /dev/null; then
    print_success "Local health check passed"
    curl -s "http://localhost:8000/health"
else
    print_error "Local health check failed"
fi

echo ""
print_info "Step 6: Check Docker network"
docker network ls
docker network inspect mcp-memory-server_mcp-network 2>/dev/null || echo "Network not found"

echo ""
print_info "Step 7: Check container internal connectivity"
if $DOCKER_COMPOSE exec -T mcp-memory-server-http curl -s -f "http://localhost:8000/health" > /dev/null; then
    print_success "Container internal connectivity OK"
else
    print_error "Container internal connectivity failed"
fi

echo ""
print_info "Step 8: Manual container inspection"
$DOCKER_COMPOSE exec -T mcp-memory-server-http python -c "
import os
print('Environment variables:')
for key in ['HOST', 'PORT', 'PROJECT_NAME', 'DATABASE_NAME']:
    print(f'{key}: {os.getenv(key, \"NOT SET\")}')

print('\nTesting imports:')
try:
    import aiohttp
    print('✅ aiohttp imported')
except Exception as e:
    print(f'❌ aiohttp error: {e}')

try:
    from src.services.database_service import DatabaseService
    print('✅ Database service imported')
except Exception as e:
    print(f'❌ Database service error: {e}')
"

echo ""
print_info "Debugging completed!"
echo ""
echo "🔧 Common fixes:"
echo "1. Open firewall: sudo ufw allow 8000"
echo "2. Restart container: $DOCKER_COMPOSE restart mcp-memory-server-http"
echo "3. Check logs: $DOCKER_COMPOSE logs -f mcp-memory-server-http"
echo "4. Rebuild: $DOCKER_COMPOSE down && $DOCKER_COMPOSE build --no-cache && $DOCKER_COMPOSE up -d mcp-memory-server-http"
