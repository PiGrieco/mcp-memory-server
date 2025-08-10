# 🔌 API Reference - MCP Memory Server

## Overview

The MCP Memory Server provides both MCP protocol tools and HTTP REST API endpoints for memory management with intelligent auto-triggering capabilities.

## MCP Tools

### save_memory

Save important information to the memory system.

**Input Schema:**
```json
{
  "type": "object",
  "properties": {
    "content": {
      "type": "string",
      "description": "Information to save"
    },
    "project": {
      "type": "string", 
      "description": "Project name",
      "default": "default"
    },
    "importance": {
      "type": "number",
      "description": "Importance score (0.0-1.0)",
      "default": 0.7
    },
    "memory_type": {
      "type": "string",
      "enum": ["conversation", "knowledge", "decision", "solution", "error"],
      "default": "conversation"
    },
    "tags": {
      "type": "array",
      "items": {"type": "string"},
      "description": "Tags for categorization"
    },
    "metadata": {
      "type": "object",
      "description": "Additional metadata"
    }
  },
  "required": ["content"]
}
```

**Example:**
```python
await client.call_tool("save_memory", {
    "content": "Use useCallback to optimize React re-renders",
    "project": "react-optimization",
    "importance": 0.8,
    "memory_type": "knowledge",
    "tags": ["react", "performance", "optimization"],
    "metadata": {"source": "code_review", "date": "2024-01-15"}
})
```

### search_memories

Search for relevant memories using semantic similarity.

**Input Schema:**
```json
{
  "type": "object", 
  "properties": {
    "query": {
      "type": "string",
      "description": "Search query"
    },
    "project": {
      "type": "string",
      "description": "Project to search in"
    },
    "max_results": {
      "type": "integer",
      "minimum": 1,
      "maximum": 100,
      "default": 5
    },
    "similarity_threshold": {
      "type": "number",
      "minimum": 0.0,
      "maximum": 1.0,
      "default": 0.3
    },
    "memory_types": {
      "type": "array",
      "items": {"type": "string"},
      "description": "Filter by memory types"
    },
    "tags": {
      "type": "array", 
      "items": {"type": "string"},
      "description": "Filter by tags"
    }
  },
  "required": ["query"]
}
```

**Example:**
```python
await client.call_tool("search_memories", {
    "query": "React performance optimization",
    "project": "react-optimization", 
    "max_results": 10,
    "similarity_threshold": 0.7,
    "memory_types": ["knowledge", "solution"],
    "tags": ["react", "performance"]
})
```

### list_memories

List all saved memories with optional filtering.

**Input Schema:**
```json
{
  "type": "object",
  "properties": {
    "project": {
      "type": "string", 
      "description": "Filter by project"
    },
    "memory_type": {
      "type": "string",
      "description": "Filter by memory type"
    },
    "limit": {
      "type": "integer",
      "minimum": 1,
      "maximum": 1000,
      "default": 50
    },
    "offset": {
      "type": "integer",
      "minimum": 0,
      "default": 0
    }
  }
}
```

### memory_status

Get system status and statistics.

**Input Schema:**
```json
{
  "type": "object",
  "properties": {},
  "additionalProperties": false
}
```

**Response includes:**
- Total memory count
- Memory count by project
- Memory count by type
- System health status
- Auto-trigger statistics
- Database connection status
- Embedding model status

## Auto-Trigger Configuration

### Environment Variables

```bash
# Auto-trigger settings
AUTO_TRIGGER_ENABLED=true
TRIGGER_KEYWORDS="ricorda,nota,importante,salva,memorizza,remember"
SOLUTION_PATTERNS="risolto,solved,fixed,bug fix,solution"
AUTO_SAVE_THRESHOLD=0.7
SEMANTIC_THRESHOLD=0.8
TRIGGER_COOLDOWN=30

# Database settings
MONGODB_URI="mongodb://localhost:27017"
MONGODB_DATABASE="mcp_memory"
MONGODB_COLLECTION="memories"

# Embedding settings
EMBEDDING_MODEL="all-MiniLM-L6-v2"
EMBEDDING_DEVICE="cpu"
MODEL_CACHE_DIR="./models"

# Server settings
SERVER_HOST="0.0.0.0"
SERVER_PORT=8000
LOG_LEVEL="INFO"
```

### Auto-Trigger Rules

The system automatically triggers based on:

1. **Keyword Detection**
   - Keywords: `ricorda`, `nota`, `importante`, `salva`, `memorizza`, `remember`
   - Action: Auto-save with high importance

2. **Pattern Recognition**  
   - Patterns: `risolto`, `solved`, `fixed`, `bug fix`, `solution`
   - Action: Auto-save as solution type

3. **Semantic Similarity**
   - Threshold: 0.8+ similarity with existing memories
   - Action: Auto-search and provide context

4. **Importance Analysis**
   - Threshold: 0.7+ calculated importance score
   - Action: Auto-save with priority flag

5. **Conversation Length**
   - Trigger: 5+ substantial messages
   - Action: Auto-summarize conversation

6. **Context Changes**
   - Keywords: `nuovo progetto`, `new project`, `different`
   - Action: Load relevant project memories

7. **Time-based**
   - Interval: Every 10 minutes of active conversation
   - Action: Proactive memory suggestions

## HTTP REST API

When running with HTTP mode enabled:

### POST /memories
Create a new memory.

```bash
curl -X POST http://localhost:8000/memories \
  -H "Content-Type: application/json" \
  -d '{
    "content": "Important information",
    "project": "my-project",
    "importance": 0.8
  }'
```

### GET /memories/search
Search memories.

```bash
curl "http://localhost:8000/memories/search?query=timeout&limit=5"
```

### GET /memories
List memories.

```bash
curl "http://localhost:8000/memories?project=my-project&limit=10"
```

### GET /status
Get system status.

```bash
curl http://localhost:8000/status
```

## Error Handling

### Common Error Codes

| Code | Description | Solution |
|------|-------------|----------|
| `EMBEDDING_ERROR` | Embedding generation failed | Check model and device |
| `DATABASE_ERROR` | Database connection failed | Verify MongoDB connection |
| `VALIDATION_ERROR` | Invalid input parameters | Check input schema |
| `AUTO_TRIGGER_ERROR` | Auto-trigger system failed | Check trigger configuration |

### Error Response Format

```json
{
  "error": {
    "code": "EMBEDDING_ERROR",
    "message": "Failed to generate embedding for text",
    "details": {
      "text_length": 0,
      "model_status": "uninitialized"
    }
  }
}
```

## Performance

### Optimization Settings

```bash
# Embedding batch size
EMBEDDING_BATCH_SIZE=32

# Database connection pooling  
MONGODB_MAX_POOL_SIZE=10
MONGODB_MIN_POOL_SIZE=1

# Memory caching
MEMORY_CACHE_SIZE=1000
EMBEDDING_CACHE_SIZE=5000

# Auto-trigger performance
TRIGGER_ANALYSIS_INTERVAL=1.0
MAX_CONVERSATION_BUFFER=50
```

### Monitoring Metrics

- **Memory operations/sec**
- **Embedding generation time**
- **Database query time** 
- **Auto-trigger hit rate**
- **Cache hit rate**
- **Active conversation buffers**

## Integration Examples

### Python Client
```python
import asyncio
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

class MemoryClient:
    def __init__(self, server_path="main_simple.py"):
        self.server_path = server_path
        
    async def __aenter__(self):
        server_params = StdioServerParameters(
            command="python",
            args=[self.server_path]
        )
        
        self.read_stream, self.write_stream = await stdio_client(server_params)
        self.client = ClientSession(self.read_stream, self.write_stream)
        await self.client.initialize()
        return self.client
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.client.close()

# Usage
async def main():
    async with MemoryClient() as client:
        # Save memory
        await client.call_tool("save_memory", {
            "content": "Important information",
            "importance": 0.8
        })
        
        # Search memories
        results = await client.call_tool("search_memories", {
            "query": "information"
        })
        
        print(results)

asyncio.run(main())
```

### JavaScript/Node.js Client
```javascript
const { spawn } = require('child_process');
const { createInterface } = require('readline');

class MCPMemoryClient {
    constructor(serverPath = 'main_simple.py') {
        this.serverPath = serverPath;
        this.requestId = 0;
    }
    
    async connect() {
        this.process = spawn('python', [this.serverPath]);
        this.readline = createInterface({
            input: this.process.stdout,
            output: this.process.stdin
        });
        
        // Initialize
        await this.sendRequest('initialize', {});
    }
    
    async sendRequest(method, params) {
        const request = {
            jsonrpc: '2.0',
            id: ++this.requestId,
            method,
            params
        };
        
        return new Promise((resolve, reject) => {
            this.process.stdin.write(JSON.stringify(request) + '\n');
            
            this.readline.once('line', (line) => {
                const response = JSON.parse(line);
                if (response.error) {
                    reject(new Error(response.error.message));
                } else {
                    resolve(response.result);
                }
            });
        });
    }
    
    async saveMemory(content, options = {}) {
        return await this.sendRequest('tools/call', {
            name: 'save_memory',
            arguments: { content, ...options }
        });
    }
    
    async searchMemories(query, options = {}) {
        return await this.sendRequest('tools/call', {
            name: 'search_memories', 
            arguments: { query, ...options }
        });
    }
}

// Usage
async function example() {
    const client = new MCPMemoryClient();
    await client.connect();
    
    await client.saveMemory("Important JavaScript pattern", {
        importance: 0.8,
        tags: ["javascript", "pattern"]
    });
    
    const results = await client.searchMemories("JavaScript");
    console.log(results);
}
```

## Security

### Authentication
```bash
# Enable API key authentication
ENABLE_AUTH=true
API_KEY_HEADER="X-API-Key"
API_KEY="your-secret-api-key"
```

### CORS Configuration
```bash
# Allowed origins
CORS_ORIGINS="http://localhost:3000,https://app.example.com"

# Or allow all (development only)
CORS_ORIGINS="*"
```

### Rate Limiting
```bash
# Requests per minute
RATE_LIMIT=100

# Burst size
RATE_LIMIT_BURST=20
```

For more examples and advanced usage, see the [examples/](examples/) directory.
