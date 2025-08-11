#!/bin/bash
cd "$(dirname "$0")"
source venv/bin/activate
echo "🔮 Starting CLAUDE MCP Memory Server..."
python claude_mcp_server.py
