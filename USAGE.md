# 🧠 Usage Guide - MCP Memory Server

## Quick Start

### 1. Start the Server
```bash
python main_simple.py  # Zero dependencies
```

### 2. Test in Cursor/Claude
Try these examples:

**Auto-save keyword trigger:**
```
"Ricorda che per fixare i CORS devi aggiungere Access-Control-Allow-Origin"
```
→ 💾 **Automatically saved as memory!**

**Pattern recognition:**
```
"Ho risolto il bug di timeout aumentando connection_timeout a 30 secondi"
```
→ 💾 **Automatically saved as solution!**

**Smart context retrieval:**
```
"Come posso gestire i timeout nel database?"
```
→ 🔍 **Automatically searches previous timeout solutions!**

## Available Tools

### `save_memory`
Save important information to memory.

```python
{
  "content": "Information to save",
  "project": "project-name",      # Optional
  "importance": 0.7,              # 0.0-1.0
  "memory_type": "conversation"   # Optional
}
```

### `search_memories`
Search for relevant memories.

```python
{
  "query": "search query",
  "max_results": 5,              # Optional
  "similarity_threshold": 0.3    # Optional
}
```

### `list_memories`
List all saved memories.

```python
{}  # No parameters needed
```

### `memory_status`
Check system status.

```python
{}  # No parameters needed
```

## Auto-Trigger System

### 7 Types of Intelligent Triggers

| Trigger Type | When It Activates | Example |
|--------------|-------------------|---------|
| 🔤 **Keywords** | "ricorda", "importante", "nota" | "Ricorda questa fix" → Auto-save |
| 🔍 **Patterns** | "risolto", "bug fix", "solution" | "Ho risolto il problema" → Auto-save |
| 🎯 **Semantic** | Similar content detected | "Timeout error" → Auto-search previous |
| ⭐ **Importance** | High-value content identified | Critical info → Auto-save |
| 📏 **Length** | Long conversations | 5+ messages → Auto-summary |
| 🔄 **Context** | Topic changes detected | "New project" → Load relevant memories |
| ⏰ **Time** | Periodic checks | Every 10 min → Proactive suggestions |

### Customizing Triggers

```bash
# Environment variables
export TRIGGER_KEYWORDS="ricorda,nota,importante,save,remember"
export SOLUTION_PATTERNS="risolto,solved,fixed,bug fix,solution"
export AUTO_SAVE_THRESHOLD="0.7"
export SEMANTIC_THRESHOLD="0.8"
```

## API Integration

### Direct Python Integration
```python
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

async def use_memory():
    server_params = StdioServerParameters(
        command="python",
        args=["main_simple.py"]
    )
    
    read_stream, write_stream = await stdio_client(server_params)
    client = ClientSession(read_stream, write_stream)
    await client.initialize()
    
    # Save memory
    await client.call_tool("save_memory", {
        "content": "Important information",
        "importance": 0.8
    })
    
    # Search memories
    result = await client.call_tool("search_memories", {
        "query": "timeout database"
    })
```

### Browser Extension
The browser extension works automatically on:
- ChatGPT (chat.openai.com)
- Claude (claude.ai)
- Perplexity (perplexity.ai)
- Poe (poe.com)

## Production Deployment

### Using Docker
```bash
# Build and run
make build
make up

# Check logs
make logs

# Health check
make health
```

### Using MongoDB
```bash
# Start with MongoDB backend
python main.py

# Environment variables
export MONGODB_URI="mongodb://localhost:27017"
export MONGODB_DATABASE="mcp_memory"
```

## Monitoring

### Real-time Logs
```bash
# Watch auto-triggers
tail -f logs/auto_trigger.log

# Watch main server
tail -f logs/mcp_memory_server.log
```

### Memory Statistics
```bash
# Get stats via API
curl http://localhost:8000/stats

# Or use memory_status tool in AI
```

## Use Cases

### For Developers
- **Bug Solutions:** Never lose a working fix again
- **Code Patterns:** Remember effective implementations  
- **Configuration:** Recall complex setup procedures
- **Learning:** Build permanent knowledge base

### For Content Creators
- **Ideas:** Capture creative insights automatically
- **Research:** Remember important findings
- **Templates:** Save effective formats
- **References:** Quick access to sources

### For Students
- **Study Notes:** Automatic concept capture
- **Problem Solutions:** Never re-solve same problems
- **Research:** Permanent reference library
- **Learning Paths:** Track progress automatically

## Best Practices

1. **Use descriptive content** when saving memories
2. **Set appropriate importance levels** (0.0-1.0)
3. **Use project names** to organize memories
4. **Let auto-triggers work** - they capture 95% of important content
5. **Monitor logs** to understand trigger behavior

## Troubleshooting

### Performance Issues
- Use `main_simple.py` for faster startup
- Increase memory with environment variables
- Check log files for errors

### Memory Not Saving
- Verify auto-trigger keywords are working
- Check server logs for errors
- Test with manual `save_memory` calls

### Search Not Working
- Ensure embeddings are generated
- Check similarity thresholds
- Verify database connectivity (if using MongoDB)

## Advanced Configuration

See [API.md](API.md) for detailed API documentation and advanced configuration options.
