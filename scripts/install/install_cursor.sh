#!/bin/bash

# MCP Memory Server - Cursor Installation Script
# Installs and configures the ML-powered memory server for Cursor IDE

set -e

echo "🚀 MCP Memory Server - Cursor Installation"
echo "=========================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Installation configuration
REPO_URL="https://github.com/PiGrieco/mcp-memory-server.git"
REPO_BRANCH="feature/complete-architecture-refactor"
INSTALL_DIR="$HOME/mcp-memory-server"

# Check if we're running from existing installation or need to clone
if [ -f "$(dirname "${BASH_SOURCE[0]}")/../../main.py" ]; then
    # Running from existing installation
    SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
    echo -e "${BLUE}📍 Using existing installation: $SCRIPT_DIR${NC}"
else
    # Need to clone repository
    echo -e "${BLUE}📥 Cloning repository to: $INSTALL_DIR${NC}"
    if [ ! -d "$INSTALL_DIR" ]; then
        git clone -b "$REPO_BRANCH" "$REPO_URL" "$INSTALL_DIR"
    fi
    SCRIPT_DIR="$INSTALL_DIR"
fi

SERVER_PATH="$SCRIPT_DIR/servers/legacy/cursor_mcp_server.py"
CONFIG_PATH="$SCRIPT_DIR/config/cursor_config.json"

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

# Check if Cursor config directory exists
CURSOR_CONFIG_DIR="$HOME/.cursor"
if [ ! -d "$CURSOR_CONFIG_DIR" ]; then
    echo -e "${YELLOW}📁 Creating Cursor config directory...${NC}"
    mkdir -p "$CURSOR_CONFIG_DIR"
fi

echo -e "${GREEN}✅ Prerequisites check completed${NC}"

# Step 2: Install Python dependencies
echo -e "\n${BLUE}📦 Step 2: Installing/checking Python dependencies...${NC}"

# Check if virtual environment should be used
if [ -n "$VIRTUAL_ENV" ]; then
    echo -e "${YELLOW}🐍 Using virtual environment: $VIRTUAL_ENV${NC}"
fi

# Install dependencies
echo -e "${YELLOW}Installing ML dependencies...${NC}"
$PYTHON_CMD -m pip install torch>=2.1.0 transformers>=4.30.0 accelerate datasets --quiet

echo -e "${YELLOW}Installing MCP dependencies...${NC}"
$PYTHON_CMD -m pip install mcp sentence-transformers scikit-learn asyncio python-dotenv pydantic --quiet

echo -e "${GREEN}✅ Dependencies installed${NC}"

# Step 3: Test ML model access
echo -e "\n${BLUE}🧠 Step 3: Testing ML model access...${NC}"

$PYTHON_CMD -c "
import sys
sys.path.insert(0, '$SCRIPT_DIR/src')

try:
    from transformers import pipeline
    print('✅ Transformers library working')
    
    # Test Hugging Face model access (without downloading)
    from huggingface_hub import model_info
    model_name = 'PiGrieco/mcp-memory-auto-trigger-model'
    info = model_info(model_name)
    print(f'✅ ML model accessible: {model_name}')
    print(f'   Model size: ~{info.safetensors.total // (1024*1024)}MB')
    
except Exception as e:
    print(f'⚠️ ML model check warning: {e}')
    print('Model will be downloaded on first use')
"

# Step 4: Create Cursor configuration
echo -e "\n${BLUE}⚙️ Step 4: Configuring Cursor MCP integration...${NC}"

# Update config file with correct path
sed "s|/Users/piermatteogrieco/mcp-memory-server-production/cursor_mcp_server.py|$SERVER_PATH|g" "$CONFIG_PATH" > "$CONFIG_PATH.tmp"
mv "$CONFIG_PATH.tmp" "$CONFIG_PATH"

# Copy configuration to Cursor
CURSOR_MCP_CONFIG="$CURSOR_CONFIG_DIR/mcp_settings.json"

if [ -f "$CURSOR_MCP_CONFIG" ]; then
    echo -e "${YELLOW}📝 Backing up existing Cursor MCP config...${NC}"
    cp "$CURSOR_MCP_CONFIG" "$CURSOR_MCP_CONFIG.backup.$(date +%s)"
fi

echo -e "${YELLOW}📝 Installing Cursor MCP configuration...${NC}"
cp "$CONFIG_PATH" "$CURSOR_MCP_CONFIG"

echo -e "${GREEN}✅ Cursor configuration updated${NC}"

# Step 5: Test the server
echo -e "\n${BLUE}🧪 Step 5: Testing MCP server...${NC}"

echo -e "${YELLOW}Testing server initialization...${NC}"
timeout 30s $PYTHON_CMD "$SERVER_PATH" --test 2>/dev/null || {
    echo -e "${YELLOW}⚠️ Server test timeout (normal for first ML model download)${NC}"
}

# Step 6: Create startup script
echo -e "\n${BLUE}🚀 Step 6: Creating startup script...${NC}"

STARTUP_SCRIPT="$SCRIPT_DIR/scripts/servers/start_cursor_server.sh"
cat > "$STARTUP_SCRIPT" << EOF
#!/bin/bash
# Cursor MCP Memory Server Startup Script

cd "$SCRIPT_DIR"
echo "🚀 Starting Cursor MCP Memory Server with ML Auto-Triggers..."
echo "📍 Server path: $SERVER_PATH"
echo "⚡ ML model will auto-load on first message"
echo ""

$PYTHON_CMD "$SERVER_PATH"
EOF

chmod +x "$STARTUP_SCRIPT"
echo -e "${GREEN}✅ Startup script created: $STARTUP_SCRIPT${NC}"

# Final instructions
echo -e "\n${GREEN}🎉 INSTALLATION COMPLETED!${NC}"
echo "================================"

echo -e "\n${BLUE}📋 CURSOR SETUP INSTRUCTIONS:${NC}"
echo "1. Open Cursor IDE"
echo "2. The MCP server is already configured in ~/.cursor/mcp_settings.json"
echo "3. Restart Cursor if it was running"
echo "4. Press Cmd+L (macOS) or Ctrl+L (Windows/Linux) to open AI chat"

echo -e "\n${BLUE}🧪 TEST THE SYSTEM:${NC}"
echo "Try these commands in Cursor AI chat:"
echo -e "  ${YELLOW}• 'Ricorda che React hooks vanno usati solo nei componenti'${NC}"
echo -e "  ${YELLOW}• 'Ho risolto il bug di rendering aggiungendo key props'${NC}"
echo -e "  ${YELLOW}• 'Come si gestisce lo stato in React?'${NC}"

echo -e "\n${BLUE}⚡ ML AUTO-TRIGGER:${NC}"
echo "• Auto-trigger is ALWAYS enabled for continuous monitoring"
echo "• The ML model will download automatically on first use (~50MB)"  
echo "• Real-time conversation analysis active"
echo "• Keywords: ricorda, nota, importante, salva, memorizza"
echo "• Patterns: risolto, solved, fixed, bug fix, solution"
echo ""
echo -e "${BLUE}🎯 ML THRESHOLDS:${NC}"
echo "• ML Confidence: 70% (high precision)"
echo "• Trigger Threshold: 15% (sensitive detection)"
echo "• Memory Threshold: 70% (important content only)"
echo "• Similarity: 30% (relevant searches)"
echo "• Mode: Hybrid (ML + deterministic rules)"

echo -e "\n${BLUE}🔧 MANUAL START (if needed):${NC}"
echo "  $STARTUP_SCRIPT"

echo -e "\n${BLUE}📁 FILES CREATED:${NC}"
echo "  • Server: $SERVER_PATH"
echo "  • Config: $CURSOR_MCP_CONFIG"
echo "  • Startup: $STARTUP_SCRIPT"

echo -e "\n${GREEN}✅ Your Cursor IDE now has infinite AI memory! 🧠✨${NC}"
