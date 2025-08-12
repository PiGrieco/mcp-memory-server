# 🗂️ **Legacy Servers - MCP Memory Server**

> **Deprecated server implementations**

## ⚠️ **Important Notice**

This directory contains **deprecated** server implementations that are no longer maintained or supported. These files are kept for reference only and should not be used in production.

## 📂 **Legacy Files**

### **Deprecated Servers**
- `mcp_memory_server_http.py` - Old HTTP server implementation
- `mcp_memory_server_mcp.py` - Old MCP server implementation
- `test_server.py` - Old test server
- `test_server_simple.py` - Old simple test server

### **Why Deprecated?**
- ❌ **Outdated Architecture**: Don't follow the new modular design
- ❌ **Poor Error Handling**: Limited error handling and recovery
- ❌ **No Plugin Support**: Don't support the plugin system
- ❌ **Limited Features**: Missing advanced features like caching, backup, etc.
- ❌ **Security Issues**: Don't follow current security best practices

## 🚀 **Current Implementation**

### **Use These Instead**
- **HTTP Server**: `servers/http_server.py` - Modern HTTP server
- **MCP Server**: `main.py` - Unified MCP server
- **Test Server**: `tests/test_complete_services.py` - Comprehensive tests

### **How to Use Current Servers**
```bash
# Start HTTP server (recommended)
./scripts/main.sh server http

# Start MCP server (recommended)
./scripts/main.sh server mcp

# Run tests (recommended)
./scripts/main.sh server test
```

## 🔄 **Migration Guide**

### **From Legacy to Current**
1. **Stop using legacy servers**
2. **Use the new script system**: `./scripts/main.sh`
3. **Update configurations** to use new settings format
4. **Test with new servers** before deploying

### **Key Differences**
| Feature | Legacy | Current |
|---------|--------|---------|
| Architecture | Monolithic | Modular |
| Plugin Support | ❌ No | ✅ Yes |
| Error Handling | Basic | Advanced |
| Configuration | Hardcoded | YAML-based |
| Testing | Limited | Comprehensive |
| Documentation | Minimal | Complete |

## 📚 **Reference Only**

These files are kept for:
- 📖 **Historical reference**
- 🔍 **Debugging old issues**
- 📝 **Understanding evolution**
- 🧪 **Educational purposes**

## 🗑️ **Cleanup**

### **When to Remove**
- After all users have migrated
- When no longer needed for reference
- When maintenance burden is too high

### **Removal Process**
1. **Announce deprecation** (30 days notice)
2. **Document migration path**
3. **Remove from documentation**
4. **Delete files**

---

**⚠️ Do not use these files in production. Use the current implementation instead.** 