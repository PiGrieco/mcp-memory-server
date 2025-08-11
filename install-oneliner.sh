#!/bin/bash

# 🧠 MCP Memory Server - One-Liner Installer
# Usage: curl -sSL https://raw.githubusercontent.com/PiGrieco/mcp-memory-server/production-ready-v2/install-oneliner.sh | bash

set -e

REPO_URL="https://raw.githubusercontent.com/PiGrieco/mcp-memory-server/production-ready-v2"

echo "🧠 MCP Memory Server - One-Liner Installation"
echo "=============================================="

# Download and execute main installer
curl -sSL "$REPO_URL/install.sh" | bash

echo ""
echo "🎉 One-liner installation completed!"
echo "💡 Run: cd ~/mcp-memory-server && ./start.sh"
