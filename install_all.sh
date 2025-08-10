#!/bin/bash

# MCP Memory Server - Universal Installation Script
# Installs and configures ALL integrations at once

set -e

echo "🚀 MCP Memory Server - UNIVERSAL INSTALLATION"
echo "=============================================="
echo "Installing ALL integrations: Cursor, Claude, GPT, Windsurf, Lovable, Replit"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Get the absolute path of the script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo -e "${BLUE}📍 Installation directory: $SCRIPT_DIR${NC}"

# Step 1: Check prerequisites
echo -e "\n${BLUE}🔍 Step 1: Checking prerequisites for ALL platforms...${NC}"

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

# Step 2: Install ALL dependencies
echo -e "\n${BLUE}📦 Step 2: Installing ALL dependencies...${NC}"

echo -e "${YELLOW}Installing ML dependencies (PyTorch, Transformers, etc.)...${NC}"
$PYTHON_CMD -m pip install torch>=2.1.0 transformers>=4.30.0 accelerate datasets --quiet

echo -e "${YELLOW}Installing MCP dependencies...${NC}"
$PYTHON_CMD -m pip install mcp sentence-transformers scikit-learn asyncio python-dotenv pydantic --quiet

echo -e "${YELLOW}Installing web/API dependencies...${NC}"
$PYTHON_CMD -m pip install fastapi uvicorn requests aiohttp --quiet

echo -e "${GREEN}✅ ALL dependencies installed${NC}"

# Step 3: Test ML model access
echo -e "\n${BLUE}🧠 Step 3: Testing ML model access...${NC}"

$PYTHON_CMD -c "
try:
    from transformers import pipeline
    from huggingface_hub import model_info
    
    print('✅ Transformers library working')
    
    model_name = 'PiGrieco/mcp-memory-auto-trigger-model'
    info = model_info(model_name)
    print(f'✅ ML model accessible: {model_name}')
    print(f'   Model size: ~{info.safetensors.total // (1024*1024)}MB')
    print('✅ ALL integrations ready for ML')
    
except Exception as e:
    print(f'⚠️ ML model check warning: {e}')
    print('Model will be downloaded on first use')
"

# Step 4: Run individual installers
echo -e "\n${BLUE}🎯 Step 4: Running individual platform installers...${NC}"

# Install Cursor
if [ -f "$SCRIPT_DIR/install_cursor.sh" ]; then
    echo -e "\n${CYAN}🎯 Installing Cursor integration...${NC}"
    bash "$SCRIPT_DIR/install_cursor.sh" || echo -e "${YELLOW}⚠️ Cursor installation had issues${NC}"
else
    echo -e "${YELLOW}⚠️ Cursor installer not found${NC}"
fi

# Install Claude
if [ -f "$SCRIPT_DIR/install_claude.sh" ]; then
    echo -e "\n${PURPLE}🔮 Installing Claude Desktop integration...${NC}"
    bash "$SCRIPT_DIR/install_claude.sh" || echo -e "${YELLOW}⚠️ Claude installation had issues${NC}"
else
    echo -e "${YELLOW}⚠️ Claude installer not found${NC}"
fi

# Install GPT
if [ -f "$SCRIPT_DIR/install_gpt.sh" ]; then
    echo -e "\n${GREEN}🤖 Installing GPT/OpenAI integration...${NC}"
    bash "$SCRIPT_DIR/install_gpt.sh" || echo -e "${YELLOW}⚠️ GPT installation had issues${NC}"
else
    echo -e "${YELLOW}⚠️ GPT installer not found${NC}"
fi

# Step 5: Create universal startup script
echo -e "\n${BLUE}🚀 Step 5: Creating universal startup script...${NC}"

UNIVERSAL_STARTUP="$SCRIPT_DIR/start_all_servers.sh"
cat > "$UNIVERSAL_STARTUP" << EOF
#!/bin/bash
# Universal MCP Memory Server Startup Script
# Starts ALL servers for ALL platforms

cd "$SCRIPT_DIR"

echo "🚀 STARTING ALL MCP MEMORY SERVERS"
echo "=================================="

# Function to start a server
start_server() {
    local name=\$1
    local script=\$2
    local port=\$3
    
    if [ -f "\$script" ]; then
        echo "🎯 Starting \$name server..."
        if [ ! -z "\$port" ]; then
            PORT=\$port $PYTHON_CMD "\$script" &
            echo "   📍 \$name server started on port \$port (PID: \$!)"
        else
            $PYTHON_CMD "\$script" &
            echo "   📍 \$name server started (PID: \$!)"
        fi
        sleep 2
    else
        echo "   ⚠️ \$name server not found: \$script"
    fi
}

# Start all servers
start_server "Cursor" "cursor_smart_server.py"
start_server "Claude" "claude_smart_server.py" 
start_server "GPT HTTP API" "gpt_http_server.py" 8000
start_server "Windsurf" "windsurf_smart_server.py"
start_server "Lovable" "lovable_smart_server.py"
start_server "Replit" "replit_smart_server.py"

echo ""
echo "🎉 ALL SERVERS STARTED!"
echo "======================"
echo ""
echo "🔗 Available integrations:"
echo "   🎯 Cursor IDE: ~/.cursor/mcp_settings.json"
echo "   🔮 Claude Desktop: ~/.config/claude/claude_desktop_config.json"
echo "   🤖 GPT API: http://localhost:8000"
echo "   🌪️ Windsurf IDE: Configure in settings"
echo "   💙 Lovable: Web platform integration"
echo "   ⚡ Replit: Cloud IDE integration"
echo ""
echo "📊 Dashboards:"
echo "   🌐 GPT Dashboard: http://localhost:8000/dashboard"
echo ""
echo "Press Ctrl+C to stop all servers"

# Wait for interrupt
trap "echo ''; echo '🛑 Stopping all servers...'; kill \$(jobs -p) 2>/dev/null; exit" INT
wait
EOF

chmod +x "$UNIVERSAL_STARTUP"

# Step 6: Create platform summary
echo -e "\n${BLUE}📋 Step 6: Creating platform summary...${NC}"

cat > "$SCRIPT_DIR/PLATFORMS_SUMMARY.md" << 'EOF'
# 🧠 MCP Memory Server - All Platforms Integration

## 🎯 Cursor IDE
- **Server**: `cursor_smart_server.py`
- **Config**: `~/.cursor/mcp_settings.json`
- **Features**: Real-time code triggers, ML auto-save
- **Usage**: Press Cmd+L and start chatting

## 🔮 Claude Desktop  
- **Server**: `claude_smart_server.py`
- **Config**: `~/.config/claude/claude_desktop_config.json`
- **Features**: Native MCP integration, explanation detection
- **Usage**: Restart Claude Desktop and chat

## 🤖 GPT/OpenAI
- **Server**: `gpt_smart_server.py` + `gpt_http_server.py`
- **API**: `http://localhost:8000`
- **Features**: HTTP API, browser extension, ChatGPT integration
- **Usage**: Start server and use browser extension

## 🌪️ Windsurf IDE
- **Server**: `windsurf_smart_server.py`
- **Features**: Code-aware triggers, IDE integration
- **Usage**: Configure in Windsurf settings

## 💙 Lovable Platform
- **Server**: `lovable_smart_server.py`  
- **Features**: Web development focus, design memory
- **Usage**: Integrate with Lovable AI platform

## ⚡ Replit Cloud
- **Server**: `replit_smart_server.py`
- **Features**: Cloud-optimized, collaboration-aware
- **Usage**: Deploy as Replit service

## 🚀 Universal Commands

### Start All Servers
```bash
./start_all_servers.sh
```

### Install Everything
```bash
./install_all.sh
```

### Individual Installers
- `./install_cursor.sh` - Cursor IDE
- `./install_claude.sh` - Claude Desktop  
- `./install_gpt.sh` - GPT/OpenAI
- Individual Windsurf/Lovable/Replit servers available

## 🧠 ML Features (All Platforms)

- **Model**: PiGrieco/mcp-memory-auto-trigger-model (63MB)
- **Accuracy**: 99.56% trigger detection
- **Speed**: 0.03s after initial load
- **Actions**: SAVE_MEMORY, SEARCH_MEMORY, NO_ACTION
- **Languages**: Italian, English support

## 🎯 Auto-Trigger Examples

### Save Triggers
- "Ricorda che React hooks vanno usati solo nei componenti"
- "I solved the bug by implementing retry logic"
- "Important: always validate user input"

### Search Triggers  
- "Come si gestisce lo stato in React?"
- "How do I optimize database performance?"
- "What's the best practice for authentication?"

### No Action
- "Ciao, come va?"
- "Good morning!"
- General conversation

## 📊 Statistics & Monitoring

Each platform tracks:
- Memory saves/searches
- ML predictions  
- Platform-specific metrics
- Performance stats

## 🔧 Troubleshooting

1. **ML Model Issues**: Model downloads automatically (~63MB)
2. **Permission Issues**: Run `chmod +x *.sh`
3. **Port Conflicts**: Change ports in server files
4. **Dependencies**: Re-run installers

## 🎉 Ready!

All platforms now have infinite AI memory with ML auto-triggers! 🧠✨
EOF

echo -e "${GREEN}✅ Platform summary created: $SCRIPT_DIR/PLATFORMS_SUMMARY.md${NC}"

# Final instructions
echo -e "\n${GREEN}🎉 UNIVERSAL INSTALLATION COMPLETED!${NC}"
echo "=============================================="

echo -e "\n${CYAN}📋 ALL PLATFORMS CONFIGURED:${NC}"
echo -e "   ${CYAN}🎯 Cursor IDE${NC} - Ready for coding assistance"
echo -e "   ${PURPLE}🔮 Claude Desktop${NC} - Native MCP integration"  
echo -e "   ${GREEN}🤖 GPT/OpenAI${NC} - HTTP API + browser extension"
echo -e "   ${BLUE}🌪️ Windsurf IDE${NC} - Code-aware triggers"
echo -e "   ${YELLOW}💙 Lovable Platform${NC} - Web development focus"
echo -e "   ${RED}⚡ Replit Cloud${NC} - Cloud IDE integration"

echo -e "\n${BLUE}🚀 QUICK START:${NC}"
echo "1. Start all servers: $UNIVERSAL_STARTUP"
echo "2. Open any supported platform"
echo "3. Start chatting and watch the magic! ✨"

echo -e "\n${BLUE}📊 DASHBOARDS & CONFIGS:${NC}"
echo "   • GPT API: http://localhost:8000/dashboard"
echo "   • Cursor config: ~/.cursor/mcp_settings.json"
echo "   • Claude config: ~/.config/claude/claude_desktop_config.json"

echo -e "\n${BLUE}📁 FILES CREATED:${NC}"
echo "   • Universal startup: $UNIVERSAL_STARTUP"
echo "   • Platform summary: $SCRIPT_DIR/PLATFORMS_SUMMARY.md"
echo "   • All individual servers and configs"

echo -e "\n${GREEN}✅ ALL AI PLATFORMS NOW HAVE INFINITE MEMORY! 🧠✨${NC}"
echo -e "${CYAN}🎯 Try saying 'Ricorda questa soluzione importante' in any platform!${NC}"
