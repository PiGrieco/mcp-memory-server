# 🚀 Enhanced Minimal Production Kit - Quick Start

Get the **MCP Memory Server** running in production with both **MCP standard protocol** and **HTTP API**.

## ⚡ **1-Minute Docker Setup**

```bash
# 1. Copy environment configuration
cp .env.example .env
# Edit .env with your MongoDB URI and settings

# 2. Start both services
docker-compose up -d

# 3. Verify services
curl http://localhost:8000/health  # HTTP API
# MCP server running on stdio for IDE integration
```

## 🎯 **What You Get**

### **MCP Standard Server** (Primary)
- **Protocol:** MCP over stdio 
- **Usage:** Direct integration with IDEs (Cursor, Claude, etc.)
- **Tools:** `save_memory`, `search_memories`, `list_memories`, `memory_status`
- **Features:** ML auto-triggers, semantic search, full MCP protocol

### **HTTP API Server** (Secondary)
- **Protocol:** HTTP/REST + MCP over HTTP
- **Port:** 8000
- **Endpoints:** `/health`, `/info`, `/mcp`, `/mcp/capabilities`
- **Usage:** Remote access, web integrations, monitoring

## 🔧 **IDE Integration Examples**

### **Cursor Configuration**
```json
// ~/.cursor/mcp_settings.json
{
  "mcpServers": {
    "memory": {
      "command": "python",
      "args": ["/path/to/mcp_memory_server.py"],
      "env": {
        "AUTO_TRIGGER_ENABLED": "true",
        "MONGODB_URI": "your_mongodb_uri"
      }
    }
  }
}
```

### **Claude Desktop Configuration**  
```json
// ~/.config/claude/claude_desktop_config.json
{
  "mcpServers": {
    "memory": {
      "command": "python", 
      "args": ["/path/to/mcp_memory_server.py"],
      "env": {
        "AUTO_TRIGGER_ENABLED": "true",
        "CLAUDE_AUTO_CONTEXT": "true"
      }
    }
  }
}
```

## 📋 **Environment Configuration**

Key variables in `.env`:

```bash
# Database
MONGODB_URI=mongodb+srv://user:pass@cluster.mongodb.net/
MONGODB_DATABASE=mcp_memory_production

# ML Auto-Trigger
ML_MODEL_TYPE=huggingface
HUGGINGFACE_MODEL_NAME=PiGrieco/mcp-memory-auto-trigger-model
ML_TRIGGER_MODE=hybrid

# Embedding
EMBEDDING_PROVIDER=sentence_transformers
EMBEDDING_MODEL=all-MiniLM-L6-v2

# Server
SERVER_HOST=localhost
SERVER_PORT=8000
ENVIRONMENT=production
```

## 🧪 **Testing**

```bash
# Run basic tests
pytest tests/ -v

# Test MCP server
python mcp_memory_server.py

# Test HTTP server
python mcp_memory_server_http.py
curl http://localhost:8000/health
```

## 📁 **What's Included**

- ✅ **MCP Standard Server** - Core MCP protocol implementation
- ✅ **HTTP Server** - Web API and remote access
- ✅ **Production Dockerfile** - Security, health checks, non-root user
- ✅ **Docker Compose** - Both services, networks, volumes
- ✅ **Complete Configuration** - 260+ settings in `.env.example`
- ✅ **IDE Examples** - Ready configs for Cursor, Claude
- ✅ **Core Services** - Memory, Database, Embedding, ML triggers
- ✅ **Minimal CI** - Lint, test, build

## 🔗 **Architecture**

```
┌─────────────────────────────────────────────────────────────┐
│                    MCP Memory Server                        │
├─────────────────────────────────────────────────────────────┤
│  MCP Standard (stdio)     │     HTTP API (port 8000)       │
│  ├─ Tool: save_memory     │     ├─ GET /health             │
│  ├─ Tool: search_memories │     ├─ GET /info               │
│  ├─ Tool: list_memories   │     ├─ POST /mcp (JSON-RPC)    │
│  └─ Tool: memory_status   │     └─ GET /mcp/capabilities   │
├─────────────────────────────────────────────────────────────┤
│           Core Services (src/)                              │
│  ├─ Memory Service        ├─ Database Service              │
│  ├─ Embedding Service     ├─ ML Auto-Trigger System        │
│  └─ Health Service        └─ Metrics Service               │
├─────────────────────────────────────────────────────────────┤
│                     MongoDB Atlas                          │
└─────────────────────────────────────────────────────────────┘
```

## 🆘 **Troubleshooting**

### **MongoDB Connection**
```bash
# Test MongoDB connection
python -c "from src.services.database_service import DatabaseService; print('OK' if DatabaseService().health_check() else 'FAIL')"
```

### **ML Model Loading**
```bash
# Test ML model
python -c "from src.core.ml_trigger_system import MLTriggerSystem; MLTriggerSystem().initialize()"
```

### **Docker Issues**
```bash
# Check container logs
docker-compose logs -f mcp-memory-server
docker-compose logs -f mcp-memory-server-http

# Restart services
docker-compose restart
```

---

**🎉 Your enhanced minimal production kit is ready!**

Both **MCP standard** (for IDEs) and **HTTP API** (for web) are running with full production features while maintaining minimal complexity.
