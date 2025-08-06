# 🌐 Cursor IDE - Remote MCP Memory Server Configuration

## 🎯 Overview

This guide shows how to configure Cursor IDE to connect to your MCP Memory Server running on a remote instance via HTTP.

## 🚀 Remote Server Setup

### 1. Deploy on Remote Instance

```bash
# On your remote server/instance
git clone https://github.com/AiGotsrl/mcp-memory-server.git
cd mcp-memory-server

# Make deployment script executable
chmod +x deploy-remote-server.sh

# Deploy HTTP server
./deploy-remote-server.sh
```

### 2. Server Endpoints

After deployment, your server will be available at:

- **MCP Endpoint**: `http://YOUR_SERVER_IP:8000/mcp`
- **Health Check**: `http://YOUR_SERVER_IP:8000/health`
- **Server Info**: `http://YOUR_SERVER_IP:8000/info`

## 🔧 Cursor IDE Configuration

### Method 1: HTTP Transport (Recommended)

Add this to your Cursor `mcp.json` configuration:

```json
{
  "mcpServers": {
    "memory-server": {
      "transport": "http",
      "url": "http://YOUR_SERVER_IP:8000/mcp",
      "headers": {
        "Content-Type": "application/json"
      }
    }
  }
}
```

### Method 2: Custom HTTP Client

If Method 1 doesn't work, use this configuration:

```json
{
  "mcpServers": {
    "memory-server": {
      "command": "curl",
      "args": [
        "-X", "POST",
        "http://YOUR_SERVER_IP:8000/mcp",
        "-H", "Content-Type: application/json",
        "-d"
      ]
    }
  }
}
```

### Method 3: Python HTTP Client

Create a simple HTTP client wrapper:

```json
{
  "mcpServers": {
    "memory-server": {
      "command": "python3",
      "args": ["-c", "
import sys, json, requests
data = json.loads(sys.stdin.read())
response = requests.post('http://YOUR_SERVER_IP:8000/mcp', json=data)
print(response.text)
      "]
    }
  }
}
```

## 🧪 Testing the Connection

### 1. Test Server Health

```bash
curl http://YOUR_SERVER_IP:8000/health
```

Expected response:
```json
{
  "status": "healthy",
  "service": "mcp-memory-server",
  "timestamp": "2025-08-06T...",
  "version": "1.0.0"
}
```

### 2. Test MCP Functionality

```bash
curl -X POST http://YOUR_SERVER_IP:8000/mcp \
  -H 'Content-Type: application/json' \
  -d '{
    "jsonrpc": "2.0",
    "id": 1,
    "method": "tools/list",
    "params": {}
  }'
```

Expected response:
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "result": {
    "tools": [
      {
        "name": "save_memory",
        "description": "Save important information to memory"
      },
      ...
    ]
  }
}
```

### 3. Test Memory Operations

Save a memory:
```bash
curl -X POST http://YOUR_SERVER_IP:8000/mcp \
  -H 'Content-Type: application/json' \
  -d '{
    "jsonrpc": "2.0",
    "id": 2,
    "method": "tools/call",
    "params": {
      "name": "save_memory",
      "arguments": {
        "content": "Test memory from remote server"
      }
    }
  }'
```

## 🔒 Security Considerations

### 1. Firewall Configuration

Make sure port 8000 is open on your server:

```bash
# Ubuntu/Debian
sudo ufw allow 8000

# CentOS/RHEL
sudo firewall-cmd --permanent --add-port=8000/tcp
sudo firewall-cmd --reload
```

### 2. HTTPS Setup (Production)

For production, consider setting up HTTPS:

1. Use a reverse proxy (nginx/Apache)
2. Get SSL certificate (Let's Encrypt)
3. Update Cursor config to use `https://`

### 3. Authentication (Optional)

Add API key authentication by modifying the HTTP server:

```python
# In mcp_memory_server_http.py
API_KEY = os.getenv("API_KEY", "your-secret-key")

@middleware
async def auth_middleware(request, handler):
    auth_header = request.headers.get("Authorization")
    if not auth_header or auth_header != f"Bearer {API_KEY}":
        return web.json_response({"error": "Unauthorized"}, status=401)
    return await handler(request)
```

## 🐳 Docker Management

### Start/Stop Server

```bash
# Start HTTP server
docker-compose up -d mcp-memory-server-http

# Stop server
docker-compose down

# View logs
docker-compose logs -f mcp-memory-server-http

# Restart server
docker-compose restart mcp-memory-server-http
```

### Update Server

```bash
# Pull latest changes
git pull

# Rebuild and restart
docker-compose down
docker-compose build --no-cache
docker-compose up -d mcp-memory-server-http
```

## 📊 Monitoring

### Check Server Status

```bash
# Container status
docker-compose ps

# Resource usage
docker stats mcp-memory-server-http

# Health check
curl http://YOUR_SERVER_IP:8000/health
```

### Logs

```bash
# Real-time logs
docker-compose logs -f mcp-memory-server-http

# Last 100 lines
docker-compose logs --tail=100 mcp-memory-server-http
```

## 🎯 Cursor IDE Usage

Once configured, you can use these prompts in Cursor:

- **Save Memory**: "Save this to memory: [your content]"
- **Search Memory**: "Search my memories for [query]"
- **List Memories**: "List all my saved memories"
- **Check Status**: "Check memory system status"

The remote server will handle all requests and maintain persistent memory across sessions!

---

**🚀 Your MCP Memory Server is now accessible remotely via HTTP!**
