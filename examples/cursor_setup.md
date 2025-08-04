# Cursor + MCP Memory Server Setup

## Method 1: MCP Extension (Recommended)

### Step 1: Install MCP Extension
1. Open Cursor
2. Go to Extensions (Cmd/Ctrl + Shift + X)
3. Search for "Model Context Protocol" or "MCP"
4. Install the MCP extension

### Step 2: Configure MCP Server
1. Open Cursor Settings (Cmd/Ctrl + ,)
2. Search for "MCP" in settings
3. Add server configuration:

```json
{
  "mcp.servers": {
    "memory-server": {
      "command": "python",
      "args": ["/Users/piermatteogrieco/mcp-memory-server/main.py"],
      "cwd": "/Users/piermatteogrieco/mcp-memory-server",
      "env": {
        "MONGODB_URL": "mongodb://admin:securepassword@localhost:27017/memory_db?authSource=admin",
        "EMBEDDING_MODEL": "sentence-transformers/all-MiniLM-L6-v2"
      }
    }
  }
}
```

### Step 3: Usage in Cursor
- Use @ mentions: `@memory-server save this: "React hooks are powerful"`
- Or natural language: "Remember that I prefer TypeScript over JavaScript"

## Method 2: Direct Integration

### Step 1: Create Cursor Plugin
Create `.cursor/mcp-memory.js`:

```javascript
const { spawn } = require('child_process');

class MCPMemoryPlugin {
  constructor() {
    this.serverProcess = null;
  }

  async start() {
    this.serverProcess = spawn('python', [
      '/Users/piermatteogrieco/mcp-memory-server/main.py'
    ], {
      env: {
        ...process.env,
        MONGODB_URL: 'mongodb://admin:securepassword@localhost:27017/memory_db?authSource=admin',
        EMBEDDING_MODEL: 'sentence-transformers/all-MiniLM-L6-v2'
      }
    });
  }

  async saveMemory(text, type = 'code', project = 'cursor') {
    // Implementation for saving memories
  }

  async searchMemory(query, project = 'cursor') {
    // Implementation for searching memories
  }
}

module.exports = MCPMemoryPlugin;
```

### Step 4: Test Integration
1. Start the memory server: `docker compose up -d`
2. Restart Cursor
3. Test with: "Remember this pattern for future use" 