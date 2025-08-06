#!/bin/bash

# =============================================================================
# MCP Memory Server - Docker Test Script
# =============================================================================

echo "🧪 Testing MCP Memory Server in Docker"
echo "======================================"

# Detect Docker Compose command
if docker-compose --version 2>/dev/null; then
    DOCKER_COMPOSE="docker-compose"
elif docker compose version 2>/dev/null; then
    DOCKER_COMPOSE="docker compose"
else
    echo "❌ Docker Compose not found"
    exit 1
fi

# Check if container is running
if ! $DOCKER_COMPOSE ps | grep -q "Up"; then
    echo "❌ Container is not running. Start it with: $DOCKER_COMPOSE up -d"
    exit 1
fi

echo "✅ Container is running"

# Test 1: Basic Python functionality
echo ""
echo "🔍 Test 1: Basic Python Environment"
$DOCKER_COMPOSE exec -T mcp-memory-server python -c "
import sys
print(f'Python version: {sys.version}')
print(f'Python path: {sys.executable}')
"

# Test 2: Import core dependencies
echo ""
echo "🔍 Test 2: Core Dependencies"
$DOCKER_COMPOSE exec -T mcp-memory-server python -c "
dependencies = [
    ('motor', 'MongoDB async driver'),
    ('pymongo', 'MongoDB driver'),
    ('sentence_transformers', 'Sentence Transformers'),
    ('transformers', 'Hugging Face Transformers'),
    ('torch', 'PyTorch'),
    ('numpy', 'NumPy'),
    ('mcp', 'Model Context Protocol')
]

for package, description in dependencies:
    try:
        __import__(package)
        print(f'✅ {package}: {description}')
    except ImportError as e:
        print(f'❌ {package}: Failed to import - {e}')
"

# Test 3: MCP Memory Server components
echo ""
echo "🔍 Test 3: MCP Memory Server Components"
$DOCKER_COMPOSE exec -T mcp-memory-server python -c "
try:
    from src.services.database_service import DatabaseService
    print('✅ Database Service imported')
except Exception as e:
    print(f'❌ Database Service: {e}')

try:
    from src.services.memory_service import MemoryService
    print('✅ Memory Service imported')
except Exception as e:
    print(f'❌ Memory Service: {e}')

try:
    from src.services.embedding_service import EmbeddingService
    print('✅ Embedding Service imported')
except Exception as e:
    print(f'❌ Embedding Service: {e}')
"

# Test 4: Environment variables
echo ""
echo "🔍 Test 4: Environment Configuration"
$DOCKER_COMPOSE exec -T mcp-memory-server python -c "
import os

env_vars = [
    'PROJECT_NAME',
    'DATABASE_NAME', 
    'MONGODB_URI',
    'MONGODB_DATABASE',
    'ENVIRONMENT',
    'EMBEDDING_MODEL'
]

for var in env_vars:
    value = os.getenv(var, 'NOT SET')
    if value != 'NOT SET':
        # Hide sensitive MongoDB URI
        if 'MONGODB' in var and 'URI' in var:
            value = value[:20] + '...' + value[-20:] if len(value) > 40 else value
        print(f'✅ {var}: {value}')
    else:
        print(f'❌ {var}: NOT SET')
"

# Test 5: Run comprehensive test
echo ""
echo "🔍 Test 5: Comprehensive MCP Server Test"
$DOCKER_COMPOSE exec -T mcp-memory-server python comprehensive_test.py

echo ""
echo "🎉 Docker testing completed!"
echo ""
echo "📋 Container Status:"
$DOCKER_COMPOSE ps
echo ""
echo "📊 Container Resource Usage:"
docker stats --no-stream mcp-memory-server
echo ""
echo "✅ If all tests passed, your MCP Memory Server is ready for production!"
