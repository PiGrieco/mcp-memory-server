#!/bin/bash
cd "$(dirname "$0")"
source venv/bin/activate
echo "�� Starting CURSOR MCP Memory Server..."
python cursor_mcp_server.py
