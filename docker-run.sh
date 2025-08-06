#!/bin/bash

# =============================================================================
# MCP Memory Server - One-Command Docker Setup & Run
# =============================================================================

set -e  # Exit on any error

echo "🐳 MCP Memory Server - Docker One-Command Setup"
echo "==============================================="

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

# Check Docker installation
if ! command -v docker &> /dev/null; then
    print_error "Docker is not installed!"
    echo "Please install Docker: https://docs.docker.com/get-docker/"
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    print_error "Docker Compose is not installed!"
    echo "Please install Docker Compose: https://docs.docker.com/compose/install/"
    exit 1
fi

print_status "Docker and Docker Compose found"

# Generate requirements.txt from .myenv
if [ -d ".myenv" ]; then
    print_info "Generating requirements.txt from .myenv virtual environment..."
    python3 generate_requirements.py

    if [ $? -eq 0 ]; then
        print_status "requirements.txt generated from .myenv"
    else
        print_error "Failed to generate requirements.txt from .myenv"
        exit 1
    fi
else
    print_warning ".myenv virtual environment not found"
    print_info "Using existing requirements.txt"
fi

# Check if .env exists, create if not
if [ ! -f ".env" ]; then
    print_warning ".env file not found, creating template..."
    cat > .env << 'EOF'
# =============================================================================
# MCP Memory Server - Docker Environment Configuration
# =============================================================================

# Project & Database Settings
PROJECT_NAME=cursor_project
DATABASE_NAME=mcp_memory_production

# MongoDB Configuration (Update with your credentials)
MONGODB_URI=mongodb+srv://rjawaissaleem:tpQMJUV4cmknQqn3@cluster0.4ixuae0.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0
MONGODB_DATABASE=mcp_memory_production
MONGODB_COLLECTION=memories

# Environment
ENVIRONMENT=production

# Embedding Model
EMBEDDING_MODEL=all-MiniLM-L6-v2
EOF
    print_status ".env file created with default MongoDB credentials"
else
    print_status ".env file found"
fi

# Create logs directory
mkdir -p logs
print_status "Created logs directory"

# Stop any existing containers
print_info "Stopping any existing containers..."
docker-compose down 2>/dev/null || true

# Build the Docker image
print_info "Building Docker image (this may take a few minutes)..."
docker-compose build --no-cache

if [ $? -eq 0 ]; then
    print_status "Docker image built successfully"
else
    print_error "Failed to build Docker image"
    exit 1
fi

# Start the container
print_info "Starting MCP Memory Server container..."
docker-compose up -d

if [ $? -eq 0 ]; then
    print_status "Container started successfully"
else
    print_error "Failed to start container"
    exit 1
fi

# Wait for container to be ready
print_info "Waiting for container to be ready..."
sleep 5

# Check container status
if docker-compose ps | grep -q "Up"; then
    print_status "Container is running"
else
    print_error "Container failed to start"
    echo "Checking logs..."
    docker-compose logs
    exit 1
fi

# Run a quick test
print_info "Running quick functionality test..."
docker-compose exec -T mcp-memory-server python -c "
import sys
print('🐳 Docker Container Test')
print('=' * 30)

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

print('🎉 Container test completed!')
" 2>/dev/null

echo ""
print_status "🎉 MCP Memory Server is running in Docker!"
echo ""
echo "📋 Container Information:"
echo "• Container Name: mcp-memory-server"
echo "• Status: $(docker-compose ps --services --filter status=running)"
echo "• Logs: docker-compose logs -f"
echo ""
echo "🔧 Management Commands:"
echo "• View logs: docker-compose logs -f"
echo "• Stop server: docker-compose down"
echo "• Restart: docker-compose restart"
echo "• Shell access: docker-compose exec mcp-memory-server bash"
echo ""
echo "🧪 Test Commands:"
echo "• Run tests: docker-compose exec mcp-memory-server python comprehensive_test.py"
echo "• Check status: docker-compose ps"
echo ""
echo "📁 Cursor IDE Configuration:"
echo "Update your mcp.json with:"
echo '{
  "mcpServers": {
    "memory-server": {
      "command": "docker-compose",
      "args": ["exec", "-T", "mcp-memory-server", "python", "mcp_memory_server.py"],
      "cwd": "'$(pwd)'"
    }
  }
}'
echo ""
print_status "🚀 Your MCP Memory Server is ready!"
