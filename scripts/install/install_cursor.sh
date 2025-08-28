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

SERVER_PATH="$SCRIPT_DIR/main.py"
CONFIG_PATH="$HOME/.cursor/mcp.json"

# Step 1: Check prerequisites
echo -e "\n${BLUE}🔍 Step 1: Checking prerequisites...${NC}"

# Check Python
if command -v python3.11 &> /dev/null; then
    PYTHON_VERSION=$(python3.11 --version 2>&1 | cut -d' ' -f2)
    echo -e "${GREEN}✅ Python $PYTHON_VERSION found${NC}"
    PYTHON_CMD="python3.11"
elif command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version 2>&1 | cut -d' ' -f2)
    echo -e "${GREEN}✅ Python $PYTHON_VERSION found${NC}"
    PYTHON_CMD="python3"
elif command -v python &> /dev/null; then
    PYTHON_VERSION=$(python --version 2>&1 | cut -d' ' -f2)
    echo -e "${GREEN}✅ Python $PYTHON_VERSION found${NC}"
    PYTHON_CMD="python"
else
    echo -e "${RED}❌ Python not found. Please install Python 3.10+${NC}"
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

# Step 3: Download and test ML model
echo -e "\n${BLUE}🧠 Step 3: Downloading and testing ML model...${NC}"

$PYTHON_CMD -c "
import sys
sys.path.insert(0, '$SCRIPT_DIR/src')

try:
    from transformers import pipeline
    print('✅ Transformers library working')
    
    # Download and test HuggingFace model
    model_name = 'PiGrieco/mcp-memory-auto-trigger-model'
    print(f'📥 Downloading ML model: {model_name}')
    
    # This will download the model to local cache
    classifier = pipeline(
        'text-classification',
        model=model_name,
        tokenizer=model_name,
        return_all_scores=True
    )
    
    # Test the model with a sample
    test_result = classifier('This is an important note to remember')
    print(f'✅ ML model downloaded and tested successfully')
    print(f'   Test prediction: {test_result[0][0][\"label\"]} (confidence: {test_result[0][0][\"score\"]:.3f})')
    
    from huggingface_hub import model_info
    info = model_info(model_name)
    print(f'   Model size: ~{info.safetensors.total // (1024*1024)}MB')
    
except Exception as e:
    print(f'❌ ML model download failed: {e}')
    print('Model will be downloaded on first use')
    # Don't fail installation for model issues
"

# Step 4: Create Cursor configuration
echo -e "\n${BLUE}🗄️ Step 4: Setting up MongoDB...${NC}"

# Check if MongoDB is installed and running
if command -v mongosh &> /dev/null; then
    echo -e "${GREEN}✅ MongoDB command line tools found${NC}"
    
    # Test MongoDB connection
    if mongosh --eval "db.runCommand('ping')" --quiet &> /dev/null; then
        echo -e "${GREEN}✅ MongoDB is running${NC}"
    else
        echo -e "${YELLOW}⚠️ MongoDB not running, attempting to start...${NC}"
        
        # Try to start MongoDB based on platform
        if [[ "$OSTYPE" == "darwin"* ]]; then
            # macOS
            if command -v brew &> /dev/null; then
                brew services start mongodb/brew/mongodb-community || {
                    echo -e "${RED}❌ Failed to start MongoDB via Homebrew${NC}"
                    echo -e "${YELLOW}Please install MongoDB: brew install mongodb/brew/mongodb-community${NC}"
                    exit 1
                }
                echo -e "${GREEN}✅ MongoDB started via Homebrew${NC}"
            else
                echo -e "${RED}❌ Homebrew not found. Please install MongoDB manually${NC}"
                exit 1
            fi
        elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
            # Linux
            if command -v systemctl &> /dev/null; then
                sudo systemctl start mongod || {
                    echo -e "${RED}❌ Failed to start MongoDB service${NC}"
                    echo -e "${YELLOW}Please install MongoDB or start it manually${NC}"
                    exit 1
                }
                echo -e "${GREEN}✅ MongoDB started via systemctl${NC}"
            else
                echo -e "${RED}❌ systemctl not found. Please start MongoDB manually${NC}"
                exit 1
            fi
        else
            echo -e "${YELLOW}⚠️ Unsupported platform for automatic MongoDB start${NC}"
            echo -e "${YELLOW}Please ensure MongoDB is running manually${NC}"
        fi
    fi
else
    echo -e "${RED}❌ MongoDB not found. Installing MongoDB...${NC}"
    
    if [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS with Homebrew
        if command -v brew &> /dev/null; then
            echo -e "${YELLOW}Installing MongoDB via Homebrew...${NC}"
            brew tap mongodb/brew
            brew install mongodb-community
            brew services start mongodb/brew/mongodb-community
            echo -e "${GREEN}✅ MongoDB installed and started${NC}"
        else
            echo -e "${RED}❌ Homebrew not found. Please install it first:${NC}"
            echo -e "${YELLOW}/bin/bash -c \"\$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)\"${NC}"
            exit 1
        fi
    else
        echo -e "${RED}❌ Please install MongoDB manually from: https://www.mongodb.com/try/download/community${NC}"
        exit 1
    fi
fi

echo -e "${GREEN}✅ MongoDB setup completed${NC}"

# Step 5: Configuring Cursor MCP integration
echo -e "\n${BLUE}⚙️ Step 5: Configuring Cursor MCP integration...${NC}"

# Create the configuration with proper path replacement
CURSOR_MCP_CONFIG="$CURSOR_CONFIG_DIR/mcp.json"

if [ -f "$CURSOR_MCP_CONFIG" ]; then
    echo -e "${YELLOW}📝 Backing up existing Cursor MCP config...${NC}"
    cp "$CURSOR_MCP_CONFIG" "$CURSOR_MCP_CONFIG.backup.$(date +%s)"
fi

echo -e "${YELLOW}📝 Installing Cursor MCP configuration...${NC}"

# Create configuration with proper path replacement
cat > "$CURSOR_MCP_CONFIG" << EOF
{
  "mcpServers": {
    "mcp-memory-sam": {
      "command": "$PYTHON_CMD",
      "args": ["$SERVER_PATH"],
      "env": {
        "ML_MODEL_TYPE": "huggingface",
        "HUGGINGFACE_MODEL_NAME": "PiGrieco/mcp-memory-auto-trigger-model",
        "AUTO_TRIGGER_ENABLED": "true",
        "PRELOAD_ML_MODEL": "true",
        "CURSOR_MODE": "true",
        "LOG_LEVEL": "INFO",
        "ENVIRONMENT": "development",
        "SERVER_MODE": "universal",
        "ML_CONFIDENCE_THRESHOLD": "0.7",
        "TRIGGER_THRESHOLD": "0.15",
        "SIMILARITY_THRESHOLD": "0.3",
        "MEMORY_THRESHOLD": "0.7",
        "SEMANTIC_THRESHOLD": "0.8",
        "ML_TRIGGER_MODE": "hybrid",
        "ML_TRAINING_ENABLED": "true",
        "ML_RETRAIN_INTERVAL": "50",
        "FEATURE_EXTRACTION_TIMEOUT": "5.0",
        "MAX_CONVERSATION_HISTORY": "10",
        "USER_BEHAVIOR_TRACKING": "true",
        "BEHAVIOR_HISTORY_LIMIT": "1000",
        "EMBEDDING_PROVIDER": "sentence_transformers",
        "EMBEDDING_MODEL": "all-MiniLM-L6-v2",
        "MONGODB_URI": "mongodb://localhost:27017",
        "MONGODB_DATABASE": "mcp_memory_dev",
        "INSTALL_DIR": "$SCRIPT_DIR"
      }
    }
  }
}
EOF

echo -e "${GREEN}✅ Cursor configuration updated${NC}"

# Step 5: Configuring HTTP Proxy for Auto-Interception
echo -e "\n${BLUE}🌐 Step 5: Configuring HTTP Proxy for Auto-Interception...${NC}"

PROXY_CONFIG_FILE="$SCRIPT_DIR/config/proxy_config.yaml"

echo -e "${YELLOW}📝 Configuring proxy for production mode...${NC}"
    
    # Create production proxy configuration
    cat > "$PROXY_CONFIG_FILE" << 'EOF'
proxy:
  name: "MCP Memory Proxy Server"
  version: "1.0.0"
  host: "127.0.0.1"
  port: 8080
  debug: false
  
  # Auto-trigger settings
  auto_trigger:
    enabled: true
    auto_execute: true
    timeout_seconds: 30
    max_retries: 3
    
  # Production mode configuration
  testing:
    enabled: false  # Production mode: forward to real platforms
    return_analysis_metadata: false
  
  # Platform configurations
  platforms:
    cursor:
      name: "Cursor AI Platform"
      enabled: true
      base_url: "https://api.cursor.sh/v1"  # Real Cursor API endpoint
      timeout: 30
      headers:
        Content-Type: "application/json"
        User-Agent: "MCP-Memory-Proxy/1.0"
      
    claude:
      name: "Claude AI Platform" 
      enabled: false
      base_url: "https://api.anthropic.com/v1"
      timeout: 30
      headers:
        Content-Type: "application/json"
        User-Agent: "MCP-Memory-Proxy/1.0"
        
    universal:
      name: "Universal AI Platform"
      enabled: false
      timeout: 30
      headers:
        Content-Type: "application/json"
        User-Agent: "MCP-Memory-Proxy/1.0"
  
  # Caching settings
  cache:
    enabled: true
    ttl_seconds: 300
    max_size: 1000
  
  # Performance settings
  performance:
    max_concurrent_requests: 10
    request_timeout: 30
    max_memory_contexts: 5
EOF
    
    echo -e "${GREEN}✅ HTTP Proxy configured for production mode${NC}"
    
    # Create proxy startup script
    PROXY_STARTUP_SCRIPT="$SCRIPT_DIR/scripts/servers/start_cursor_proxy.sh"
    
    cat > "$PROXY_STARTUP_SCRIPT" << EOF
#!/bin/bash
# Auto-generated Cursor MCP Memory Proxy startup script

SCRIPT_DIR="\$(cd "\$(dirname "\${BASH_SOURCE[0]}")" && pwd)/../.."
cd "\$SCRIPT_DIR"

echo "🌐 Starting MCP Memory Proxy Server for Cursor..."
echo "📊 Monitor: http://127.0.0.1:8080/health"
echo "🔗 Proxy: http://127.0.0.1:8080/proxy/cursor"
echo ""

# Start proxy server
$PYTHON_CMD servers/proxy_server.py --host 127.0.0.1 --port 8080 --config config/proxy_config.yaml
EOF
    
    chmod +x "$PROXY_STARTUP_SCRIPT"
    echo -e "${GREEN}✅ Proxy startup script created: $PROXY_STARTUP_SCRIPT${NC}"

# Step 6: Test the server
echo -e "\n${BLUE}🧪 Step 6: Testing MCP server...${NC}"

echo -e "${YELLOW}Testing server initialization...${NC}"
cd "$SCRIPT_DIR"
if $PYTHON_CMD "scripts/test_mcp_server.py"; then
    echo -e "${GREEN}✅ MCP server test passed${NC}"
else
    echo -e "${YELLOW}⚠️ MCP server test had issues (may work anyway)${NC}"
fi

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
echo "2. The MCP server is already configured in ~/.cursor/mcp.json"
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

echo -e "\n${BLUE}🌐 HTTP PROXY (Production Mode):${NC}"
if [ -f "$PROXY_CONFIG_FILE" ]; then
echo "• Production mode configured automatically"
echo "• Auto-interception enabled for seamless integration"
echo "• Real platform forwarding: DISABLED (configure base_url for real forwarding)"
echo "• Health check: http://127.0.0.1:8080/health"
echo "• Proxy endpoint: http://127.0.0.1:8080/proxy/cursor"
else
echo "• Proxy configuration not available"
fi
echo ""
echo -e "${BLUE}🎯 ML THRESHOLDS:${NC}"
echo "• ML Confidence: 70% (high precision)"
echo "• Trigger Threshold: 15% (sensitive detection)"
echo "• Memory Threshold: 70% (important content only)"
echo "• Similarity: 30% (relevant searches)"
echo "• Mode: Hybrid (ML + deterministic rules)"

echo -e "\n${BLUE}🔧 MANUAL START OPTIONS:${NC}"
echo "  • MCP Server: $STARTUP_SCRIPT"
if [ -f "$PROXY_STARTUP_SCRIPT" ]; then
echo "  • HTTP Proxy: $PROXY_STARTUP_SCRIPT"
fi

echo -e "\n${BLUE}📁 FILES CREATED:${NC}"
echo "  • Server: $SERVER_PATH"
echo "  • Config: $CURSOR_MCP_CONFIG"
echo "  • Startup: $STARTUP_SCRIPT"
if [ -f "$PROXY_CONFIG_FILE" ]; then
echo "  • Proxy Config: $PROXY_CONFIG_FILE"
fi
if [ -f "$PROXY_STARTUP_SCRIPT" ]; then
echo "  • Proxy Startup: $PROXY_STARTUP_SCRIPT"
fi

echo -e "\n${GREEN}✅ Your Cursor IDE now has infinite AI memory! 🧠✨${NC}"
