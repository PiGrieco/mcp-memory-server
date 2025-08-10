# 🚀 Installation Guide - MCP Memory Server

## One-Click Installation

### Quick Start (Recommended)
```bash
# Clone repository
git clone https://github.com/PiGrieco/mcp-memory-server.git
cd mcp-memory-server

# One-click install
python install.py
```

### Manual Installation
```bash
# Install dependencies
pip install -r requirements.txt

# Start server
python main_simple.py  # Zero dependencies, in-memory
# OR
python main.py         # Full server with MongoDB
```

## What the Installer Does

✅ **Checks Python version** (3.8+ required)
✅ **Installs all dependencies** automatically  
✅ **Creates Cursor configuration** (`~/.cursor/mcp_settings.json`)
✅ **Creates Claude configuration** (`~/.config/claude/config.json`)
✅ **Tests auto-trigger system**
✅ **Downloads models** (97MB, works offline)

## Configuration Options

### For Cursor IDE
```json
{
  "mcpServers": {
    "mcp-memory-auto": {
      "command": "python",
      "args": ["path/to/main_simple.py"],
      "env": {
        "AUTO_TRIGGER": "true",
        "KEYWORDS": "ricorda,nota,importante"
      }
    }
  }
}
```

### For Claude Desktop
```json
{
  "mcpServers": {
    "mcp-memory-auto": {
      "command": "python",
      "args": ["path/to/main_simple.py"],
      "env": {
        "AUTO_TRIGGER": "true",
        "CLAUDE_MODE": "true"
      }
    }
  }
}
```

## Server Options

| Server | Description | Use Case |
|--------|-------------|----------|
| `main_simple.py` | Zero dependencies, in-memory | Testing, development |
| `main.py` | Full server with MongoDB | Production |
| `main_auto.py` | Enhanced with auto-trigger | Advanced features |

## System Requirements

- **Python:** 3.8 or higher
- **Memory:** 2GB RAM minimum (4GB recommended)
- **Storage:** 500MB free space
- **MongoDB:** Optional (for production)

## Troubleshooting

### Common Issues

**Q: "ModuleNotFoundError: mcp"**
```bash
pip install mcp>=1.0.0
```

**Q: "Auto-trigger not working"**
```bash
# Check server status
ps aux | grep main_simple.py

# Restart server
pkill -f main_simple.py && python main_simple.py
```

**Q: "Cursor not connecting"**
```bash
# Verify config
cat ~/.cursor/mcp_settings.json

# Recreate config
python install.py
```

## Support

- 📚 [Usage Guide](USAGE.md)
- 🐛 [Report Issues](https://github.com/PiGrieco/mcp-memory-server/issues)
- 💬 [Discussions](https://github.com/PiGrieco/mcp-memory-server/discussions)
