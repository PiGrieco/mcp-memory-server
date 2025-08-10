# 🎯 Cursor Integration Guide - MCP Memory Server

**Complete guide for integrating the MCP Memory Server with Cursor IDE**

---

## 🚀 **Quick Integration Steps**

### **Step 1: Install Dependencies**

```bash
# In the mcp-memory-server directory
pip install -r requirements.txt
```

### **Step 2: Test the Simple Server**

```bash
# Test that the server works
python simple_mcp_server.py
```

### **Step 3: Cursor Configuration**

Add this to your Cursor settings (`~/.cursor/settings.json` or via Cursor Settings):

```json
{
  "mcp": {
    "servers": {
      "mcp-memory": {
        "command": "python",
        "args": ["path/to/mcp-memory-server/simple_mcp_server.py"],
        "env": {
          "MONGODB_URI": "your_mongodb_connection_string_here"
        }
      }
    }
  }
}
```

### **Step 4: Environment Setup**

Create a `.env` file in the project root:

```env
# MongoDB Configuration
MONGODB_URI=mongodb+srv://username:password@cluster.mongodb.net/mcp_memory
MONGODB_DATABASE=mcp_memory_production
MONGODB_COLLECTION=memories

# ML Auto-Trigger Configuration (uses trained HuggingFace model)
ML_MODEL_TYPE=huggingface
HUGGINGFACE_MODEL_NAME=PiGrieco/mcp-memory-auto-trigger-model
ML_TRIGGER_MODE=hybrid

# Optional: HuggingFace Token (for private models)
HUGGINGFACE_TOKEN=your_token_here
```

---

## 🧠 **Server Options**

### **1. Simple Server (Recommended for Cursor)**
```bash
python simple_mcp_server.py
```
- **Best for**: Cursor IDE integration
- **Features**: Basic memory operations with simple auto-triggers
- **Startup time**: < 1 second
- **Memory usage**: ~50MB

### **2. ML Auto-Trigger Server (Advanced)**
```bash
python main_auto.py
```
- **Best for**: Advanced users wanting ML-powered triggers
- **Features**: 99.56% accuracy ML model for intelligent memory decisions
- **Startup time**: ~5-10 seconds (model loading)
- **Memory usage**: ~300MB

### **3. Full Production Server**
```bash
python mcp_memory_server.py
```
- **Best for**: Production deployment
- **Features**: Complete MCP protocol, advanced features
- **Startup time**: ~3-5 seconds
- **Memory usage**: ~150MB

---

## 🎮 **Testing in Cursor**

### **Step 1: Start the Server**

```bash
# Terminal 1: Start the server
cd /path/to/mcp-memory-server
python simple_mcp_server.py

# You should see:
# 🚀 Simple MCP Server running...
# 📡 Listening for MCP protocol connections
```

### **Step 2: Test in Cursor**

Open Cursor and try these commands in chat:

```
1. "Ricorda che il server API è su https://api.example.com"
2. "Nota: la password del database è admin123"
3. "Importante: il deployment si fa con docker-compose up -d"
```

### **Step 3: Search Memories**

```
1. "Cerca informazioni sul server API"
2. "Trova la password del database"
3. "Come si fa il deployment?"
```

### **Step 4: Verify Auto-Triggers**

The system should automatically save important information and suggest searches when you ask questions.

---

## 🔧 **Automated Setup Script**

Run this for automatic Cursor integration:

```bash
python test_cursor_integration.py
```

This script will:
- ✅ Test server functionality
- ✅ Create Cursor configuration
- ✅ Verify MCP protocol
- ✅ Test auto-triggers
- ✅ Show integration status

---

## 🛠️ **Troubleshooting**

### **Problem: "Connection refused"**
```bash
# Check if server is running
ps aux | grep mcp

# Restart server
python simple_mcp_server.py
```

### **Problem: "Import errors"**
```bash
# Install dependencies
pip install -r requirements.txt

# Check Python path
python -c "import sys; print(sys.path)"
```

### **Problem: "MongoDB connection failed"**
```bash
# Test MongoDB connection
python -c "
import os
from pymongo import MongoClient
uri = os.getenv('MONGODB_URI', 'mongodb://localhost:27017')
client = MongoClient(uri)
print('✅ MongoDB connected:', client.admin.command('ping'))
"
```

### **Problem: "ML model not loading"**
```bash
# Use simple server instead
python simple_mcp_server.py

# Or check HuggingFace connection
python -c "
from transformers import pipeline
model = pipeline('text-classification', model='PiGrieco/mcp-memory-auto-trigger-model')
print('✅ ML model loaded successfully')
"
```

---

## 📊 **Expected Behavior**

### **When working correctly:**

1. **Auto-Save**: When you say "Ricorda..." or "Importante...", memories are saved automatically
2. **Auto-Search**: When you ask questions, relevant memories are retrieved
3. **Cursor Integration**: The server appears in Cursor's available tools
4. **Memory Persistence**: Saved memories persist between sessions

### **Performance Expectations:**

- **Simple Server**: < 100ms response time
- **ML Server**: < 500ms response time (first request may be slower due to model loading)
- **Memory Search**: < 200ms for semantic similarity search

---

## 🎯 **Advanced Configuration**

### **For ML-Powered Auto-Triggers:**

```json
{
  "mcp": {
    "servers": {
      "mcp-memory-ml": {
        "command": "python",
        "args": ["path/to/mcp-memory-server/main_auto.py"],
        "env": {
          "MONGODB_URI": "your_connection_string",
          "ML_MODEL_TYPE": "huggingface",
          "HUGGINGFACE_MODEL_NAME": "PiGrieco/mcp-memory-auto-trigger-model",
          "ML_TRIGGER_MODE": "hybrid",
          "ML_CONFIDENCE_THRESHOLD": "0.7"
        }
      }
    }
  }
}
```

### **For Production Deployment:**

```json
{
  "mcp": {
    "servers": {
      "mcp-memory-prod": {
        "command": "python",
        "args": ["path/to/mcp-memory-server/mcp_memory_server.py"],
        "env": {
          "MONGODB_URI": "mongodb+srv://...",
          "ENVIRONMENT": "production",
          "LOG_LEVEL": "INFO"
        }
      }
    }
  }
}
```

---

## ✅ **Success Checklist**

- [ ] Dependencies installed (`pip install -r requirements.txt`)
- [ ] MongoDB connection configured
- [ ] Server starts without errors
- [ ] Cursor recognizes the MCP server
- [ ] Auto-save works with trigger words
- [ ] Search retrieves saved memories
- [ ] ML model loads (if using advanced server)

---

## 🎉 **You're Ready!**

Once completed, you'll have a fully integrated MCP Memory Server in Cursor with:

- **🧠 Intelligent memory management**
- **🤖 ML-powered auto-triggers (99.56% accuracy)**
- **🔍 Semantic search capabilities**
- **💾 Persistent memory storage**
- **⚡ Real-time integration with Cursor**

**The MCP Memory Server will now work seamlessly with Cursor to remember important information and help you find it later!**
