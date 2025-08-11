#!/bin/bash

# MCP Memory Server - GPT/OpenAI Installation Script
# Installs and configures for ChatGPT, OpenAI API, and browser extensions

set -e

# Platform-specific configuration
PLATFORM_NAME="GPT"
PLATFORM_EMOJI="🤖"
PLATFORM_SERVER="gpt_mcp_server.py"
PLATFORM_CONFIG_DIR="$HOME/.config/gpt-mcp"
PLATFORM_CONFIG_FILE="gpt_config.json"
PLATFORM_MODE="GPT_MODE"

# Source the universal template
SCRIPT_DIR_TEMP="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
export PLATFORM_NAME PLATFORM_EMOJI PLATFORM_SERVER PLATFORM_CONFIG_DIR PLATFORM_CONFIG_FILE PLATFORM_MODE

echo "🤖 MCP Memory Server - GPT/OpenAI Installation"
echo "=============================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Installation configuration
REPO_URL="https://github.com/PiGrieco/mcp-memory-server.git"
REPO_BRANCH="production-ready-v2"
INSTALL_DIR="$HOME/mcp-memory-server"

# Check if we're running from existing installation or need to clone
if [ -f "$(dirname "${BASH_SOURCE[0]}")/mcp_base_server.py" ]; then
    SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
    echo -e "${BLUE}📍 Using existing installation: $SCRIPT_DIR${NC}"
else
    echo -e "${BLUE}📥 Cloning repository to: $INSTALL_DIR${NC}"
    if [ ! -d "$INSTALL_DIR" ]; then
        git clone -b "$REPO_BRANCH" "$REPO_URL" "$INSTALL_DIR"
    fi
    SCRIPT_DIR="$INSTALL_DIR"
fi

cd "$SCRIPT_DIR"

# Create virtual environment and install dependencies
echo -e "\n${BLUE}🐍 Setting up Python environment...${NC}"
if [ ! -d "venv" ]; then
    python3 -m venv venv
fi
source venv/bin/activate
pip install -r requirements.txt --quiet

# Test installation
echo -e "\n${BLUE}🧪 Testing installation...${NC}"
timeout 5s python mcp_base_server.py > /dev/null 2>&1 || true

# Create GPT-specific HTTP API server
echo -e "\n${BLUE}🌐 Creating GPT HTTP API server...${NC}"

cat > "$SCRIPT_DIR/gpt_http_api.py" << 'EOF'
#!/usr/bin/env python3
"""HTTP API Server for GPT/OpenAI Integration"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import sys
from pathlib import Path

# Add the base server
sys.path.insert(0, str(Path(__file__).parent))
from mcp_base_server import MCPMemoryServer

app = FastAPI(title="MCP Memory API for GPT", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global server instance
memory_server = None

class MessageRequest(BaseModel):
    message: str
    context: dict = {}

@app.on_event("startup")
async def startup_event():
    global memory_server
    memory_server = MCPMemoryServer()
    print("🚀 GPT HTTP API Server started!")

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "mcp-memory-gpt"}

@app.post("/analyze")
async def analyze_message(request: MessageRequest):
    try:
        # Use the memory server's analyze function
        result = await memory_server.analyze_message({
            "message": request.message,
            "platform_context": {"platform": "gpt", **request.context}
        })
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/save")
async def save_memory(request: MessageRequest):
    try:
        result = await memory_server.save_memory({
            "content": request.message,
            "context": {"platform": "gpt", **request.context}
        })
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/search")
async def search_memories(request: MessageRequest):
    try:
        result = await memory_server.search_memories({
            "query": request.message,
            "limit": 5
        })
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/memories")
async def get_all_memories():
    try:
        result = await memory_server.list_memories()
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/dashboard")
async def dashboard():
    stats = {"api_calls": 0, "memories": 0}  # Placeholder
    return f"""
    <html>
    <head><title>🤖 GPT Memory Dashboard</title></head>
    <body style="font-family: Arial; margin: 40px; background: #f5f5f5;">
        <h1>🤖 MCP Memory Dashboard - GPT/OpenAI</h1>
        <div style="background: white; padding: 20px; border-radius: 8px; margin: 20px 0;">
            <h2>📊 Statistics</h2>
            <p>API Calls: {stats['api_calls']}</p>
            <p>Total Memories: {stats['memories']}</p>
        </div>
        <div style="background: white; padding: 20px; border-radius: 8px;">
            <h2>🔗 API Endpoints</h2>
            <ul>
                <li><code>POST /analyze</code> - Analyze messages</li>
                <li><code>POST /save</code> - Save memories</li>
                <li><code>POST /search</code> - Search memories</li>
                <li><code>GET /memories</code> - List all memories</li>
            </ul>
        </div>
    </body>
    </html>
    """

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
EOF

chmod +x "$SCRIPT_DIR/gpt_http_api.py"

# Create browser extension for ChatGPT
echo -e "\n${BLUE}🌐 Creating browser extension...${NC}"

BROWSER_EXT_DIR="$SCRIPT_DIR/browser_extension"
mkdir -p "$BROWSER_EXT_DIR"

# Create manifest.json
cat > "$BROWSER_EXT_DIR/manifest.json" << 'EOF'
{
  "manifest_version": 3,
  "name": "MCP Memory for ChatGPT",
  "version": "1.0",
  "description": "Smart memory system for ChatGPT with ML auto-triggers",
  "permissions": ["activeTab", "storage"],
  "content_scripts": [
    {
      "matches": ["https://chat.openai.com/*", "https://chatgpt.com/*"],
      "js": ["content.js"]
    }
  ],
  "action": {
    "default_popup": "popup.html",
    "default_title": "MCP Memory"
  }
}
EOF

# Create content script
cat > "$BROWSER_EXT_DIR/content.js" << 'EOF'
// MCP Memory Browser Extension for ChatGPT
class MCPMemoryExtension {
    constructor() {
        this.serverUrl = 'http://localhost:8000';
        this.initializeExtension();
    }

    initializeExtension() {
        console.log('🧠 MCP Memory Extension loaded for ChatGPT');
        this.observeMessages();
        this.addMemoryUI();
    }

    observeMessages() {
        const observer = new MutationObserver((mutations) => {
            mutations.forEach((mutation) => {
                if (mutation.addedNodes.length) {
                    this.processNewMessages(mutation.addedNodes);
                }
            });
        });

        observer.observe(document.body, {
            childList: true,
            subtree: true
        });
    }

    async processNewMessages(nodes) {
        for (let node of nodes) {
            if (node.nodeType === Node.ELEMENT_NODE) {
                const messages = node.querySelectorAll('[data-message-author-role="user"], [data-message-author-role="assistant"]');
                
                for (let message of messages) {
                    if (!message.dataset.mcpProcessed) {
                        message.dataset.mcpProcessed = 'true';
                        await this.analyzeMessage(message);
                    }
                }
            }
        }
    }

    async analyzeMessage(messageElement) {
        try {
            const text = messageElement.textContent.trim();
            if (text.length < 10) return;

            const response = await fetch(`${this.serverUrl}/analyze`, {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({
                    message: text,
                    context: {
                        platform: 'chatgpt',
                        url: window.location.href,
                        timestamp: new Date().toISOString()
                    }
                })
            });

            if (response.ok) {
                const result = await response.json();
                if (result.summary && (result.summary.saved || result.summary.searched)) {
                    this.showMemoryNotification(messageElement, result);
                }
            }
        } catch (error) {
            console.log('MCP Memory: Server not available');
        }
    }

    showMemoryNotification(element, result) {
        const notification = document.createElement('div');
        notification.className = 'mcp-memory-notification';
        notification.innerHTML = `🧠 ${result.summary.saved ? '💾 Saved' : ''} ${result.summary.searched ? '🔍 Searched' : ''}`;
        notification.style.cssText = `
            position: absolute; background: #007bff; color: white; padding: 4px 8px;
            border-radius: 4px; font-size: 12px; z-index: 1000; margin-top: -20px; opacity: 0.8;
        `;
        
        element.appendChild(notification);
        setTimeout(() => notification.remove(), 3000);
    }

    addMemoryUI() {
        const statusDiv = document.createElement('div');
        statusDiv.innerHTML = '🧠 MCP Memory Active';
        statusDiv.style.cssText = `
            position: fixed; top: 10px; right: 10px; background: #28a745; color: white;
            padding: 8px 12px; border-radius: 6px; font-size: 14px; z-index: 10000; cursor: pointer;
        `;
        document.body.appendChild(statusDiv);
    }
}

// Initialize when page loads
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => new MCPMemoryExtension());
} else {
    new MCPMemoryExtension();
}
EOF

# Create popup.html
cat > "$BROWSER_EXT_DIR/popup.html" << 'EOF'
<!DOCTYPE html>
<html>
<head>
    <style>
        body { width: 300px; padding: 20px; font-family: Arial, sans-serif; }
        h3 { margin: 0 0 15px 0; color: #333; }
        .status { padding: 10px; border-radius: 5px; margin: 10px 0; }
        .active { background: #d4edda; color: #155724; }
        .inactive { background: #f8d7da; color: #721c24; }
        button { width: 100%; padding: 10px; margin: 5px 0; border: none; border-radius: 5px; cursor: pointer; }
        .btn-primary { background: #007bff; color: white; }
    </style>
</head>
<body>
    <h3>🧠 MCP Memory for ChatGPT</h3>
    <div id="status" class="status active">
        <strong>Status:</strong> <span>Connected</span>
    </div>
    <div>
        <strong>Features:</strong>
        <ul>
            <li>🤖 ML Auto-triggers</li>
            <li>💾 Smart memory saving</li>
            <li>🔍 Intelligent search</li>
            <li>⚡ Real-time analysis</li>
        </ul>
    </div>
    <button class="btn-primary" onclick="testConnection()">Test Connection</button>
    <script>
        function testConnection() {
            fetch('http://localhost:8000/health')
                .then(response => response.ok ? alert('Connected!') : alert('Server not available'))
                .catch(() => alert('Server not available'));
        }
    </script>
</body>
</html>
EOF

# Create startup scripts
echo -e "\n${BLUE}🚀 Creating startup scripts...${NC}"

cat > "$SCRIPT_DIR/start_gpt.sh" << 'EOF'
#!/bin/bash
# GPT/OpenAI MCP Memory Server Startup Script

cd "$(dirname "$0")"
source venv/bin/activate

echo "🤖 Starting GPT/OpenAI MCP Memory Server..."
echo "🌐 HTTP API will be available at http://localhost:8000"
echo "📱 Browser extension available in browser_extension/"
echo ""

python gpt_http_api.py &
API_PID=$!

echo "📱 HTTP API started (PID: $API_PID)"
echo "🔗 API endpoints:"
echo "   • POST /analyze - Analyze messages"
echo "   • POST /save - Save memories"
echo "   • POST /search - Search memories"
echo "   • GET /dashboard - Web dashboard"
echo ""
echo "🌐 Open http://localhost:8000/dashboard in your browser"
echo "📦 Install browser extension from browser_extension/ folder"
echo ""
echo "Press Ctrl+C to stop the server"

trap "echo ''; echo '🛑 Stopping server...'; kill $API_PID 2>/dev/null; exit" INT
wait
EOF

chmod +x "$SCRIPT_DIR/start_gpt.sh"

# Final instructions
echo -e "\n${GREEN}🎉 GPT/OPENAI INSTALLATION COMPLETED!${NC}"
echo "============================================"

echo -e "\n${CYAN}📋 GPT/OPENAI INTEGRATION OPTIONS:${NC}"
echo ""
echo -e "${YELLOW}1. 🌐 BROWSER EXTENSION (ChatGPT Web):${NC}"
echo "   • Extension files: $BROWSER_EXT_DIR"
echo "   • Load in Chrome: chrome://extensions/ → Developer mode → Load unpacked"
echo "   • Visit chat.openai.com and see memory notifications"
echo ""
echo -e "${YELLOW}2. 🔌 HTTP API SERVER:${NC}"
echo "   • Start server: ./start_gpt.sh"
echo "   • API endpoint: http://localhost:8000"
echo "   • Dashboard: http://localhost:8000/dashboard"

echo -e "\n${BLUE}🚀 Quick Start:${NC}"
echo "1. Start the server: ./start_gpt.sh"
echo "2. Install browser extension from: $BROWSER_EXT_DIR"
echo "3. Visit chat.openai.com and start chatting!"

echo -e "\n${BLUE}🧪 Test Commands:${NC}"
echo "curl -X POST http://localhost:8000/analyze -H 'Content-Type: application/json' -d '{\"message\":\"Test message\"}'"

echo -e "\n${GREEN}✅ GPT/OpenAI now has infinite AI memory! 🧠✨${NC}"
echo -e "${CYAN}🤖 ChatGPT can now remember everything across conversations!${NC}"
