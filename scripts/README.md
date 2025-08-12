# 📁 Scripts - MCP Memory Server

This folder contains all scripts organized by category to facilitate MCP Memory Server management.

## 🚀 **Main Script**

### **`main.sh`** - Main Manager
```bash
# View all options
./scripts/main.sh help

# Or use directly
./main.sh help
```

## 📂 **Organized Structure**

```
scripts/
├── 📄 main.sh                    # 🚀 Main manager
├── 📁 servers/                   # 🌐 Server management
│   ├── start_server.sh          # Main server
│   ├── start_http_server.sh     # HTTP server
│   └── start_mcp_server.sh      # MCP server
├── 📁 install/                   # 📦 Installation and setup
│   ├── install.sh               # Main installation
│   ├── install.py               # Python installation script
│   ├── install_cursor.sh        # Cursor configuration
│   ├── install_claude.sh        # Claude configuration
│   ├── install_lovable.sh       # Lovable configuration
│   ├── install_replit.sh        # Replit configuration
│   └── install_windsurf.sh      # Windsurf configuration
├── 📁 utils/                     # 🔧 Utilities
│   └── manage_environments.sh   # Environment management
└── 📁 platforms/                 # 🔌 Platform configurations
    └── (specific files)
```

## 🎯 **Main Commands**

### **🌐 Servers**
```bash
# HTTP server (development)
./main.sh server http

# MCP server (integration)
./main.sh server mcp

# Run tests
./main.sh server test

# View server options
./main.sh server help
```

### **📦 Installation**
```bash
# Complete installation
./main.sh install all

# Core dependencies only
./main.sh install core

# ML only
./main.sh install ml

# View installation options
./main.sh install help
```

### **🔌 Platforms**
```bash
# Configure Cursor
./main.sh platform cursor

# Configure Claude
./main.sh platform claude

# View available platforms
./main.sh platform help
```

### **🔧 Utilities**
```bash
# Environment management
./main.sh utils env list
./main.sh utils env switch development

# View available utilities
./main.sh utils help
```

## 💡 **Usage Examples**

### **Daily Development**
```bash
# 1. Install everything
./main.sh install all

# 2. Start HTTP server
./main.sh server http

# 3. In another terminal, run tests
./main.sh server test
```

### **Platform Configuration**
```bash
# 1. Configure Cursor
./main.sh platform cursor

# 2. Start MCP server
./main.sh server mcp
```

### **Environment Management**
```bash
# 1. List environments
./main.sh utils env list

# 2. Switch to development
./main.sh utils env switch development

# 3. Check current configuration
./main.sh utils env current
```

## 🔧 **Individual Scripts**

### **Servers**
- **`servers/start_server.sh`** - Server manager
- **`servers/start_http_server.sh`** - HTTP server for development
- **`servers/start_mcp_server.sh`** - MCP server for integration

### **Installation**
- **`install/install.sh`** - Main installation
- **`install/install.py`** - Python installation script
- **`install/install_*.sh`** - Platform-specific configurations

### **Utilities**
- **`utils/manage_environments.sh`** - Environment configuration management

## 🎨 **Colors and Interface**

All scripts use colors for better experience:
- 🔵 **Blue**: Titles and information
- 🟢 **Green**: Success and commands
- 🟡 **Yellow**: Warnings and examples
- 🔴 **Red**: Errors
- 🟣 **Purple**: Tips and help

## 📝 **Important Notes**

1. **Always use `./main.sh`** to access organized scripts
2. **Check help** with `./main.sh [category] help`
3. **Scripts are executable** - no need for `bash` before
4. **Virtual environment** is activated automatically
5. **Services** (MongoDB, Redis) are checked and started automatically

## 🆘 **Troubleshooting**

### **Problem**: Script not found
```bash
# Check if script exists
ls -la scripts/main.sh

# Make executable if necessary
chmod +x scripts/main.sh
```

### **Problem**: Permissions
```bash
# Make all scripts executable
chmod +x scripts/**/*.sh
chmod +x scripts/*.sh
```

### **Problem**: Virtual environment not found
```bash
# Install first
./main.sh install all
``` 