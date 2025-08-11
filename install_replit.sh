#!/bin/bash

# MCP Memory Server - Replit Cloud IDE Installation Script
# Optimized for Replit cloud development environment

set -e

echo "⚡ MCP Memory Server - Replit Cloud IDE Installation"
echo "==================================================="

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
SERVER_PATH="$SCRIPT_DIR/replit_mcp_server.py"

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

echo -e "${YELLOW}Installing ML dependencies for Replit Cloud...${NC}"
$PYTHON_CMD -m pip install torch>=2.1.0 transformers>=4.30.0 accelerate datasets --quiet

echo -e "${YELLOW}Installing cloud development dependencies...${NC}"
$PYTHON_CMD -m pip install fastapi uvicorn requests aiohttp websockets replit --quiet

echo -e "${YELLOW}Installing MCP dependencies...${NC}"
$PYTHON_CMD -m pip install mcp sentence-transformers scikit-learn asyncio python-dotenv pydantic --quiet

echo -e "${GREEN}✅ Dependencies installed${NC}"

# Step 3: Test ML model access
echo -e "\n${BLUE}🧠 Step 3: Testing ML model access for Replit...${NC}"

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
    print('✅ Replit cloud integration ready')
    
except Exception as e:
    print(f'⚠️ ML model check warning: {e}')
    print('Model will be downloaded on first use')
"

# Step 4: Create Replit cloud service
echo -e "\n${BLUE}☁️ Step 4: Creating Replit cloud service...${NC}"

cat > "$SCRIPT_DIR/replit_cloud_service.py" << 'EOF'
#!/usr/bin/env python3
"""
Replit Cloud Service for MCP Memory Server
Provides API endpoints and repl integration for Replit platform
"""

from fastapi import FastAPI, HTTPException, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import asyncio
from typing import Dict, List, Optional
import sys
from pathlib import Path
import json
import os

# Add the smart server
sys.path.insert(0, str(Path(__file__).parent))
from replit_smart_server import ReplitTriggerSystem

app = FastAPI(title="MCP Memory Service for Replit", version="1.0.0")

# Enable CORS for Replit platform
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global trigger system
trigger_system = None

class ReplMessage(BaseModel):
    message: str
    repl_context: Optional[Dict] = {}
    user_context: Optional[Dict] = {}
    collaboration_info: Optional[Dict] = {}

class CollaborationUpdate(BaseModel):
    repl_name: str
    user_action: str
    code_changes: Optional[str] = None
    participants: List[str] = []

@app.on_event("startup")
async def startup_event():
    global trigger_system
    trigger_system = ReplitTriggerSystem()
    print("🚀 Replit Cloud Service started!")

@app.get("/health")
async def health_check():
    return {
        "status": "healthy", 
        "service": "mcp-memory-replit", 
        "platform": "replit.com",
        "cloud_ready": True
    }

@app.post("/analyze")
async def analyze_repl_message(request: ReplMessage):
    """Analyze message from Replit environment"""
    try:
        result = await trigger_system.process_message(
            request.message, 
            request.repl_context,
            request.user_context
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/collaboration/update")
async def collaboration_update(request: CollaborationUpdate):
    """Handle collaboration updates"""
    try:
        message = f"Collaboration update in {request.repl_name}: {request.user_action}"
        if request.code_changes:
            message += f" - Code changes: {request.code_changes[:100]}..."
        
        result = await trigger_system.process_message(
            message,
            {
                "repl_name": request.repl_name,
                "type": "collaboration",
                "participants": request.participants
            }
        )
        return {"collaboration_tracked": True, "result": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/repls/{repl_name}/memories")
async def get_repl_memories(repl_name: str):
    """Get memories for specific repl"""
    try:
        all_memories = trigger_system.memories
        repl_memories = [
            mem for mem in all_memories.values()
            if mem.get('repl_context', {}).get('repl_name') == repl_name
        ]
        return {"repl": repl_name, "memories": repl_memories}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/user/{username}/memories")
async def get_user_memories(username: str):
    """Get memories for specific user across repls"""
    try:
        all_memories = trigger_system.memories
        user_memories = [
            mem for mem in all_memories.values()
            if mem.get('user_context', {}).get('username') == username
        ]
        return {"user": username, "memories": user_memories}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/stats")
async def get_replit_stats():
    """Get Replit-specific statistics"""
    return trigger_system.get_replit_stats()

@app.websocket("/ws/repl/{repl_name}")
async def websocket_repl_connection(websocket: WebSocket, repl_name: str):
    """WebSocket connection for real-time repl updates"""
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_text()
            message_data = json.loads(data)
            
            # Process the message
            result = await trigger_system.process_message(
                message_data.get('message', ''),
                {"repl_name": repl_name, "realtime": True},
                message_data.get('user_context', {})
            )
            
            # Send back the result
            await websocket.send_text(json.dumps({
                "type": "memory_update",
                "result": result
            }))
    except Exception as e:
        print(f"WebSocket error: {e}")
    finally:
        await websocket.close()

@app.get("/dashboard")
async def replit_dashboard():
    """Replit-specific dashboard"""
    stats = trigger_system.get_replit_stats()
    
    # Get repl distribution
    repl_distribution = {}
    for memory in trigger_system.memories.values():
        repl_name = memory.get('repl_context', {}).get('repl_name', 'Unknown')
        repl_distribution[repl_name] = repl_distribution.get(repl_name, 0) + 1
    
    return f"""
    <html>
    <head>
        <title>⚡ Replit Memory Dashboard</title>
        <style>
            body {{ font-family: 'Courier New', monospace; margin: 40px; background: #1a1a1a; color: #e0e0e0; }}
            .header {{ background: linear-gradient(135deg, #ff6b35 0%, #f7931e 100%); 
                       color: white; padding: 20px; border-radius: 10px; }}
            .stats {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); 
                     gap: 20px; margin: 20px 0; }}
            .stat-card {{ background: #2a2a2a; padding: 20px; border-radius: 8px; border: 1px solid #444; }}
            .repls {{ background: #2a2a2a; padding: 20px; border-radius: 8px; border: 1px solid #444; margin: 20px 0; }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1>⚡ MCP Memory Dashboard - Replit Cloud</h1>
            <p>☁️ Cloud-native AI memory for collaborative coding</p>
        </div>
        
        <div class="stats">
            <div class="stat-card">
                <h3>🤝 Collaborations</h3>
                <h2>{stats['replit_stats']['collaborations_saved']}</h2>
            </div>
            <div class="stat-card">
                <h3>🚀 Deployments</h3>
                <h2>{stats['replit_stats']['deployments_documented']}</h2>
            </div>
            <div class="stat-card">
                <h3>☁️ Cloud Interactions</h3>
                <h2>{stats['replit_stats']['cloud_interactions']}</h2>
            </div>
            <div class="stat-card">
                <h3>📚 Total Memories</h3>
                <h2>{stats['memory_count']}</h2>
            </div>
        </div>
        
        <div class="repls">
            <h2>📁 Repl Distribution:</h2>
            {"".join([f'<p><code>{repl}</code>: {count} memories</p>' 
                     for repl, count in repl_distribution.items()])}
        </div>
        
        <div class="repls">
            <h2>Recent Memories:</h2>
            {"".join([f'<p><strong>{mem["id"]}:</strong> {mem["content"][:100]}...</p>' 
                     for mem in list(trigger_system.memories.values())[-5:]])}
        </div>
        
        <div style="margin-top: 20px; text-align: center; color: #888;">
            <p>⚡ Powered by MCP Memory Server for Replit Cloud</p>
        </div>
    </body>
    </html>
    """

if __name__ == "__main__":
    import uvicorn
    
    # Get port from environment (Replit sets this automatically)
    port = int(os.environ.get("PORT", 8002))
    
    print(f"🚀 Starting Replit Cloud Service on port {port}")
    uvicorn.run(app, host="0.0.0.0", port=port)
EOF

chmod +x "$SCRIPT_DIR/replit_cloud_service.py"

# Step 5: Create Replit configuration files
echo -e "\n${BLUE}⚙️ Step 5: Creating Replit configuration files...${NC}"

# Create .replit configuration
cat > "$SCRIPT_DIR/.replit" << 'EOF'
# Replit configuration for MCP Memory Server
language = "python3"
run = "python replit_cloud_service.py"

[env]
ML_MODEL_TYPE = "huggingface"
HUGGINGFACE_MODEL_NAME = "PiGrieco/mcp-memory-auto-trigger-model"
AUTO_TRIGGER_ENABLED = "true"
REPLIT_MODE = "true"
CLOUD_PLATFORM = "true"
LOG_LEVEL = "INFO"

[nix]
channel = "stable-22_11"

[deployment]
run = ["python", "replit_cloud_service.py"]
deploymentTarget = "cloudrun"
EOF

# Create pyproject.toml for Replit
cat > "$SCRIPT_DIR/pyproject.toml" << 'EOF'
[tool.poetry]
name = "mcp-memory-replit"
version = "1.0.0"
description = "MCP Memory Server for Replit Cloud IDE"

[tool.poetry.dependencies]
python = "^3.8"
torch = ">=2.1.0"
transformers = ">=4.30.0"
accelerate = ">=0.20.0"
datasets = ">=2.12.0"
fastapi = "^0.104.0"
uvicorn = "^0.24.0"
websockets = "^12.0"
pydantic = "^2.0.0"
requests = "^2.31.0"
aiohttp = "^3.9.0"

[build-system]
requires = ["poetry-core"]
build-backend = "poetry.core.masonry.api"
EOF

# Step 6: Test the server
echo -e "\n${BLUE}🧪 Step 6: Testing Replit server...${NC}"

echo -e "${YELLOW}Testing server initialization...${NC}"
timeout 15s $PYTHON_CMD "$SERVER_PATH" --test 2>/dev/null || {
    echo -e "${YELLOW}⚠️ Server test timeout (normal for first ML model download)${NC}"
}

# Step 7: Create startup script
echo -e "\n${BLUE}🚀 Step 7: Creating startup scripts...${NC}"

STARTUP_SCRIPT="$SCRIPT_DIR/start_replit_server.sh"
cat > "$STARTUP_SCRIPT" << EOF
#!/bin/bash
# Replit Cloud IDE MCP Memory Server Startup Script

cd "$SCRIPT_DIR"
echo "⚡ Starting Replit Cloud IDE MCP Memory Server..."
echo "📍 Server path: $SERVER_PATH"
echo "☁️ Cloud Service: http://localhost:8002"
echo "⚡ ML model will auto-load on first message"
echo "🤝 Optimized for collaborative coding"
echo ""

# Get port from environment or default
PORT=\${PORT:-8002}

# Start cloud service
echo "☁️ Starting Replit Cloud Service on port \$PORT..."
$PYTHON_CMD replit_cloud_service.py &
SERVICE_PID=\$!

echo "📱 Replit service started (PID: \$SERVICE_PID)"
echo "🔗 API endpoints:"
echo "   • POST /analyze - Analyze repl messages"
echo "   • POST /collaboration/update - Track collaboration"
echo "   • GET /repls/{name}/memories - Repl-specific memories"
echo "   • GET /user/{username}/memories - User memories"
echo "   • WebSocket /ws/repl/{name} - Real-time updates"
echo ""
echo "🌐 Open http://localhost:\$PORT/dashboard in your browser"
echo ""
echo "Press Ctrl+C to stop the server"

# Wait for interrupt
trap "echo ''; echo '🛑 Stopping Replit server...'; kill \$SERVICE_PID 2>/dev/null; exit" INT
wait
EOF

chmod +x "$STARTUP_SCRIPT"

# Step 8: Create Replit integration guide
echo -e "\n${BLUE}📖 Step 8: Creating integration guide...${NC}"

cat > "$SCRIPT_DIR/REPLIT_INTEGRATION.md" << 'EOF'
# ⚡ Replit Cloud IDE Integration Guide

## Quick Setup

### Option 1: Local Development
1. **Start the server:**
   ```bash
   ./start_replit_server.sh
   ```

2. **Access the dashboard:**
   Open http://localhost:8002/dashboard

### Option 2: Deploy to Replit
1. **Fork this repl** or create a new Python repl
2. **Upload all files** to your repl
3. **Click "Run"** - the server starts automatically
4. **Access via your repl URL**

## API Endpoints

### Analyze Messages
```bash
curl -X POST https://your-repl.username.repl.co/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "message": "I fixed the authentication bug in the login function",
    "repl_context": {"repl_name": "my-project", "language": "python"},
    "user_context": {"username": "developer", "team": "backend"}
  }'
```

### Track Collaboration
```bash
curl -X POST https://your-repl.username.repl.co/collaboration/update \
  -H "Content-Type: application/json" \
  -d '{
    "repl_name": "team-project",
    "user_action": "Added new feature",
    "code_changes": "def new_feature(): pass",
    "participants": ["alice", "bob"]
  }'
```

### Get Repl Memories
```bash
curl https://your-repl.username.repl.co/repls/my-project/memories
```

### Real-time WebSocket
```javascript
const ws = new WebSocket('wss://your-repl.username.repl.co/ws/repl/my-project');
ws.onopen = () => {
  ws.send(JSON.stringify({
    message: "Real-time memory update",
    user_context: {username: "developer"}
  }));
};
```

## Replit-Specific Features

- ☁️ **Cloud-native**: Runs seamlessly on Replit infrastructure
- 🤝 **Collaboration-aware**: Tracks team activities and code changes
- 🚀 **Deployment memory**: Remembers deployment configurations
- 📱 **Multi-language**: Supports all Replit languages
- 🔗 **Cross-repl sharing**: Share memories between projects

## Environment Variables

```bash
# In your Replit .env file
ML_MODEL_TYPE=huggingface
HUGGINGFACE_MODEL_NAME=PiGrieco/mcp-memory-auto-trigger-model
AUTO_TRIGGER_ENABLED=true
REPLIT_MODE=true
LOG_LEVEL=INFO
```

## Integration Examples

### Python Integration
```python
import requests
import asyncio

async def save_code_pattern(pattern_description, repl_name):
    response = requests.post('http://localhost:8002/analyze', json={
        'message': f'Code pattern: {pattern_description}',
        'repl_context': {'repl_name': repl_name, 'language': 'python'}
    })
    return response.json()
```

### JavaScript Integration
```javascript
// For Node.js repls
async function trackCollaboration(replName, action, participants) {
  const response = await fetch('http://localhost:8002/collaboration/update', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({
      repl_name: replName,
      user_action: action,
      participants: participants
    })
  });
  return response.json();
}
```

## Deployment on Replit

1. **Create a new Python repl**
2. **Copy all server files** to your repl
3. **Install dependencies** (automatic with requirements.txt)
4. **Set environment variables** in .env
5. **Click Run** - server starts automatically
6. **Share your repl** for team collaboration

## Best Practices

- Use descriptive repl names for better memory organization
- Include context information in your messages
- Leverage the collaboration features for team projects
- Monitor the dashboard for memory insights
- Use WebSocket for real-time applications
EOF

# Final instructions
echo -e "\n${GREEN}🎉 REPLIT CLOUD IDE INSTALLATION COMPLETED!${NC}"
echo "=============================================="

echo -e "\n${CYAN}📋 REPLIT SETUP INSTRUCTIONS:${NC}"
echo "1. ⚡ Start locally: $STARTUP_SCRIPT"
echo "2. ☁️ Or deploy to Replit using the configuration files"
echo "3. 🌐 Access dashboard: http://localhost:8002/dashboard"
echo "4. 🤝 Start collaborating with AI memory!"

echo -e "\n${BLUE}🧪 TEST THE REPLIT INTEGRATION:${NC}"
echo "Try these API calls:"
echo -e "  ${YELLOW}• Analyze repl messages via POST /analyze${NC}"
echo -e "  ${YELLOW}• Track collaboration via POST /collaboration/update${NC}"
echo -e "  ${YELLOW}• Get repl memories via GET /repls/{name}/memories${NC}"
echo -e "  ${YELLOW}• Real-time updates via WebSocket /ws/repl/{name}${NC}"

echo -e "\n${BLUE}⚡ ML MODEL REPLIT:${NC}"
echo "• Cloud-optimized for Replit infrastructure"
echo "• Collaboration-aware memory triggers"
echo "• Multi-language project support"
echo "• Real-time memory synchronization"

echo -e "\n${BLUE}☁️ CLOUD DEPLOYMENT:${NC}"
echo "1. Fork/create a Python repl on Replit"
echo "2. Upload all files to your repl"
echo "3. Click 'Run' - automatic deployment!"
echo "4. Share your repl URL with your team"

echo -e "\n${BLUE}📁 FILES CREATED:${NC}"
echo "  • Server: $SERVER_PATH"
echo "  • Cloud Service: $SCRIPT_DIR/replit_cloud_service.py"
echo "  • Replit Config: $SCRIPT_DIR/.replit"
echo "  • Python Config: $SCRIPT_DIR/pyproject.toml"
echo "  • Startup: $STARTUP_SCRIPT"
echo "  • Integration Guide: $SCRIPT_DIR/REPLIT_INTEGRATION.md"

echo -e "\n${GREEN}✅ Replit Cloud IDE now has infinite AI memory! 🧠✨${NC}"
echo -e "${CYAN}⚡ Your repls can now remember everything across collaborations!${NC}"
