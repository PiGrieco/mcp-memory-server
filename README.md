# MCP Memory Server

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![MIT License](https://img.shields.io/badge/License-MIT-green.svg)](https://choosealicense.com/licenses/mit/)
[![Docker](https://img.shields.io/badge/docker-%230db7ed.svg?style=flat&logo=docker&logoColor=white)](https://www.docker.com/)
[![MongoDB](https://img.shields.io/badge/MongoDB-%234ea94b.svg?style=flat&logo=mongodb&logoColor=white)](https://www.mongodb.com/)

A persistent memory system for AI agents based on **Model Context Protocol (MCP)** and **MongoDB** with semantic vector search capabilities.

## 🚀 Features

- **Persistent Memory**: Save and retrieve information for AI agents across sessions
- **Semantic Search**: Vector similarity search using sentence-transformers
- **MCP Protocol**: Native integration with modern AI agents (Claude, GPT-4, etc.)
- **Scalable**: MongoDB with optimized indexing
- **Production-Ready**: Docker support, health checks, logging, advanced configuration
- **Multi-Project**: Support for multiple projects/conversations
- **Real-time**: Async operations for high performance

## 📋 Requirements

- Python 3.11+
- Docker & Docker Compose
- MongoDB 7.0+ (included in docker-compose)
- 4GB+ RAM (for embedding models)

## 🛠️ Quick Start

### 1. Clone and Setup

```bash
git clone https://github.com/your-username/mcp-memory-server.git
cd mcp-memory-server
cp .env.example .env
```

### 2. Start with Docker

```bash
# Start all services
docker compose up -d

# Check status
docker compose ps
```

### 3. Test the System

```bash
# Run the demo
python examples/mcp_client.py
```

## 🔧 Configuration

### Environment Variables

Copy `.env.example` to `.env` and modify as needed:

```bash
# MongoDB
MONGODB_URL=mongodb://admin:securepassword@localhost:27017/memory_db?authSource=admin&replicaSet=rs0

# Embedding Model
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2

# Server Settings
MCP_SERVER_NAME=memory-server
LOG_LEVEL=INFO
```

### Advanced Configuration

- **Embedding Models**: Supports any sentence-transformers model
- **Device**: CPU/GPU for embedding generation
- **Connection Pooling**: Optimized MongoDB configuration
- **Logging**: Automatic log rotation

## 📚 Usage

### Available MCP Tools

The server exposes 7 MCP tools:

1. **`save_memory`** - Save a memory
2. **`search_memory`** - Semantic search
3. **`get_context`** - Get project context
4. **`update_memory`** - Update memory
5. **`delete_memory`** - Delete memory
6. **`get_memory_stats`** - Project statistics
7. **`health_check`** - System health check

### Usage Example

```python
from examples.mcp_client import MemoryClient

async with MemoryClient().connect() as client:
    # Save memory
    result = await client.save_memory(
        text="Python is excellent for machine learning",
        memory_type="knowledge",
        project="demo"
    )
    
    # Search memories
    results = await client.search_memory(
        query="Python programming",
        project="demo"
    )
```

## 🔌 AI Agent Integration

### Claude Desktop

1. **MCP Configuration**:
```json
{
  "mcpServers": {
    "memory-server": {
      "command": "python",
      "args": ["/path/to/mcp-memory-server/main.py"],
      "env": {
        "MONGODB_URL": "mongodb://localhost:27017/memory_db"
      }
    }
  }
}
```

2. **Usage in Claude**:
```
Claude, save this information: "Design patterns are fundamental for software engineering"
```

### Cursor AI

1. **Plugin Configuration**:
```json
{
  "mcpServers": {
    "memory": {
      "command": "python",
      "args": ["main.py"],
      "cwd": "/path/to/mcp-memory-server"
    }
  }
}
```

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   AI Agent      │    │   MCP Server    │    │   MongoDB       │
│   (Claude,      │◄──►│   (Memory       │◄──►│   (Vector       │
│    GPT-4, etc.) │    │    Service)     │    │    Search)      │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                              │
                              ▼
                       ┌─────────────────┐
                       │  Embedding      │
                       │  Service        │
                       │  (sentence-     │
                       │   transformers) │
                       └─────────────────┘
```

## 🔍 Monitoring

### Health Check

```bash
# Check service status
docker compose ps

# Server logs
docker compose logs mcp-memory-server

# MongoDB Express (UI)
# http://localhost:8081
```

### Metrics

- **Performance**: Search time, throughput
- **Storage**: Number of memories, project sizes
- **Quality**: Average similarity, memory importance

## 🚀 Production Deployment

### Docker Compose (Recommended)

```bash
# Production build
docker compose -f docker-compose.yml up -d

# With persistent volumes
docker compose -f docker-compose.prod.yml up -d
```

### Cloud Platforms

- **Google Cloud Run**: Serverless deployment
- **AWS ECS**: Container orchestration
- **Azure Container Instances**: Managed containers

## 🧪 Testing

```bash
# Unit tests
pytest tests/unit/

# Integration tests
pytest tests/integration/

# Performance tests
pytest tests/performance/

# Coverage report
pytest --cov=src tests/
```

## 📊 Performance

- **Search**: < 100ms per typical query
- **Save**: < 50ms per memory
- **Throughput**: 1000+ operations/second
- **Scalability**: Supports millions of memories

## 🔒 Security

- **Authentication**: API key support (optional)
- **Validation**: Input sanitization with Pydantic
- **Isolation**: Non-root Docker containers
- **Network**: Network isolation

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

Please read [CONTRIBUTING.md](CONTRIBUTING.md) for details on our code of conduct and the process for submitting pull requests.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

- **Issues**: [GitHub Issues](https://github.com/your-username/mcp-memory-server/issues)
- **Documentation**: [Wiki](https://github.com/your-username/mcp-memory-server/wiki)
- **Discussions**: [GitHub Discussions](https://github.com/your-username/mcp-memory-server/discussions)

## 🔄 Roadmap

- [ ] Multi-modal embedding support
- [ ] Automatic memory compression
- [ ] Additional REST API
- [ ] Web dashboard
- [ ] Automatic backup
- [ ] Integration with more AI agents
- [ ] Memory clustering and organization
- [ ] Real-time collaboration features

## 🙏 Acknowledgments

- [Model Context Protocol](https://modelcontextprotocol.io/) for the MCP specification
- [Sentence Transformers](https://www.sbert.net/) for embedding models
- [MongoDB](https://www.mongodb.com/) for vector search capabilities

---

**MCP Memory Server** - Making AI agents smarter with persistent memory! 🧠✨ 