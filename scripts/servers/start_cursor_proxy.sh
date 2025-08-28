#!/bin/bash
# Auto-generated Cursor MCP Memory Proxy startup script

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/../.."
cd "$SCRIPT_DIR"

echo "🌐 Starting MCP Memory Proxy Server for Cursor..."
echo "📊 Monitor: http://127.0.0.1:8080/health"
echo "🔗 Proxy: http://127.0.0.1:8080/proxy/cursor"
echo ""

# Start proxy server
python3 servers/proxy_server.py --host 127.0.0.1 --port 8080 --config config/proxy_config.yaml
