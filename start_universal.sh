#!/bin/bash
# Universal MCP Memory Server Startup

cd "$(dirname "$0")"
source venv/bin/activate

echo "🧠 Universal MCP Memory Server Starting..."
echo "🌐 API available at: http://localhost:8080"
echo "🎯 Supports: Cursor, Claude, GPT, Windsurf, and more"
echo ""

python universal_api.py &
API_PID=$!

echo "📱 Universal API started (PID: $API_PID)"
echo "🔗 Dashboard: http://localhost:8080/"
echo ""
echo "Press Ctrl+C to stop"

trap "echo ''; echo '🛑 Stopping...'; kill $API_PID 2>/dev/null; exit" INT
wait
