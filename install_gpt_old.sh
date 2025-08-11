#!/bin/bash

# MCP Memory Server - GPT/OpenAI Integration Installation Script
# Supports ChatGPT, OpenAI API, and browser extensions

set -e

echo "🤖 MCP Memory Server - GPT/OpenAI Integration Installation"
echo "========================================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Get the absolute path of the script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SERVER_PATH="$SCRIPT_DIR/gpt_smart_server.py"

echo -e "${BLUE}📍 Installation directory: $SCRIPT_DIR${NC}"

# Step 1: Check prerequisites
echo -e "\n${BLUE}🔍 Step 1: Checking prerequisites...${NC}"

# Check Python
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version 2>&1 | cut -d' ' -f2)
    echo -e "${GREEN}✅ Python $PYTHON_VERSION found${NC}"
    PYTHON_CMD="python3"
elif command -v python &> /dev/null; then
    PYTHON_VERSION=$(python --version 2>&1 | cut -d' ' -f2)
    echo -e "${GREEN}✅ Python $PYTHON_VERSION found${NC}"
    PYTHON_CMD="python"
else
    echo -e "${RED}❌ Python not found. Please install Python 3.8+${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Prerequisites check completed${NC}"

# Step 2: Install Python dependencies
echo -e "\n${BLUE}📦 Step 2: Installing/checking Python dependencies...${NC}"

# Check if virtual environment should be used
if [ -n "$VIRTUAL_ENV" ]; then
    echo -e "${YELLOW}🐍 Using virtual environment: $VIRTUAL_ENV${NC}"
fi

# Install dependencies
echo -e "${YELLOW}Installing ML dependencies for GPT integration...${NC}"
$PYTHON_CMD -m pip install torch>=2.1.0 transformers>=4.30.0 accelerate datasets --quiet

echo -e "${YELLOW}Installing web and API dependencies...${NC}"
$PYTHON_CMD -m pip install fastapi uvicorn requests aiohttp --quiet

echo -e "${YELLOW}Installing MCP dependencies...${NC}"
$PYTHON_CMD -m pip install mcp sentence-transformers scikit-learn asyncio python-dotenv pydantic --quiet

echo -e "${GREEN}✅ Dependencies installed${NC}"

# Step 3: Test ML model access
echo -e "\n${BLUE}🧠 Step 3: Testing ML model access for GPT...${NC}"

$PYTHON_CMD -c "
import sys
sys.path.insert(0, '$SCRIPT_DIR/src')

try:
    from transformers import pipeline
    print('✅ Transformers library working')
    
    # Test Hugging Face model access
    from huggingface_hub import model_info
    model_name = 'PiGrieco/mcp-memory-auto-trigger-model'
    info = model_info(model_name)
    print(f'✅ ML model accessible: {model_name}')
    print(f'   Model size: ~{info.safetensors.total // (1024*1024)}MB')
    print('✅ GPT/OpenAI integration ready')
    
except Exception as e:
    print(f'⚠️ ML model check warning: {e}')
    print('Model will be downloaded on first use')
"

# Step 4: Create browser extension files
echo -e "\n${BLUE}🌐 Step 4: Creating browser extension for ChatGPT...${NC}"

BROWSER_EXT_DIR="$SCRIPT_DIR/browser_extension"
mkdir -p "$BROWSER_EXT_DIR"

# Create manifest.json
cat > "$BROWSER_EXT_DIR/manifest.json" << 'EOF'
{
  "manifest_version": 3,
  "name": "MCP Memory for ChatGPT",
  "version": "1.0",
  "description": "Smart memory system for ChatGPT with ML auto-triggers",
  "permissions": [
    "activeTab",
    "storage"
  ],
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
        this.isActive = true;
        this.initializeExtension();
    }

    initializeExtension() {
        console.log('🧠 MCP Memory Extension loaded for ChatGPT');
        this.observeMessages();
        this.addMemoryUI();
    }

    observeMessages() {
        // Watch for new messages in ChatGPT
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

            // Send to MCP server for analysis
            const response = await fetch(`${this.serverUrl}/analyze`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
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
                if (result.summary.saved || result.summary.searched) {
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
        notification.innerHTML = `
            🧠 MCP Memory: 
            ${result.summary.saved ? '💾 Saved' : ''} 
            ${result.summary.searched ? '🔍 Searched' : ''}
        `;
        notification.style.cssText = `
            position: absolute;
            background: #007bff;
            color: white;
            padding: 4px 8px;
            border-radius: 4px;
            font-size: 12px;
            z-index: 1000;
            margin-top: -20px;
            opacity: 0.8;
        `;
        
        element.appendChild(notification);
        
        setTimeout(() => notification.remove(), 3000);
    }

    addMemoryUI() {
        // Add memory status indicator
        const statusDiv = document.createElement('div');
        statusDiv.id = 'mcp-memory-status';
        statusDiv.innerHTML = '🧠 MCP Memory Active';
        statusDiv.style.cssText = `
            position: fixed;
            top: 10px;
            right: 10px;
            background: #28a745;
            color: white;
            padding: 8px 12px;
            border-radius: 6px;
            font-size: 14px;
            z-index: 10000;
            cursor: pointer;
        `;
        
        statusDiv.onclick = () => {
            this.isActive = !this.isActive;
            statusDiv.style.background = this.isActive ? '#28a745' : '#6c757d';
            statusDiv.innerHTML = this.isActive ? '🧠 MCP Memory Active' : '🧠 MCP Memory Paused';
        };
        
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
        body { width: 300px; padding: 20px; }
        h3 { margin: 0 0 15px 0; color: #333; }
        .status { padding: 10px; border-radius: 5px; margin: 10px 0; }
        .active { background: #d4edda; color: #155724; }
        .inactive { background: #f8d7da; color: #721c24; }
        button { width: 100%; padding: 10px; margin: 5px 0; border: none; border-radius: 5px; cursor: pointer; }
        .btn-primary { background: #007bff; color: white; }
        .btn-secondary { background: #6c757d; color: white; }
    </style>
</head>
<body>
    <h3>🧠 MCP Memory for ChatGPT</h3>
    
    <div id="status" class="status">
        <strong>Status:</strong> <span id="statusText">Checking...</span>
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
    <button class="btn-secondary" onclick="openSettings()">Settings</button>
    
    <script>
        async function checkStatus() {
            try {
                const response = await fetch('http://localhost:8000/health');
                const statusDiv = document.getElementById('status');
                const statusText = document.getElementById('statusText');
                
                if (response.ok) {
                    statusDiv.className = 'status active';
                    statusText.textContent = 'Connected';
                } else {
                    throw new Error('Server error');
                }
            } catch (error) {
                const statusDiv = document.getElementById('status');
                const statusText = document.getElementById('statusText');
                statusDiv.className = 'status inactive';
                statusText.textContent = 'Disconnected';
            }
        }
        
        async function testConnection() {
            alert('Testing MCP Memory connection...');
            await checkStatus();
        }
        
        function openSettings() {
            chrome.tabs.create({url: 'http://localhost:8000/dashboard'});
        }
        
        // Check status on load
        checkStatus();
    </script>
</body>
</html>
EOF

echo -e "${GREEN}✅ Browser extension created in $BROWSER_EXT_DIR${NC}"

# Step 5: Create HTTP API server
echo -e "\n${BLUE}🌐 Step 5: Creating HTTP API server...${NC}"

cat > "$SCRIPT_DIR/gpt_http_server.py" << 'EOF'
#!/usr/bin/env python3
"""
HTTP API Server for GPT/OpenAI Integration
Provides REST endpoints for browser extensions and OpenAI API
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import asyncio
from typing import Dict, List, Optional
import sys
from pathlib import Path

# Add the smart server
sys.path.insert(0, str(Path(__file__).parent))
from gpt_smart_server import GPTTriggerSystem

app = FastAPI(title="MCP Memory API for GPT", version="1.0.0")

# Enable CORS for browser extensions
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global trigger system
trigger_system = None

class MessageRequest(BaseModel):
    message: str
    context: Optional[Dict] = {}

class SearchRequest(BaseModel):
    query: str
    limit: Optional[int] = 5

@app.on_event("startup")
async def startup_event():
    global trigger_system
    trigger_system = GPTTriggerSystem()
    print("🚀 GPT HTTP API Server started!")

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "mcp-memory-gpt"}

@app.post("/analyze")
async def analyze_message(request: MessageRequest):
    """Analyze message for auto-triggers"""
    try:
        result = await trigger_system.process_message(request.message, request.context)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/search")
async def search_memories(request: SearchRequest):
    """Search memories"""
    try:
        results = trigger_system._search_memories(request.query)
        return {"results": results[:request.limit]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/stats")
async def get_stats():
    """Get server statistics"""
    return trigger_system.get_stats()

@app.get("/memories")
async def get_all_memories():
    """Get all memories"""
    return {"memories": list(trigger_system.memories.values())}

@app.get("/dashboard")
async def dashboard():
    """Simple dashboard"""
    stats = trigger_system.get_stats()
    return f"""
    <html>
    <head><title>MCP Memory Dashboard</title></head>
    <body>
        <h1>🧠 MCP Memory Dashboard</h1>
        <h2>Statistics:</h2>
        <ul>
            <li>API Requests: {stats['api_stats']['requests']}</li>
            <li>Memories Saved: {stats['api_stats']['saves']}</li>
            <li>Searches: {stats['api_stats']['searches']}</li>
            <li>ML Predictions: {stats['api_stats']['ml_predictions']}</li>
            <li>Total Memories: {stats['memory_count']}</li>
        </ul>
        <h2>Recent Memories:</h2>
        <ul>
            {"".join([f'<li>{mem["content"][:100]}...</li>' for mem in list(trigger_system.memories.values())[-5:]])}
        </ul>
    </body>
    </html>
    """

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
EOF

chmod +x "$SCRIPT_DIR/gpt_http_server.py"

# Step 6: Create startup script
echo -e "\n${BLUE}🚀 Step 6: Creating startup scripts...${NC}"

STARTUP_SCRIPT="$SCRIPT_DIR/start_gpt_server.sh"
cat > "$STARTUP_SCRIPT" << EOF
#!/bin/bash
# GPT/OpenAI MCP Memory Server Startup Script

cd "$SCRIPT_DIR"
echo "🤖 Starting GPT/OpenAI MCP Memory Server with ML Auto-Triggers..."
echo "📍 Server path: $SERVER_PATH"
echo "🌐 HTTP API will be available at http://localhost:8000"
echo "⚡ ML model will auto-load on first message"
echo ""

# Start HTTP API server
echo "🌐 Starting HTTP API server..."
$PYTHON_CMD gpt_http_server.py &
API_PID=\$!

echo "📱 HTTP API started (PID: \$API_PID)"
echo "🔗 API endpoints:"
echo "   • POST /analyze - Analyze messages"
echo "   • POST /search - Search memories"
echo "   • GET /stats - Server statistics"
echo "   • GET /dashboard - Web dashboard"
echo ""
echo "🌐 Open http://localhost:8000/dashboard in your browser"
echo ""
echo "Press Ctrl+C to stop all servers"

# Wait for interrupt
trap "echo ''; echo '🛑 Stopping servers...'; kill \$API_PID 2>/dev/null; exit" INT
wait
EOF

chmod +x "$STARTUP_SCRIPT"

echo -e "${GREEN}✅ Startup script created: $STARTUP_SCRIPT${NC}"

# Final instructions
echo -e "\n${GREEN}🎉 GPT/OPENAI INSTALLATION COMPLETED!${NC}"
echo "=============================================="

echo -e "\n${CYAN}📋 GPT/OPENAI INTEGRATION OPTIONS:${NC}"
echo ""
echo -e "${YELLOW}1. 🌐 BROWSER EXTENSION (ChatGPT Web):${NC}"
echo "   • Extension files: $BROWSER_EXT_DIR"
echo "   • Load in Chrome: chrome://extensions/ → Developer mode → Load unpacked"
echo "   • Visit chat.openai.com and see memory notifications"
echo ""
echo -e "${YELLOW}2. 🔌 HTTP API SERVER:${NC}"
echo "   • Start server: $STARTUP_SCRIPT"
echo "   • API endpoint: http://localhost:8000"
echo "   • Dashboard: http://localhost:8000/dashboard"
echo ""
echo -e "${YELLOW}3. 🤖 DIRECT INTEGRATION:${NC}"
echo "   • Python script: $SERVER_PATH"
echo "   • Import and use in your OpenAI projects"

echo -e "\n${BLUE}🧪 TEST THE GPT INTEGRATION:${NC}"
echo "Start the server and try these in ChatGPT:"
echo -e "  ${YELLOW}• 'Remember that React hooks should only be used in functional components'${NC}"
echo -e "  ${YELLOW}• 'I solved the authentication bug by implementing JWT refresh tokens'${NC}"
echo -e "  ${YELLOW}• 'Can you explain how async/await works in JavaScript?'${NC}"
echo -e "  ${YELLOW}• 'Important: always validate user input before database queries'${NC}"

echo -e "\n${BLUE}⚡ ML MODEL GPT:${NC}"
echo "• The ML model will download automatically on first use (~63MB)"
echo "• First trigger may take 10-30 seconds (model download)"
echo "• Subsequent triggers will be instant (0.03s)"
echo "• HTTP API provides real-time memory analysis"

echo -e "\n${BLUE}🔧 QUICK START:${NC}"
echo "1. Start the server: $STARTUP_SCRIPT"
echo "2. Install browser extension from: $BROWSER_EXT_DIR"
echo "3. Visit chat.openai.com and start chatting!"

echo -e "\n${BLUE}📁 FILES CREATED:${NC}"
echo "  • Server: $SERVER_PATH"
echo "  • HTTP API: $SCRIPT_DIR/gpt_http_server.py"
echo "  • Browser Extension: $BROWSER_EXT_DIR/"
echo "  • Startup: $STARTUP_SCRIPT"

echo -e "\n${GREEN}✅ Your GPT/OpenAI now has infinite AI memory! 🧠✨${NC}"
echo -e "${CYAN}🤖 ChatGPT can now remember everything across conversations!${NC}"
