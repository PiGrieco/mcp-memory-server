#!/bin/bash

# =============================================================================
# MCP Memory Server - Complete Docker Setup Script
# =============================================================================

set -e  # Exit on any error

echo "🐳 MCP Memory Server - Docker Setup"
echo "===================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    print_error "Docker is not installed. Please install Docker first."
    echo "Visit: https://docs.docker.com/get-docker/"
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    print_error "Docker Compose is not installed. Please install Docker Compose first."
    echo "Visit: https://docs.docker.com/compose/install/"
    exit 1
fi

print_status "Docker and Docker Compose are installed"

# Check if virtual environment exists and is activated
if [ -d ".myenv" ]; then
    print_info "Virtual environment found"
    
    # Check if we're in virtual environment
    if [[ "$VIRTUAL_ENV" != "" ]]; then
        print_status "Virtual environment is activated"
        
        # Generate requirements.txt from current environment
        print_info "Generating requirements.txt from virtual environment..."
        python generate_requirements.py
        
        if [ $? -eq 0 ]; then
            print_status "Requirements.txt generated successfully"
        else
            print_error "Failed to generate requirements.txt"
            exit 1
        fi
    else
        print_warning "Virtual environment not activated"
        print_info "Activating virtual environment..."
        source .myenv/bin/activate
        
        print_info "Generating requirements.txt..."
        python generate_requirements.py
    fi
else
    print_warning "Virtual environment not found"
    print_info "Using existing requirements.txt"
fi

# Check if .env file exists
if [ ! -f ".env" ]; then
    print_warning ".env file not found"
    print_info "Creating .env template..."
    
    cat > .env << EOF
# =============================================================================
# MCP Memory Server - Docker Environment Configuration
# =============================================================================

# Project & Database Settings
PROJECT_NAME=cursor_project
DATABASE_NAME=mcp_memory_production

# MongoDB Configuration (Update with your credentials)
MONGODB_URI=mongodb+srv://username:password@cluster.mongodb.net/?retryWrites=true&w=majority
MONGODB_DATABASE=mcp_memory_production
MONGODB_COLLECTION=memories

# Environment
ENVIRONMENT=production

# Embedding Model
EMBEDDING_MODEL=all-MiniLM-L6-v2

# =============================================================================
# IMPORTANT: Update MONGODB_URI with your actual MongoDB credentials!
# =============================================================================
EOF
    
    print_warning "Please update .env file with your MongoDB credentials before running Docker"
else
    print_status ".env file found"
fi

# Create logs directory
mkdir -p logs
print_status "Created logs directory"

# Build Docker image
print_info "Building Docker image..."
docker-compose build

if [ $? -eq 0 ]; then
    print_status "Docker image built successfully"
else
    print_error "Failed to build Docker image"
    exit 1
fi

# Test the build
print_info "Testing Docker container..."
docker-compose run --rm mcp-memory-server python -c "
import sys
print(f'Python version: {sys.version}')

try:
    import motor
    print('✅ Motor (MongoDB) imported successfully')
except ImportError as e:
    print(f'❌ Motor import failed: {e}')

try:
    import sentence_transformers
    print('✅ Sentence Transformers imported successfully')
except ImportError as e:
    print(f'❌ Sentence Transformers import failed: {e}')

try:
    from src.services.database_service import DatabaseService
    print('✅ Database Service imported successfully')
except ImportError as e:
    print(f'❌ Database Service import failed: {e}')

print('🐳 Docker container test completed!')
"

if [ $? -eq 0 ]; then
    print_status "Docker container test passed"
else
    print_error "Docker container test failed"
    exit 1
fi

echo ""
print_status "Docker setup completed successfully!"
echo ""
echo "📋 Next steps:"
echo "1. Update .env file with your MongoDB credentials"
echo "2. Start the server: docker-compose up -d"
echo "3. View logs: docker-compose logs -f"
echo "4. Stop the server: docker-compose down"
echo ""
echo "🧪 Test commands:"
echo "• Run tests: docker-compose run --rm mcp-memory-server python comprehensive_test.py"
echo "• Check status: docker-compose ps"
echo "• Shell access: docker-compose exec mcp-memory-server bash"
echo ""
print_status "🚀 Your MCP Memory Server is ready for Docker deployment!"
