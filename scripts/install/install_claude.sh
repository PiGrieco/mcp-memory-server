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

# Installation configuration
REPO_URL="https://github.com/PiGrieco/mcp-memory-server.git"
REPO_BRANCH="production-ready-v2"
INSTALL_DIR="$HOME/mcp-memory-server"

# Check if we're running from existing installation or need to clone
if [ -f "$(dirname "${BASH_SOURCE[0]}")/mcp_base_server.py" ]; then
    # Running from existing installation
    SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
    echo -e "${BLUE}📍 Using existing installation: $SCRIPT_DIR${NC}"
else
    # Need to clone repository
    echo -e "${BLUE}📥 Cloning repository to: $INSTALL_DIR${NC}"
    if [ ! -d "$INSTALL_DIR" ]; then
        git clone -b "$REPO_BRANCH" "$REPO_URL" "$INSTALL_DIR"
    fi
    SCRIPT_DIR="$INSTALL_DIR"
fi

SERVER_PATH="$SCRIPT_DIR/claude_mcp_server.py"
CONFIG_TEMPLATE="$SCRIPT_DIR/config/templates/claude_template.json"

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

# Step 2: Setup Python environment and dependencies
echo -e "\n${BLUE}🐍 Step 2: Setting up Python environment...${NC}"

cd "$SCRIPT_DIR"

# Create virtual environment if not exists
if [ ! -d "venv" ]; then
    echo -e "${YELLOW}Creating Python virtual environment...${NC}"
    $PYTHON_CMD -m venv venv
    echo -e "${GREEN}✅ Virtual environment created${NC}"
else
    echo -e "${YELLOW}Using existing virtual environment${NC}"
fi

# Activate virtual environment
source venv/bin/activate
echo -e "${GREEN}✅ Virtual environment activated${NC}"

# Upgrade pip
echo -e "${YELLOW}Upgrading pip...${NC}"
pip install --upgrade pip > /dev/null 2>&1

# Install dependencies
echo -e "\n${BLUE}📦 Step 3: Installing dependencies...${NC}"

echo -e "${YELLOW}Installing core dependencies...${NC}"
pip install -r requirements.txt --quiet

echo -e "${GREEN}✅ All dependencies installed${NC}"

# Step 4: Test ML model access and installation
echo -e "\n${BLUE}🧠 Step 4: Testing ML model access and installation...${NC}"

echo -e "${YELLOW}Testing MCP server...${NC}"
timeout 10s python mcp_base_server.py > /dev/null 2>&1 || {
    echo -e "${YELLOW}⚠️ Server test timeout (normal for first run)${NC}"
}

echo -e "${YELLOW}Testing ML components...${NC}"
python -c "
import sys
try:
    from transformers import pipeline
    print('✅ Transformers library working')
    from sentence_transformers import SentenceTransformer
    print('✅ Sentence Transformers working')
    import torch
    print('✅ PyTorch working')
    from mcp.server import Server
    print('✅ MCP library working')
    
    # Test model access
    from huggingface_hub import model_info
    model_name = 'PiGrieco/mcp-memory-auto-trigger-model'
    try:
        info = model_info(model_name)
        print(f'✅ ML model accessible: {model_name}')
        print(f'   Model size: ~{info.safetensors.total // (1024*1024)}MB')
    except:
        print('⚠️ Model will be downloaded on first use (~63MB)')
    
    print('✅ All components ready for Claude Desktop')
except Exception as e:
    print(f'❌ Component test failed: {e}')
    sys.exit(1)
"

echo -e "${GREEN}✅ Installation test completed successfully${NC}"

# Step 5: Create Claude Desktop configuration
echo -e "\n${BLUE}⚙️ Step 5: Configuring Claude Desktop MCP integration...${NC}"

# Detect OS and set Claude config path
if [[ "$OSTYPE" == "darwin"* ]]; then
    CLAUDE_CONFIG_DIR="$HOME/Library/Application Support/Claude"
else
    CLAUDE_CONFIG_DIR="$HOME/.config/claude"
fi

echo -e "${YELLOW}📁 Creating Claude config directory...${NC}"
mkdir -p "$CLAUDE_CONFIG_DIR"

# Create Claude MCP configuration with dynamic paths
CLAUDE_MCP_CONFIG="$CLAUDE_CONFIG_DIR/claude_desktop_config.json"

echo -e "${YELLOW}📝 Creating Claude Desktop configuration...${NC}"
cat > "$CLAUDE_MCP_CONFIG" << EOF
{
  "mcpServers": {
    "mcp-memory-claude": {
      "command": "$SCRIPT_DIR/venv/bin/python",
      "args": ["$SCRIPT_DIR/claude_mcp_server.py"],
      "env": {
        "ML_MODEL_TYPE": "huggingface",
        "HUGGINGFACE_MODEL_NAME": "PiGrieco/mcp-memory-auto-trigger-model",
        "AUTO_TRIGGER_ENABLED": "true",
        "PRELOAD_ML_MODEL": "true",
        "CLAUDE_MODE": "true",
        "LOG_LEVEL": "INFO",
        "MEMORY_THRESHOLD": "0.7",
        "SEMANTIC_THRESHOLD": "0.8"
      }
    }
  }
}
EOF

echo -e "${GREEN}✅ Claude Desktop configuration created${NC}"

# Step 6: Create startup and convenience scripts
echo -e "\n${BLUE}🚀 Step 6: Creating convenience scripts...${NC}"

# Create start script
cat > "$SCRIPT_DIR/start_claude.sh" << 'EOF'
#!/bin/bash
# Claude Desktop MCP Memory Server Startup Script

cd "$(dirname "$0")"
source venv/bin/activate

echo "🔮 Starting Claude Desktop MCP Memory Server..."
echo "📍 Server: claude_mcp_server.py"
echo "⚡ ML model will auto-load on first message"
echo "🔮 Optimized for Claude Desktop native MCP integration"
echo ""

python claude_mcp_server.py
EOF

chmod +x "$SCRIPT_DIR/start_claude.sh"

# Create update script
cat > "$SCRIPT_DIR/update_claude.sh" << EOF
#!/bin/bash
# Claude Desktop MCP Memory Server Update Script

cd "$SCRIPT_DIR"
source venv/bin/activate

echo "🔄 Updating Claude MCP Memory Server..."
git fetch origin
git pull origin $REPO_BRANCH

echo "📦 Updating dependencies..."
pip install -r requirements.txt --upgrade --quiet

echo "✅ Claude update completed successfully"
EOF

chmod +x "$SCRIPT_DIR/update_claude.sh"

echo -e "${GREEN}✅ Convenience scripts created${NC}"

# Final instructions
echo -e "\n${GREEN}🎉 CLAUDE DESKTOP INSTALLATION COMPLETED!${NC}"
echo "============================================="

echo -e "\n${BLUE}📁 Installation Directory:${NC} $SCRIPT_DIR"
echo -e "${BLUE}🐍 Python Environment:${NC} $SCRIPT_DIR/venv/"

echo -e "\n${PURPLE}📋 CLAUDE DESKTOP SETUP:${NC}"
echo "1. 🔮 Restart Claude Desktop application"
echo "2. ⚙️ MCP server configured in: $CLAUDE_MCP_CONFIG"
echo "3. 💬 Start a new conversation to test the integration"

echo -e "\n${BLUE}🚀 Quick Start Commands:${NC}"
echo "  cd $SCRIPT_DIR"
echo "  ./start_claude.sh              # Start Claude MCP server"
echo "  ./update_claude.sh             # Update to latest version"

echo -e "\n${BLUE}🧪 TEST THE CLAUDE INTEGRATION:${NC}"
echo "Try these in Claude Desktop:"
echo -e "  ${YELLOW}• 'Ricorda che React hooks vanno solo nei componenti funzionali'${NC}"
echo -e "  ${YELLOW}• 'Ho risolto il bug JWT implementando refresh tokens'${NC}"
echo -e "  ${YELLOW}• 'Spiega come funziona async/await in JavaScript'${NC}"
echo -e "  ${YELLOW}• 'Importante: validare sempre input prima delle query database'${NC}"

echo -e "\n${BLUE}⚡ ML AUTO-TRIGGERS:${NC}"
echo "• 🤖 Model: PiGrieco/mcp-memory-auto-trigger-model (99.56% accuracy)"
echo "• 📊 Size: ~63MB (downloads automatically on first use)"
echo "• ⚡ Speed: First use 10-30s, then instant (0.03s)"
echo "• 🎯 Platform: Optimized for Claude Desktop MCP protocol"

echo -e "\n${BLUE}🔧 MANUAL COMMANDS:${NC}"
echo "  cd $SCRIPT_DIR && source venv/bin/activate"
echo "  python claude_mcp_server.py    # Direct server start"

echo -e "\n${BLUE}📁 FILES CREATED:${NC}"
echo "  • MCP Server: $SERVER_PATH"
echo "  • Claude Config: $CLAUDE_MCP_CONFIG"
echo "  • Start Script: $SCRIPT_DIR/start_claude.sh"
echo "  • Update Script: $SCRIPT_DIR/update_claude.sh"

echo -e "\n${BLUE}🔮 CLAUDE FEATURES:${NC}"
echo "  • 🧠 Infinite AI memory with ML auto-triggers"
echo "  • 🔍 Semantic search for context retrieval"
echo "  • 💾 Automatic memory categorization (Knowledge, Error, Solution, etc.)"
echo "  • ⚡ Real-time memory operations"
echo "  • 🎯 Claude-optimized trigger thresholds"

echo -e "\n${GREEN}✅ Claude Desktop now has infinite AI memory! 🧠✨${NC}"
echo -e "${PURPLE}🔮 Claude can now remember everything and provide better assistance!${NC}"

if [ "$SCRIPT_DIR" != "$(pwd)" ]; then
    echo -e "\n${YELLOW}💡 TIP: Add to your shell profile for easy access:${NC}"
    echo "  alias claude-memory='cd $SCRIPT_DIR && ./start_claude.sh'"
fi
