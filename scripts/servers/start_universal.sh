#!/bin/bash

# Start MCP Memory Server + HTTP Proxy (Full Features Mode)
# Runs both servers simultaneously for complete auto-trigger experience

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$(dirname "$SCRIPT_DIR")")"

echo -e "${CYAN}🚀 MCP Memory Server + HTTP Proxy (Universal Mode)${NC}"
echo -e "${CYAN}====================================================${NC}"

# Change to project root
cd "$PROJECT_ROOT"

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
missing_deps=""

if ! python3 -c "import fastapi" 2>/dev/null; then
    missing_deps="$missing_deps fastapi"
fi

if ! python3 -c "import aiohttp" 2>/dev/null; then
    missing_deps="$missing_deps aiohttp"
fi

if ! python3 -c "import yaml" 2>/dev/null; then
    missing_deps="$missing_deps pyyaml"
fi

if ! python3 -c "import uvicorn" 2>/dev/null; then
    missing_deps="$missing_deps uvicorn"
fi

if [ -n "$missing_deps" ]; then
    echo -e "${YELLOW}⚠️ Installing missing dependencies: $missing_deps${NC}"
    pip3 install $missing_deps
fi

# Create logs directory
mkdir -p logs

# Set environment variables
export PYTHONPATH="$PROJECT_ROOT:$PYTHONPATH"
export MCP_ENVIRONMENT="${MCP_ENVIRONMENT:-development}"

echo -e "${GREEN}📊 Configuration:${NC}"
echo -e "  Environment: $MCP_ENVIRONMENT"
echo -e "  Project Root: $PROJECT_ROOT"
echo -e "  MCP Server: http://localhost:8000 (stdio)"
echo -e "  HTTP Proxy: http://localhost:8080"

# Function to start MCP server
start_mcp_server() {
    echo -e "${BLUE}🧠 Starting MCP Memory Server (stdio)...${NC}"
    python3 main.py &
    MCP_PID=$!
    echo "MCP Server PID: $MCP_PID"
}

# Function to start Proxy server
start_proxy_server() {
    echo -e "${BLUE}🌐 Starting HTTP Proxy Server...${NC}"
    python3 servers/proxy_server.py --host 0.0.0.0 --port 8080 &
    PROXY_PID=$!
    echo "Proxy Server PID: $PROXY_PID"
}

# Function to cleanup on exit
cleanup() {
    echo -e "\n${YELLOW}🛑 Shutting down servers...${NC}"
    
    if [ ! -z "$MCP_PID" ]; then
        echo "Stopping MCP Server (PID: $MCP_PID)"
        kill $MCP_PID 2>/dev/null || true
    fi
    
    if [ ! -z "$PROXY_PID" ]; then
        echo "Stopping Proxy Server (PID: $PROXY_PID)"
        kill $PROXY_PID 2>/dev/null || true
    fi
    
    echo -e "${GREEN}✅ Servers stopped${NC}"
    exit 0
}

# Set up signal handlers
trap cleanup SIGINT SIGTERM

echo -e "${CYAN}🚀 Starting both servers...${NC}"

# Start MCP server in background
start_mcp_server

# Give MCP server time to initialize
sleep 2

# Start Proxy server in background
start_proxy_server

# Give proxy server time to initialize
sleep 3

echo -e "\n${GREEN}✅ Both servers are running!${NC}"
echo -e "${GREEN}================================${NC}"
echo -e "🧠 MCP Server: Ready for IDE integration (stdio)"
echo -e "🌐 HTTP Proxy: http://localhost:8080"
echo -e "📊 Health Check: http://localhost:8080/health"
echo -e "📖 API Docs: http://localhost:8080/docs"
echo ""
echo -e "${CYAN}🎯 Usage Patterns:${NC}"
echo -e "  • ${YELLOW}Direct MCP${NC}: Configure your IDE to use main.py"
echo -e "  • ${YELLOW}Proxy Mode${NC}: Point your app to localhost:8080/proxy/[platform]"
echo -e "  • ${YELLOW}Hybrid${NC}: Use both simultaneously for maximum features"
echo ""
echo -e "${BLUE}📝 Example Proxy Usage:${NC}"
echo -e "  curl -X POST http://localhost:8080/proxy/cursor \\"
echo -e "       -H 'Content-Type: application/json' \\"
echo -e "       -d '{\"message\": \"Remember this config: port=5432\"}'"
echo ""
echo -e "${YELLOW}Press Ctrl+C to stop both servers${NC}"

# Wait for both processes
wait