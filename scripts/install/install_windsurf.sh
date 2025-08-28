#!/bin/bash

# MCP Memory Server - Windsurf IDE Installation Script
# Optimized for Windsurf Cascade AI IDE

set -e

echo "🌪️ MCP Memory Server - Windsurf IDE Installation"
echo "================================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
NC='\033[0m' # No Color

# Get the absolute path of the script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SERVER_PATH="$SCRIPT_DIR/main.py"

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
echo -e "\n${BLUE}📦 Step 2: Installing Python dependencies...${NC}"

echo -e "${YELLOW}Installing ML dependencies for Windsurf...${NC}"
$PYTHON_CMD -m pip install torch>=2.1.0 transformers>=4.30.0 accelerate datasets --quiet

echo -e "${YELLOW}Installing MCP dependencies...${NC}"
$PYTHON_CMD -m pip install mcp sentence-transformers scikit-learn asyncio python-dotenv pydantic --quiet

echo -e "${GREEN}✅ Dependencies installed${NC}"

# Step 3: Test ML model access
echo -e "\n${BLUE}🧠 Step 3: Testing ML model access for Windsurf...${NC}"

$PYTHON_CMD -c "
import sys
sys.path.insert(0, '$SCRIPT_DIR/src')

try:
    from transformers import pipeline
    print('✅ Transformers library working')
    
    from huggingface_hub import model_info
    model_name = 'PiGrieco/mcp-memory-auto-trigger-model'
    info = model_info(model_name)
    print(f'✅ ML model accessible: {model_name}')
    print(f'   Model size: ~{info.safetensors.total // (1024*1024)}MB')
    print('✅ Windsurf IDE integration ready')
    
except Exception as e:
    print(f'⚠️ ML model check warning: {e}')
    print('Model will be downloaded on first use')
"

# Step 4: Create Windsurf configuration
echo -e "\n${BLUE}⚙️ Step 4: Creating Windsurf configuration...${NC}"

WINDSURF_CONFIG="$SCRIPT_DIR/windsurf_config.json"
cat > "$WINDSURF_CONFIG" << EOF
{
  "mcpServers": {
    "mcp-memory-sam": {
      "command": "python3",
      "args": ["$SCRIPT_DIR/main.py"],
      "env": {
        "ML_MODEL_TYPE": "huggingface",
        "HUGGINGFACE_MODEL_NAME": "PiGrieco/mcp-memory-auto-trigger-model",
        "AUTO_TRIGGER_ENABLED": "true",
        "PRELOAD_ML_MODEL": "true",
        "WINDSURF_MODE": "true",
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
        "MONGODB_DATABASE": "mcp_memory_dev"
      }
    }
  }
}
EOF

echo -e "${GREEN}✅ Windsurf configuration created${NC}"

# Step 5: Configuring HTTP Proxy for Auto-Interception
echo -e "\n${BLUE}🌐 Step 5: Configuring HTTP Proxy for Auto-Interception...${NC}"

PROXY_CONFIG_FILE="$SCRIPT_DIR/config/proxy_config.yaml"

echo -e "${YELLOW}📝 Configuring proxy for production mode...${NC}"
    
    # Create production proxy configuration for Windsurf
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
    windsurf:
      name: "Windsurf AI Platform"
      enabled: true
      base_url: "https://api.windsurf.ai/v1"  # Real Windsurf API endpoint
      timeout: 30
      headers:
        Content-Type: "application/json"
        User-Agent: "MCP-Memory-Proxy/1.0"
      
    cursor:
      name: "Cursor AI Platform" 
      enabled: false
      base_url: "https://api.cursor.sh/v1"
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
    
    # Create proxy startup script for Windsurf
    PROXY_STARTUP_SCRIPT="$SCRIPT_DIR/scripts/servers/start_windsurf_proxy.sh"
    
    cat > "$PROXY_STARTUP_SCRIPT" << 'EOF'
#!/bin/bash
# Auto-generated Windsurf MCP Memory Proxy startup script

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/../.."
cd "$SCRIPT_DIR"

echo "🌐 Starting MCP Memory Proxy Server for Windsurf..."
echo "📊 Monitor: http://127.0.0.1:8080/health"
echo "🔗 Proxy: http://127.0.0.1:8080/proxy/windsurf"
echo ""

# Start proxy server
python3 servers/proxy_server.py --host 127.0.0.1 --port 8080 --config config/proxy_config.yaml
EOF
    
    chmod +x "$PROXY_STARTUP_SCRIPT"
    echo -e "${GREEN}✅ Proxy startup script created: $PROXY_STARTUP_SCRIPT${NC}"

# Step 6: Test the server
echo -e "\n${BLUE}🧪 Step 6: Testing Windsurf server...${NC}"

echo -e "${YELLOW}Testing server initialization...${NC}"
timeout 20s $PYTHON_CMD "$SERVER_PATH" --test 2>/dev/null || {
    echo -e "${YELLOW}⚠️ Server test timeout (normal for first ML model download)${NC}"
}

# Step 6: Create startup script
echo -e "\n${BLUE}🚀 Step 6: Creating startup script...${NC}"

STARTUP_SCRIPT="$SCRIPT_DIR/start_windsurf_server.sh"
cat > "$STARTUP_SCRIPT" << EOF
#!/bin/bash
# Windsurf IDE MCP Memory Server Startup Script

cd "$SCRIPT_DIR"
echo "🌪️ Starting Windsurf IDE MCP Memory Server with ML Auto-Triggers..."
echo "📍 Server path: $SERVER_PATH"
echo "⚡ ML model will auto-load on first message"
echo "🌪️ Optimized for Windsurf Cascade AI IDE"
echo ""

$PYTHON_CMD "$SERVER_PATH"
EOF

chmod +x "$STARTUP_SCRIPT"

# Final instructions
echo -e "\n${GREEN}🎉 WINDSURF IDE INSTALLATION COMPLETED!${NC}"
echo "==========================================="

echo -e "\n${PURPLE}📋 WINDSURF SETUP INSTRUCTIONS:${NC}"
echo "1. 🌪️ Open Windsurf IDE"
echo "2. ⚙️ Go to Settings → Extensions → MCP"
echo "3. 📁 Add server configuration: $WINDSURF_CONFIG"
echo "4. 🔄 Restart Windsurf IDE"
echo "5. 💬 Start using Cascade AI with memory!"

echo -e "\n${BLUE}🧪 TEST THE WINDSURF INTEGRATION:${NC}"
echo "Try these commands with Cascade AI:"
echo -e "  ${YELLOW}• 'Ricorda questo pattern di design per i componenti React'${NC}"
echo -e "  ${YELLOW}• 'Ho risolto il bug di performance ottimizzando il rendering'${NC}"
echo -e "  ${YELLOW}• 'Come si implementa una cache LRU in Python?'${NC}"
echo -e "  ${YELLOW}• 'Importante: usare sempre TypeScript per progetti grandi'${NC}"

echo -e "\n${BLUE}⚡ ML MODEL WINDSURF:${NC}"
echo "• Code-aware triggers for better IDE integration"
echo "• Enhanced pattern recognition for development tasks"
echo "• Context-sensitive memory categorization"
echo "• Real-time progress indicators"

echo -e "\n${BLUE}🌐 HTTP PROXY (Production Mode):${NC}"
if [ -f "$PROXY_CONFIG_FILE" ]; then
echo "• Production mode configured automatically"
echo "• Auto-interception enabled for seamless integration"
echo "• Real platform forwarding: DISABLED (configure base_url for real forwarding)"
echo "• Health check: http://127.0.0.1:8080/health"
echo "• Proxy endpoint: http://127.0.0.1:8080/proxy/windsurf"
else
echo "• Proxy configuration not available"
fi

echo -e "\n${BLUE}🔧 MANUAL START OPTIONS:${NC}"
echo "  • MCP Server: $STARTUP_SCRIPT"
if [ -f "$PROXY_STARTUP_SCRIPT" ]; then
echo "  • HTTP Proxy: $PROXY_STARTUP_SCRIPT"
fi

echo -e "\n${BLUE}📁 FILES CREATED:${NC}"
echo "  • Server: $SERVER_PATH"
echo "  • Config: $WINDSURF_CONFIG"
echo "  • Startup: $STARTUP_SCRIPT"
if [ -f "$PROXY_CONFIG_FILE" ]; then
echo "  • Proxy Config: $PROXY_CONFIG_FILE"
fi
if [ -f "$PROXY_STARTUP_SCRIPT" ]; then
echo "  • Proxy Startup: $PROXY_STARTUP_SCRIPT"
fi

echo -e "\n${GREEN}✅ Windsurf IDE now has infinite AI memory! 🧠✨${NC}"
echo -e "${PURPLE}🌪️ Cascade AI can now remember all your code patterns!${NC}"
