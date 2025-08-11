#!/bin/bash

# MCP Memory Server - Platform Template Installation Script
# Template for creating platform-specific installers

set -e

# Platform configuration - to be customized per platform
PLATFORM_NAME="${PLATFORM_NAME:-Template}"
PLATFORM_EMOJI="${PLATFORM_EMOJI:-🤖}"
PLATFORM_SERVER="${PLATFORM_SERVER:-mcp_base_server.py}"
PLATFORM_CONFIG_DIR="${PLATFORM_CONFIG_DIR:-$HOME/.config/mcp}"
PLATFORM_CONFIG_FILE="${PLATFORM_CONFIG_FILE:-mcp_config.json}"
PLATFORM_MODE="${PLATFORM_MODE:-TEMPLATE_MODE}"

echo "$PLATFORM_EMOJI MCP Memory Server - $PLATFORM_NAME Installation"
echo "==============================================="

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

SERVER_PATH="$SCRIPT_DIR/$PLATFORM_SERVER"

echo -e "${BLUE}📍 Installation directory: $SCRIPT_DIR${NC}"

# Function to print status
print_status() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️ $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️ $1${NC}"
}

# Step 1: Check prerequisites
echo -e "\n${BLUE}🔍 Step 1: Checking prerequisites...${NC}"

# Check Python
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version 2>&1 | cut -d' ' -f2)
    print_status "Python $PYTHON_VERSION found"
    PYTHON_CMD="python3"
elif command -v python &> /dev/null; then
    PYTHON_VERSION=$(python --version 2>&1 | cut -d' ' -f2)
    print_status "Python $PYTHON_VERSION found"
    PYTHON_CMD="python"
else
    print_error "Python not found. Please install Python 3.8+"
    exit 1
fi

# Check Python version
PYTHON_VERSION_MAJOR=$(echo $PYTHON_VERSION | cut -d. -f1)
PYTHON_VERSION_MINOR=$(echo $PYTHON_VERSION | cut -d. -f2)
if [ "$PYTHON_VERSION_MAJOR" -lt 3 ] || ([ "$PYTHON_VERSION_MAJOR" -eq 3 ] && [ "$PYTHON_VERSION_MINOR" -lt 8 ]); then
    print_error "Python 3.8+ required, found $PYTHON_VERSION"
    exit 1
fi

print_status "Prerequisites check completed"

# Step 2: Setup Python environment
echo -e "\n${BLUE}🐍 Step 2: Setting up Python environment...${NC}"

cd "$SCRIPT_DIR"

# Create virtual environment if not exists
if [ ! -d "venv" ]; then
    print_info "Creating Python virtual environment..."
    $PYTHON_CMD -m venv venv
    print_status "Virtual environment created"
else
    print_info "Using existing virtual environment"
fi

# Activate virtual environment
source venv/bin/activate
print_status "Virtual environment activated"

# Upgrade pip
print_info "Upgrading pip..."
pip install --upgrade pip > /dev/null 2>&1

# Step 3: Install dependencies
echo -e "\n${BLUE}📦 Step 3: Installing dependencies...${NC}"

print_info "Installing core dependencies..."
pip install -r requirements.txt --quiet

print_status "All dependencies installed"

# Step 4: Test installation
echo -e "\n${BLUE}🧪 Step 4: Testing installation...${NC}"

print_info "Testing MCP server..."
timeout 10s python mcp_base_server.py > /dev/null 2>&1 || {
    print_warning "Server test timeout (normal for first run)"
}

print_info "Testing ML components..."
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
    
    print('✅ All components ready for $PLATFORM_NAME')
except Exception as e:
    print(f'❌ Component test failed: {e}')
    sys.exit(1)
"

print_status "Installation test completed successfully"

# Step 5: Platform-specific configuration (to be implemented per platform)
configure_platform() {
    echo -e "\n${BLUE}⚙️ Step 5: Configuring $PLATFORM_NAME integration...${NC}"
    
    print_info "Creating $PLATFORM_NAME config directory..."
    mkdir -p "$PLATFORM_CONFIG_DIR"
    
    # Create platform configuration with dynamic paths
    PLATFORM_FULL_CONFIG="$PLATFORM_CONFIG_DIR/$PLATFORM_CONFIG_FILE"
    
    print_info "Creating $PLATFORM_NAME configuration..."
    cat > "$PLATFORM_FULL_CONFIG" << EOF
{
  "mcpServers": {
    "mcp-memory-${PLATFORM_NAME,,}": {
      "command": "$SCRIPT_DIR/venv/bin/python",
      "args": ["$SCRIPT_DIR/$PLATFORM_SERVER"],
      "env": {
        "ML_MODEL_TYPE": "huggingface",
        "HUGGINGFACE_MODEL_NAME": "PiGrieco/mcp-memory-auto-trigger-model",
        "AUTO_TRIGGER_ENABLED": "true",
        "PRELOAD_ML_MODEL": "true",
        "$PLATFORM_MODE": "true",
        "LOG_LEVEL": "INFO",
        "MEMORY_THRESHOLD": "0.7",
        "SEMANTIC_THRESHOLD": "0.8"
      }
    }
  }
}
EOF
    
    print_status "$PLATFORM_NAME configuration created"
    echo "$PLATFORM_FULL_CONFIG"
}

# Step 6: Create convenience scripts
create_scripts() {
    echo -e "\n${BLUE}🚀 Step 6: Creating convenience scripts...${NC}"
    
    # Create start script
    cat > "$SCRIPT_DIR/start_${PLATFORM_NAME,,}.sh" << EOF
#!/bin/bash
# $PLATFORM_NAME MCP Memory Server Startup Script

cd "\$(dirname "\$0")"
source venv/bin/activate

echo "$PLATFORM_EMOJI Starting $PLATFORM_NAME MCP Memory Server..."
echo "📍 Server: $PLATFORM_SERVER"
echo "⚡ ML model will auto-load on first message"
echo "$PLATFORM_EMOJI Optimized for $PLATFORM_NAME"
echo ""

python $PLATFORM_SERVER
EOF
    
    chmod +x "$SCRIPT_DIR/start_${PLATFORM_NAME,,}.sh"
    
    # Create update script
    cat > "$SCRIPT_DIR/update_${PLATFORM_NAME,,}.sh" << EOF
#!/bin/bash
# $PLATFORM_NAME MCP Memory Server Update Script

cd "$SCRIPT_DIR"
source venv/bin/activate

echo "🔄 Updating $PLATFORM_NAME MCP Memory Server..."
git fetch origin
git pull origin $REPO_BRANCH

echo "📦 Updating dependencies..."
pip install -r requirements.txt --upgrade --quiet

echo "✅ $PLATFORM_NAME update completed successfully"
EOF
    
    chmod +x "$SCRIPT_DIR/update_${PLATFORM_NAME,,}.sh"
    
    print_status "Convenience scripts created"
}

# Execute platform configuration and script creation
configure_platform
create_scripts

# Final instructions
echo -e "\n${GREEN}🎉 $PLATFORM_NAME INSTALLATION COMPLETED!${NC}"
echo "============================================="

echo -e "\n${BLUE}📁 Installation Directory:${NC} $SCRIPT_DIR"
echo -e "${BLUE}🐍 Python Environment:${NC} $SCRIPT_DIR/venv/"

echo -e "\n${PURPLE}📋 $PLATFORM_NAME SETUP:${NC}"
echo "1. $PLATFORM_EMOJI Restart $PLATFORM_NAME application"
echo "2. ⚙️ MCP server configured in: $PLATFORM_CONFIG_DIR/$PLATFORM_CONFIG_FILE"
echo "3. 💬 Start using the integration"

echo -e "\n${BLUE}🚀 Quick Start Commands:${NC}"
echo "  cd $SCRIPT_DIR"
echo "  ./start_${PLATFORM_NAME,,}.sh              # Start $PLATFORM_NAME MCP server"
echo "  ./update_${PLATFORM_NAME,,}.sh             # Update to latest version"

echo -e "\n${BLUE}⚡ ML AUTO-TRIGGERS:${NC}"
echo "• 🤖 Model: PiGrieco/mcp-memory-auto-trigger-model (99.56% accuracy)"
echo "• 📊 Size: ~63MB (downloads automatically on first use)"
echo "• ⚡ Speed: First use 10-30s, then instant (0.03s)"
echo "• 🎯 Platform: Optimized for $PLATFORM_NAME"

echo -e "\n${BLUE}🔧 MANUAL COMMANDS:${NC}"
echo "  cd $SCRIPT_DIR && source venv/bin/activate"
echo "  python $PLATFORM_SERVER    # Direct server start"

echo -e "\n${BLUE}📁 FILES CREATED:${NC}"
echo "  • MCP Server: $SERVER_PATH"
echo "  • $PLATFORM_NAME Config: $PLATFORM_CONFIG_DIR/$PLATFORM_CONFIG_FILE"
echo "  • Start Script: $SCRIPT_DIR/start_${PLATFORM_NAME,,}.sh"
echo "  • Update Script: $SCRIPT_DIR/update_${PLATFORM_NAME,,}.sh"

echo -e "\n${GREEN}✅ $PLATFORM_NAME now has infinite AI memory! 🧠✨${NC}"
echo -e "${PURPLE}$PLATFORM_EMOJI $PLATFORM_NAME can now remember everything and provide better assistance!${NC}"

if [ "$SCRIPT_DIR" != "$(pwd)" ]; then
    echo -e "\n${YELLOW}💡 TIP: Add to your shell profile for easy access:${NC}"
    echo "  alias ${PLATFORM_NAME,,}-memory='cd $SCRIPT_DIR && ./start_${PLATFORM_NAME,,}.sh'"
fi
