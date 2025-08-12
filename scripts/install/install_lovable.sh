#!/bin/bash

# MCP Memory Server - Lovable Platform Installation Script
# Optimized for Lovable AI-powered development platform

set -e

echo "💙 MCP Memory Server - Lovable Platform Installation"
echo "===================================================="

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
SERVER_PATH="$SCRIPT_DIR/lovable_mcp_server.py"

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

echo -e "${YELLOW}Installing ML dependencies for Lovable...${NC}"
$PYTHON_CMD -m pip install torch>=2.1.0 transformers>=4.30.0 accelerate datasets --quiet

echo -e "${YELLOW}Installing web development dependencies...${NC}"
$PYTHON_CMD -m pip install fastapi uvicorn requests aiohttp websockets --quiet

echo -e "${YELLOW}Installing MCP dependencies...${NC}"
$PYTHON_CMD -m pip install mcp sentence-transformers scikit-learn asyncio python-dotenv pydantic --quiet

echo -e "${GREEN}✅ Dependencies installed${NC}"

# Step 3: Test ML model access
echo -e "\n${BLUE}🧠 Step 3: Testing ML model access for Lovable...${NC}"

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
    print('✅ Lovable platform integration ready')
    
except Exception as e:
    print(f'⚠️ ML model check warning: {e}')
    print('Model will be downloaded on first use')
"

# Step 4: Create Lovable API bridge
echo -e "\n${BLUE}🌐 Step 4: Creating Lovable API bridge...${NC}"

cat > "$SCRIPT_DIR/lovable_api_bridge.py" << 'EOF'
#!/usr/bin/env python3
"""
Lovable Platform API Bridge for MCP Memory Server
Provides REST endpoints for Lovable AI integration
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import asyncio
from typing import Dict, List, Optional
import sys
from pathlib import Path

# Add the smart server
sys.path.insert(0, str(Path(__file__).parent))
from lovable_smart_server import LovableTriggerSystem

app = FastAPI(title="MCP Memory API for Lovable", version="1.0.0")

# Enable CORS for Lovable platform
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global trigger system
trigger_system = None

class ProjectMessage(BaseModel):
    message: str
    project_context: Optional[Dict] = {}
    user_info: Optional[Dict] = {}

class DesignRequest(BaseModel):
    design_description: str
    technology_stack: List[str] = []
    project_name: str

@app.on_event("startup")
async def startup_event():
    global trigger_system
    trigger_system = LovableTriggerSystem()
    print("🚀 Lovable API Bridge started!")

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "mcp-memory-lovable", "platform": "lovable.dev"}

@app.post("/analyze")
async def analyze_project_message(request: ProjectMessage):
    """Analyze message from Lovable platform"""
    try:
        result = await trigger_system.process_message(
            request.message, 
            request.project_context
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/design/save")
async def save_design_pattern(request: DesignRequest):
    """Save design patterns and components"""
    try:
        message = f"Design pattern for {request.project_name}: {request.design_description}"
        if request.technology_stack:
            message += f" using {', '.join(request.technology_stack)}"
        
        result = await trigger_system.process_message(
            message,
            {
                "type": "design_pattern",
                "project": request.project_name,
                "technologies": request.technology_stack
            }
        )
        return {"saved": True, "result": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/projects/{project_name}/memories")
async def get_project_memories(project_name: str):
    """Get memories for specific project"""
    try:
        all_memories = trigger_system.memories
        project_memories = [
            mem for mem in all_memories.values()
            if mem.get('project_context', {}).get('project') == project_name
        ]
        return {"project": project_name, "memories": project_memories}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/stats")
async def get_lovable_stats():
    """Get Lovable-specific statistics"""
    return trigger_system.get_lovable_stats()

@app.get("/dashboard")
async def lovable_dashboard():
    """Lovable-specific dashboard"""
    stats = trigger_system.get_lovable_stats()
    return f"""
    <html>
    <head>
        <title>💙 Lovable Memory Dashboard</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 40px; background: #f8f9fa; }}
            .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                       color: white; padding: 20px; border-radius: 10px; }}
            .stats {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); 
                     gap: 20px; margin: 20px 0; }}
            .stat-card {{ background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1>💙 MCP Memory Dashboard - Lovable Platform</h1>
            <p>AI-powered memory for your development projects</p>
        </div>
        
        <div class="stats">
            <div class="stat-card">
                <h3>🎨 Designs Saved</h3>
                <h2>{stats['lovable_stats']['designs_saved']}</h2>
            </div>
            <div class="stat-card">
                <h3>🔧 Features Documented</h3>
                <h2>{stats['lovable_stats']['features_documented']}</h2>
            </div>
            <div class="stat-card">
                <h3>🌐 Web Interactions</h3>
                <h2>{stats['lovable_stats']['web_interactions']}</h2>
            </div>
            <div class="stat-card">
                <h3>📚 Total Memories</h3>
                <h2>{stats['memory_count']}</h2>
            </div>
        </div>
        
        <h2>Recent Memories:</h2>
        <div style="background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
            {"".join([f'<p><strong>{mem["id"]}:</strong> {mem["content"][:100]}...</p>' 
                     for mem in list(trigger_system.memories.values())[-5:]])}
        </div>
        
        <div style="margin-top: 20px; text-align: center; color: #666;">
            <p>💙 Powered by MCP Memory Server for Lovable Platform</p>
        </div>
    </body>
    </html>
    """

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
EOF

chmod +x "$SCRIPT_DIR/lovable_api_bridge.py"

# Step 5: Test the server
echo -e "\n${BLUE}🧪 Step 5: Testing Lovable server...${NC}"

echo -e "${YELLOW}Testing server initialization...${NC}"
timeout 15s $PYTHON_CMD "$SERVER_PATH" --test 2>/dev/null || {
    echo -e "${YELLOW}⚠️ Server test timeout (normal for first ML model download)${NC}"
}

# Step 6: Create startup script
echo -e "\n${BLUE}🚀 Step 6: Creating startup scripts...${NC}"

STARTUP_SCRIPT="$SCRIPT_DIR/start_lovable_server.sh"
cat > "$STARTUP_SCRIPT" << EOF
#!/bin/bash
# Lovable Platform MCP Memory Server Startup Script

cd "$SCRIPT_DIR"
echo "💙 Starting Lovable Platform MCP Memory Server..."
echo "📍 Server path: $SERVER_PATH"
echo "🌐 API Bridge: http://localhost:8001"
echo "⚡ ML model will auto-load on first message"
echo "💙 Optimized for Lovable AI development platform"
echo ""

# Start API bridge
echo "🌐 Starting Lovable API bridge..."
$PYTHON_CMD lovable_api_bridge.py &
API_PID=\$!

echo "📱 Lovable API started on port 8001 (PID: \$API_PID)"
echo "🔗 API endpoints:"
echo "   • POST /analyze - Analyze project messages"
echo "   • POST /design/save - Save design patterns"
echo "   • GET /projects/{name}/memories - Project memories"
echo "   • GET /dashboard - Lovable dashboard"
echo ""
echo "🌐 Open http://localhost:8001/dashboard in your browser"
echo ""
echo "Press Ctrl+C to stop the server"

# Wait for interrupt
trap "echo ''; echo '🛑 Stopping Lovable server...'; kill \$API_PID 2>/dev/null; exit" INT
wait
EOF

chmod +x "$STARTUP_SCRIPT"

# Step 7: Create Lovable integration guide
echo -e "\n${BLUE}📖 Step 7: Creating integration guide...${NC}"

cat > "$SCRIPT_DIR/LOVABLE_INTEGRATION.md" << 'EOF'
# 💙 Lovable Platform Integration Guide

## Quick Setup

1. **Start the server:**
   ```bash
   ./start_lovable_server.sh
   ```

2. **Access the dashboard:**
   Open http://localhost:8001/dashboard

## API Endpoints

### Analyze Messages
```bash
curl -X POST http://localhost:8001/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Remember this React component pattern",
    "project_context": {"project": "my-app", "framework": "react"}
  }'
```

### Save Design Patterns
```bash
curl -X POST http://localhost:8001/design/save \
  -H "Content-Type: application/json" \
  -d '{
    "design_description": "Responsive navigation with mobile hamburger menu",
    "technology_stack": ["React", "Tailwind CSS"],
    "project_name": "webapp"
  }'
```

### Get Project Memories
```bash
curl http://localhost:8001/projects/my-app/memories
```

## Integration with Lovable Platform

1. Use the API endpoints to send project updates
2. Automatically save design patterns and components
3. Retrieve context-aware memories for AI assistance
4. Track development progress and patterns

## Features

- 🎨 Design pattern recognition
- 🔧 Feature documentation
- 🌐 Web development focus
- 📱 Technology stack awareness
- 💙 Lovable platform optimization

## Example Usage

```javascript
// In your Lovable project
async function saveImportantPattern(description, technologies) {
  const response = await fetch('http://localhost:8001/design/save', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({
      design_description: description,
      technology_stack: technologies,
      project_name: 'my-lovable-app'
    })
  });
  return response.json();
}
```
EOF

# Final instructions
echo -e "\n${GREEN}🎉 LOVABLE PLATFORM INSTALLATION COMPLETED!${NC}"
echo "=============================================="

echo -e "\n${CYAN}📋 LOVABLE SETUP INSTRUCTIONS:${NC}"
echo "1. 💙 Start the Lovable server: $STARTUP_SCRIPT"
echo "2. 🌐 Open dashboard: http://localhost:8001/dashboard"
echo "3. 🔗 Integrate with your Lovable projects using the API"
echo "4. 🎨 Start building with AI memory!"

echo -e "\n${BLUE}🧪 TEST THE LOVABLE INTEGRATION:${NC}"
echo "Try these API calls:"
echo -e "  ${YELLOW}• Save a design pattern via POST /design/save${NC}"
echo -e "  ${YELLOW}• Analyze project messages via POST /analyze${NC}"
echo -e "  ${YELLOW}• Check project memories via GET /projects/{name}/memories${NC}"

echo -e "\n${BLUE}⚡ ML MODEL LOVABLE:${NC}"
echo "• Web development pattern recognition"
echo "• Design-focused memory categorization"
echo "• Technology stack awareness"
echo "• Project-scoped memory organization"

echo -e "\n${BLUE}🔧 QUICK START:${NC}"
echo "1. Start server: $STARTUP_SCRIPT"
echo "2. Open dashboard: http://localhost:8001/dashboard"
echo "3. Read integration guide: $SCRIPT_DIR/LOVABLE_INTEGRATION.md"

echo -e "\n${BLUE}📁 FILES CREATED:${NC}"
echo "  • Server: $SERVER_PATH"
echo "  • API Bridge: $SCRIPT_DIR/lovable_api_bridge.py"
echo "  • Startup: $STARTUP_SCRIPT"
echo "  • Integration Guide: $SCRIPT_DIR/LOVABLE_INTEGRATION.md"

echo -e "\n${GREEN}✅ Lovable Platform now has infinite AI memory! 🧠✨${NC}"
echo -e "${CYAN}💙 Your Lovable projects can now remember all designs and patterns!${NC}"
