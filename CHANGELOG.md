# 📝 Changelog - MCP Memory Server

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.0.0] - 2024-01-15

### 🚀 Added - Revolutionary Auto-Trigger System
- **7-Type Auto-Trigger System**: Intelligent automatic triggering based on keywords, patterns, semantic similarity, importance, conversation length, context changes, and time
- **Zero-Dependency Mode**: `main_simple.py` for instant testing without external dependencies
- **Pre-downloaded Models**: 97MB sentence-transformers model included for offline operation
- **One-Click Installer**: `install.py` with automatic Cursor and Claude configuration
- **Multi-Platform Support**: Cursor IDE, Claude Desktop, Browser Extension integration
- **Advanced Browser Extension**: Auto-trigger support for ChatGPT, Claude, Perplexity, Poe
- **Production Docker Support**: Complete containerization with MongoDB
- **Professional Packaging**: `setup.py` and `Makefile` for distribution
- **Comprehensive Examples**: Integration examples for various AI platforms

### 🧠 Auto-Trigger Features
- **Keyword Detection**: Automatic save on "ricorda", "importante", "nota", etc.
- **Pattern Recognition**: Auto-save solutions when "risolto", "fixed", "solved" detected
- **Semantic Search**: Automatic context retrieval for similar questions
- **Importance Analysis**: AI-powered importance scoring and auto-save
- **Conversation Summarization**: Automatic summaries for long conversations
- **Context Change Detection**: Smart project memory loading
- **Time-based Triggers**: Proactive memory suggestions

### 🔧 Enhanced Core Features
- **Enhanced MCP Server**: `src/core/mcp_server_enhanced.py` with auto-trigger integration
- **Advanced Memory Service**: Improved embeddings and search capabilities
- **Cloud Integration**: MongoDB Atlas support with connection pooling
- **Metrics and Monitoring**: Performance tracking and health checks
- **Graceful Shutdown**: Production-ready error handling and cleanup

### 📚 Documentation & Guides
- **Complete Installation Guide**: Step-by-step setup for all platforms
- **Comprehensive Usage Guide**: Examples and best practices
- **API Reference**: Detailed API documentation with examples
- **Model Documentation**: Pre-downloaded model information and management

### 🎯 Platform Integration
- **Cursor IDE**: Native MCP integration with auto-configuration
- **Claude Desktop**: Seamless integration with auto-trigger support
- **Browser Extension**: Universal support for web-based AI platforms
- **Direct API**: Python and JavaScript client examples

## [1.0.0] - 2023-12-01

### 🎉 Initial Release
- **Basic MCP Server**: Standard memory save/search functionality
- **MongoDB Integration**: Database storage for memories
- **Sentence Transformers**: Semantic similarity search
- **Simple Browser Extension**: Basic memory management
- **Docker Support**: Basic containerization

### Core Features
- `save_memory` tool for storing information
- `search_memories` tool for finding relevant content  
- `list_memories` tool for browsing stored memories
- Basic embedding generation and similarity matching
- Project-based memory organization

### Technical Foundation
- Python 3.8+ support
- MCP protocol implementation
- MongoDB database backend
- Sentence-transformers for embeddings
- FastAPI for HTTP endpoints

## [Unreleased]

### 🔮 Planned Features
- **Visual Dashboard**: Web interface for memory management
- **Team Collaboration**: Shared memory spaces
- **Cloud Sync**: Cross-device memory synchronization
- **Mobile App**: Access memories on mobile devices
- **Advanced Analytics**: Memory usage insights and patterns
- **Plugin System**: Extensible trigger architecture
- **More AI Platforms**: GitHub Copilot, Codium integration
- **Smart Categorization**: AI-powered memory organization

### Performance Improvements
- **Caching Layer**: Redis integration for faster access
- **Batch Processing**: Improved embedding generation
- **Background Tasks**: Async memory processing
- **Memory Optimization**: Reduced resource usage

---

## Migration Guides

### From v1.0.0 to v2.0.0

#### Breaking Changes
- **Server Entry Points**: `main.py` now requires MongoDB by default
- **Configuration Format**: New environment variable structure
- **Auto-Trigger**: New automatic behavior may change user experience

#### Migration Steps

1. **Update Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Run Migration Script**:
   ```bash
   python scripts/migrate_v1_to_v2.py
   ```

3. **Update Configuration**:
   ```bash
   # Old format
   MONGODB_URL="mongodb://localhost:27017/memory_db"
   
   # New format  
   MONGODB_URI="mongodb://localhost:27017"
   MONGODB_DATABASE="mcp_memory"
   ```

4. **Test Auto-Triggers**:
   ```bash
   python test_auto_trigger.py
   ```

#### New Features Available
- Use `main_simple.py` for zero-dependency testing
- Configure auto-triggers with environment variables
- Access pre-downloaded models in `models/` directory
- Use one-click installer for new setups

#### Deprecated Features
- Direct database URL configuration (use separate host/port)
- Manual memory saving required (auto-triggers now available)
- Single server mode (multiple entry points now available)

### Compatibility

| Feature | v1.0.0 | v2.0.0 |
|---------|--------|--------|
| **Basic Memory Tools** | ✅ | ✅ |
| **MongoDB Storage** | ✅ | ✅ |
| **Semantic Search** | ✅ | ✅ Enhanced |
| **Browser Extension** | ✅ Basic | ✅ Advanced |
| **Auto-Triggers** | ❌ | ✅ New |
| **Zero Dependencies** | ❌ | ✅ New |
| **Pre-downloaded Models** | ❌ | ✅ New |
| **One-Click Install** | ❌ | ✅ New |
| **Multi-Platform** | ❌ | ✅ New |

---

## Development

### Contributing
1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Release Process
1. Update version in `setup.py` and `src/config/settings.py`
2. Update `CHANGELOG.md` with new features
3. Create release branch (`git checkout -b release/v2.1.0`)
4. Run full test suite (`make test`)
5. Create pull request to main
6. Tag release after merge (`git tag v2.1.0`)
7. Build and publish (`make build && make publish`)

### Version Support

| Version | Status | Support Until |
|---------|--------|---------------|
| **2.0.x** | ✅ Active | TBD |
| **1.0.x** | 🔄 Maintenance | 2024-06-01 |

---

For detailed information about any version, see the documentation in the corresponding release tag.
