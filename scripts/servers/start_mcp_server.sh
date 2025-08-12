#!/bin/bash

# MCP Memory Server - MCP Server Startup Script
# This script starts the main MCP server for platform integration

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

echo -e "${BLUE}🚀 MCP Memory Server - MCP Server${NC}"
echo -e "${BLUE}===============================${NC}"

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

# Check if main.py exists
if [ ! -f "$PROJECT_ROOT/main.py" ]; then
    echo -e "${RED}❌ Main server file not found!${NC}"
    echo -e "${YELLOW}💡 Please ensure main.py exists in the project root${NC}"
    exit 1
fi

# Start the MCP server
echo -e "${GREEN}✅ Starting MCP server...${NC}"
echo -e "${BLUE}🎯 Server mode: Universal (MCP + HTTP)${NC}"
echo -e "${BLUE}🌐 HTTP endpoint: http://localhost:8000${NC}"
echo -e "${YELLOW}💡 Press Ctrl+C to stop the server${NC}"
echo ""

cd "$PROJECT_ROOT"
python main.py 