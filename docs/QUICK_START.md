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

### **HTTP Proxy Server** (Enhanced Auto-Trigger)
- **Protocol:** HTTP Proxy with auto-interception
- **Port:** 8080
- **Endpoints:** `/proxy/cursor`, `/proxy/claude`, `/proxy/universal`
- **Features:** Automatic message analysis, context enhancement, seamless UX
- **Usage:** Route AI platform requests through proxy for auto-trigger

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

### **HTTP Proxy Configuration** (Enhanced Mode)
```bash
# Start HTTP Proxy for auto-interception
./scripts/main.sh server proxy

# Or start both MCP + Proxy
./scripts/main.sh server both
```

**Usage Examples:**
```bash
# Route Cursor requests through proxy
curl -X POST http://localhost:8080/proxy/cursor \
  -H "Content-Type: application/json" \
  -d '{"message": "Remember this database config: host=localhost, port=5432"}'

# Route Claude requests through proxy  
curl -X POST http://localhost:8080/proxy/claude \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Save this API key configuration"}'
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

# HTTP Proxy
PROXY_HOST=0.0.0.0
PROXY_PORT=8080

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
python -c "
import asyncio
from mcp_memory_server import MCPServer

async def test():
    server = MCPServer()
    await server.start()
    # Test memory operations
    await server.save_memory('Test memory content', 'test_project')
    memories = await server.search_memories('test')
    print(f'Found {len(memories)} memories')
    await server.stop()

asyncio.run(test())
"

# Test HTTP API
curl -X POST http://localhost:8000/memories/ \
  -H "Content-Type: application/json" \
  -d '{"content": "Test memory", "project": "test"}'

curl http://localhost:8000/memories/search?q=test
```

## 🔍 **Monitoring**

```bash
# Health check
curl http://localhost:8000/health

# Server info
curl http://localhost:8000/info

# MCP capabilities
curl http://localhost:8000/mcp/capabilities
```

## 🚀 **Production Deployment**

### **Docker Compose**
```yaml
# docker-compose.yml
version: '3.8'
services:
  mcp-memory-server:
    build: .
    ports:
      - "8000:8000"
    environment:
      - MONGODB_URI=mongodb://mongo:27017
      - ENVIRONMENT=production
    depends_on:
      - mongo
      - redis

  mongo:
    image: mongo:6.0
    volumes:
      - mongo_data:/data/db

  redis:
    image: redis:7-alpine
    volumes:
      - redis_data:/data

volumes:
  mongo_data:
  redis_data:
```

### **Kubernetes**
```yaml
# deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: mcp-memory-server
spec:
  replicas: 3
  selector:
    matchLabels:
      app: mcp-memory-server
  template:
    metadata:
      labels:
        app: mcp-memory-server
    spec:
      containers:
      - name: mcp-memory-server
        image: mcp-memory-server:latest
        ports:
        - containerPort: 8000
        env:
        - name: ENVIRONMENT
          value: "production"
        - name: MONGODB_URI
          valueFrom:
            secretKeyRef:
              name: mongo-secret
              key: uri
```

## 📊 **Performance Tuning**

### **Memory Optimization**
```bash
# Increase memory limits
export MCP_MEMORY_LIMIT=4GB
export MCP_CACHE_SIZE=2GB

# Optimize embedding model
export EMBEDDING_MODEL=all-MiniLM-L6-v2  # Fast and efficient
export EMBEDDING_BATCH_SIZE=128
```

### **Database Optimization**
```bash
# MongoDB indexes
db.memories.createIndex({"embeddings": "vector"})
db.memories.createIndex({"project": 1})
db.memories.createIndex({"created_at": -1})

# Connection pooling
export MONGODB_MAX_POOL_SIZE=20
export MONGODB_MIN_POOL_SIZE=5
```

## 🔒 **Security**

### **Authentication**
```bash
# Enable JWT authentication
export JWT_SECRET=your-secret-key
export JWT_EXPIRY=3600

# API key authentication
export API_KEY_REQUIRED=true
export API_KEY=your-api-key
```

### **CORS Configuration**
```bash
# Configure CORS
export CORS_ORIGINS=https://your-domain.com
export CORS_METHODS=GET,POST,PUT,DELETE
export CORS_HEADERS=*
```

## 📈 **Scaling**

### **Horizontal Scaling**
```bash
# Multiple instances
docker-compose up -d --scale mcp-memory-server=3

# Load balancer
nginx -s reload
```

### **Database Scaling**
```bash
# MongoDB replica set
export MONGODB_URI=mongodb://mongo1:27017,mongo2:27017,mongo3:27017

# Redis cluster
export REDIS_CLUSTER=true
export REDIS_NODES=redis1:6379,redis2:6379,redis3:6379
```

## 🔧 **Troubleshooting**

### **Common Issues**

#### **1. MongoDB Connection**
```bash
# Check MongoDB status
docker exec mongo mongosh --eval "db.runCommand('ping')"

# Check connection string
echo $MONGODB_URI
```

#### **2. Memory Issues**
```bash
# Check memory usage
docker stats mcp-memory-server

# Increase memory limits
docker-compose down
docker-compose up -d --scale mcp-memory-server=1
```

#### **3. Performance Issues**
```bash
# Check logs
docker logs mcp-memory-server

# Monitor metrics
curl http://localhost:8000/metrics
```

### **Debug Mode**
```bash
# Enable debug logging
export LOG_LEVEL=DEBUG
export DEBUG=true

# Restart with debug
docker-compose restart mcp-memory-server
```

## 📚 **Next Steps**

### **1. Advanced Configuration**
- [Environment Configuration](docs/environments.md)
- [Plugin Development](docs/plugins/README.md)
- [API Reference](docs/development/api.md)

### **2. Integration**
- [Cursor Integration](docs/integrations/cursor.md)
- [Claude Integration](docs/integrations/claude.md)
- [Custom Platform Integration](docs/integrations/universal.md)

### **3. Monitoring**
- [Health Checks](docs/operations/monitoring.md)
- [Logging](docs/operations/logs.md)
- [Metrics](docs/operations/metrics.md)

### **4. Development**
- [Development Guide](docs/development/guide.md)
- [Testing](docs/development/testing.md)
- [Deployment](docs/development/deploy.md)

## 🆘 **Support**

### **Getting Help**
- **Documentation**: [docs/](docs/)
- **Issues**: [GitHub Issues](https://github.com/your-repo/mcp-memory-server/issues)
- **Discord**: [Discord Server]
- **Email**: support@mcp-memory-server.com

### **Community**
- **GitHub Discussions**: [Discussions](https://github.com/your-repo/mcp-memory-server/discussions)
- **Stack Overflow**: Tag with `mcp-memory-server`
- **Reddit**: r/MCPMemoryServer

---

**🎉 You're now ready to use the MCP Memory Server in production!**
