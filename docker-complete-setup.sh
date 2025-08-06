#!/bin/bash

# =============================================================================
# MCP Memory Server - Complete Docker Setup Script
# Run this in bash where Docker is available
# =============================================================================

set -e  # Exit on any error

echo "🐳 MCP Memory Server - Complete Docker Setup"
echo "============================================="

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

print_status() { echo -e "${GREEN}✅ $1${NC}"; }
print_warning() { echo -e "${YELLOW}⚠️  $1${NC}"; }
print_error() { echo -e "${RED}❌ $1${NC}"; }
print_info() { echo -e "${BLUE}ℹ️  $1${NC}"; }

# Step 1: Check Docker
print_info "Checking Docker installation..."
if ! docker --version; then
    print_error "Docker not found in current environment"
    exit 1
fi

# Check for Docker Compose (try both old and new syntax)
if docker-compose --version 2>/dev/null; then
    DOCKER_COMPOSE="docker-compose"
    print_status "Docker Compose (classic) found"
elif docker compose version 2>/dev/null; then
    DOCKER_COMPOSE="docker compose"
    print_status "Docker Compose (plugin) found"
else
    print_error "Docker Compose not found in current environment"
    print_info "Please install Docker Compose or use Docker Desktop"
    exit 1
fi

# Step 2: Generate requirements.txt from .myenv
print_info "Generating requirements.txt from .myenv..."
if [ -d ".myenv" ]; then
    .myenv/bin/python -m pip freeze > requirements_temp.txt
    
    # Create formatted requirements.txt
    cat > requirements.txt << 'EOF'
# =============================================================================
# MCP Memory Server - Docker Requirements (Generated from .myenv)
# =============================================================================

EOF
    
    # Add packages, filtering out unnecessary ones
    grep -v "^-e " requirements_temp.txt | \
    grep -v "^pkg-resources" | \
    sort >> requirements.txt
    
    rm requirements_temp.txt
    print_status "Generated requirements.txt with $(grep -v "^#" requirements.txt | grep -v "^$" | wc -l) packages"
else
    print_warning ".myenv not found, using existing requirements.txt"
fi

# Step 3: Create .env if not exists
if [ ! -f ".env" ]; then
    print_info "Creating .env file..."
    cat > .env << 'EOF'
# =============================================================================
# MCP Memory Server - Docker Environment Configuration
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
EOF
    print_status "Created .env file"
else
    print_status ".env file already exists"
fi

# Step 4: Create logs directory
mkdir -p logs
print_status "Created logs directory"

# Step 5: Stop any existing containers
print_info "Stopping any existing containers..."
$DOCKER_COMPOSE down 2>/dev/null || true

# Step 6: Build Docker image
print_info "Building Docker image (this may take several minutes)..."
$DOCKER_COMPOSE build --no-cache

if [ $? -eq 0 ]; then
    print_status "Docker image built successfully"
else
    print_error "Failed to build Docker image"
    exit 1
fi

# Step 7: Start the container
print_info "Starting MCP Memory Server container..."
$DOCKER_COMPOSE up -d

if [ $? -eq 0 ]; then
    print_status "Container started successfully"
else
    print_error "Failed to start container"
    $DOCKER_COMPOSE logs
    exit 1
fi

# Step 8: Wait for container to be ready
print_info "Waiting for container to initialize..."
sleep 10

# Step 9: Check container status
print_info "Checking container status..."
$DOCKER_COMPOSE ps

# Step 10: Run functionality test
print_info "Running functionality test..."
$DOCKER_COMPOSE exec -T mcp-memory-server python -c "
print('🐳 Docker Container Functionality Test')
print('=' * 40)

try:
    import motor
    print('✅ MongoDB driver (motor) loaded')
except Exception as e:
    print(f'❌ Motor error: {e}')

try:
    import sentence_transformers
    print('✅ Sentence Transformers loaded')
except Exception as e:
    print(f'❌ Sentence Transformers error: {e}')

try:
    from src.services.database_service import DatabaseService
    print('✅ Database Service loaded')
except Exception as e:
    print(f'❌ Database Service error: {e}')

try:
    import os
    print(f'✅ Environment: {os.getenv(\"ENVIRONMENT\", \"not set\")}')
    print(f'✅ Project: {os.getenv(\"PROJECT_NAME\", \"not set\")}')
    print(f'✅ Database: {os.getenv(\"DATABASE_NAME\", \"not set\")}')
except Exception as e:
    print(f'❌ Environment error: {e}')

print('🎉 Container test completed!')
"

echo ""
print_status "🎉 MCP Memory Server Docker setup completed!"
echo ""
echo "📋 Container Information:"
$DOCKER_COMPOSE ps
echo ""
echo "🔧 Management Commands:"
echo "• View logs: $DOCKER_COMPOSE logs -f"
echo "• Stop server: $DOCKER_COMPOSE down"
echo "• Restart: $DOCKER_COMPOSE restart"
echo "• Shell access: $DOCKER_COMPOSE exec mcp-memory-server bash"
echo ""
echo "🧪 Test Commands:"
echo "• Run comprehensive test: $DOCKER_COMPOSE exec mcp-memory-server python comprehensive_test.py"
echo "• Check memory status: $DOCKER_COMPOSE exec mcp-memory-server python -c \"import asyncio; from src.services.database_service import database_service; print(asyncio.run(database_service.get_memory_count()))\""
echo ""
echo "📁 Cursor IDE Configuration:"
echo "Update your mcp.json with:"
echo "{"
echo "  \"mcpServers\": {"
echo "    \"memory-server\": {"
echo "      \"command\": \"$DOCKER_COMPOSE\","
echo "      \"args\": [\"exec\", \"-T\", \"mcp-memory-server\", \"python\", \"mcp_memory_server.py\"],"
echo "      \"cwd\": \"$(pwd)\""
echo "    }"
echo "  }"
echo "}"
echo ""
print_status "🚀 Your MCP Memory Server is running in Docker!"
echo ""
echo "📊 Next steps:"
echo "1. Test the server with: $DOCKER_COMPOSE exec mcp-memory-server python comprehensive_test.py"
echo "2. Configure Cursor IDE with the mcp.json above"
echo "3. Start using memory features in Cursor!"
