# 🚀 Claude Desktop & Windsurf IDE - Setup Guide

**Enhanced MCP Memory Server with Complete ML Configuration**

---

## 🎯 **Quick Installation**

### **Claude Desktop** 🤖
```bash
# Automatic installation
curl -sSL https://raw.githubusercontent.com/PiGrieco/mcp-memory-server/feature/complete-architecture-refactor/scripts/install/install_claude.sh | bash
```

### **Windsurf IDE** 🌊
```bash
# Automatic installation  
curl -sSL https://raw.githubusercontent.com/PiGrieco/mcp-memory-server/feature/complete-architecture-refactor/scripts/install/install_windsurf.sh | bash
```

---

## 🧠 **What Gets Installed**

### **✅ Complete ML Configuration:**
- **ML Model**: `PiGrieco/mcp-memory-auto-trigger-model`
- **Entry Point**: `main.py` (unified modern server)
- **Architecture**: Enhanced server with all legacy ML features

### **🎯 ML Thresholds Configured:**
```bash
ML_CONFIDENCE_THRESHOLD=0.7    # 70% ML confidence
TRIGGER_THRESHOLD=0.15         # 15% general trigger
SIMILARITY_THRESHOLD=0.3       # 30% search similarity  
MEMORY_THRESHOLD=0.7           # 70% memory importance
SEMANTIC_THRESHOLD=0.8         # 80% semantic similarity
ML_TRIGGER_MODE=hybrid         # Hybrid ML + rules
```

### **📚 Continuous Learning:**
```bash
ML_TRAINING_ENABLED=true
ML_RETRAIN_INTERVAL=50
FEATURE_EXTRACTION_TIMEOUT=5.0
MAX_CONVERSATION_HISTORY=10
USER_BEHAVIOR_TRACKING=true
BEHAVIOR_HISTORY_LIMIT=1000
```

---

## 📋 **Configuration Files Created**

### **Claude Desktop:**
- **Path**: `~/.config/claude/claude_desktop_config.json` (Linux/Windows)
- **Path**: `~/Library/Application Support/Claude/claude_desktop_config.json` (macOS)

### **Windsurf IDE:**
- **Path**: `~/mcp-memory-server/windsurf_config.json`

---

## 🔧 **Manual Configuration**

If you prefer manual setup, use these templates:

### **Claude Template:**
```json
{
  "mcpServers": {
    "mcp-memory-sam": {
      "command": "/path/to/mcp-memory-server/venv/bin/python",
      "args": ["/path/to/mcp-memory-server/main.py"],
      "env": {
        "ML_MODEL_TYPE": "huggingface",
        "HUGGINGFACE_MODEL_NAME": "PiGrieco/mcp-memory-auto-trigger-model",
        "AUTO_TRIGGER_ENABLED": "true",
        "CLAUDE_MODE": "true",
        "ML_CONFIDENCE_THRESHOLD": "0.7",
        "TRIGGER_THRESHOLD": "0.15",
        "SIMILARITY_THRESHOLD": "0.3",
        "MEMORY_THRESHOLD": "0.7",
        "SEMANTIC_THRESHOLD": "0.8",
        "ML_TRIGGER_MODE": "hybrid"
      }
    }
  }
}
```

### **Windsurf Template:**
```json
{
  "mcpServers": {
    "mcp-memory-sam": {
      "command": "/path/to/mcp-memory-server/venv/bin/python", 
      "args": ["/path/to/mcp-memory-server/main.py"],
      "env": {
        "ML_MODEL_TYPE": "huggingface",
        "HUGGINGFACE_MODEL_NAME": "PiGrieco/mcp-memory-auto-trigger-model",
        "AUTO_TRIGGER_ENABLED": "true",
        "WINDSURF_MODE": "true",
        "ML_CONFIDENCE_THRESHOLD": "0.7",
        "TRIGGER_THRESHOLD": "0.15",
        "SIMILARITY_THRESHOLD": "0.3",
        "MEMORY_THRESHOLD": "0.7", 
        "SEMANTIC_THRESHOLD": "0.8",
        "ML_TRIGGER_MODE": "hybrid"
      }
    }
  }
}
```

---

## 🧪 **Testing Installation**

After installation, verify everything works:

```bash
# Test server startup
cd ~/mcp-memory-server  
python main.py --test

# Should output: ✅ Server imports and configuration successful
```

---

## 🎉 **Available SAM Tools**

Once installed, you'll have access to all SAM tools:

- **`save_memory`** - Save memories with ML embeddings
- **`search_memory`** - Semantic search through memories
- **`analyze_message`** - Auto-trigger analysis with ML
- **`get_memory_stats`** - Complete system statistics
- **`list_memories`** - List all saved memories

---

## 🔄 **Differences from Legacy**

### **✅ Enhanced Features:**
- **Modern Architecture**: Unified server (`main.py`) vs separate legacy servers
- **Complete ML Config**: All thresholds from legacy server included
- **Better Error Handling**: Improved stability and logging
- **Flexible Configuration**: YAML + environment variable support
- **SAM Compatibility**: 100% compatible with existing SAM workflows

### **📈 Migration Path:**
- **Old**: `cursor_mcp_server.py`, `claude_mcp_server.py`, `windsurf_mcp_server.py`
- **New**: `main.py` with platform-specific environment variables
- **Result**: Same functionality, better architecture

---

## 🛠️ **Troubleshooting**

### **Common Issues:**

1. **Python Version**: Requires Python 3.8+
2. **Virtual Environment**: Auto-created during installation
3. **ML Model Download**: ~63MB, downloaded on first use
4. **MongoDB**: Auto-configured for local development

### **Support:**
For issues, check the main repository: https://github.com/PiGrieco/mcp-memory-server

---

**🧠 Ready to use SAM with enhanced ML capabilities!** 🚀
