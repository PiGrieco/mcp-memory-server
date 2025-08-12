#!/bin/bash
# Cursor MCP Memory Server Startup Script

cd "/Users/m1pro/Documents/GitHub/mcp-memory-server"
echo "🚀 Starting Cursor MCP Memory Server with ML Auto-Triggers..."
echo "📍 Server path: /Users/m1pro/Documents/GitHub/mcp-memory-server/servers/legacy/cursor_mcp_server.py"
echo "⚡ ML model will auto-load on first message"
echo ""

python3.11 "/Users/m1pro/Documents/GitHub/mcp-memory-server/servers/legacy/cursor_mcp_server.py"
