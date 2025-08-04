# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Initial repository structure and documentation
- GitHub Actions CI/CD pipeline
- Comprehensive testing framework
- Security scanning with bandit

## [1.0.0] - 2024-01-XX

### Added
- Initial release of MCP Memory Server
- Persistent memory system for AI agents using MongoDB
- Semantic search with vector similarity using sentence-transformers
- Model Context Protocol (MCP) server implementation
- Docker support for easy deployment
- Comprehensive MCP tool set with 7 core tools:
  - `save_memory` - Save memories with metadata
  - `search_memory` - Semantic search across memories
  - `get_context` - Retrieve project context
  - `update_memory` - Update existing memories
  - `delete_memory` - Remove memories
  - `get_memory_stats` - Project statistics
  - `health_check` - System health monitoring
- Multi-project support for organizing memories
- Production-ready configuration with health checks
- Async operations for high performance
- Integration examples for Claude Desktop and Cursor AI
- Comprehensive test suite with unit and integration tests
- Development tools and linting configuration
- Documentation and contribution guidelines

### Technical Details
- Python 3.11+ support
- MongoDB 7.0+ with optimized indexing
- sentence-transformers for embedding generation
- Pydantic for data validation
- Docker Compose for development and production
- Comprehensive logging and error handling 