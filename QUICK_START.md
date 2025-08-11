# 🚀 Quick Start Guide

Get MCP Memory Server running in **under 5 minutes**!

## ⚡ **1-Minute Setup (Docker)**

```bash
# Clone and start
git clone https://github.com/PiGrieco/mcp-memory-server.git
cd mcp-memory-server
./docker-setup.sh
docker-compose up -d

# Verify
curl http://localhost:8000/health
```

✅ **Done!** Your memory server is running at `http://localhost:8000`

---

## 🎯 **Platform Integration**

### **Cursor IDE**

1. **Install MCP Server**:
   ```bash
   python cursor_mcp_server.py
   ```

2. **Configure Cursor**:
   ```json
   // ~/.cursor/mcp_settings.json
   {
     "mcpServers": {
       "memory": {
         "command": "python",
         "args": ["/path/to/cursor_mcp_server.py"]
       }
     }
   }
   ```

3. **Test**: Type "remember this solution" in Cursor - it should auto-save!

### **Claude Desktop**

1. **Start Server**:
   ```bash
   python claude_mcp_server.py
   ```

2. **Configure Claude**:
   ```json
   // ~/.config/claude/claude_desktop_config.json
   {
     "mcpServers": {
       "memory": {
         "command": "python", 
         "args": ["/path/to/claude_mcp_server.py"]
       }
     }
   }
   ```

3. **Test**: Ask Claude to "save this important fact" - it should work automatically!

---

## 🔧 **Manual Setup**

### **Prerequisites**
- Python 3.8+
- MongoDB (local or Atlas)

### **Installation**
```bash
# 1. Clone repository
git clone https://github.com/PiGrieco/mcp-memory-server.git
cd mcp-memory-server

# 2. Install dependencies
pip install -r requirements.txt

# 3. Configure environment
cp config/environment.template .env
# Edit .env with your MongoDB URI

# 4. Start server
python main.py
```

---

## 🧪 **Quick Test**

### **Test Memory Operations**

```bash
# Save a memory
curl -X POST http://localhost:8000/api/v1/memories \
  -H "Content-Type: application/json" \
  -d '{"content": "Python is a great programming language", "context": {"importance": 0.8}}'

# Search memories
curl "http://localhost:8000/api/v1/memories/search?q=Python&limit=5"

# Check stats
curl http://localhost:8000/api/v1/stats
```

### **Test Auto-Triggers**

```bash
# Analyze a message for triggers
curl -X POST http://localhost:8000/api/v1/analyze \
  -H "Content-Type: application/json" \
  -d '{"content": "Remember: always use async/await in Python for better performance"}'
```

---

## 🎮 **Interactive Demo**

### **Try the ML Auto-Trigger**

1. **Start the server**:
   ```bash
   python main_auto.py
   ```

2. **Send test messages**:
   ```python
   import requests
   
   # This should trigger auto-save
   response = requests.post('http://localhost:8000/api/v1/analyze', json={
       'content': 'Important: remember to always validate user input in web applications'
   })
   print(response.json())
   
   # This should trigger auto-search
   response = requests.post('http://localhost:8000/api/v1/analyze', json={
       'content': 'How do I validate user input in Python?'
   })
   print(response.json())
   ```

---

## 🔍 **Verification**

### **Check Everything Works**

```bash
# 1. Health check
curl http://localhost:8000/health
# Should return: {"status": "healthy"}

# 2. ML model status
curl http://localhost:8000/ml/status
# Should show ML model is loaded

# 3. Database connection
curl http://localhost:8000/db/status
# Should show database is connected

# 4. Memory count
curl http://localhost:8000/api/v1/stats
# Should show current memory statistics
```

---

## 🐛 **Common Issues**

### **MongoDB Connection Failed**
```bash
# Check MongoDB is running
mongosh --eval "db.adminCommand('ping')"

# Or use MongoDB Atlas
# Update MONGODB_URI in .env with your Atlas connection string
```

### **ML Model Not Loading**
```bash
# Check internet connection for HuggingFace download
ping huggingface.co

# Or use offline mode
export ML_MODEL_TYPE=deterministic_only
```

### **Port Already in Use**
```bash
# Change port in .env
echo "SERVER_PORT=8001" >> .env

# Or kill existing process
lsof -ti:8000 | xargs kill -9
```

---

## 🎯 **Next Steps**

### **Production Deployment**
- Set up MongoDB Atlas
- Configure environment variables
- Use Docker Compose for production
- Set up monitoring and logging

### **Advanced Features**
- Configure custom ML models
- Set up multiple platform integrations
- Implement custom trigger rules
- Add analytics and monitoring

### **Integration**
- Connect to your AI platforms
- Build custom applications
- Integrate with existing workflows
- Develop custom plugins

---

## 📚 **Learn More**

- 📖 [Full Documentation](README.md)
- 🔧 [Configuration Guide](config/examples/)
- 🐳 [Docker Deployment](docker-compose.yml)
- 🤝 [Contributing](CONTRIBUTING.md)
- 📝 [API Reference](docs/api.md)

---

## 🆘 **Need Help?**

- 💬 [Discord Community](https://discord.gg/mcp-memory-server)
- 🐛 [Report Issues](https://github.com/PiGrieco/mcp-memory-server/issues)
- 📧 [Email Support](mailto:support@mcp-memory-server.com)

---

**🎉 Congratulations! You now have a fully functional AI memory system running!**

The server will automatically:
- ✅ Save important information when you say "remember this"
- 🔍 Search for relevant context when you ask questions
- 🧠 Learn from your conversations to improve over time
- 📊 Provide analytics and insights about your memory usage

**Happy memory managing! 🧠✨**
