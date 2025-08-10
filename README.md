# 🧠 MCP Memory Server

**Production-Ready AI Memory Management System with Intelligent Auto-Triggers**

![Version](https://img.shields.io/badge/version-2.0-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![Python](https://img.shields.io/badge/python-3.8+-blue.svg)
![Docker](https://img.shields.io/badge/docker-ready-brightgreen.svg)

---

## 🎯 **Overview**

The MCP Memory Server is a sophisticated **Model Context Protocol (MCP)** server that provides intelligent memory management for AI systems. It features world-class ML-powered auto-triggering with **99.56% accuracy** for automatic memory operations.

### 🌟 **Key Features**

- **🤖 Intelligent Auto-Triggers**: ML model with 99.56% accuracy automatically decides when to save/search memories
- **🔄 Hybrid System**: Combines deterministic rules with ML intelligence for optimal performance  
- **☁️ Cloud-Ready**: Built-in cloud integration with MongoDB Atlas support
- **🔌 AI Integrations**: Native support for Claude, GPT, Cursor, and other AI agents
- **🐳 Docker Support**: Full containerization with production-ready deployment
- **📊 Advanced Analytics**: Memory importance scoring and semantic search
- **🔒 Production Security**: Environment-based configuration and secure authentication

---

## 🚀 **Quick Start**

### **Prerequisites**

- Python 3.8+
- Docker & Docker Compose (recommended)
- MongoDB Atlas account (or local MongoDB)

### **1. Docker Deployment (Recommended)**

```bash
# Clone the repository
git clone https://github.com/PiGrieco/mcp-memory-server.git
cd mcp-memory-server

# Quick setup
./docker-setup.sh

# Start the complete system
docker-compose up -d

# Check status
docker-compose ps
```

### **2. Simple Setup**

```bash
# Quick install
./install.sh

# Run simple server
python simple_mcp_server.py
```

### **3. Production HTTP Server**

```bash
# Setup environment
./setup.sh

# Run production HTTP server
python mcp_memory_server_http.py
```

---

## 🎮 **Available Servers**

### **1. 📡 Simple MCP Server**
```bash
python simple_mcp_server.py
```
- Basic MCP protocol support
- Memory save/search operations
- Lightweight and fast

### **2. 🧠 Full MCP Server** 
```bash
python mcp_memory_server.py
```
- Complete MCP protocol implementation
- Advanced memory management
- Auto-trigger system integration

### **3. 🌐 HTTP Server**
```bash
python mcp_memory_server_http.py
```
- REST API interface
- Web integration support
- Production monitoring

### **4. 🤖 Auto-Trigger Server**
```bash
python main_auto.py
```
- ML-powered auto-triggers (99.56% accuracy)
- Intelligent memory decisions
- Hybrid deterministic/ML system

---

## ⚙️ **Configuration**

### **Environment Variables**

```env
# MongoDB Configuration
MONGODB_URI=mongodb+srv://username:password@cluster.mongodb.net/
MONGODB_DATABASE=mcp_memory_production
MONGODB_COLLECTION=memories

# ML Auto-Trigger Configuration
ML_MODEL_TYPE=huggingface                    # Use trained HF model
HUGGINGFACE_MODEL_NAME=PiGrieco/mcp-memory-auto-trigger-model
ML_TRIGGER_MODE=hybrid                       # hybrid, ml_only, deterministic_only

# Embedding Configuration
EMBEDDING_PROVIDER=sentence_transformers
EMBEDDING_MODEL=all-MiniLM-L6-v2

# Security
API_KEY=your_api_key_here
```

---

## 🏗️ **Architecture**

### **Core Components**

```
mcp-memory-server/
├── src/                           # Core system implementation
│   ├── core/                      # Central server and trigger systems
│   ├── services/                  # Business logic services
│   ├── config/                    # Configuration management
│   └── models/                    # Data models and schemas
├── cloud/                        # Cloud infrastructure
├── integrations/                 # AI agent integrations
├── config/                       # Configuration examples
├── Server entry points:
│   ├── simple_mcp_server.py      # Simple MCP server
│   ├── mcp_memory_server.py      # Full MCP server
│   ├── mcp_memory_server_http.py # HTTP API server
│   └── main_auto.py              # Auto-trigger server
└── Setup and deployment files
```

### **🧠 ML Auto-Trigger System**

The system uses a **world-class trained model** hosted on [Hugging Face Hub](https://huggingface.co/PiGrieco/mcp-memory-auto-trigger-model):

- **Model**: DistilBERT-based classifier
- **Training Data**: 47K+ high-quality examples (68% real data)
- **Performance**: 99.56% accuracy
- **Actions**: `SAVE_MEMORY`, `SEARCH_MEMORY`, `NO_ACTION`

---

## 🔌 **AI Agent Integration**

### **Claude Desktop**

Add to your Claude Desktop configuration:

```json
{
  "mcpServers": {
    "memory": {
      "command": "python",
      "args": ["/path/to/simple_mcp_server.py"],
      "env": {
        "MONGODB_URI": "your_mongodb_connection_string"
      }
    }
  }
}
```

### **Cursor IDE**

Use the integration example:

```bash
python test_cursor_integration.py
```

---

## ☁️ **Cloud & Deployment**

### **Docker Deployment**

```bash
# Complete setup
./docker-complete-setup.sh

# Run with Docker
./docker-run.sh

# Deploy to remote server
./deploy-remote-server.sh
```

### **Local Setup**

```bash
# Install dependencies
./install.sh

# Setup environment
./setup.sh

# Fix permissions (if needed)
./fix-permissions.sh
```

---

## 🛠️ **Development & Testing**

### **Testing**

```bash
# Test auto-trigger system
python test_auto_trigger.py

# Test Cursor integration
python test_cursor_integration.py
```

### **Models & Dependencies**

```bash
# Download required models
python download_models.py

# Or use simple script
./download_models_simple.sh
```

---

## 📊 **API Usage**

### **Memory Operations**

```python
# Using simple server
from simple_mcp_server import MCPMemoryServer

server = MCPMemoryServer()
await server.save_memory("Important configuration: API_KEY=abc123")

# Search memories
results = await server.search_memories("API configuration")
```

### **HTTP API**

```bash
# Start HTTP server
python mcp_memory_server_http.py

# Save memory via REST
curl -X POST http://localhost:8000/memories \
  -H "Content-Type: application/json" \
  -d '{"content": "Remember this API key", "importance": "high"}'

# Search memories
curl "http://localhost:8000/search?q=API+key"
```

---

## 🔒 **Security**

- **Environment Variables**: No hardcoded credentials
- **API Authentication**: Optional API key protection
- **Database Security**: MongoDB Atlas encryption
- **Container Security**: Docker isolation
- **Token Management**: Secure HuggingFace token handling

---

## 📝 **Quick Setup Scripts**

- **`./install.sh`** - Install all dependencies
- **`./setup.sh`** - Environment setup
- **`./docker-setup.sh`** - Docker configuration
- **`./quick-fix-env.sh`** - Fix environment issues
- **`./localhost_setup_guide.sh`** - Local development setup

---

## 🎯 **Current Status**

**✅ Production Ready** - The MCP Memory Server is fully functional with:

- ✅ **Multiple server options** (simple, full, HTTP, auto-trigger)
- ✅ **World-class ML model** (99.56% accuracy) integrated
- ✅ **Complete setup automation** with scripts
- ✅ **Docker containerization** ready
- ✅ **AI agent integrations** for Claude, Cursor
- ✅ **Cloud infrastructure** support
- ✅ **Production security** practices

Ready for immediate deployment and AI agent integration.

---

## 🔗 **Resources**

- **🤖 Trained Model**: [Hugging Face Hub](https://huggingface.co/PiGrieco/mcp-memory-auto-trigger-model)
- **📊 Training Dataset**: [Hugging Face Datasets](https://huggingface.co/datasets/PiGrieco/mcp-memory-auto-trigger-ultimate)
- **📖 MCP Protocol**: [Model Context Protocol](https://modelcontextprotocol.io/)

---

**Made with ❤️ for the AI community**