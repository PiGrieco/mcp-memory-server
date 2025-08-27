#!/bin/bash

# MCP Memory Server - Main Script Manager
# This script provides access to all available scripts in an organized way

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

show_help() {
    echo -e "${BLUE}🚀 MCP Memory Server - Script Manager${NC}"
    echo -e "${BLUE}====================================${NC}"
    echo ""
    echo -e "${GREEN}Usage:${NC}"
    echo -e "  $0 [CATEGORY] [COMMAND]"
    echo ""
    echo -e "${GREEN}Categories:${NC}"
    echo -e "  ${YELLOW}server${NC}     - Server management (start, stop, status)"
    echo -e "  ${YELLOW}install${NC}    - Installation and setup"
    echo -e "  ${YELLOW}platform${NC}   - Platform-specific configurations"
    echo -e "  ${YELLOW}utils${NC}      - Utility scripts"
    echo -e "  ${YELLOW}help${NC}       - Show this help message"
    echo ""
    echo -e "${GREEN}Examples:${NC}"
    echo -e "  $0 server http     # Start HTTP server"
    echo -e "  $0 server mcp      # Start MCP server"
    echo -e "  $0 install all     # Install everything"
    echo -e "  $0 platform cursor # Configure Cursor"
    echo -e "  $0 utils env       # Manage environments"
    echo ""
    echo -e "${PURPLE}💡 Use '$0 [CATEGORY] help' to see specific commands${NC}"
}

show_server_help() {
    echo -e "${BLUE}🌐 Server Management${NC}"
    echo -e "${BLUE}==================${NC}"
    echo ""
    echo -e "${GREEN}Commands:${NC}"
    echo -e "  ${YELLOW}http${NC}     - Start HTTP server (development)"
    echo -e "  ${YELLOW}mcp${NC}      - Start MCP server (integration)"
    echo -e "  ${YELLOW}proxy${NC}    - Start HTTP Proxy server (auto-intercept)"
    echo -e "  ${YELLOW}both${NC}     - Start MCP + Proxy servers (full features)"
    echo -e "  ${YELLOW}test${NC}     - Run service tests"
    echo -e "  ${YELLOW}help${NC}     - Show this help"
    echo ""
    echo -e "${GREEN}Examples:${NC}"
    echo -e "  $0 server http    # Start HTTP server at http://localhost:8000"
    echo -e "  $0 server mcp     # Start MCP server for platform integration"
    echo -e "  $0 server proxy   # Start HTTP Proxy at http://localhost:8080"
    echo -e "  $0 server both    # Start both MCP + Proxy (recommended)"
    echo -e "  $0 server test    # Run all service tests"
}

show_install_help() {
    echo -e "${BLUE}📦 Installation & Setup${NC}"
    echo -e "${BLUE}=====================${NC}"
    echo ""
    echo -e "${GREEN}Commands:${NC}"
    echo -e "  ${YELLOW}all${NC}      - Install everything (recommended)"
    echo -e "  ${YELLOW}core${NC}     - Install core dependencies only"
    echo -e "  ${YELLOW}ml${NC}       - Install ML dependencies"
    echo -e "  ${YELLOW}dev${NC}      - Install development dependencies"
    echo -e "  ${YELLOW}help${NC}     - Show this help"
    echo ""
    echo -e "${GREEN}Examples:${NC}"
    echo -e "  $0 install all    # Complete installation"
    echo -e "  $0 install core   # Core dependencies only"
    echo -e "  $0 install ml     # ML dependencies only"
}

show_platform_help() {
    echo -e "${BLUE}🔌 Platform Configuration${NC}"
    echo -e "${BLUE}========================${NC}"
    echo ""
    echo -e "${GREEN}Commands:${NC}"
    echo -e "  ${YELLOW}cursor${NC}   - Configure Cursor IDE"
    echo -e "  ${YELLOW}claude${NC}   - Configure Claude Desktop"
    echo -e "  ${YELLOW}lovable${NC}  - Configure Lovable"
    echo -e "  ${YELLOW}replit${NC}   - Configure Replit"
    echo -e "  ${YELLOW}windsurf${NC} - Configure Windsurf"
    echo -e "  ${YELLOW}help${NC}     - Show this help"
    echo ""
    echo -e "${GREEN}Examples:${NC}"
    echo -e "  $0 platform cursor   # Configure Cursor IDE"
    echo -e "  $0 platform claude   # Configure Claude Desktop"
}

show_utils_help() {
    echo -e "${BLUE}🔧 Utility Scripts${NC}"
    echo -e "${BLUE}=================${NC}"
    echo ""
    echo -e "${GREEN}Commands:${NC}"
    echo -e "  ${YELLOW}env${NC}      - Manage environment configurations"
    echo -e "  ${YELLOW}help${NC}     - Show this help"
    echo ""
    echo -e "${GREEN}Examples:${NC}"
    echo -e "  $0 utils env list    # List available environments"
    echo -e "  $0 utils env switch development  # Switch to development"
}

# Server management
handle_server() {
    case "${2:-help}" in
        "http")
            "$SCRIPT_DIR/servers/start_http_server.sh"
            ;;
        "mcp")
            "$SCRIPT_DIR/servers/start_mcp_server.sh"
            ;;
        "proxy")
            "$SCRIPT_DIR/servers/start_proxy.sh"
            ;;
        "both")
            "$SCRIPT_DIR/servers/start_universal.sh"
            ;;
        "test")
            "$SCRIPT_DIR/servers/start_server.sh" test
            ;;
        "help"|"-h"|"--help")
            show_server_help
            ;;
        *)
            echo -e "${RED}❌ Unknown server command: $2${NC}"
            show_server_help
            exit 1
            ;;
    esac
}

# Installation management
handle_install() {
    case "${2:-help}" in
        "all")
            "$SCRIPT_DIR/install/install.sh"
            ;;
        "core")
            "$SCRIPT_DIR/install/install.sh" core
            ;;
        "ml")
            "$SCRIPT_DIR/install/install.sh" ml
            ;;
        "dev")
            "$SCRIPT_DIR/install/install.sh" dev
            ;;
        "help"|"-h"|"--help")
            show_install_help
            ;;
        *)
            echo -e "${RED}❌ Unknown install command: $2${NC}"
            show_install_help
            exit 1
            ;;
    esac
}

# Platform management
handle_platform() {
    case "${2:-help}" in
        "cursor")
            "$SCRIPT_DIR/install/install_cursor.sh"
            ;;
        "claude")
            "$SCRIPT_DIR/install/install_claude.sh"
            ;;
        "lovable")
            "$SCRIPT_DIR/install/install_lovable.sh"
            ;;
        "replit")
            "$SCRIPT_DIR/install/install_replit.sh"
            ;;
        "windsurf")
            "$SCRIPT_DIR/install/install_windsurf.sh"
            ;;
        "help"|"-h"|"--help")
            show_platform_help
            ;;
        *)
            echo -e "${RED}❌ Unknown platform command: $2${NC}"
            show_platform_help
            exit 1
            ;;
    esac
}

# Utils management
handle_utils() {
    case "${2:-help}" in
        "env")
            shift 2
            "$SCRIPT_DIR/utils/manage_environments.sh" "$@"
            ;;
        "help"|"-h"|"--help")
            show_utils_help
            ;;
        *)
            echo -e "${RED}❌ Unknown utils command: $2${NC}"
            show_utils_help
            exit 1
            ;;
    esac
}

# Main script logic
case "${1:-help}" in
    "server")
        handle_server "$@"
        ;;
    "install")
        handle_install "$@"
        ;;
    "platform")
        handle_platform "$@"
        ;;
    "utils")
        handle_utils "$@"
        ;;
    "help"|"-h"|"--help")
        show_help
        ;;
    *)
        echo -e "${RED}❌ Unknown category: $1${NC}"
        echo ""
        show_help
        exit 1
        ;;
esac 