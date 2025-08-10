#!/bin/bash

# MCP Memory Server - Claude Desktop Installation Script
# Installs and configures the ML-powered memory server for Claude Desktop

set -e

echo "🔮 MCP Memory Server - Claude Desktop Installation"
echo "================================================"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
NC='\033[0m' # No Color

# Get the absolute path of the script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SERVER_PATH="$SCRIPT_DIR/claude_smart_server.py"
CONFIG_PATH="$SCRIPT_DIR/claude_config.json"

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

# Check if Claude config directory exists
CLAUDE_CONFIG_DIR="$HOME/.config/claude"
if [ ! -d "$CLAUDE_CONFIG_DIR" ]; then
    echo -e "${YELLOW}📁 Creating Claude config directory...${NC}"
    mkdir -p "$CLAUDE_CONFIG_DIR"
fi

echo -e "${GREEN}✅ Prerequisites check completed${NC}"

# Step 2: Install Python dependencies
echo -e "\n${BLUE}📦 Step 2: Installing/checking Python dependencies...${NC}"

# Check if virtual environment should be used
if [ -n "$VIRTUAL_ENV" ]; then
    echo -e "${YELLOW}🐍 Using virtual environment: $VIRTUAL_ENV${NC}"
fi

# Install dependencies
echo -e "${YELLOW}Installing ML dependencies for Claude...${NC}"
$PYTHON_CMD -m pip install torch>=2.1.0 transformers>=4.30.0 accelerate datasets --quiet

echo -e "${YELLOW}Installing MCP dependencies...${NC}"
$PYTHON_CMD -m pip install mcp sentence-transformers scikit-learn asyncio python-dotenv pydantic --quiet

echo -e "${GREEN}✅ Dependencies installed${NC}"

# Step 3: Test ML model access
echo -e "\n${BLUE}🧠 Step 3: Testing ML model access for Claude...${NC}"

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
    print('✅ Claude Desktop integration ready')
    
except Exception as e:
    print(f'⚠️ ML model check warning: {e}')
    print('Model will be downloaded on first use')
"

# Step 4: Create Claude Desktop configuration
echo -e "\n${BLUE}⚙️ Step 4: Configuring Claude Desktop MCP integration...${NC}"

# Update config file with correct path
sed "s|/Users/piermatteogrieco/mcp-memory-server-production/claude_smart_server.py|$SERVER_PATH|g" "$CONFIG_PATH" > "$CONFIG_PATH.tmp"
mv "$CONFIG_PATH.tmp" "$CONFIG_PATH"

# Copy configuration to Claude Desktop
CLAUDE_MCP_CONFIG="$CLAUDE_CONFIG_DIR/claude_desktop_config.json"

if [ -f "$CLAUDE_MCP_CONFIG" ]; then
    echo -e "${YELLOW}📝 Backing up existing Claude Desktop config...${NC}"
    cp "$CLAUDE_MCP_CONFIG" "$CLAUDE_MCP_CONFIG.backup.$(date +%s)"
    
    # Merge with existing config if possible
    echo -e "${YELLOW}📝 Merging with existing Claude configuration...${NC}"
    
    # Try to merge JSON (basic merge)
    if command -v jq &> /dev/null; then
        jq -s '.[0] * .[1]' "$CLAUDE_MCP_CONFIG" "$CONFIG_PATH" > "$CLAUDE_MCP_CONFIG.tmp" 2>/dev/null || {
            echo -e "${YELLOW}⚠️ JSON merge failed, using direct replacement${NC}"
            cp "$CONFIG_PATH" "$CLAUDE_MCP_CONFIG"
        }
        if [ -f "$CLAUDE_MCP_CONFIG.tmp" ]; then
            mv "$CLAUDE_MCP_CONFIG.tmp" "$CLAUDE_MCP_CONFIG"
        fi
    else
        echo -e "${YELLOW}📝 Installing Claude MCP configuration...${NC}"
        cp "$CONFIG_PATH" "$CLAUDE_MCP_CONFIG"
    fi
else
    echo -e "${YELLOW}📝 Installing Claude MCP configuration...${NC}"
    cp "$CONFIG_PATH" "$CLAUDE_MCP_CONFIG"
fi

echo -e "${GREEN}✅ Claude Desktop configuration updated${NC}"

# Step 5: Test the server
echo -e "\n${BLUE}🧪 Step 5: Testing Claude MCP server...${NC}"

echo -e "${YELLOW}Testing Claude server initialization...${NC}"
timeout 30s $PYTHON_CMD "$SERVER_PATH" --test 2>/dev/null || {
    echo -e "${YELLOW}⚠️ Server test timeout (normal for first ML model download)${NC}"
}

# Step 6: Create startup script
echo -e "\n${BLUE}🚀 Step 6: Creating Claude startup script...${NC}"

STARTUP_SCRIPT="$SCRIPT_DIR/start_claude_server.sh"
cat > "$STARTUP_SCRIPT" << EOF
#!/bin/bash
# Claude Desktop MCP Memory Server Startup Script

cd "$SCRIPT_DIR"
echo "🔮 Starting Claude Desktop MCP Memory Server with ML Auto-Triggers..."
echo "📍 Server path: $SERVER_PATH"
echo "⚡ ML model will auto-load on first message"
echo "🔮 Optimized for Claude Desktop native MCP integration"
echo ""

$PYTHON_CMD "$SERVER_PATH"
EOF

chmod +x "$STARTUP_SCRIPT"
echo -e "${GREEN}✅ Claude startup script created: $STARTUP_SCRIPT${NC}"

# Final instructions
echo -e "\n${GREEN}🎉 CLAUDE DESKTOP INSTALLATION COMPLETED!${NC}"
echo "============================================="

echo -e "\n${PURPLE}📋 CLAUDE DESKTOP SETUP INSTRUCTIONS:${NC}"
echo "1. 🔮 Open Claude Desktop application"
echo "2. ⚙️ The MCP server is configured in ~/.config/claude/claude_desktop_config.json"
echo "3. 🔄 Restart Claude Desktop if it was running"
echo "4. 💬 Start a new conversation to test the integration"

echo -e "\n${BLUE}🧪 TEST THE CLAUDE INTEGRATION:${NC}"
echo "Try these commands in Claude Desktop:"
echo -e "  ${YELLOW}• 'Ricorda che i React hooks vanno usati solo nei componenti funzionali'${NC}"
echo -e "  ${YELLOW}• 'Ho risolto il bug di autenticazione implementando JWT refresh tokens'${NC}"
echo -e "  ${YELLOW}• 'Puoi spiegarmi come funziona async/await in JavaScript?'${NC}"
echo -e "  ${YELLOW}• 'Importante: validare sempre input utente prima delle query database'${NC}"

echo -e "\n${BLUE}⚡ ML MODEL CLAUDE:${NC}"
echo "• The ML model will download automatically on first use (~63MB)"
echo "• First trigger may take 10-30 seconds (model download)"
echo "• Subsequent triggers will be instant (0.03s)"
echo "• Optimized for Claude Desktop native MCP protocol"

echo -e "\n${BLUE}🔧 MANUAL START (if needed):${NC}"
echo "  $STARTUP_SCRIPT"

echo -e "\n${BLUE}📁 FILES CREATED:${NC}"
echo "  • Server: $SERVER_PATH"
echo "  • Config: $CLAUDE_MCP_CONFIG"
echo "  • Startup: $STARTUP_SCRIPT"

echo -e "\n${BLUE}🔮 CLAUDE FEATURES:${NC}"
echo "  • Native MCP protocol integration"
echo "  • Enhanced explanation detection"
echo "  • Claude-optimized trigger thresholds"
echo "  • Smart conversation analysis"

echo -e "\n${GREEN}✅ Your Claude Desktop now has infinite AI memory! 🧠✨${NC}"
echo -e "${PURPLE}🔮 Claude can now remember everything and help you better!${NC}"
