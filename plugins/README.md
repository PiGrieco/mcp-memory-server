# 🔌 **Plugin System - MCP Memory Server**

> **Extensible plugin system for MCP Memory Server**

## 🎯 **Overview**

The plugin system allows you to extend the MCP Memory Server functionality with custom features, hooks, and integrations. Plugins can respond to events, add new endpoints, and enhance the server's capabilities.

## 📂 **Structure**

```
plugins/
├── 📄 README.md                   # This file
├── 📁 memory_analytics/           # Memory Analytics Plugin
│   ├── plugin.py                  # Plugin implementation
│   ├── requirements.txt           # Plugin dependencies
│   └── README.md                  # Plugin documentation
├── 📁 backup_manager/             # Backup Manager Plugin
│   ├── plugin.py                  # Plugin implementation
│   ├── requirements.txt           # Plugin dependencies
│   └── README.md                  # Plugin documentation
├── 📁 notification_service/       # Notification Service Plugin
│   ├── plugin.py                  # Plugin implementation
│   ├── requirements.txt           # Plugin dependencies
│   └── README.md                  # Plugin documentation
└── 📁 export_service/             # Export Service Plugin
    ├── plugin.py                  # Plugin implementation
    ├── requirements.txt           # Plugin dependencies
    └── README.md                  # Plugin documentation
```

## 🚀 **Quick Start**

### **1. Create a Plugin**
```python
# plugins/my_plugin/plugin.py
PLUGIN_INFO = {
    "name": "My Plugin",
    "version": "1.0.0",
    "description": "A custom plugin for MCP Memory Server",
    "author": "Your Name",
    "hooks": ["memory_created", "search_performed"]
}

async def memory_created(memory, context):
    """Called when a new memory is created"""
    print(f"New memory created: {memory.id}")
    
async def search_performed(query, results, context):
    """Called when a search is performed"""
    print(f"Search performed: {query} -> {len(results)} results")
```

### **2. Install Plugin Dependencies**
```bash
# Create requirements.txt for your plugin
echo "requests==2.31.0" > plugins/my_plugin/requirements.txt

# Install plugin dependencies
pip install -r plugins/my_plugin/requirements.txt
```

### **3. Enable Plugin**
```yaml
# config/settings.yaml
plugins:
  enabled: true
  auto_load: true
  plugins:
    - "memory_analytics"
    - "my_plugin"
```

## 🔌 **Available Hooks**

### **Memory Events**
- `memory_created(memory, context)` - When a new memory is created
- `memory_updated(memory, context)` - When a memory is updated
- `memory_deleted(memory_id, context)` - When a memory is deleted
- `memory_retrieved(memory, context)` - When a memory is retrieved

### **Search Events**
- `search_performed(query, results, context)` - When a search is performed
- `search_failed(query, error, context)` - When a search fails

### **Server Events**
- `server_started(context)` - When the server starts
- `server_stopped(context)` - When the server stops
- `health_check(context)` - During health checks

### **Cache Events**
- `cache_hit(key, value, context)` - When cache hit occurs
- `cache_miss(key, context)` - When cache miss occurs
- `cache_updated(key, value, context)` - When cache is updated

## 📝 **Plugin Development**

### **Plugin Structure**
```python
# Required plugin information
PLUGIN_INFO = {
    "name": "Plugin Name",
    "version": "1.0.0",
    "description": "Plugin description",
    "author": "Author Name",
    "hooks": ["hook1", "hook2"],  # List of hooks this plugin uses
    "priority": 1,  # Execution priority (lower = higher priority)
    "enabled": True  # Whether plugin is enabled by default
}

# Hook functions (all are async)
async def hook1(data, context):
    """Hook function implementation"""
    pass

async def hook2(data, context):
    """Another hook function"""
    pass

# Optional: Plugin initialization
async def initialize(context):
    """Called when plugin is loaded"""
    print("Plugin initialized")

# Optional: Plugin cleanup
async def cleanup(context):
    """Called when plugin is unloaded"""
    print("Plugin cleaned up")
```

### **Context Object**
The `context` parameter contains:
```python
context = {
    "plugin_name": "my_plugin",
    "server_config": {...},  # Server configuration
    "logger": logger,  # Plugin logger
    "memory_service": memory_service,  # Access to memory service
    "database_service": database_service,  # Access to database service
    "embedding_service": embedding_service,  # Access to embedding service
    "cache_service": cache_service,  # Access to cache service
    "user_id": "user123",  # Current user ID (if available)
    "session_id": "session456",  # Current session ID (if available)
    "project": "project_name",  # Current project (if available)
    "metadata": {...}  # Additional metadata
}
```

### **Error Handling**
```python
async def memory_created(memory, context):
    try:
        # Your plugin logic here
        await process_memory(memory)
    except Exception as e:
        context["logger"].error(f"Plugin error: {e}")
        # Don't raise the exception - handle it gracefully
```

## 🔧 **Built-in Plugins**

### **Memory Analytics Plugin**
- **Location**: `plugins/memory_analytics/`
- **Description**: Provides advanced memory analysis and insights
- **Features**:
  - Memory usage statistics
  - Search pattern analysis
  - Memory growth tracking
  - Performance metrics

### **Backup Manager Plugin**
- **Location**: `plugins/backup_manager/`
- **Description**: Advanced backup and restore functionality
- **Features**:
  - Automated backups
  - Backup scheduling
  - Compression and encryption
  - Restore functionality

### **Notification Service Plugin**
- **Location**: `plugins/notification_service/`
- **Description**: Multi-channel notification system
- **Features**:
  - Email notifications
  - Webhook notifications
  - Slack integration
  - Custom notification channels

### **Export Service Plugin**
- **Location**: `plugins/export_service/`
- **Description**: Data export in multiple formats
- **Features**:
  - JSON export
  - CSV export
  - Markdown export
  - Batch processing

## 🧪 **Testing Plugins**

### **Unit Testing**
```python
# tests/unit/test_my_plugin.py
import pytest
from plugins.my_plugin.plugin import memory_created

@pytest.mark.asyncio
async def test_memory_created():
    # Create test memory
    memory = Memory(id="test123", content="Test content")
    context = {"logger": mock_logger}
    
    # Test hook
    await memory_created(memory, context)
    
    # Assert expected behavior
    assert mock_logger.info.called
```

### **Integration Testing**
```python
# tests/integration/test_plugin_system.py
@pytest.mark.asyncio
async def test_plugin_loading():
    # Test plugin loading
    plugin_service = PluginService(settings)
    await plugin_service.initialize()
    
    # Verify plugin is loaded
    assert "my_plugin" in plugin_service.loaded_plugins
```

## 📊 **Plugin Management**

### **List Loaded Plugins**
```bash
# Check loaded plugins
curl http://localhost:8000/plugins/list
```

### **Enable/Disable Plugins**
```bash
# Enable plugin
curl -X POST http://localhost:8000/plugins/enable/my_plugin

# Disable plugin
curl -X POST http://localhost:8000/plugins/disable/my_plugin
```

### **Plugin Status**
```bash
# Check plugin status
curl http://localhost:8000/plugins/status/my_plugin
```

## 🔒 **Security Considerations**

### **Plugin Isolation**
- Plugins run in isolated contexts
- Limited access to server internals
- Error handling prevents plugin crashes

### **Dependency Management**
- Each plugin has its own requirements
- Dependencies are isolated
- Version conflicts are handled

### **Access Control**
- Plugins can only access provided services
- No direct file system access
- Logging of all plugin activities

## 📚 **Documentation**

### **Plugin API Reference**
- [Hook Reference](docs/plugins/hooks.md)
- [Context Object](docs/plugins/context.md)
- [Error Handling](docs/plugins/errors.md)

### **Examples**
- [Basic Plugin](examples/basic_plugin/)
- [Advanced Plugin](examples/advanced_plugin/)
- [Integration Plugin](examples/integration_plugin/)

### **Best Practices**
- [Plugin Development](docs/plugins/development.md)
- [Testing Plugins](docs/plugins/testing.md)
- [Deployment](docs/plugins/deployment.md)

## 🤝 **Contributing**

### **Creating Plugins**
1. Create plugin directory in `plugins/`
2. Implement plugin logic
3. Add tests
4. Update documentation
5. Submit pull request

### **Plugin Guidelines**
- Follow naming conventions
- Include proper error handling
- Add comprehensive tests
- Document all features
- Use async/await patterns

## 🆘 **Troubleshooting**

### **Common Issues**
- **Plugin not loading**: Check `PLUGIN_INFO` structure
- **Hook not called**: Verify hook name in `hooks` list
- **Import errors**: Check plugin dependencies
- **Performance issues**: Optimize hook functions

### **Debugging**
```python
# Enable debug logging
context["logger"].setLevel("DEBUG")

# Add debug information
context["logger"].debug(f"Plugin data: {data}")
```

---

**For more information, see the [Plugin Development Guide](docs/plugins/development.md)** 