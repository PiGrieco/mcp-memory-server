#!/bin/bash

# Start MCP Memory Proxy Server
# Usage: ./scripts/servers/start_proxy.sh [host] [port]

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Default configuration
DEFAULT_HOST="0.0.0.0"
DEFAULT_PORT="8080"
DEFAULT_CONFIG="config/proxy_config.yaml"

# Script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$(dirname "$SCRIPT_DIR")")"

# Parse arguments
HOST="${1:-$DEFAULT_HOST}"
PORT="${2:-$DEFAULT_PORT}"
CONFIG="${3:-$DEFAULT_CONFIG}"

echo -e "${BLUE}🚀 Starting MCP Memory Proxy Server${NC}"
echo -e "${BLUE}======================================${NC}"

# Check if project root exists
if [ ! -d "$PROJECT_ROOT" ]; then
    echo -e "${RED}❌ Project root not found: $PROJECT_ROOT${NC}"
    exit 1
fi

# Change to project root
cd "$PROJECT_ROOT"

# Check configuration file
if [ ! -f "$CONFIG" ]; then
    echo -e "${YELLOW}⚠️ Configuration file not found: $CONFIG${NC}"
    echo -e "${YELLOW}Creating default configuration...${NC}"
    
    # Create config directory if it doesn't exist
    mkdir -p "$(dirname "$CONFIG")"
    
    # You could copy from a template here if needed
    echo -e "${GREEN}✅ Please ensure $CONFIG exists with proper configuration${NC}"
fi

# Check if MongoDB is running
echo -e "${BLUE}🗄️ Checking MongoDB connection...${NC}"
if ! python3 -c "
import pymongo
try:
    client = pymongo.MongoClient('mongodb://localhost:27017', serverSelectionTimeoutMS=2000)
    client.admin.command('ping')
    print('✅ MongoDB is running')
except Exception as e:
    print(f'❌ MongoDB not available: {e}')
    exit(1)
" 2>/dev/null; then
    echo -e "${RED}❌ MongoDB is not running. Please start MongoDB first.${NC}"
    echo -e "${YELLOW}💡 Try: brew services start mongodb-community${NC}"
    exit 1
fi

# Check dependencies
echo -e "${BLUE}📦 Checking dependencies...${NC}"
if ! python3 -c "import fastapi, aiohttp, yaml" 2>/dev/null; then
    echo -e "${RED}❌ Missing dependencies. Installing...${NC}"
    pip3 install fastapi aiohttp pyyaml uvicorn
fi

# Create logs directory
mkdir -p logs

# Set environment variables
export PYTHONPATH="$PROJECT_ROOT:$PYTHONPATH"
export MCP_ENVIRONMENT="${MCP_ENVIRONMENT:-development}"

echo -e "${GREEN}📊 Configuration:${NC}"
echo -e "  Host: $HOST"
echo -e "  Port: $PORT"
echo -e "  Config: $CONFIG"
echo -e "  Environment: $MCP_ENVIRONMENT"
echo -e "  Project Root: $PROJECT_ROOT"

echo -e "${BLUE}🌐 Starting proxy server...${NC}"

# Start the proxy server
python3 servers/proxy_server.py \
    --host "$HOST" \
    --port "$PORT" \
    --config "$CONFIG"
