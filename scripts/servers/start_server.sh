#!/bin/bash

# MCP Memory Server - Main Server Startup Script
# This script provides options to start different types of servers

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
NC='\033[0m' # No Color

# Script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$(dirname "$SCRIPT_DIR")")"

show_help() {
    echo -e "${BLUE}🚀 MCP Memory Server - Server Manager${NC}"
    echo -e "${BLUE}====================================${NC}"
    echo ""
    echo -e "${GREEN}Usage:${NC}"
    echo -e "  $0 [OPTION]"
    echo ""
    echo -e "${GREEN}Options:${NC}"
    echo -e "  ${YELLOW}http${NC}     - Start HTTP server only (for testing)"
    echo -e "  ${YELLOW}mcp${NC}      - Start MCP server only (for platform integration)"
    echo -e "  ${YELLOW}test${NC}     - Run service tests"
    echo -e "  ${YELLOW}help${NC}     - Show this help message"
    echo ""
    echo -e "${GREEN}Examples:${NC}"
    echo -e "  $0 http    # Start HTTP server at http://localhost:8000"
    echo -e "  $0 mcp     # Start MCP server for Cursor/Claude integration"
    echo -e "  $0 test    # Run all service tests"
    echo ""
    echo -e "${PURPLE}💡 For development, use 'http' mode${NC}"
    echo -e "${PURPLE}💡 For platform integration, use 'mcp' mode${NC}"
}

start_http_server() {
    echo -e "${GREEN}🌐 Starting HTTP Server...${NC}"
    "$SCRIPT_DIR/start_http_server.sh"
}

start_mcp_server() {
    echo -e "${GREEN}🎯 Starting MCP Server...${NC}"
    "$SCRIPT_DIR/start_mcp_server.sh"
}

run_tests() {
    echo -e "${GREEN}🧪 Running Service Tests...${NC}"
    
    # Activate virtual environment
    source "$PROJECT_ROOT/venv/bin/activate"
    
    # Run the test script
    cd "$PROJECT_ROOT"
    python tests/test_server_simple.py
}

# Main script logic
case "${1:-help}" in
    "http")
        start_http_server
        ;;
    "mcp")
        start_mcp_server
        ;;
    "test")
        run_tests
        ;;
    "help"|"-h"|"--help")
        show_help
        ;;
    *)
        echo -e "${RED}❌ Unknown option: $1${NC}"
        echo ""
        show_help
        exit 1
        ;;
esac 