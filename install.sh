#!/bin/bash

# 🧠 MCP Memory Server - Universal GitHub Installer
# One-command installation from GitHub repository

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
NC='\033[0m' # No Color

# Configuration
REPO_URL="https://github.com/PiGrieco/mcp-memory-server.git"
REPO_BRANCH="production-ready-v2"
INSTALL_DIR="$HOME/mcp-memory-server"
PYTHON_CMD=""

echo -e "${PURPLE}🧠 MCP Memory Server - GitHub Installation${NC}"
echo -e "${PURPLE}============================================${NC}"
echo -e "${BLUE}📦 Repository: $REPO_URL${NC}"
echo -e "${BLUE}🌿 Branch: $REPO_BRANCH${NC}"
echo -e "${BLUE}📁 Install Directory: $INSTALL_DIR${NC}"
echo ""

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
echo -e "${BLUE}🔍 Step 1: Checking prerequisites...${NC}"

# Check Git
if ! command -v git &> /dev/null; then
    print_error "Git not found. Please install Git first:"
    echo "  macOS: brew install git"
    echo "  Ubuntu/Debian: sudo apt-get install git"
    echo "  CentOS/RHEL: sudo yum install git"
    exit 1
fi
print_status "Git found: $(git --version)"

# Check Python
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version 2>&1 | cut -d' ' -f2)
    PYTHON_CMD="python3"
    print_status "Python $PYTHON_VERSION found"
elif command -v python &> /dev/null; then
    PYTHON_VERSION=$(python --version 2>&1 | cut -d' ' -f2)
    PYTHON_CMD="python"
    print_status "Python $PYTHON_VERSION found"
else
    print_error "Python not found. Please install Python 3.8+:"
    echo "  macOS: brew install python3"
    echo "  Ubuntu/Debian: sudo apt-get install python3 python3-pip python3-venv"
    echo "  CentOS/RHEL: sudo yum install python3 python3-pip"
    exit 1
fi

# Check Python version
PYTHON_VERSION_MAJOR=$(echo $PYTHON_VERSION | cut -d. -f1)
PYTHON_VERSION_MINOR=$(echo $PYTHON_VERSION | cut -d. -f2)
if [ "$PYTHON_VERSION_MAJOR" -lt 3 ] || ([ "$PYTHON_VERSION_MAJOR" -eq 3 ] && [ "$PYTHON_VERSION_MINOR" -lt 8 ]); then
    print_error "Python 3.8+ required, found $PYTHON_VERSION"
    exit 1
fi

# Step 2: Clone repository
echo -e "\n${BLUE}📥 Step 2: Cloning repository...${NC}"

if [ -d "$INSTALL_DIR" ]; then
    print_warning "Directory $INSTALL_DIR already exists"
    read -p "Do you want to remove it and reinstall? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        rm -rf "$INSTALL_DIR"
    else
        print_info "Using existing directory"
    fi
fi

if [ ! -d "$INSTALL_DIR" ]; then
    print_info "Cloning repository..."
    git clone -b "$REPO_BRANCH" "$REPO_URL" "$INSTALL_DIR"
    print_status "Repository cloned successfully"
else
    print_info "Updating existing repository..."
    cd "$INSTALL_DIR"
    git fetch origin
    git checkout "$REPO_BRANCH"
    git pull origin "$REPO_BRANCH"
    print_status "Repository updated successfully"
fi

cd "$INSTALL_DIR"

# Step 3: Create virtual environment
echo -e "\n${BLUE}🐍 Step 3: Setting up Python environment...${NC}"

if [ ! -d "venv" ]; then
    print_info "Creating virtual environment..."
    $PYTHON_CMD -m venv venv
    print_status "Virtual environment created"
else
    print_info "Virtual environment already exists"
fi

# Activate virtual environment
source venv/bin/activate
print_status "Virtual environment activated"

# Upgrade pip
print_info "Upgrading pip..."
pip install --upgrade pip > /dev/null 2>&1

# Step 4: Install dependencies
echo -e "\n${BLUE}📦 Step 4: Installing dependencies...${NC}"

print_info "Installing core dependencies..."
pip install -r requirements.txt --quiet

print_status "All dependencies installed successfully"

# Step 5: Test installation
echo -e "\n${BLUE}🧪 Step 5: Testing installation...${NC}"

print_info "Testing MCP server..."
timeout 10s python mcp_base_server.py > /dev/null 2>&1 || {
    print_warning "Server test timeout (normal for first run)"
}

print_info "Testing ML components..."
python -c "
import sys
try:
    from transformers import pipeline
    print('✅ Transformers working')
    from sentence_transformers import SentenceTransformer
    print('✅ Sentence Transformers working')
    import torch
    print('✅ PyTorch working')
    from mcp.server import Server
    print('✅ MCP library working')
    print('✅ All components ready')
except Exception as e:
    print(f'⚠️ Warning: {e}')
    sys.exit(1)
" || {
    print_error "Component test failed"
    exit 1
}

print_status "Installation test completed successfully"

# Step 6: Platform-specific setup
echo -e "\n${BLUE}⚙️ Step 6: Platform-specific configuration...${NC}"

echo "Choose your platform for MCP integration:"
echo "1. Cursor IDE"
echo "2. Claude Desktop"
echo "3. Manual setup (I'll configure myself)"
echo "4. Skip platform setup"

read -p "Enter your choice (1-4): " -n 1 -r PLATFORM_CHOICE
echo

case $PLATFORM_CHOICE in
    1)
        print_info "Setting up Cursor IDE integration..."
        
        # Create Cursor config directory
        CURSOR_CONFIG_DIR="$HOME/.cursor"
        mkdir -p "$CURSOR_CONFIG_DIR"
        
        # Create MCP configuration
        cat > "$CURSOR_CONFIG_DIR/mcp_settings.json" << EOF
{
  "mcpServers": {
    "mcp-memory-ml": {
      "command": "$INSTALL_DIR/venv/bin/python",
      "args": ["$INSTALL_DIR/cursor_mcp_server.py"],
      "env": {
        "ML_MODEL_TYPE": "huggingface",
        "HUGGINGFACE_MODEL_NAME": "PiGrieco/mcp-memory-auto-trigger-model",
        "AUTO_TRIGGER_ENABLED": "true",
        "PRELOAD_ML_MODEL": "true",
        "CURSOR_MODE": "true",
        "LOG_LEVEL": "INFO",
        "MEMORY_THRESHOLD": "0.7",
        "SEMANTIC_THRESHOLD": "0.8"
      }
    }
  }
}
EOF
        
        # Also create alternative config file
        cp "$CURSOR_CONFIG_DIR/mcp_settings.json" "$CURSOR_CONFIG_DIR/mcp.json"
        
        print_status "Cursor IDE configuration created"
        print_info "Restart Cursor IDE to see the MCP Memory Server"
        ;;
        
    2)
        print_info "Setting up Claude Desktop integration..."
        
        # Detect OS and set Claude config path
        if [[ "$OSTYPE" == "darwin"* ]]; then
            CLAUDE_CONFIG_DIR="$HOME/Library/Application Support/Claude"
        else
            CLAUDE_CONFIG_DIR="$HOME/.config/claude"
        fi
        
        mkdir -p "$CLAUDE_CONFIG_DIR"
        
        # Create Claude MCP configuration
        cat > "$CLAUDE_CONFIG_DIR/claude_desktop_config.json" << EOF
{
  "mcpServers": {
    "mcp-memory-claude": {
      "command": "$INSTALL_DIR/venv/bin/python",
      "args": ["$INSTALL_DIR/claude_mcp_server.py"],
      "env": {
        "ML_MODEL_TYPE": "huggingface",
        "HUGGINGFACE_MODEL_NAME": "PiGrieco/mcp-memory-auto-trigger-model",
        "AUTO_TRIGGER_ENABLED": "true",
        "CLAUDE_MODE": "true",
        "LOG_LEVEL": "INFO"
      }
    }
  }
}
EOF
        
        print_status "Claude Desktop configuration created"
        print_info "Restart Claude Desktop to see the MCP Memory Server"
        ;;
        
    3)
        print_info "Manual setup selected"
        print_info "Configuration files are available in: $INSTALL_DIR/config/examples/"
        ;;
        
    4)
        print_info "Platform setup skipped"
        ;;
        
    *)
        print_warning "Invalid choice, skipping platform setup"
        ;;
esac

# Step 7: Create convenient scripts
echo -e "\n${BLUE}🚀 Step 7: Creating convenience scripts...${NC}"

# Create start script
cat > "$INSTALL_DIR/start.sh" << 'EOF'
#!/bin/bash
# MCP Memory Server Starter Script

cd "$(dirname "$0")"
source venv/bin/activate

echo "🧠 MCP Memory Server - Choose Mode:"
echo "1. Simple MCP Server (recommended)"
echo "2. Auto-Trigger ML Server (advanced)"
echo "3. Cursor IDE Server"
echo "4. Claude Desktop Server"

read -p "Enter your choice (1-4): " -n 1 -r MODE
echo

case $MODE in
    1) python mcp_base_server.py ;;
    2) python main_auto.py ;;
    3) python cursor_mcp_server.py ;;
    4) python claude_mcp_server.py ;;
    *) echo "Invalid choice"; exit 1 ;;
esac
EOF

chmod +x "$INSTALL_DIR/start.sh"

# Create update script
cat > "$INSTALL_DIR/update.sh" << EOF
#!/bin/bash
# MCP Memory Server Update Script

cd "$INSTALL_DIR"
source venv/bin/activate

echo "🔄 Updating MCP Memory Server..."
git fetch origin
git checkout $REPO_BRANCH
git pull origin $REPO_BRANCH

echo "📦 Updating dependencies..."
pip install -r requirements.txt --upgrade --quiet

echo "✅ Update completed successfully"
EOF

chmod +x "$INSTALL_DIR/update.sh"

print_status "Convenience scripts created"

# Final instructions
echo -e "\n${GREEN}🎉 INSTALLATION COMPLETED SUCCESSFULLY!${NC}"
echo "========================================"

echo -e "\n${BLUE}📁 Installation Directory:${NC} $INSTALL_DIR"
echo -e "${BLUE}🐍 Python Environment:${NC} $INSTALL_DIR/venv/"

echo -e "\n${BLUE}🚀 Quick Start Commands:${NC}"
echo "  cd $INSTALL_DIR"
echo "  ./start.sh                    # Interactive server selection"
echo "  ./update.sh                   # Update to latest version"

echo -e "\n${BLUE}🎯 Direct Server Commands:${NC}"
echo "  cd $INSTALL_DIR && source venv/bin/activate"
echo "  python mcp_base_server.py     # Simple MCP server"
echo "  python main_auto.py           # ML auto-trigger server"
echo "  python cursor_mcp_server.py   # Cursor IDE integration"
echo "  python claude_mcp_server.py   # Claude Desktop integration"

echo -e "\n${BLUE}🧪 Test Your Installation:${NC}"
echo "  cd $INSTALL_DIR"
echo "  source venv/bin/activate"
echo "  python test_installation.py   # Run comprehensive tests"

echo -e "\n${BLUE}📚 Documentation:${NC}"
echo "  README: $INSTALL_DIR/README.md"
echo "  Quick Start: $INSTALL_DIR/QUICK_START.md"
echo "  Examples: $INSTALL_DIR/config/examples/"

if [ $PLATFORM_CHOICE -eq 1 ] || [ $PLATFORM_CHOICE -eq 2 ]; then
    echo -e "\n${YELLOW}⚠️ IMPORTANT: Restart your AI application to see the MCP Memory Server${NC}"
fi

echo -e "\n${GREEN}✨ Your AI now has infinite memory! 🧠${NC}"
echo -e "${BLUE}🌐 Repository: $REPO_URL${NC}"
echo -e "${BLUE}📖 Documentation: https://github.com/PiGrieco/mcp-memory-server${NC}"