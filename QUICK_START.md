# 🚀 Quick Start Guide - MCP Memory Server

## ⚡ 5-Minute Setup

### 1. Install Dependencies
```bash
# Clone and setup
git clone https://github.com/AiGotsrl/mcp-memory-server.git
cd mcp-memory-server

# Run automated setup
./setup.sh
```

### 2. Configure Cursor IDE
Add to your Cursor MCP configuration (`mcp.json`):

```json
{
  "mcpServers": {
    "memory-server": {
      "command": "/path/to/your/project/.myenv/bin/python",
      "args": ["/path/to/your/project/mcp_memory_server.py"]
    }
  }
}
```

### 3. Test Integration
```bash
# Test the server
python comprehensive_test.py

# Expected output: ✅ All tests completed successfully!
```

## 🧪 Quick Test Prompts

### In Cursor IDE, try these prompts:

1. **Save Memory**: 
   > "Save this to memory: We decided to use React and Node.js for the new project"

2. **Search Memory**: 
   > "Search my memories for 'React'"

3. **List All**: 
   > "List all my saved memories"

4. **Check Status**: 
   > "Check memory system status"

## ✅ Expected Results

- **Mode**: Full Server ✅
- **Database**: MongoDB with embeddings ✅
- **Search**: Semantic similarity matching ✅
- **Project**: Environment-based organization ✅

## 🔧 Configuration Files

- **`.env`** - Environment variables (MongoDB, project settings)
- **`mcp.json`** - Cursor IDE integration
- **`requirements.txt`** - Python dependencies

## 📊 Production Features

- ✅ **No Simple Mode** - Always Full Server
- ✅ **MongoDB Backend** - Persistent storage
- ✅ **Sentence Transformers** - AI-powered search
- ✅ **Environment Variables** - Flexible configuration
- ✅ **Comprehensive Testing** - Production validation

---

**🎯 Ready to revolutionize your AI conversations with persistent memory!**
