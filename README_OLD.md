# MCP Memory Server - Production Ready

<div align="center">

![MCP Memory Server](https://img.shields.io/badge/MCP-Memory%20Server-blue?style=for-the-badge)
![Version](https://img.shields.io/badge/version-2.0.0-green?style=for-the-badge)
![Production Ready](https://img.shields.io/badge/status-Production%20Ready-success?style=for-the-badge)

*Persistent memory for AI assistants with cloud sync, multi-platform support, and production-grade reliability*

[Quick Start](#quick-start) • [Features](#features) • [Integrations](#integrations) • [Documentation](#documentation) • [Support](#support)

</div>

---

## 🌟 Overview

MCP Memory Server is a **production-ready** persistent memory system for AI assistants that enables:

- 🧠 **Persistent Memory** - Remember conversations across sessions
- ⚡ **Auto-Trigger System** - Intelligent automatic memory operations (NEW!)
- 🌩️ **Cloud Synchronization** - Sync memories across devices  
- 🔌 **Multi-Platform Support** - Works with Cursor, Claude, ChatGPT, and more
- 🏗️ **Production Architecture** - Scalable, secure, and reliable
- 📊 **Analytics Dashboard** - Monitor usage and insights
- 🔧 **Easy Integration** - One-click setup for popular AI tools

### 🚀 **NEW: Auto-Trigger System**
The revolutionary auto-trigger system makes memory management completely automatic:

- 🔤 **Keyword Detection**: Auto-saves when you say "ricorda", "importante", etc.
- 🔍 **Pattern Recognition**: Detects solutions, bug fixes, tutorials automatically  
- 🎯 **Semantic Similarity**: Auto-searches for relevant memories
- ⭐ **Importance Scoring**: Automatically determines what to save
- 📏 **Conversation Tracking**: Summarizes long conversations
- 🔄 **Context Changes**: Loads relevant memories when switching topics
- ⏰ **Time-Based**: Periodic proactive memory suggestions

**No more manual "remember this" - the system intelligently captures everything important!**

## 🚀 Quick Start

### Option 1: Auto-Trigger Server (NEW!)
```bash
# Clone the repository
git clone https://github.com/your-repo/mcp-memory-server.git
cd mcp-memory-server

# Start with Auto-Trigger System
python main_auto.py

# Test auto-triggers immediately
python test_auto_trigger.py
```

### Option 2: Docker (Recommended)
```bash
# Start with Docker
docker-compose up -d

# Access the dashboard
open http://localhost:3000
```

### Option 3: Local Installation
```bash
# Install dependencies
pip install -r requirements.txt
npm install --prefix frontend

# Start the server
python main.py

# Start the frontend (separate terminal)
cd frontend && npm start
```

### Option 3: One-Line Setup
```bash
curl -sSL https://raw.githubusercontent.com/your-repo/mcp-memory-server/main/setup.sh | bash
```

## ✨ Features

### 🏭 Production-Ready Architecture
- **Enhanced MCP Server** - Robust Model Context Protocol implementation
- **Cloud Infrastructure** - MongoDB Atlas integration with automatic provisioning
- **Health Monitoring** - Comprehensive health checks and metrics
- **Error Handling** - Graceful error recovery and retry logic
- **Security** - Encryption, authentication, and secure connections

### 🔌 AI Platform Integrations

#### Cursor IDE Integration
```json
// .cursor/mcp.json (auto-generated)
{
  "mcpServers": {
    "mcp-memory-server": {
      "command": "python",
      "args": ["-m", "mcp_memory_server"]
    }
  }
}
```

#### Claude Desktop Integration
```json
// claude_desktop_config.json (auto-generated)
{
  "mcpServers": {
    "mcp-memory-server": {
      "command": "python", 
      "args": ["-m", "mcp_memory_server"]
    }
  }
}
```

#### Browser Extension
- **Multi-Platform Support** - ChatGPT, Claude, Poe, Perplexity, Bing Chat
- **Real-time Suggestions** - Contextual memory recommendations
- **Auto-save** - Intelligent conversation saving
- **Cross-browser** - Chrome, Firefox, Safari, Edge

### 🌩️ Cloud Features
- **MongoDB Atlas** - Scalable cloud database
- **Cross-device Sync** - Access memories anywhere
- **Backup & Recovery** - Automatic backups
- **Usage Analytics** - Track memory usage and costs
- **Multi-tenant** - Secure user isolation

### 📊 Web Dashboard
- **Memory Management** - Create, edit, search memories
- **Analytics** - Usage insights and trends  
- **Integration Status** - Monitor all connected platforms
- **Settings** - Configure projects, importance, sync
- **Real-time Updates** - Live status and notifications

## 🔧 Installation & Setup

### Prerequisites
- Python 3.8+
- Node.js 16+ (for frontend)
- MongoDB (local or Atlas)
- Docker (optional)

### Detailed Setup

1. **Clone and Install**
   ```bash
   git clone https://github.com/your-repo/mcp-memory-server.git
   cd mcp-memory-server
   pip install -r requirements.txt
   ```

2. **Configure Environment**
   ```bash
   cp .env.example .env
   # Edit .env with your settings
   ```

3. **Initialize Database**
   ```bash
   # Local MongoDB
   python -c "from src.services.database_service import DatabaseService; import asyncio; asyncio.run(DatabaseService().initialize())"
   
   # Or setup cloud (interactive)
   python -m cloud.cloud_integration --setup
   ```

4. **Setup Integrations**
   ```bash
   # Setup all integrations
   python integrations/integration_manager.py setup
   
   # Or setup individually
   python integrations/ai-agents/cursor_integration.py setup
   python integrations/ai-agents/claude_integration.py setup
   ```

5. **Start Services**
   ```bash
   # Start MCP server
   python main.py
   
   # Start web dashboard (new terminal)
   cd frontend && npm start
   ```

## 🤖 Platform Integrations

### Cursor IDE
```bash
# Auto-setup Cursor integration
python integrations/ai-agents/cursor_integration.py setup

# Manual setup
# 1. Creates .cursor/mcp.json automatically
# 2. Restart Cursor
# 3. Memory tools available in AI chat
```

### Claude Desktop
```bash
# Auto-setup Claude integration  
python integrations/ai-agents/claude_integration.py setup

# Manual setup
# 1. Updates claude_desktop_config.json
# 2. Restart Claude Desktop
# 3. Access memory tools via MCP
```

### Browser Extension
```bash
# Load extension in Chrome/Firefox
# 1. Go to chrome://extensions
# 2. Enable Developer mode
# 3. Load unpacked: ./browser-extension/
# 4. Extension auto-connects to server
```

### API Integration
```python
# Direct API usage
import asyncio
from integrations.ai-agents import GPTMemoryIntegration

async def main():
    gpt = GPTMemoryIntegration()
    await gpt.start_integration()
    
    # Save conversation
    result = await gpt.process_conversation({
        'messages': [
            {'role': 'user', 'content': 'Remember this important fact'},
            {'role': 'assistant', 'content': 'I will remember that'}
        ]
    })
    
    # Search memories
    memories = await gpt.search_relevant_memories('important fact')
    print(f"Found {len(memories)} relevant memories")

asyncio.run(main())
```

## 📁 Project Structure

```
mcp-memory-server/
├── 🏗️ src/                          # Core server implementation
│   ├── config/                      # Configuration management
│   ├── core/                        # MCP server core
│   ├── services/                    # Business logic services
│   ├── models/                      # Data models
│   └── utils/                       # Utilities
├── 🌩️ cloud/                        # Cloud infrastructure
│   ├── cloud_integration.py        # Main cloud client
│   ├── mongodb_provisioner.py      # Database provisioning
│   └── cloud_config.example        # Configuration template
├── 🔌 integrations/                 # AI platform integrations
│   ├── ai-agents/                   # Individual integrations
│   │   ├── cursor_integration.py   # Cursor IDE
│   │   ├── claude_integration.py   # Claude Desktop
│   │   ├── gpt_integration.py      # GPT/OpenAI
│   │   └── base_integration.py     # Base integration class
│   └── integration_manager.py      # Unified management
├── 🌐 browser-extension/            # Browser extension
│   ├── manifest.json              # Extension manifest
│   ├── background.js               # Service worker
│   ├── content.js                  # Content script
│   └── popup.html                  # Extension popup
├── 🖥️ frontend/                     # Web dashboard
│   ├── src/components/             # React components
│   ├── package.json               # Dependencies
│   └── public/                     # Static assets
├── 🐳 docker-compose.yml           # Docker setup
├── 📋 requirements.txt             # Python dependencies
└── 📚 docs/                        # Documentation
```

## 🔧 Configuration

### Environment Variables
```bash
# Database
MONGODB_URI=mongodb://localhost:27017
MONGODB_DATABASE=mcp_memory

# Cloud (optional)
MONGODB_ATLAS_PUBLIC_KEY=your_key
MONGODB_ATLAS_PRIVATE_KEY=your_key
MONGODB_ATLAS_PROJECT_ID=your_project

# Server
SERVER_HOST=0.0.0.0
SERVER_PORT=8000
LOG_LEVEL=INFO

# Security
SECRET_KEY=your_secret_key
ENCRYPTION_ENABLED=true

# Features
CLOUD_SYNC_ENABLED=true
AUTO_SAVE_ENABLED=true
HEALTH_CHECK_INTERVAL=30
```

### Integration Settings
```json
// ~/.mcp_memory/integrations/cursor.json
{
  "auto_save_enabled": true,
  "importance_threshold": 0.5,
  "max_context_length": 4000,
  "memory_search_limit": 5,
  "triggers": {
    "trigger_type": "auto",
    "threshold": 0.7,
    "cooldown_seconds": 30
  }
}
```

## 📊 Monitoring & Analytics

### Health Checks
```bash
# Check server health
curl http://localhost:8000/health

# Check integration status
python integrations/integration_manager.py health

# View metrics
curl http://localhost:8000/metrics
```

### Web Dashboard
- **Real-time Status** - Server and integration health
- **Memory Analytics** - Usage patterns and trends
- **Search Interface** - Find and manage memories
- **Integration Management** - Configure platforms
- **Settings** - Customize behavior

## 🧪 Testing

### Run Tests
```bash
# Backend tests
python -m pytest tests/

# Frontend tests  
cd frontend && npm test

# Integration tests
python tests/test_integrations.py

# End-to-end tests
python tests/test_e2e.py
```

### Manual Testing
```bash
# Test MCP server
python -c "
import asyncio
from src.services.memory_service import MemoryService
async def test():
    service = MemoryService()
    result = await service.create_memory('Test memory', 0.8)
    print(f'Created memory: {result}')
asyncio.run(test())
"

# Test integrations
python integrations/integration_manager.py setup
```

## 🚀 Deployment

### Docker Production
```yaml
# docker-compose.prod.yml
version: '3.8'
services:
  mcp-server:
    build: .
    environment:
      - MONGODB_URI=mongodb+srv://...
      - LOG_LEVEL=INFO
    ports:
      - "8000:8000"
    restart: unless-stopped
    
  frontend:
    build: ./frontend
    ports:
      - "80:80"
    depends_on:
      - mcp-server
```

### Cloud Deployment
```bash
# Deploy to cloud provider
./deploy.sh production

# Or use Kubernetes
kubectl apply -f k8s/
```

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

### Development Setup
```bash
# Fork and clone
git clone https://github.com/your-username/mcp-memory-server.git

# Install dev dependencies
pip install -r requirements-dev.txt
npm install --prefix frontend

# Run in development mode
python main.py --debug
cd frontend && npm run dev
```

## 📚 Documentation

- [**API Reference**](docs/api.md) - Complete API documentation
- [**Integration Guide**](docs/integrations.md) - Platform integration details
- [**Cloud Setup**](docs/cloud.md) - Cloud deployment guide
- [**Troubleshooting**](docs/troubleshooting.md) - Common issues and solutions
- [**Architecture**](docs/architecture.md) - System design overview

## 🆘 Support

- **Issues** - [GitHub Issues](https://github.com/your-repo/mcp-memory-server/issues)
- **Discussions** - [GitHub Discussions](https://github.com/your-repo/mcp-memory-server/discussions)
- **Documentation** - [docs/](docs/)
- **Email** - support@your-domain.com

## 📄 License

MIT License - see [LICENSE](LICENSE) for details.

## 🙏 Acknowledgments

- **MCP Protocol** - Model Context Protocol specification
- **MongoDB** - Database and cloud infrastructure
- **OpenAI** - GPT integration support
- **Anthropic** - Claude integration support
- **Cursor** - IDE integration platform

---

<div align="center">

**Made with ❤️ for the AI community**

[⭐ Star us on GitHub](https://github.com/your-repo/mcp-memory-server) • [🐛 Report Issues](https://github.com/your-repo/mcp-memory-server/issues) • [💬 Join Discussions](https://github.com/your-repo/mcp-memory-server/discussions)

</div>