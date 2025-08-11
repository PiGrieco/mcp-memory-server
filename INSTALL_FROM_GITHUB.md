# 🚀 Install MCP Memory Server from GitHub

**One-command installation directly from GitHub repository**

---

## ⚡ **Quick Installation (Recommended)**

### **Option 1: Interactive Installer**

```bash
curl -sSL https://raw.githubusercontent.com/PiGrieco/mcp-memory-server/production-ready-v2/install.sh | bash
```

This script will:
- ✅ Clone the repository to `~/mcp-memory-server`
- ✅ Set up Python virtual environment
- ✅ Install all dependencies
- ✅ Configure your chosen AI platform (Cursor/Claude)
- ✅ Create convenience scripts
- ✅ Test the installation

### **Option 2: One-Liner (Fully Automatic)**

```bash
curl -sSL https://raw.githubusercontent.com/PiGrieco/mcp-memory-server/production-ready-v2/install-oneliner.sh | bash
```

### **Option 3: Platform-Specific Install**

**For Cursor IDE:**
```bash
curl -sSL https://raw.githubusercontent.com/PiGrieco/mcp-memory-server/production-ready-v2/install_cursor.sh | bash
```

**For Claude Desktop:**
```bash
curl -sSL https://raw.githubusercontent.com/PiGrieco/mcp-memory-server/production-ready-v2/install_claude.sh | bash
```

---

## 🔧 **Manual Installation**

If you prefer to install manually:

```bash
# 1. Clone repository
git clone -b production-ready-v2 https://github.com/PiGrieco/mcp-memory-server.git
cd mcp-memory-server

# 2. Set up environment
python3 -m venv venv
source venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Test installation
python mcp_base_server.py

# 5. Configure your platform (see below)
```

---

## 🎯 **Platform Configuration**

### **Cursor IDE Configuration**

After installation, configure Cursor by creating `~/.cursor/mcp_settings.json`:

```json
{
  "mcpServers": {
    "mcp-memory-ml": {
      "command": "/Users/YOUR_USERNAME/mcp-memory-server/venv/bin/python",
      "args": ["/Users/YOUR_USERNAME/mcp-memory-server/cursor_mcp_server.py"],
      "env": {
        "ML_MODEL_TYPE": "huggingface",
        "HUGGINGFACE_MODEL_NAME": "PiGrieco/mcp-memory-auto-trigger-model",
        "AUTO_TRIGGER_ENABLED": "true",
        "CURSOR_MODE": "true"
      }
    }
  }
}
```

**Replace `YOUR_USERNAME` with your actual username or use the installer script!**

### **Claude Desktop Configuration**

For Claude Desktop, create configuration file:

**macOS:** `~/Library/Application Support/Claude/claude_desktop_config.json`
**Linux:** `~/.config/claude/claude_desktop_config.json`

```json
{
  "mcpServers": {
    "mcp-memory-claude": {
      "command": "/Users/YOUR_USERNAME/mcp-memory-server/venv/bin/python",
      "args": ["/Users/YOUR_USERNAME/mcp-memory-server/claude_mcp_server.py"],
      "env": {
        "ML_MODEL_TYPE": "huggingface",
        "HUGGINGFACE_MODEL_NAME": "PiGrieco/mcp-memory-auto-trigger-model",
        "AUTO_TRIGGER_ENABLED": "true"
      }
    }
  }
}
```

---

## 🚀 **Post-Installation**

### **Quick Start**

```bash
cd ~/mcp-memory-server
./start.sh  # Interactive mode selector
```

### **Direct Commands**

```bash
cd ~/mcp-memory-server
source venv/bin/activate

# Choose your server mode:
python mcp_base_server.py      # Simple MCP server
python main_auto.py            # ML auto-trigger server  
python cursor_mcp_server.py    # Cursor IDE optimized
python claude_mcp_server.py    # Claude Desktop optimized
```

### **Update to Latest Version**

```bash
cd ~/mcp-memory-server
./update.sh
```

### **Test Your Installation**

```bash
cd ~/mcp-memory-server
source venv/bin/activate
python test_installation.py
```

---

## 🔍 **Verify Installation**

### **In Cursor IDE:**
1. Restart Cursor IDE
2. Press `Cmd+L` (macOS) or `Ctrl+L` (Windows/Linux)
3. Look for "mcp-memory-ml" in available tools
4. Test: `"Ricorda questa informazione importante"`

### **In Claude Desktop:**
1. Restart Claude Desktop
2. Check if "mcp-memory-claude" appears in tools
3. Test: `"Save this to memory: React hooks best practices"`

---

## 📁 **Installation Directories**

- **Main Installation:** `~/mcp-memory-server/`
- **Virtual Environment:** `~/mcp-memory-server/venv/`
- **Configuration Files:** 
  - Cursor: `~/.cursor/mcp_settings.json`
  - Claude: `~/Library/Application Support/Claude/claude_desktop_config.json` (macOS)

---

## 🆘 **Troubleshooting**

### **Common Issues:**

**"Command not found: python"**
```bash
# Try python3 instead
python3 -m venv venv
```

**"Permission denied"**
```bash
chmod +x ~/mcp-memory-server/start.sh
chmod +x ~/mcp-memory-server/update.sh
```

**"MCP server not visible in Cursor/Claude"**
- Restart your AI application completely
- Check the configuration file paths
- Verify Python virtual environment path is correct

**"Module not found errors"**
```bash
cd ~/mcp-memory-server
source venv/bin/activate
pip install -r requirements.txt
```

### **Get Help:**

- 📖 **Documentation:** [README.md](README.md)
- 🐛 **Issues:** [GitHub Issues](https://github.com/PiGrieco/mcp-memory-server/issues)
- 💬 **Community:** [GitHub Discussions](https://github.com/PiGrieco/mcp-memory-server/discussions)

---

## ✨ **Features After Installation**

- 🧠 **Infinite AI Memory** - Never lose important information
- 🤖 **99.56% ML Accuracy** - Intelligent auto-triggers for memory operations
- 🔍 **Semantic Search** - Find information by meaning, not keywords
- 🎯 **Multi-Platform** - Works with Cursor, Claude, GPT, and more
- ⚡ **Real-time** - Instant memory save/search operations
- 🌐 **Always Updated** - Easy updates from GitHub repository

**Your AI assistant now has infinite memory! 🚀✨**
