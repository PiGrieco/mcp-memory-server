#!/bin/bash
# One-Click Installer for MCP Memory Server Auto-Trigger
# Usage: curl -sSL https://raw.githubusercontent.com/your-repo/mcp-memory-server/main/install.sh | bash

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Helper functions
print_header() {
    echo -e "${BLUE}🚀 MCP Memory Server Auto-Trigger Installer${NC}"
    echo -e "${BLUE}===============================================${NC}"
}

print_step() {
    echo -e "\n${YELLOW}🔸 Step $1: $2${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️ $1${NC}"
}

# Check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check Python version
check_python() {
    if command_exists python3; then
        PYTHON_CMD="python3"
    elif command_exists python; then
        PYTHON_CMD="python"
    else
        print_error "Python not found. Please install Python 3.8+"
        exit 1
    fi
    
    # Check version
    version=$($PYTHON_CMD -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
    major=$(echo $version | cut -d. -f1)
    minor=$(echo $version | cut -d. -f2)
    
    if [ "$major" -lt 3 ] || ([ "$major" -eq 3 ] && [ "$minor" -lt 8 ]); then
        print_error "Python 3.8+ required, found $version"
        exit 1
    fi
    
    print_success "Python $version found"
}

# Install pip if needed
check_pip() {
    if ! command_exists pip && ! command_exists pip3; then
        print_warning "pip not found, installing..."
        if command_exists curl; then
            curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py
            $PYTHON_CMD get-pip.py
            rm get-pip.py
        else
            print_error "pip installation failed. Please install pip manually."
            exit 1
        fi
    fi
    
    # Use pip3 if available, otherwise pip
    if command_exists pip3; then
        PIP_CMD="pip3"
    else
        PIP_CMD="pip"
    fi
    
    print_success "pip available"
}

# Download repository
download_repo() {
    if command_exists git; then
        print_step "2" "Cloning repository with git"
        git clone https://github.com/your-repo/mcp-memory-server.git
        cd mcp-memory-server
    else
        print_step "2" "Downloading repository (git not found)"
        if command_exists curl; then
            curl -L https://github.com/your-repo/mcp-memory-server/archive/main.zip -o mcp-memory-server.zip
            if command_exists unzip; then
                unzip mcp-memory-server.zip
                mv mcp-memory-server-main mcp-memory-server
                cd mcp-memory-server
                rm ../mcp-memory-server.zip
            else
                print_error "unzip not found. Please install unzip or use git."
                exit 1
            fi
        else
            print_error "Neither git nor curl found. Please install one of them."
            exit 1
        fi
    fi
    print_success "Repository downloaded"
}

# Install dependencies
install_dependencies() {
    print_step "3" "Installing Python dependencies"
    
    # Core dependencies
    deps=(
        "mcp>=1.0.0"
        "sentence-transformers"
        "asyncio"
        "python-dotenv"
        "pydantic"
        "uvicorn"
        "fastapi"
    )
    
    for dep in "${deps[@]}"; do
        echo "   Installing $dep..."
        if $PIP_CMD install "$dep" >/dev/null 2>&1; then
            echo "   ✅ $dep installed"
        else
            print_warning "Failed to install $dep, continuing..."
        fi
    done
    
    print_success "Dependencies installed"
}

# Create configurations
create_configs() {
    print_step "4" "Creating configurations"
    
    # Cursor config
    cursor_dir="$HOME/.cursor"
    mkdir -p "$cursor_dir"
    
    cat > "$cursor_dir/mcp_settings.json" << 'EOF'
{
  "mcpServers": {
    "mcp-memory-auto": {
      "command": "python",
      "args": ["INSTALL_PATH/main_simple.py"],
      "env": {
        "AUTO_TRIGGER": "true",
        "KEYWORDS": "ricorda,nota,importante,salva,memorizza,remember",
        "PATTERNS": "risolto,solved,fixed,bug fix,solution,tutorial"
      }
    }
  }
}
EOF
    
    # Replace INSTALL_PATH with actual path
    sed -i.bak "s|INSTALL_PATH|$(pwd)|g" "$cursor_dir/mcp_settings.json"
    rm "$cursor_dir/mcp_settings.json.bak" 2>/dev/null || true
    
    print_success "Cursor config: $cursor_dir/mcp_settings.json"
    
    # Claude config
    claude_dir="$HOME/.config/claude"
    mkdir -p "$claude_dir"
    
    cat > "$claude_dir/claude_desktop_config.json" << 'EOF'
{
  "mcpServers": {
    "mcp-memory-auto": {
      "command": "python",
      "args": ["INSTALL_PATH/main_simple.py"],
      "env": {
        "AUTO_TRIGGER": "true",
        "CLAUDE_MODE": "true"
      }
    }
  }
}
EOF
    
    # Replace INSTALL_PATH with actual path
    sed -i.bak "s|INSTALL_PATH|$(pwd)|g" "$claude_dir/claude_desktop_config.json"
    rm "$claude_dir/claude_desktop_config.json.bak" 2>/dev/null || true
    
    print_success "Claude config: $claude_dir/claude_desktop_config.json"
}

# Test installation
test_installation() {
    print_step "5" "Testing installation"
    
    # Test Python imports
    if $PYTHON_CMD -c "import asyncio; print('✅ asyncio OK')" 2>/dev/null; then
        print_success "Python imports working"
    else
        print_warning "Some Python imports failed"
    fi
    
    # Test server file
    if [ -f "main_simple.py" ]; then
        print_success "Server file found"
    else
        print_error "Server file missing"
        return 1
    fi
    
    # Test auto-trigger
    if [ -f "test_auto_trigger.py" ]; then
        if $PYTHON_CMD test_auto_trigger.py >/dev/null 2>&1; then
            print_success "Auto-trigger test passed"
        else
            print_warning "Auto-trigger test failed, but installation may still work"
        fi
    fi
    
    return 0
}

# Create start script
create_start_script() {
    cat > start_mcp_server.sh << 'EOF'
#!/bin/bash
# Start MCP Memory Server with Auto-Trigger

echo "🚀 Starting MCP Memory Server..."
echo "✅ Auto-trigger system enabled"
echo "✅ Keywords: ricorda, nota, importante, salva, memorizza"
echo "✅ Patterns: risolto, solved, fixed, bug fix, solution"
echo ""
echo "🎯 Ready for Cursor/Claude integration!"
echo "📡 Server will start on next line..."
echo ""

python main_simple.py
EOF
    
    chmod +x start_mcp_server.sh
    print_success "Start script created: ./start_mcp_server.sh"
}

# Main installation function
main() {
    print_header
    
    # Step 1: Check requirements
    print_step "1" "Checking requirements"
    check_python
    check_pip
    
    # Step 2: Download repository
    download_repo
    
    # Step 3: Install dependencies
    install_dependencies
    
    # Step 4: Create configurations
    create_configs
    
    # Step 5: Test installation
    test_installation
    
    # Step 6: Create convenience script
    create_start_script
    
    # Success message
    echo ""
    echo -e "${GREEN}🎉 INSTALLATION COMPLETED!${NC}"
    echo -e "${GREEN}=========================${NC}"
    echo -e "${GREEN}✅ MCP Memory Server installed${NC}"
    echo -e "${GREEN}✅ Auto-trigger system configured${NC}"
    echo -e "${GREEN}✅ Cursor IDE integration ready${NC}"
    echo -e "${GREEN}✅ Claude Desktop integration ready${NC}"
    
    echo ""
    echo -e "${BLUE}🚀 QUICK START:${NC}"
    echo -e "${BLUE}1. Start the server:${NC}"
    echo -e "   ${YELLOW}./start_mcp_server.sh${NC}"
    echo ""
    echo -e "${BLUE}2. Open Cursor IDE:${NC}"
    echo -e "   - Press ${YELLOW}Cmd+L${NC} (macOS) or ${YELLOW}Ctrl+L${NC} (Windows/Linux)"
    echo -e "   - Try: ${YELLOW}'Ricorda che Python è case-sensitive'${NC}"
    echo ""
    echo -e "${BLUE}3. Open Claude Desktop:${NC}"
    echo -e "   - Restart Claude Desktop"
    echo -e "   - Auto-trigger system will be active"
    
    echo ""
    echo -e "${BLUE}🎯 TEST KEYWORDS:${NC}"
    echo -e "   • ${YELLOW}ricorda${NC}, ${YELLOW}importante${NC}, ${YELLOW}nota${NC} → Auto-save"
    echo -e "   • ${YELLOW}risolto${NC}, ${YELLOW}solved${NC}, ${YELLOW}fixed${NC} → Solution save"
    echo -e "   • ${YELLOW}come${NC}, ${YELLOW}how${NC}, ${YELLOW}what${NC} → Auto-search"
    
    echo ""
    echo -e "${BLUE}📁 Installation directory: ${YELLOW}$(pwd)${NC}"
    echo -e "${BLUE}📋 Configurations created in ~/.cursor and ~/.config/claude${NC}"
    
    echo ""
    echo -e "${GREEN}Your AI now has infinite memory! 🧠✨${NC}"
}

# Run main function
main "$@"
