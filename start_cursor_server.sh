#!/bin/bash
# Cursor MCP Memory Server Startup Script

cd "/Users/piermatteogrieco/mcp-memory-server-production"
echo "🚀 Starting Cursor MCP Memory Server with ML Auto-Triggers..."
echo "📍 Server path: /Users/piermatteogrieco/mcp-memory-server-production/cursor_mcp_server.py"
echo "⚡ ML model will auto-load on first message"
echo ""

python3 "/Users/piermatteogrieco/mcp-memory-server-production/cursor_mcp_server.py"
