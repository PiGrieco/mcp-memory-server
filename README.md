# 🧠 MCP Memory Server
**Persistent Memory with Smart Automation for AI Tools**

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://python.org)
[![MIT License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Docker](https://img.shields.io/badge/Docker-Supported-2496ED.svg)](https://docker.com)
[![MongoDB](https://img.shields.io/badge/MongoDB-Database-47A248.svg)](https://mongodb.com)
[![Real-time](https://img.shields.io/badge/Memory-Real--time-ff6b6b.svg)](#)

🤖 **NUOVO**: Sistema di Automazione Intelligente per Claude, GPT, Cursor, Lovable e Replit!

A persistent memory system for AI agents using the Model Context Protocol (MCP). This server provides semantic memory storage with vector search capabilities, enabling AI agents to remember and recall information across conversations.

## 🎯 What's New: Smart Automation

Transform your AI tools into intelligent assistants that **automatically remember, learn, and suggest** based on your patterns!

### 🚀 Available Smart Integrations

| Tool | File | Features | Status |
|------|------|----------|--------|
| 🧠 **Claude Desktop** | `claude_smart_auto.py` | Auto-save preferences, Context enhancement, Proactive suggestions | ✅ Ready |
| 💬 **GPT/ChatGPT** | `gpt_smart_auto.py` | Smart API, User profiling, Predictive analytics | ✅ Ready |
| 💻 **Cursor** | `cursor_smart_auto.py` | Code-aware patterns, Workspace analysis, Productivity tracking | ✅ Ready |
| 💖 **Lovable** | `lovable_smart_auto.js` | Component tracking, UI patterns, AI prompt enhancement | ✅ Ready |
| 🌐 **Replit** | `replit_smart_auto.py` | Cloud development, Collaboration intelligence, Deployment analytics | ✅ Ready |

### 🎯 Smart Features

- **🔄 Auto-Save**: Automatically detects and saves preferences, solutions, and patterns
- **🔍 Auto-Search**: Intelligently retrieves relevant context before AI responses  
- **💡 Proactive Suggestions**: Suggests optimizations based on your history
- **📊 Learning Analytics**: Tracks productivity and learning efficiency
- **🎛️ 5 Automation Levels**: From basic pattern recognition to self-learning AI

## ⚡ Quick Smart Setup

```bash
# 1. Automated setup for all integrations
./setup_smart_automation.sh

# 2. Or manual setup
docker compose up -d
python examples/gpt_smart_auto.py &

# 3. Test smart features
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message":"I prefer TypeScript over JavaScript","user_id":"demo"}'
```

## 🎪 Smart Automation Demo

**Before (Manual)**:
```
You: "I prefer TypeScript for React projects"
AI: "Okay, I'll help with TypeScript"
[No memory saved]

You: "How should I setup React?"
AI: "Here's how to setup React..."
[Doesn't remember TypeScript preference]
```

**After (Smart Automation)**:
```
You: "I prefer TypeScript for React projects"  
🔄 [Auto-saved: "Preference: TypeScript for React"]
AI: "Got it! I'll remember your TypeScript preference."

You: "How should I setup React?"
🔍 [Auto-search: Found "Preference: TypeScript for React"]
💡 [Enhanced Response]
AI: "Based on your preference for TypeScript, here's how to setup React with TypeScript template..."
```

## 🏗️ Features

### Core Memory System
- **Semantic Vector Search**: Find information by meaning, not just keywords
- **MongoDB Backend**: Persistent storage with ACID compliance
- **Real-time Embedding**: Uses sentence-transformers for semantic understanding
- **MCP Protocol**: Compatible with Claude Desktop and MCP-enabled tools
- **RESTful API**: Direct integration for GPT/ChatGPT and web applications

### Smart Automation (NEW)
- **Intelligent Triggers**: 50+ regex patterns for automatic detection
- **Context Enhancement**: Automatic context injection before AI responses
- **User Profiling**: Dynamic learning from interaction patterns
- **Predictive Suggestions**: Proactive recommendations based on history
- **Cross-Platform Sync**: Memory sharing across all AI tools
- **Analytics Dashboard**: Real-time productivity and learning metrics

## 📁 Project Structure

```
mcp-memory-server/
├── 🧠 Smart Automation
│   ├── examples/claude_smart_auto.py      # Claude Desktop integration
│   ├── examples/gpt_smart_auto.py         # GPT/ChatGPT API server
│   ├── examples/cursor_smart_auto.py      # Cursor code-aware integration
│   ├── examples/lovable_smart_auto.js     # Lovable AI development platform
│   ├── examples/replit_smart_auto.py      # Replit cloud development
│   ├── examples/smart_triggers.py         # Smart trigger system
│   └── examples/auto_memory_system.py     # Core automation engine
├── 📚 Guides
│   ├── SMART_AUTOMATION_GUIDE.md          # Complete automation guide
│   ├── AUTO_MEMORY_GUIDE.md               # Automatic memory concepts
│   └── INTEGRATION_GUIDE.md               # Platform-specific guides
├── 🛠️ Setup
│   ├── setup_smart_automation.sh          # Automated setup script
│   └── config/smart_automation_config.json # Central configuration
├── 🏗️ Core System
│   ├── src/
│   │   ├── core/mcp_server.py             # MCP protocol implementation
│   │   ├── core/memory_manager.py         # Memory operations
│   │   ├── core/vector_store.py           # Vector search engine
│   │   └── core/embedding_service.py      # Embedding generation
│   ├── deployment/
│   │   ├── docker-compose.yml             # Docker services
│   │   └── Dockerfile                     # Container definition
│   └── tests/                             # Test suite
```

## 🚀 Installation & Usage

### Method 1: Smart Automation Setup (Recommended)
```bash
git clone https://github.com/AiGotsrl/mcp-memory-server
cd mcp-memory-server
./setup_smart_automation.sh
```

### Method 2: Manual Setup
```bash
# Clone and setup
git clone https://github.com/AiGotsrl/mcp-memory-server
cd mcp-memory-server
pip install -r requirements.txt

# Start services
docker compose up -d

# Test basic system
python -m pytest tests/ -v
```

### Method 3: Development Mode
```bash
# Start MongoDB only
docker run -d --name mongodb \
  -p 27017:27017 \
  -e MONGO_INITDB_ROOT_USERNAME=admin \
  -e MONGO_INITDB_ROOT_PASSWORD=securepassword \
  mongo:latest

# Run server directly
python src/main.py
```

## 🤖 AI Tool Configurations

### Claude Desktop Smart Integration
```json
{
  "mcpServers": {
    "claude-smart-auto": {
      "command": "python",
      "args": ["examples/claude_smart_auto.py"],
      "env": {
        "MONGODB_URL": "mongodb://admin:securepassword@localhost:27017/memory_db?authSource=admin",
        "AUTO_MEMORY": "advanced"
      }
    }
  }
}
```

### GPT/ChatGPT Smart API
```bash
# Start smart API server
python examples/gpt_smart_auto.py

# Use smart endpoints
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message":"Your message","user_id":"your_id"}'
```

### Cursor Smart Integration
```json
{
  "mcp.servers": {
    "cursor-smart-auto": {
      "command": "python", 
      "args": ["examples/cursor_smart_auto.py"],
      "env": {"CODE_AWARE": "true"}
    }
  }
}
```

## 📊 Smart Analytics

Monitor your AI productivity with real-time analytics:

```python
# Get comprehensive analytics
analytics = smart_system.get_session_analytics()

print(f"""
🎯 Smart Automation Analytics
============================
Productivity Score: {analytics['productivity_score']:.2f}
Automation Efficiency: {analytics['automation_efficiency']:.2f}
Learning Rate: {analytics['learning_efficiency']:.2f}
Auto-Saves: {analytics['auto_saves']}
Context Retrievals: {analytics['context_retrievals']}
""")
```

## 🔧 MCP Tools

The server provides these MCP tools for AI agents:

| Tool | Description | Parameters |
|------|-------------|------------|
| `save_memory` | Store information with semantic understanding | `text`, `memory_type`, `project`, `importance`, `tags` |
| `search_memory` | Find relevant memories using semantic search | `query`, `project`, `limit`, `threshold` |
| `get_context` | Retrieve memories for AI context enhancement | `project`, `limit` |
| `get_stats` | Get memory usage statistics | `project` |
| `health_check` | Check system health | None |

### Usage Examples

```python
# Save a preference (now automatic with smart triggers)
await mcp_server.call_tool("save_memory", {
    "text": "I prefer TypeScript over JavaScript for large projects",
    "memory_type": "preference",
    "project": "development",
    "importance": 0.8,
    "tags": ["programming", "typescript", "preference"]
})

# Search for relevant information (enhanced with smart context)
result = await mcp_server.call_tool("search_memory", {
    "query": "TypeScript setup",
    "project": "development", 
    "limit": 5,
    "threshold": 0.7
})
```

## 🧪 Testing

```bash
# Run all tests
python -m pytest tests/ -v

# Test with coverage
python -m pytest tests/ --cov=src --cov-report=html

# Test smart automation
python examples/claude_smart_auto.py demo
python examples/cursor_smart_auto.py demo
python examples/replit_smart_auto.py demo

# Test API
curl http://localhost:8000/docs
```

## 📈 Roadmap

### Current Features ✅
- [x] MCP protocol implementation
- [x] MongoDB vector storage
- [x] Semantic search with embeddings
- [x] Smart automation system
- [x] 5 AI tool integrations
- [x] Real-time analytics
- [x] Auto-save triggers
- [x] Context enhancement

### Upcoming Features 🚧
- [ ] Advanced learning algorithms
- [ ] Team collaboration features
- [ ] Custom trigger patterns UI
- [ ] Performance optimization
- [ ] Multi-language support
- [ ] Cloud deployment options
- [ ] Advanced security features
- [ ] Plugin ecosystem

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

### Development Setup
```bash
# Clone repository
git clone https://github.com/AiGotsrl/mcp-memory-server
cd mcp-memory-server

# Install development dependencies
pip install -r requirements.txt

# Install pre-commit hooks
pre-commit install

# Run tests
python -m pytest tests/ -v
```

### Code Style
- Use [Black](https://github.com/psf/black) for code formatting
- Follow [PEP 8](https://pep8.org/) guidelines  
- Add type hints using [MyPy](https://mypy.readthedocs.io/)
- Write comprehensive tests for new features

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

- 📖 **Documentation**: Read our comprehensive guides in the `/docs` folder
- 🐛 **Bug Reports**: [GitHub Issues](https://github.com/AiGotsrl/mcp-memory-server/issues)
- 💬 **Discussions**: [GitHub Discussions](https://github.com/AiGotsrl/mcp-memory-server/discussions)
- 📧 **Email**: support@aigotsrl.com

## 🙏 Acknowledgments

- [Model Context Protocol (MCP)](https://github.com/modelcontextprotocol) for the protocol specification
- [MongoDB](https://www.mongodb.com/) for the robust database backend
- [Sentence Transformers](https://www.sbert.net/) for semantic embeddings
- [FastAPI](https://fastapi.tiangolo.com/) for the modern web API framework
- The AI development community for inspiration and feedback

---

**⭐ Star this repository if you find it helpful!**

**🚀 Ready to make your AI tools super-intelligent? Start with our [Smart Automation Guide](SMART_AUTOMATION_GUIDE.md)!** 