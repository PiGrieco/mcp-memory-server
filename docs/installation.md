# 🚀 **Installation Guide - MCP Memory Server**

## 📋 **Prerequisites**

### **Operating System**
- ✅ **macOS** 10.15+ (Catalina)
- ✅ **Linux** Ubuntu 18.04+, CentOS 7+
- ✅ **Windows** 10+ (WSL2 recommended)

### **Required Software**
- **Python** 3.8+ (3.11+ recommended)
- **MongoDB** 4.4+ (or MongoDB Atlas)
- **Redis** 6.0+ (optional, for distributed cache)
- **Git** 2.20+

### **System Requirements**
- **RAM**: Minimum 4GB, 8GB+ recommended
- **Storage**: Minimum 10GB free space
- **CPU**: 2 cores minimum, 4+ cores recommended

## 🔧 **Quick Installation**

### **1. Clone Repository**
```bash
git clone https://github.com/your-repo/mcp-memory-server.git
cd mcp-memory-server
```

### **2. Automatic Installation**
```bash
# Run installation script
./scripts/install.py

# Or use shell script
./install.sh
```

### **3. Verify Installation**
```bash
# Test all services
python test_complete_services.py

# Check configuration
python -c "from src.config.settings import get_settings; print('✅ Configuration loaded')"
```

## 📦 **Manual Installation**

### **1. Set Up Virtual Environment**
```bash
# Create virtual environment
python3 -m venv venv

# Activate environment
source venv/bin/activate  # Linux/macOS
# or
venv\Scripts\activate     # Windows
```

### **2. Install Dependencies**
```bash
# Install basic dependencies
pip install -r requirements.txt

# Install optional dependencies
pip install redis pandas schedule aiohttp
```

### **3. Configure MongoDB**
```bash
# Install MongoDB (Ubuntu)
sudo apt update
sudo apt install mongodb

# Start MongoDB
sudo systemctl start mongodb
sudo systemctl enable mongodb

# Check status
sudo systemctl status mongodb
```

### **4. Configure Redis (Optional)**
```bash
# Install Redis (Ubuntu)
sudo apt install redis-server

# Start Redis
sudo systemctl start redis
sudo systemctl enable redis

# Check status
redis-cli ping
```

## ⚙️ **Configuration**

### **1. Configuration File**
```bash
# Copy example configuration
cp config/settings.yaml.example config/settings.yaml

# Edit configuration
nano config/settings.yaml
```

### **2. Environment Variables**
```bash
# Copy environment file
cp .env.example .env

# Edit environment variables
nano .env
```

### **3. Database Configuration**
```yaml
# config/settings.yaml
database:
  mongodb:
    uri: "mongodb://localhost:27017"
    database: "mcp_memory_dev"
    collection: "memories"
    username: ""
    password: ""
    auth_source: "admin"
    max_pool_size: 5
    min_pool_size: 1
    max_idle_time_ms: 30000
    server_selection_timeout_ms: 5000
    socket_timeout: 5000
    connect_timeout: 5000
```

### **4. Memory Service Configuration**
```yaml
# config/settings.yaml
memory:
  auto_save: true
  storage: "mongodb"
  ml_triggers: true
  trigger_threshold: 0.6
  min_text_length: 20
  max_text_length: 5000
  default_project: "default"
  retention_days: 365
```

## 🔌 **Platform Configuration**

### **Cursor IDE**
```bash
# Configure Cursor
./scripts/install_cursor.sh

# Verify configuration
cat config/cursor_config.json
```

### **Claude Desktop**
```bash
# Configure Claude
./scripts/install_claude.sh
```

### **Universal Configuration**
```bash
# Configure universal platform
./scripts/install_universal.sh
```

## 🧪 **Testing Installation**

### **1. Run Service Tests**
```bash
# Test all services
python tests/test_complete_services.py

# Test specific services
python tests/test_memory_service.py
python tests/test_database_service.py
```

### **2. Start HTTP Server**
```bash
# Start HTTP server
./scripts/main.sh server http

# Test endpoints
curl http://localhost:8000/health
curl http://localhost:8000/status
```

### **3. Start MCP Server**
```bash
# Start MCP server
./scripts/main.sh server mcp

# Test MCP integration
# (Use your platform's MCP client)
```

## 🔧 **Troubleshooting**

### **Common Issues**

#### **1. MongoDB Connection Error**
```bash
# Check MongoDB status
sudo systemctl status mongodb

# Check MongoDB logs
sudo journalctl -u mongodb

# Test connection
mongosh --eval "db.runCommand('ping')"
```

#### **2. Python Import Errors**
```bash
# Check virtual environment
which python
pip list

# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

#### **3. Permission Errors**
```bash
# Fix script permissions
chmod +x scripts/*.sh
chmod +x scripts/**/*.sh

# Fix directory permissions
chmod 755 scripts/
chmod 755 config/
```

#### **4. Port Already in Use**
```bash
# Check what's using port 8000
lsof -i :8000

# Kill process
kill -9 <PID>

# Or use different port
# Edit config/settings.yaml
```

### **Log Files**
```bash
# Check application logs
tail -f logs/mcp_memory.log

# Check system logs
sudo journalctl -f

# Check MongoDB logs
sudo tail -f /var/log/mongodb/mongod.log
```

## 📊 **Performance Tuning**

### **MongoDB Optimization**
```yaml
# config/settings.yaml
database:
  mongodb:
    max_pool_size: 10  # Increase for high load
    min_pool_size: 2
    max_idle_time_ms: 60000
```

### **Cache Configuration**
```yaml
# config/settings.yaml
cache:
  enabled: true
  type: "redis"  # or "memory"
  redis:
    host: "localhost"
    port: 6379
    db: 0
    max_connections: 10
```

### **Memory Service Tuning**
```yaml
# config/settings.yaml
memory:
  trigger_threshold: 0.7  # Adjust sensitivity
  min_text_length: 10    # Reduce for more triggers
  max_text_length: 10000 # Increase for longer content
```

## 🔒 **Security Configuration**

### **Authentication**
```yaml
# config/settings.yaml
security:
  enabled: true
  auth_type: "basic"  # or "jwt"
  jwt_secret: "your-secret-key"
  session_timeout: 3600
```

### **CORS Configuration**
```yaml
# config/settings.yaml
server:
  cors:
    enabled: true
    origins: ["http://localhost:3000", "https://your-domain.com"]
    methods: ["GET", "POST", "PUT", "DELETE"]
    headers: ["*"]
```

### **Rate Limiting**
```yaml
# config/settings.yaml
server:
  rate_limit:
    enabled: true
    requests_per_minute: 100
    burst_size: 20
```

## 🚀 **Production Deployment**

### **1. Environment Setup**
```bash
# Set production environment
export ENVIRONMENT=production

# Use production configuration
cp config/environments/production.yaml config/settings.yaml
```

### **2. Database Setup**
```bash
# Use MongoDB Atlas or production MongoDB
# Update connection string in config/settings.yaml
```

### **3. Security Setup**
```bash
# Generate secure keys
openssl rand -hex 32

# Update security configuration
# Edit config/settings.yaml
```

### **4. Monitoring Setup**
```bash
# Enable monitoring
# Configure Prometheus and Grafana
# Set up alerting
```

## 📚 **Next Steps**

### **After Installation**
1. **Read the documentation**: `docs/`
2. **Configure your platform**: Platform-specific guides
3. **Test the system**: Run comprehensive tests
4. **Set up monitoring**: Configure monitoring tools
5. **Plan backup strategy**: Set up automated backups

### **Learning Resources**
- [Architecture Guide](docs/ARCHITECTURE_COMPLETE.md)
- [Development Guide](docs/development/guide.md)
- [API Reference](docs/development/api.md)
- [Plugin Development](docs/architecture/plugins.md)

## 🆘 **Support**

### **Getting Help**
- 📖 **Documentation**: `docs/`
- 🐛 **Issues**: [GitHub Issues](https://github.com/your-repo/mcp-memory-server/issues)
- 💬 **Discord**: [Discord Server]
- 📧 **Email**: support@mcp-memory-server.com

### **Community**
- **GitHub Discussions**: [Discussions](https://github.com/your-repo/mcp-memory-server/discussions)
- **Stack Overflow**: Tag with `mcp-memory-server`
- **Reddit**: r/MCPMemoryServer

---

**🎉 Congratulations! Your MCP Memory Server is now installed and ready to use.** 