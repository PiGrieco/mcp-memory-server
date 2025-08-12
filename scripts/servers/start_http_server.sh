#!/bin/bash

# MCP Memory Server - HTTP Server Startup Script
# This script starts the HTTP server for testing and development

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$(dirname "$SCRIPT_DIR")")"

echo -e "${BLUE}🚀 MCP Memory Server - HTTP Server${NC}"
echo -e "${BLUE}================================${NC}"

# Check if virtual environment exists
if [ ! -d "$PROJECT_ROOT/venv" ]; then
    echo -e "${RED}❌ Virtual environment not found!${NC}"
    echo -e "${YELLOW}💡 Please run: ./scripts/install.sh${NC}"
    exit 1
fi

# Activate virtual environment
echo -e "${BLUE}🔧 Activating virtual environment...${NC}"
source "$PROJECT_ROOT/venv/bin/activate"

# Check if required services are running
echo -e "${BLUE}🔍 Checking required services...${NC}"

# Check MongoDB
if ! brew services list | grep -q "mongodb.*started"; then
    echo -e "${YELLOW}⚠️  MongoDB not running. Starting...${NC}"
    brew services start mongodb
    sleep 2
fi

# Check Redis (optional)
if ! brew services list | grep -q "redis.*started"; then
    echo -e "${YELLOW}⚠️  Redis not running. Starting...${NC}"
    brew services start redis
    sleep 1
fi

# Check if test_http_server.py exists
if [ ! -f "$PROJECT_ROOT/servers/http_server.py" ]; then
    echo -e "${RED}❌ HTTP server file not found!${NC}"
    echo -e "${YELLOW}💡 Please ensure http_server.py exists in servers/ directory${NC}"
    exit 1
fi

# Check dependencies
echo -e "${BLUE}📦 Checking dependencies...${NC}"
if ! python -c "import fastapi, uvicorn" 2>/dev/null; then
    echo -e "${YELLOW}⚠️  Installing missing dependencies...${NC}"
    pip install fastapi uvicorn
fi

# Start the HTTP server
echo -e "${GREEN}✅ Starting HTTP server...${NC}"
echo -e "${BLUE}🌐 Server will be available at: http://localhost:8000${NC}"
echo -e "${BLUE}📖 API Documentation: http://localhost:8000/docs${NC}"
echo -e "${YELLOW}💡 Press Ctrl+C to stop the server${NC}"
echo ""

cd "$PROJECT_ROOT"
python servers/http_server.py 