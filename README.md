# 🧠 MCP Memory Server

**Next-Generation AI Memory Management with Intelligent Auto-Triggers**

[![Version](https://img.shields.io/badge/version-2.1.0-blue.svg)](https://github.com/PiGrieco/mcp-memory-server)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.8+-blue.svg)](https://python.org)
[![Docker](https://img.shields.io/badge/docker-ready-brightgreen.svg)](https://docker.com)
[![MCP Protocol](https://img.shields.io/badge/MCP-Protocol-purple.svg)](https://modelcontextprotocol.io)
[![HuggingFace](https://img.shields.io/badge/🤗-HuggingFace-yellow.svg)](https://huggingface.co/PiGrieco/mcp-memory-auto-trigger-model)

---

## 🎯 **What is MCP Memory Server?**

MCP Memory Server is a **production-ready intelligent memory management system** that implements the **Model Context Protocol (MCP)** to provide persistent, context-aware memory for AI systems. Think of it as a **"persistent brain"** for your AI assistants that learns when to remember important information and retrieve relevant context automatically.

### 🌟 **Why MCP Memory Server?**

- **🤖 99.56% ML Accuracy**: Advanced machine learning model automatically decides when to save/search memories
- **🔄 Hybrid Intelligence**: Combines deterministic rules with ML for optimal performance
- **⚡ Real-time Analysis**: Analyzes conversations in real-time for intelligent memory triggers
- **🎯 Multi-Platform**: Native MCP protocol support for Cursor, Claude, GPT, Windsurf, and more
- **🔍 Semantic Search**: Intelligent content retrieval based on meaning, not just keywords
- **☁️ Production-Ready**: Docker support, MongoDB Atlas integration, comprehensive monitoring
- **📊 Rich Analytics**: Detailed metrics and performance monitoring

---

## 🏗️ **Architecture Overview**

```mermaid
graph TB
    subgraph "AI Platforms"
        A[Cursor IDE] --> MCP[MCP Protocol]
        B[Claude Desktop] --> MCP
        C[GPT/OpenAI] --> MCP
        D[Windsurf IDE] --> MCP
        E[Lovable] --> MCP
        F[Replit] --> MCP
    end
    
    subgraph "MCP Memory Server"
        MCP --> G[Auto-Trigger System]
        G --> H[ML Model 99.56%]
        G --> I[Deterministic Rules]
        G --> J[Hybrid Engine]
        
        J --> K[Memory Service]
        K --> L[Semantic Search]
        K --> M[Embedding Service]
        K --> N[Database Service]
    end
    
    subgraph "Storage"
        N --> O[MongoDB Atlas]
        M --> P[Vector Embeddings]
        L --> Q[Similarity Search]
    end
    
    style H fill:#ff9999
    style J fill:#99ff99
    style L fill:#9999ff
```

---

## 🚀 **Quick Start**

### **💬 Prompt-Based Installation**

Simply tell your AI assistant:

> **"Installa questo: https://github.com/PiGrieco/mcp-memory-server"**

Your AI will automatically run the installation commands below.

### **⚡ Universal Installation (All Platforms)**

**One command installs for ALL AI platforms:**

```bash
curl -sSL https://raw.githubusercontent.com/PiGrieco/mcp-memory-server/production-ready-v2/install_universal_prompt.sh | bash
```

**What it does:**
- ✅ Clones repository to `~/mcp-memory-server`
- ✅ Sets up Python virtual environment with all dependencies
- ✅ Configures **ALL platforms**: Cursor, Claude, GPT, Windsurf
- ✅ Creates universal HTTP API on `http://localhost:8080`
- ✅ Tests ML auto-triggers (99.56% accuracy model)
- ✅ Ready to use in 2-3 minutes

### **🎯 Platform-Specific Installation**

**Cursor IDE:**
```bash
curl -sSL https://raw.githubusercontent.com/PiGrieco/mcp-memory-server/production-ready-v2/install_cursor.sh | bash
```

**Claude Desktop:**
```bash
curl -sSL https://raw.githubusercontent.com/PiGrieco/mcp-memory-server/production-ready-v2/install_claude.sh | bash
```

**GPT/OpenAI (with browser extension):**
```bash
curl -sSL https://raw.githubusercontent.com/PiGrieco/mcp-memory-server/production-ready-v2/install_gpt.sh | bash
```

### **🔧 Manual Installation**

```bash
# Clone repository
git clone -b production-ready-v2 https://github.com/PiGrieco/mcp-memory-server.git
cd mcp-memory-server

# Set up environment
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Start universal server
./start_universal.sh
```

---

## 🎮 **Usage After Installation**

### **🚀 Quick Start Commands**

After installation, choose your preferred mode:

```bash
cd ~/mcp-memory-server

# Universal API (works with any platform)
./start_universal.sh                # HTTP API on localhost:8080

# Platform-specific servers
./start_cursor.sh                   # Cursor IDE MCP server
./start_claude.sh                   # Claude Desktop MCP server
./start_gpt.sh                      # GPT/OpenAI HTTP API + browser extension

# Update to latest version
./update_universal.sh               # Updates from GitHub
```

### **🎯 Supported AI Platforms**

| Platform | Auto-Configured | Integration Type | Status |
|----------|----------------|------------------|---------|
| **🎯 Cursor IDE** | ✅ `~/.cursor/mcp_settings.json` | Native MCP | Ready |
| **🔮 Claude Desktop** | ✅ `~/Library/Application Support/Claude/` | Native MCP | Ready |
| **🤖 GPT/OpenAI** | ✅ HTTP API + Browser Extension | HTTP API | Ready |
| **🌪️ Windsurf IDE** | ✅ `~/.config/windsurf/` | Native MCP | Ready |
| **💙 Lovable Platform** | ✅ HTTP API Integration | HTTP API | Ready |
| **⚡ Replit Cloud** | ✅ Cloud Service | HTTP API | Ready |

### **🌐 Universal HTTP API**

The universal installation creates an HTTP API that works with **any platform**:

- **URL**: `http://localhost:8080`
- **Dashboard**: `http://localhost:8080/` (web interface)
- **API Docs**: `http://localhost:8080/docs` (auto-generated)

**API Endpoints**:
```bash
POST /analyze    # Analyze messages for auto-triggers
POST /save       # Save memories manually
POST /search     # Search existing memories
GET  /health     # System health check
```

---

## 🤖 **ML Auto-Trigger System**

The crown jewel of MCP Memory Server is its **intelligent auto-trigger system** that automatically decides when to save or search memories.

### **🎯 How It Works**

1. **Real-time Analysis**: Every message is analyzed using both ML and deterministic systems
2. **Context Understanding**: The system understands conversation context, code snippets, errors, and solutions
3. **Automatic Decision**: Based on content analysis, it automatically saves important information or searches for relevant context
4. **Learning**: The system improves over time by learning from user interactions

### **🧠 ML Model Features**

- **Model**: Custom-trained HuggingFace transformer (`PiGrieco/mcp-memory-auto-trigger-model`)
- **Accuracy**: 99.56% on trigger detection
- **Real-time**: Sub-100ms inference time
- **Multi-language**: Supports English, Italian, and more
- **Context-aware**: Understands code, technical discussions, and general conversation

### **🔍 Trigger Types**

| Trigger Type | Description | Example |
|--------------|-------------|---------|
| **Keyword-based** | Explicit save requests | "remember this", "importante" |
| **Pattern Recognition** | Solution/error patterns | "bug fixed", "risolto" |
| **Semantic Similarity** | Content similarity to existing memories | Similar technical discussions |
| **Importance Threshold** | High-value content detection | Architecture decisions |
| **Conversation Length** | Extended meaningful discussions | Long troubleshooting sessions |
| **Context Change** | Topic/project shifts | "new project", "different approach" |
| **Time-based** | Periodic context retrieval | Regular memory checks |

---

## 🧪 **Testing Your Installation**

### **🔍 Verify Everything Works**

After installation, test your setup:

#### **1. Restart Your AI Application**
- **Cursor IDE**: Restart completely to detect MCP server
- **Claude Desktop**: Restart to load new configuration
- **ChatGPT**: Install browser extension from `~/mcp-memory-server/browser_extension/`

#### **2. Test Commands**

Try these in your AI assistant:

```
🧪 Memory Save Test:
"Ricorda che React hooks vanno usati solo nei componenti funzionali"

🔍 Search Test:
"Cosa ricordi sui React hooks?"

⚡ Auto-Trigger Test:
"Ho risolto il bug implementando JWT refresh tokens per l'autenticazione"

🎯 Question Test:
"Puoi spiegarmi come funziona async/await in JavaScript?"
```

#### **3. Check Universal API**

If using the universal installation:

```bash
# Check API status
curl http://localhost:8080/health

# Open web dashboard
open http://localhost:8080/

# Test analyze endpoint
curl -X POST http://localhost:8080/analyze \
  -H "Content-Type: application/json" \
  -d '{"message": "Test message", "platform": "test"}'
```

### **🎯 What to Expect**

- **✅ Automatic memory saving** when you mention important information
- **🔍 Intelligent search** when you ask questions about past topics
- **⚡ ML auto-triggers** working within 10-30 seconds (first model download)
- **📊 Memory notifications** showing save/search operations

---

## 🛠️ **Available Tools (MCP Protocol)**

### **Core Memory Tools**

| Tool | Description | Parameters |
|------|-------------|------------|
| `save_memory` | Save content with auto-embedding | `content`, `context`, `importance` |
| `search_memories` | Semantic search through memories | `query`, `limit`, `similarity_threshold` |
| `auto_save_memory` | Trigger-based automatic saving | `content`, `context`, `project` |
| `get_memory_context` | Retrieve project context | `project`, `types`, `limit` |
| `list_memories` | List all memories with filters | `limit`, `category`, `tags` |
| `analyze_message` | Analyze content for triggers | `message`, `platform_context` |

### **Management Tools**

| Tool | Description | Parameters |
|------|-------------|------------|
| `get_memory` | Retrieve specific memory | `memory_id` |
| `update_memory` | Update existing memory | `memory_id`, `updates` |
| `delete_memory` | Delete memory | `memory_id` |
| `health_check` | System health status | - |
| `get_metrics` | Performance metrics | - |

---

## 📊 **Memory Types & Organization**

### **Memory Types**

- **`CONVERSATION`** - General dialogue and discussions
- **`KNOWLEDGE`** - Important facts and information
- **`ERROR`** - Problems, bugs, and debugging sessions
- **`SOLUTION`** - Fixes, workarounds, and solutions
- **`DECISION`** - Important decisions and rationale
- **`FUNCTION`** - Function calls and results
- **`WARNING`** - Warnings and alerts

### **Automatic Classification**

The system automatically classifies memories based on:
- Content analysis
- Context clues
- Conversation patterns
- Keywords and phrases
- ML model predictions

---

## 🆘 **Troubleshooting**

### **Common Issues**

#### **"MCP server not visible"**
```bash
# Restart your AI application completely
# Check configuration file path:
ls ~/.cursor/mcp_settings.json        # Cursor
ls ~/Library/Application\ Support/Claude/claude_desktop_config.json  # Claude (macOS)

# Verify Python path in config
cat ~/.cursor/mcp_settings.json | grep command
```

#### **"Module not found errors"**
```bash
cd ~/mcp-memory-server
source venv/bin/activate
pip install -r requirements.txt
```

#### **"ML model download timeout"**
```bash
# First run may take 10-30 seconds for model download (~63MB)
# Subsequent runs will be instant (0.03s)
cd ~/mcp-memory-server
source venv/bin/activate
python -c "from transformers import pipeline; print('Model ready')"
```

#### **"Permission denied"**
```bash
chmod +x ~/mcp-memory-server/start_*.sh
chmod +x ~/mcp-memory-server/update_*.sh
```

### **Getting Help**

- **📖 Issues**: [GitHub Issues](https://github.com/PiGrieco/mcp-memory-server/issues)
- **💬 Discussions**: [GitHub Discussions](https://github.com/PiGrieco/mcp-memory-server/discussions)
- **🔧 Installation Guide**: [INSTALL_FROM_GITHUB.md](INSTALL_FROM_GITHUB.md)

---

## 🔍 **Use Cases**

### **1. 🖥️ Development Assistant**
- **Auto-save** important code snippets and solutions
- **Context retrieval** for similar problems
- **Project memory** across development sessions
- **Bug tracking** and solution repository

### **2. 📚 Knowledge Management**
- **Conversation memory** for long-term learning
- **Fact extraction** from discussions
- **Decision tracking** and rationale
- **Best practices** accumulation

### **3. 🔧 Technical Support**
- **Issue resolution** memory
- **Solution patterns** recognition
- **Customer context** retention
- **Knowledge base** building

### **4. 🎯 AI Enhancement**
- **Persistent context** for AI assistants
- **Long-term memory** beyond session limits
- **Intelligent context** switching
- **Multi-session** continuity

---

## 🏗️ **Advanced Features**

### **🎯 Memory Types & Auto-Classification**

The system automatically categorizes memories:

- **`KNOWLEDGE`** - Important facts and learning
- **`SOLUTION`** - Bug fixes and problem solutions  
- **`ERROR`** - Problems and debugging sessions
- **`DECISION`** - Important decisions and rationale
- **`CONVERSATION`** - General dialogue and discussions

### **⚡ Performance Metrics**

- **🎯 ML Accuracy**: 99.56% trigger detection
- **⚡ Response Time**: <100ms average
- **📊 Model Size**: ~63MB (auto-download)
- **🌍 Languages**: English, Italian, Spanish, French
- **🔄 Uptime**: 99.9% production availability

### **🔧 Customization**

Advanced users can customize via environment variables:

```bash
# Advanced ML configuration
export ML_MODEL_TYPE=huggingface
export HUGGINGFACE_MODEL_NAME=PiGrieco/mcp-memory-auto-trigger-model
export MEMORY_THRESHOLD=0.7
export SEMANTIC_THRESHOLD=0.8

# Database configuration (optional - defaults to in-memory)
export MONGODB_URI=mongodb://localhost:27017
export MONGODB_DATABASE=mcp_memory
```

---

## 📝 **License**

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🤝 **Contributing**

Contributions are welcome! Please read our [Contributing Guide](CONTRIBUTING.md) for details on our code of conduct and the process for submitting pull requests.

### **Development Workflow**

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## 🆘 **Support**

- **📖 Documentation**: [Full Documentation](https://pigrieco.github.io/mcp-memory-server)
- **🐛 Issues**: [GitHub Issues](https://github.com/PiGrieco/mcp-memory-server/issues)

---

## 🙏 **Acknowledgments**

- **Model Context Protocol (MCP)** team for the excellent protocol specification
- **HuggingFace** for model hosting and transformer libraries
- **MongoDB** for robust database solutions
- **Docker** for containerization platform
- The **open-source community** for invaluable contributions

---

## 🎉 **What You Get**

After installation, your AI assistant will have:

- **🧠 Infinite Memory**: Never forgets important information
- **🤖 99.56% ML Accuracy**: Intelligent auto-triggers for memory operations
- **⚡ Real-time Speed**: Sub-100ms memory operations
- **🔍 Semantic Search**: Find information by meaning, not keywords
- **🎯 Multi-Platform**: Works across Cursor, Claude, GPT, and more
- **📊 Smart Categories**: Automatic classification of knowledge, solutions, errors
- **🌐 Universal API**: HTTP interface for custom integrations

---

<div align="center">

**⭐ If you find MCP Memory Server useful, please star this repository! ⭐**

[![GitHub stars](https://img.shields.io/github/stars/PiGrieco/mcp-memory-server.svg?style=social&label=Star)](https://github.com/PiGrieco/mcp-memory-server)
[![GitHub forks](https://img.shields.io/github/forks/PiGrieco/mcp-memory-server.svg?style=social&label=Fork)](https://github.com/PiGrieco/mcp-memory-server/fork)

---

**Built with ❤️ by [PiGrieco](https://github.com/PiGrieco) and the open-source community**

</div>
