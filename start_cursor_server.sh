#!/bin/bash
# Cursor MCP Memory Server Startup Script

cd "/Users/pigrieco/mcp-memory-server"
echo "🚀 Starting Cursor MCP Memory Server with ML Auto-Triggers..."
echo "📍 Server path: /Users/pigrieco/mcp-memory-server/cursor_mcp_server.py"
echo "⚡ ML model will auto-load on first message"
echo ""

python3 "/Users/pigrieco/mcp-memory-server/cursor_mcp_server.py"
