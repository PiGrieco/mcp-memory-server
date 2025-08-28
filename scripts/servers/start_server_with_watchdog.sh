#!/bin/bash

# MCP Memory Server with Watchdog Service
# Starts server with auto-restart capability when deterministic keywords are detected

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

echo -e "${CYAN}🐕 MCP Memory Server with Watchdog${NC}"
echo -e "${CYAN}===================================${NC}"

# Change to project root
cd "$PROJECT_ROOT"

# Create logs directory
mkdir -p logs

# Set environment variables
export PYTHONPATH="$PROJECT_ROOT:$PYTHONPATH"
export MCP_ENVIRONMENT="${MCP_ENVIRONMENT:-development}"

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

# Function to cleanup on exit
cleanup() {
    echo -e "\n${YELLOW}🛑 Shutting down watchdog service...${NC}"
    
    if [ ! -z "$WATCHDOG_PID" ]; then
        echo "Stopping Watchdog Service (PID: $WATCHDOG_PID)"
        kill $WATCHDOG_PID 2>/dev/null || true
    fi
    
    echo -e "${GREEN}✅ Watchdog service stopped${NC}"
    exit 0
}

# Set up signal handlers
trap cleanup SIGINT SIGTERM

echo -e "${GREEN}📊 Configuration:${NC}"
echo -e "  Environment: $MCP_ENVIRONMENT"
echo -e "  Project Root: $PROJECT_ROOT"
echo -e "  Watchdog Logs: logs/watchdog.log"
echo ""

echo -e "${CYAN}🎯 Deterministic Keywords for Restart:${NC}"
echo -e "  Italian: ricorda, importante, nota, salva, memorizza, riavvia"
echo -e "  English: remember, save, note, important, store, restart"
echo -e "  Commands: mcp start, server start, wake up"
echo ""

echo -e "${YELLOW}💡 Usage:${NC}"
echo -e "  • Type any deterministic keyword to restart the server"
echo -e "  • Server will auto-restart when it detects keywords"
echo -e "  • Press Ctrl+C to stop the watchdog service"
echo ""

# Start watchdog service
echo -e "${BLUE}🐕 Starting Watchdog Service...${NC}"
python3 -m src.services.watchdog_service \
    --restart-script main.py \
    --monitor-file logs/restart_triggers.txt &

WATCHDOG_PID=$!
echo "Watchdog Service PID: $WATCHDOG_PID"

# Give watchdog time to initialize
sleep 2

echo -e "\n${GREEN}✅ Watchdog Service is running!${NC}"
echo -e "${GREEN}================================${NC}"
echo -e "🐕 Watchdog: Monitoring for restart keywords"
echo -e "🧠 Server: Will auto-start/restart on keywords"
echo -e "📝 Logs: logs/watchdog.log"
echo -e "📁 Trigger File: logs/restart_triggers.txt"
echo ""
echo -e "${CYAN}🎯 Try typing these commands:${NC}"
echo -e "  • ${YELLOW}ricorda questo${NC} - Italian restart trigger"
echo -e "  • ${YELLOW}remember this${NC} - English restart trigger"
echo -e "  • ${YELLOW}restart server${NC} - Direct restart command"
echo -e "  • ${YELLOW}emergency restart${NC} - Urgent restart (faster)"
echo ""

# Wait for watchdog to complete
wait $WATCHDOG_PID
