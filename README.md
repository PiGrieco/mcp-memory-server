# 🧠 MCP Memory Server

**Production-ready Model Context Protocol (MCP) Memory Server for AI Agents**

## 🎯 Overview

A sophisticated **Model Context Protocol (MCP) Memory Server** that provides persistent memory capabilities to AI agents and IDEs like Cursor. This server enables AI assistants to save, search, and retrieve contextual information across conversations using advanced semantic search with sentence transformers.

## ✨ Features

- **🔄 Full Server Mode**: Production-ready with MongoDB integration (no fallback modes)
- **🧠 Semantic Memory**: Advanced search using sentence transformers (all-MiniLM-L6-v2)
- **🔍 Vector Embeddings**: Intelligent memory retrieval with similarity matching
- **📊 Project-based Organization**: Separate memory spaces for different projects
- **⚡ Real-time Integration**: Seamless integration with Cursor IDE and other MCP clients
- **🌍 Environment-based Configuration**: Flexible deployment with .env settings
- **📈 Scalable Architecture**: MongoDB backend with async operations
- **🔒 Production Security**: Environment-based credentials and secure connections

## 🏗️ MCP Server Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    MCP Memory Server                        │
├─────────────────────────────────────────────────────────────┤
│  🔌 MCP Protocol Layer                                      │
│  ├── Tools: save_memory, search_memories, list_memories    │
│  ├── Resources: Memory status and metrics                  │
│  └── Prompts: Memory management prompts                    │
├─────────────────────────────────────────────────────────────┤
│  🧠 Memory Service Layer                                    │
│  ├── Memory Management (CRUD operations)                   │
│  ├── Project-based Organization                            │
│  └── Importance Scoring                                    │
├─────────────────────────────────────────────────────────────┤
│  🔍 Embedding Service Layer                                │
│  ├── Sentence Transformers (all-MiniLM-L6-v2)            │
│  ├── Vector Generation                                     │
│  └── Semantic Similarity Search                           │
├─────────────────────────────────────────────────────────────┤
│  💾 Database Service Layer                                 │
│  ├── MongoDB Connection (Motor/PyMongo)                   │
│  ├── Document Storage                                      │
│  └── Vector Index Management                              │
└─────────────────────────────────────────────────────────────┘
```

## ⚙️ Configuration

### 1. Environment Variables (.env)

Create a `.env` file in the project root:

```bash
# =============================================================================
# MCP Memory Server Configuration
# =============================================================================

# Project & Database Settings
PROJECT_NAME=cursor_project
DATABASE_NAME=mcp_memory_production

# MongoDB Configuration
MONGODB_URI=mongodb+srv://username:password@cluster.mongodb.net/?retryWrites=true&w=majority
MONGODB_DATABASE=mcp_memory_production
MONGODB_COLLECTION=memories

# Environment
ENVIRONMENT=production

# Embedding Model
EMBEDDING_MODEL=all-MiniLM-L6-v2
```

### 2. Cursor IDE Configuration (mcp.json)

Add this configuration to your Cursor IDE MCP settings:

```json
{
  "mcpServers": {
    "memory-server": {
      "command": "/path/to/your/project/.myenv/bin/python",
      "args": [
        "/path/to/your/project/mcp_memory_server.py"
      ]
    }
  }
}
```

**Configuration Location:**
- **macOS**: `~/Library/Application Support/Cursor/User/globalStorage/mcp.json`
- **Windows**: `%APPDATA%\Cursor\User\globalStorage\mcp.json`
- **Linux**: `~/.config/Cursor/User/globalStorage/mcp.json`

## 🛠️ Installation & Setup

### 1. Clone Repository
```bash
git clone https://github.com/AiGotsrl/mcp-memory-server.git
cd mcp-memory-server
```

### 2. Create Virtual Environment
```bash
python -m venv .myenv
source .myenv/bin/activate  # macOS/Linux
# or
.myenv\Scripts\activate     # Windows
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Environment
```bash
cp .env.example .env
# Edit .env with your MongoDB credentials and settings
```

### 5. Test Installation
```bash
python test_server.py
```

## 🔧 Function Documentation

### Core MCP Tools

#### 1. `save_memory`
**Purpose**: Save important information to persistent memory with semantic embeddings.

**Parameters**:
- `content` (string): The information to save
- `project` (string, optional): Project namespace (defaults to env PROJECT_NAME)
- `importance` (float, optional): Importance score 0.0-1.0 (default: 0.7)

**Returns**: Success message with memory ID and metadata

#### 2. `search_memories`
**Purpose**: Search stored memories using semantic similarity.

**Parameters**:
- `query` (string): Search query
- `max_results` (int, optional): Maximum results to return (default: 5)
- `similarity_threshold` (float, optional): Minimum similarity score (default: 0.3)
- `project` (string, optional): Project to search in

**Returns**: List of relevant memories with similarity scores

#### 3. `list_memories`
**Purpose**: List all stored memories in the current project.

**Parameters**: None

**Returns**: Complete list of memories with metadata and embedding status

#### 4. `memory_status`
**Purpose**: Check memory system status and configuration.

**Parameters**: None

**Returns**: System status including mode, project, database, and memory count

## 🧪 Testing Prompts & Expected Outputs

### Test 1: Save Memory
**Prompt**: "Save this to memory: I'm working on integrating MCP Memory Server with Cursor IDE for better AI assistance"

**Expected Output**:
```json
{
  "success": true,
  "message": "Memory saved successfully",
  "data": {
    "memory_id": "689356b8e3c8e49b289c8bf0",
    "project": "cursor_project",
    "importance": 0.7,
    "memory_type": "conversation"
  }
}
```

### Test 2: Search Memories
**Prompt**: "Search my memories for 'MCP integration'"

**Expected Output**:
```
🔍 Found 1 memories:
- ID: 689356b8e3c8e49b289c8bf0 (Similarity: 0.85)
  Content: I'm working on integrating MCP Memory Server with Cursor IDE for better AI assistance
  Project: cursor_project
  Created: 2025-08-06 13:20:56
```

### Test 3: List All Memories
**Prompt**: "List all my saved memories"

**Expected Output**:
```
📚 1 memories stored:
- 689356b8e3c8e49b289c8bf0: I'm working on integrating MCP Memory Server with Cursor IDE... (embedding: ✅)
```

### Test 4: Memory Status
**Prompt**: "Check memory system status"

**Expected Output**:
```
🧠 Memory System Status:
- Mode: Full Server
- Project: cursor_project
- Database: mcp_memory_production
- Memories stored: 1
- Working directory: /Users/awais/Desktop/Upworking/Grieco/mcp-memory-server
```

### Test 5: Complex Search
**Prompt**: "Search for memories about 'AI' with high similarity"

**Expected Output**:
```
🔍 Found 1 memories matching 'AI':
- ID: 689356b8e3c8e49b289c8bf0 (Similarity: 0.92)
  Content: I'm working on integrating MCP Memory Server with Cursor IDE for better AI assistance
  Importance: 0.7
  Tags: [conversation, integration, AI]
```

## 📁 Project Structure

```
mcp-memory-server/
├── mcp_memory_server.py          # Main MCP server
├── test_server.py                # Testing script
├── requirements.txt              # Dependencies
├── .env                          # Environment configuration
├── README.md                     # This file
└── src/
    ├── __init__.py
    ├── services/
    │   ├── __init__.py
    │   ├── database_service.py    # MongoDB operations
    │   ├── embedding_service.py   # Sentence transformers
    │   └── memory_service.py      # Memory management
    └── models/
        ├── __init__.py
        └── memory.py              # Memory data models
```

## ✅ Production Features

- **🔒 Security**: Environment-based credentials, secure MongoDB connections
- **📈 Performance**: Async operations, efficient vector search
- **🔄 Reliability**: Full Server mode only, no fallback dependencies
- **📊 Monitoring**: Comprehensive logging and status reporting
- **🌍 Scalability**: MongoDB backend, project-based organization
- **🧠 Intelligence**: Advanced semantic search with sentence transformers

---

**🚀 Ready for production deployment with Cursor IDE and other MCP clients!**
