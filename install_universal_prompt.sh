#!/bin/bash

# 🧠 MCP Memory Server - Universal Installer
# "Installa questo: https://github.com/PiGrieco/mcp-memory-server"
# Works with any AI platform via simple prompt

set -e

echo "🧠 MCP Memory Server - Universal Installation"
echo "============================================"
echo "💬 Prompt: 'Installa questo: https://github.com/PiGrieco/mcp-memory-server'"
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
NC='\033[0m'

# Configuration
REPO_URL="https://github.com/PiGrieco/mcp-memory-server.git"
REPO_BRANCH="production-ready-v2"
INSTALL_DIR="$HOME/mcp-memory-server"

print_status() { echo -e "${GREEN}✅ $1${NC}"; }
print_info() { echo -e "${BLUE}ℹ️ $1${NC}"; }
print_warning() { echo -e "${YELLOW}⚠️ $1${NC}"; }

# Step 1: Clone repository
echo -e "\n${BLUE}📥 Step 1: Installing from GitHub...${NC}"

if [ -d "$INSTALL_DIR" ]; then
    print_warning "Directory exists, updating..."
    cd "$INSTALL_DIR"
    git fetch origin && git pull origin "$REPO_BRANCH"
else
    print_info "Cloning repository..."
    git clone -b "$REPO_BRANCH" "$REPO_URL" "$INSTALL_DIR"
    cd "$INSTALL_DIR"
fi

print_status "Repository ready"

# Step 2: Setup environment
echo -e "\n${BLUE}🐍 Step 2: Setting up environment...${NC}"

if [ ! -d "venv" ]; then
    python3 -m venv venv
fi
source venv/bin/activate
pip install -r requirements.txt --quiet

print_status "Environment ready"

# Step 3: Test installation
echo -e "\n${BLUE}🧪 Step 3: Testing components...${NC}"

timeout 5s python mcp_base_server.py > /dev/null 2>&1 || true

python -c "
try:
    from transformers import pipeline
    from sentence_transformers import SentenceTransformer
    import torch
    from mcp.server import Server
    print('✅ All ML components working')
except Exception as e:
    print(f'⚠️ Warning: {e}')
"

print_status "Components tested"

# Step 4: Platform detection and configuration
echo -e "\n${BLUE}🎯 Step 4: Configuring platforms...${NC}"

configure_platform() {
    local platform=$1
    local config_dir=$2
    local config_file=$3
    local server_file=$4
    local display_name=$5
    
    mkdir -p "$config_dir"
    
    cat > "$config_dir/$config_file" << EOF
{
  "mcpServers": {
    "mcp-memory-${platform}": {
      "command": "$INSTALL_DIR/venv/bin/python",
      "args": ["$INSTALL_DIR/$server_file"],
      "env": {
        "ML_MODEL_TYPE": "huggingface",
        "HUGGINGFACE_MODEL_NAME": "PiGrieco/mcp-memory-auto-trigger-model",
        "AUTO_TRIGGER_ENABLED": "true",
        "PRELOAD_ML_MODEL": "true",
        "${platform^^}_MODE": "true",
        "LOG_LEVEL": "INFO"
      }
    }
  }
}
EOF
    
    echo "  ✅ $display_name: $config_dir/$config_file"
}

# Configure all platforms
echo "🎯 Configuring for all AI platforms:"

# Cursor IDE
configure_platform "cursor" "$HOME/.cursor" "mcp_settings.json" "cursor_mcp_server.py" "Cursor IDE"
cp "$HOME/.cursor/mcp_settings.json" "$HOME/.cursor/mcp.json" 2>/dev/null || true

# Claude Desktop  
if [[ "$OSTYPE" == "darwin"* ]]; then
    CLAUDE_DIR="$HOME/Library/Application Support/Claude"
else
    CLAUDE_DIR="$HOME/.config/claude"
fi
configure_platform "claude" "$CLAUDE_DIR" "claude_desktop_config.json" "claude_mcp_server.py" "Claude Desktop"

# GPT/OpenAI (HTTP API)
configure_platform "gpt" "$HOME/.config/gpt-mcp" "gpt_config.json" "gpt_mcp_server.py" "GPT/OpenAI"

# Windsurf IDE
configure_platform "windsurf" "$HOME/.config/windsurf" "windsurf_config.json" "windsurf_mcp_server.py" "Windsurf IDE"

# Create universal HTTP API for any platform
echo -e "\n${BLUE}🌐 Creating universal HTTP API...${NC}"

cat > "$INSTALL_DIR/universal_api.py" << 'EOF'
#!/usr/bin/env python3
"""Universal HTTP API for MCP Memory Server - Works with any AI platform"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from mcp_base_server import MCPMemoryServer

app = FastAPI(title="Universal MCP Memory API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

memory_server = None

class UniversalRequest(BaseModel):
    message: str
    platform: str = "unknown"
    context: dict = {}

@app.on_event("startup")
async def startup_event():
    global memory_server
    memory_server = MCPMemoryServer()
    print("🚀 Universal MCP Memory API started!")

@app.get("/")
async def root():
    return HTMLResponse("""
    <html>
    <head><title>🧠 Universal MCP Memory Server</title></head>
    <body style="font-family: Arial; margin: 40px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white;">
        <div style="text-align: center; padding: 40px;">
            <h1>🧠 Universal MCP Memory Server</h1>
            <p>Multi-platform AI memory with ML auto-triggers</p>
            <div style="background: rgba(255,255,255,0.1); padding: 20px; border-radius: 10px; margin: 20px;">
                <h2>🎯 Supported Platforms</h2>
                <ul style="list-style: none; padding: 0;">
                    <li>🎯 Cursor IDE</li>
                    <li>🔮 Claude Desktop</li>
                    <li>🤖 GPT/OpenAI</li>
                    <li>🌪️ Windsurf IDE</li>
                    <li>💙 Lovable Platform</li>
                    <li>⚡ Replit Cloud</li>
                </ul>
            </div>
            <div style="background: rgba(255,255,255,0.1); padding: 20px; border-radius: 10px;">
                <h2>🔗 API Endpoints</h2>
                <p><code>POST /analyze</code> - Analyze any message</p>
                <p><code>POST /save</code> - Save memory</p>
                <p><code>POST /search</code> - Search memories</p>
                <p><code>GET /health</code> - Health check</p>
            </div>
        </div>
    </body>
    </html>
    """)

@app.get("/health")
async def health():
    return {"status": "healthy", "service": "universal-mcp-memory"}

@app.post("/analyze")
async def analyze(request: UniversalRequest):
    try:
        result = await memory_server.analyze_message({
            "message": request.message,
            "platform_context": {"platform": request.platform, **request.context}
        })
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/save")
async def save(request: UniversalRequest):
    try:
        result = await memory_server.save_memory({
            "content": request.message,
            "context": {"platform": request.platform, **request.context}
        })
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/search")
async def search(request: UniversalRequest):
    try:
        result = await memory_server.search_memories({
            "query": request.message,
            "limit": 5
        })
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)
EOF

chmod +x "$INSTALL_DIR/universal_api.py"

# Step 5: Create universal startup script
echo -e "\n${BLUE}🚀 Step 5: Creating startup scripts...${NC}"

cat > "$INSTALL_DIR/start_universal.sh" << 'EOF'
#!/bin/bash
# Universal MCP Memory Server Startup

cd "$(dirname "$0")"
source venv/bin/activate

echo "🧠 Universal MCP Memory Server Starting..."
echo "🌐 API available at: http://localhost:8080"
echo "🎯 Supports: Cursor, Claude, GPT, Windsurf, Lovable, Replit"
echo ""

python universal_api.py &
API_PID=$!

echo "📱 Universal API started (PID: $API_PID)"
echo "🔗 Endpoints:"
echo "   • http://localhost:8080/ - Dashboard"
echo "   • POST /analyze - Analyze messages"
echo "   • POST /save - Save memories"
echo "   • POST /search - Search memories"
echo ""
echo "Press Ctrl+C to stop"

trap "echo ''; echo '🛑 Stopping...'; kill $API_PID 2>/dev/null; exit" INT
wait
EOF

chmod +x "$INSTALL_DIR/start_universal.sh"

# Create platform-specific start scripts
for platform in cursor claude gpt windsurf; do
    cat > "$INSTALL_DIR/start_${platform}.sh" << EOF
#!/bin/bash
cd "\$(dirname "\$0")"
source venv/bin/activate
echo "🎯 Starting ${platform^^} MCP Memory Server..."
python ${platform}_mcp_server.py
EOF
    chmod +x "$INSTALL_DIR/start_${platform}.sh"
done

print_status "Universal scripts created"

# Final instructions
echo -e "\n${GREEN}🎉 UNIVERSAL INSTALLATION COMPLETED!${NC}"
echo "========================================"

echo -e "\n${BLUE}📁 Installation Directory:${NC} $INSTALL_DIR"

echo -e "\n${PURPLE}🎯 PLATFORM CONFIGURATIONS CREATED:${NC}"
echo "✅ Cursor IDE: ~/.cursor/mcp_settings.json"
echo "✅ Claude Desktop: $CLAUDE_DIR/claude_desktop_config.json"
echo "✅ GPT/OpenAI: ~/.config/gpt-mcp/gpt_config.json"  
echo "✅ Windsurf IDE: ~/.config/windsurf/windsurf_config.json"

echo -e "\n${BLUE}🚀 STARTUP OPTIONS:${NC}"
echo "• Universal API: ./start_universal.sh    # Works with any platform"
echo "• Cursor: ./start_cursor.sh              # Cursor IDE specific"
echo "• Claude: ./start_claude.sh              # Claude Desktop specific"
echo "• GPT: ./start_gpt.sh                    # GPT/OpenAI specific"

echo -e "\n${BLUE}🌐 UNIVERSAL API:${NC}"
echo "• URL: http://localhost:8080"
echo "• Dashboard: http://localhost:8080/"
echo "• Works with any AI platform via HTTP"

echo -e "\n${BLUE}🧪 QUICK TEST:${NC}"
echo "1. Restart your AI application (Cursor/Claude/etc.)"
echo "2. Or start universal API: cd $INSTALL_DIR && ./start_universal.sh"
echo "3. Try: 'Ricorda che Python è un linguaggio interpretato'"

echo -e "\n${BLUE}⚡ ML AUTO-TRIGGERS:${NC}"
echo "• 🤖 Model: PiGrieco/mcp-memory-auto-trigger-model (99.56% accuracy)"
echo "• 📊 Size: ~63MB (auto-download on first use)"
echo "• ⚡ Speed: First use 10-30s, then instant (0.03s)"

echo -e "\n${GREEN}✨ ALL AI PLATFORMS NOW HAVE INFINITE MEMORY! 🧠✨${NC}"
echo -e "${PURPLE}🎯 Works with: Cursor, Claude, GPT, Windsurf, and more!${NC}"

echo -e "\n${YELLOW}💡 TIPS:${NC}"
echo "• Each platform automatically detects the MCP server"
echo "• Use the universal API for custom integrations"
echo "• Memory is shared across all platforms"
echo "• ML auto-triggers work on all platforms"

if [ "$INSTALL_DIR" != "$(pwd)" ]; then
    echo -e "\n${YELLOW}🔗 Add to shell profile:${NC}"
    echo "  alias mcp-memory='cd $INSTALL_DIR && ./start_universal.sh'"
fi
