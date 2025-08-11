# Contributing to MCP Memory Server

Thank you for your interest in contributing to MCP Memory Server! This document provides guidelines and information for contributors.

## 🎯 **How to Contribute**

### **Types of Contributions**

We welcome several types of contributions:

- 🐛 **Bug Reports**: Help us identify and fix issues
- ✨ **Feature Requests**: Suggest new functionality
- 🔧 **Code Contributions**: Implement features or fix bugs
- 📖 **Documentation**: Improve or add documentation
- 🧪 **Testing**: Add or improve test coverage
- 🌍 **Translations**: Help make the project multilingual

## 🚀 **Getting Started**

### **Development Setup**

1. **Fork and Clone**
   ```bash
   git clone https://github.com/yourusername/mcp-memory-server.git
   cd mcp-memory-server
   ```

2. **Set up Environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   pip install -r requirements-dev.txt
   ```

3. **Environment Configuration**
   ```bash
   cp .env.example .env.dev
   # Edit .env.dev with your development settings
   ```

4. **Run Tests**
   ```bash
   pytest tests/ -v
   ```

### **Development Workflow**

1. **Create a Branch**
   ```bash
   git checkout -b feature/your-feature-name
   # or
   git checkout -b fix/issue-description
   ```

2. **Make Changes**
   - Write clean, documented code
   - Follow existing code style
   - Add tests for new functionality
   - Update documentation as needed

3. **Test Your Changes**
   ```bash
   # Run full test suite
   pytest tests/
   
   # Run specific tests
   pytest tests/test_memory_service.py
   
   # Run with coverage
   pytest --cov=src tests/
   ```

4. **Commit and Push**
   ```bash
   git add .
   git commit -m "feat: add new auto-trigger pattern"
   git push origin feature/your-feature-name
   ```

5. **Create Pull Request**
   - Use clear, descriptive title
   - Provide detailed description
   - Reference related issues
   - Include test results

## 📝 **Code Standards**

### **Code Style**

- **Python**: Follow PEP 8 with some modifications
- **Line Length**: 100 characters max
- **Imports**: Use absolute imports, group by standard/third-party/local
- **Type Hints**: Required for all public functions
- **Docstrings**: Required for all public classes and functions

### **Example Code Style**

```python
"""
Module docstring describing the purpose of this module.
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any

from src.models import Memory, MemoryCreate
from src.services.database_service import database_service

logger = logging.getLogger(__name__)


class MemoryService:
    """
    Service for managing memory operations.
    
    This service handles all memory-related operations including
    saving, searching, and analyzing memories.
    """
    
    def __init__(self, config: Dict[str, Any]) -> None:
        """
        Initialize the memory service.
        
        Args:
            config: Configuration dictionary containing service settings
        """
        self.config = config
        self._initialized = False
    
    async def create_memory(
        self, 
        memory_create: MemoryCreate, 
        auto_embed: bool = True
    ) -> Memory:
        """
        Create a new memory with optional automatic embedding.
        
        Args:
            memory_create: Memory creation data
            auto_embed: Whether to generate embedding automatically
            
        Returns:
            Created memory object
            
        Raises:
            MemoryServiceError: If memory creation fails
        """
        logger.info(f"Creating memory with content length: {len(memory_create.content)}")
        
        # Implementation here
        pass
```

### **Commit Message Format**

Use conventional commits format:

```
type(scope): description

[optional body]

[optional footer]
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (no logic changes)
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks

**Examples:**
```
feat(ml): add new semantic similarity trigger
fix(memory): resolve embedding generation issue
docs(api): update REST API documentation
test(triggers): add tests for auto-trigger system
```

## 🧪 **Testing Guidelines**

### **Test Structure**

```
tests/
├── unit/                    # Unit tests
│   ├── test_memory_service.py
│   ├── test_embedding_service.py
│   └── test_trigger_system.py
├── integration/             # Integration tests
│   ├── test_mcp_server.py
│   └── test_database_integration.py
├── e2e/                     # End-to-end tests
│   └── test_full_workflow.py
└── fixtures/                # Test data and fixtures
    ├── sample_memories.json
    └── test_conversations.json
```

### **Writing Tests**

```python
import pytest
from unittest.mock import Mock, AsyncMock
from src.services.memory_service import MemoryService
from src.models import MemoryCreate, MemoryType


class TestMemoryService:
    """Test suite for MemoryService."""
    
    @pytest.fixture
    async def memory_service(self):
        """Create a memory service instance for testing."""
        config = {"database_url": "test://localhost"}
        service = MemoryService(config)
        await service.initialize()
        return service
    
    @pytest.mark.asyncio
    async def test_create_memory_success(self, memory_service):
        """Test successful memory creation."""
        # Arrange
        memory_create = MemoryCreate(
            content="Test memory content",
            memory_type=MemoryType.CONVERSATION,
            importance=0.8
        )
        
        # Act
        result = await memory_service.create_memory(memory_create)
        
        # Assert
        assert result is not None
        assert result.content == "Test memory content"
        assert result.importance == 0.8
    
    @pytest.mark.asyncio
    async def test_create_memory_empty_content_fails(self, memory_service):
        """Test that creating memory with empty content fails."""
        # Arrange
        memory_create = MemoryCreate(content="", memory_type=MemoryType.CONVERSATION)
        
        # Act & Assert
        with pytest.raises(ValidationError):
            await memory_service.create_memory(memory_create)
```

## 🐛 **Bug Reports**

### **Before Submitting**

1. **Search existing issues** to avoid duplicates
2. **Update to latest version** and test if issue persists
3. **Check documentation** for known limitations

### **Bug Report Template**

```markdown
## Bug Description
A clear description of what the bug is.

## Steps to Reproduce
1. Go to '...'
2. Click on '....'
3. Scroll down to '....'
4. See error

## Expected Behavior
What you expected to happen.

## Actual Behavior
What actually happened.

## Environment
- OS: [e.g. macOS 12.0, Ubuntu 20.04]
- Python Version: [e.g. 3.9.7]
- MCP Memory Server Version: [e.g. 2.1.0]
- Platform: [e.g. Cursor IDE, Claude Desktop]

## Additional Context
- Error logs
- Screenshots
- Configuration files (redacted)
```

## ✨ **Feature Requests**

### **Feature Request Template**

```markdown
## Feature Description
A clear description of the feature you'd like to see.

## Use Case
Describe the problem this feature would solve.

## Proposed Solution
Describe how you envision this feature working.

## Alternatives Considered
Other solutions you've considered.

## Additional Context
- Mock-ups
- Examples
- Related features
```

## 📖 **Documentation**

### **Documentation Types**

- **API Documentation**: Docstrings and API references
- **User Guides**: How-to guides and tutorials
- **Architecture**: System design and technical details
- **Examples**: Code examples and use cases

### **Documentation Standards**

- Use clear, concise language
- Include code examples
- Provide context and background
- Keep up-to-date with code changes

## 🌍 **Internationalization**

### **Adding Translations**

1. **Create language file**: `src/locales/{language_code}.json`
2. **Add translations**: Follow existing structure
3. **Test translations**: Ensure proper encoding and formatting
4. **Update language detection**: Add language code to supported languages

### **Translation Guidelines**

- Maintain technical accuracy
- Keep consistent terminology
- Consider cultural context
- Test with native speakers when possible

## 📦 **Release Process**

### **For Maintainers**

1. **Version Bump**
   ```bash
   # Update version in setup.py and __init__.py
   git tag v2.1.0
   git push origin v2.1.0
   ```

2. **Release Notes**
   - Document new features
   - List bug fixes
   - Note breaking changes
   - Include migration guides

3. **Distribution**
   ```bash
   # Build and upload to PyPI
   python setup.py sdist bdist_wheel
   twine upload dist/*
   
   # Update Docker images
   docker build -t pigrieco/mcp-memory-server:2.1.0 .
   docker push pigrieco/mcp-memory-server:2.1.0
   ```

## 🤝 **Community Guidelines**

### **Code of Conduct**

- **Be respectful**: Treat everyone with respect and kindness
- **Be inclusive**: Welcome people of all backgrounds and skill levels
- **Be helpful**: Assist others when possible
- **Be constructive**: Provide constructive feedback and criticism

### **Communication Channels**

- **GitHub Issues**: Bug reports and feature requests
- **GitHub Discussions**: General questions and community discussions

## 🏆 **Recognition**

### **Contributors**

I'm looking for somone to build this with: let's make the next REDIS for AI Agents together!

Contact me on LinkedIn: Piermatteo Grieco
