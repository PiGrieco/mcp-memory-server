# Contributing to MCP Memory Server

Thank you for your interest in contributing to MCP Memory Server! This document provides guidelines and information for contributors.

## 🚀 Getting Started

### Prerequisites

- Python 3.11+
- Docker & Docker Compose
- Git
- Basic understanding of async Python and MongoDB

### Development Setup

1. **Fork and Clone**
   ```bash
   git clone https://github.com/your-username/mcp-memory-server.git
   cd mcp-memory-server
   ```

2. **Environment Setup**
   ```bash
   # Copy environment file
   cp .env.example .env
   
   # Create virtual environment
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   
   # Install dependencies
   pip install -r requirements.txt
   pip install -e ".[dev]"
   ```

3. **Start Development Services**
   ```bash
   docker compose up -d mongodb
   ```

4. **Run Tests**
   ```bash
   pytest
   ```

## 📋 How to Contribute

### Reporting Bugs

1. Check if the bug has already been reported in [Issues](https://github.com/your-username/mcp-memory-server/issues)
2. If not, create a new issue with:
   - Clear bug description
   - Steps to reproduce
   - Expected vs actual behavior
   - Environment details (OS, Python version, etc.)
   - Relevant logs or error messages

### Suggesting Features

1. Check [existing feature requests](https://github.com/your-username/mcp-memory-server/issues?q=is%3Aissue+is%3Aopen+label%3Aenhancement)
2. Open a new issue with:
   - Clear feature description
   - Use case and motivation
   - Proposed implementation (if you have ideas)

### Code Contributions

1. **Find an Issue**
   - Look for issues labeled `good first issue` or `help wanted`
   - Comment on the issue to indicate you're working on it

2. **Create a Branch**
   ```bash
   git checkout -b feature/your-feature-name
   # or
   git checkout -b fix/your-bug-fix
   ```

3. **Make Changes**
   - Follow the coding standards (see below)
   - Add/update tests as needed
   - Update documentation if necessary

4. **Test Your Changes**
   ```bash
   # Run all tests
   pytest
   
   # Run with coverage
   pytest --cov=src tests/
   
   # Run linting
   black src/ tests/
   flake8 src/ tests/
   mypy src/
   ```

5. **Commit Your Changes**
   ```bash
   git add .
   git commit -m "feat: add your feature description"
   
   # Follow conventional commits format:
   # feat: new feature
   # fix: bug fix
   # docs: documentation changes
   # style: formatting changes
   # refactor: code refactoring
   # test: adding tests
   # chore: maintenance tasks
   ```

6. **Push and Create PR**
   ```bash
   git push origin your-branch-name
   ```
   Then create a Pull Request on GitHub.

## 🎯 Coding Standards

### Python Style

- **Code Formatting**: Use `black` with default settings
- **Import Sorting**: Use `isort` compatible with black
- **Linting**: Use `flake8` with project configuration
- **Type Hints**: Use type hints for all public functions
- **Docstrings**: Use Google-style docstrings

### Code Structure

```python
"""Module docstring."""

import asyncio
from typing import Dict, List, Optional

from src.models import MemoryModel


class ExampleClass:
    """Class docstring.
    
    Args:
        param1: Description of param1
        param2: Description of param2
    """
    
    def __init__(self, param1: str, param2: int) -> None:
        self.param1 = param1
        self.param2 = param2
    
    async def example_method(self, data: Dict[str, str]) -> Optional[List[str]]:
        """Method docstring.
        
        Args:
            data: Dictionary containing input data
            
        Returns:
            List of processed strings or None if processing fails
            
        Raises:
            ValueError: If data is invalid
        """
        # Implementation here
        pass
```

### Testing

- Write tests for all new functionality
- Maintain test coverage above 90%
- Use descriptive test names
- Group related tests in classes
- Use fixtures for common test data

```python
import pytest
from unittest.mock import AsyncMock, patch

from src.services.memory_service import MemoryService


class TestMemoryService:
    """Test cases for MemoryService."""
    
    @pytest.fixture
    def memory_service(self):
        """Create MemoryService instance for testing."""
        return MemoryService()
    
    @pytest.mark.asyncio
    async def test_save_memory_success(self, memory_service):
        """Test successful memory saving."""
        # Test implementation
        pass
```

## 📁 Project Structure

```
mcp-memory-server/
├── src/                    # Main source code
│   ├── core/              # Core MCP server logic
│   ├── services/          # Business logic services
│   ├── models/            # Data models
│   ├── config/            # Configuration management
│   └── utils/             # Utility functions
├── tests/                 # Test suite
│   ├── unit/             # Unit tests
│   ├── integration/      # Integration tests
│   └── fixtures/         # Test fixtures
├── examples/             # Usage examples
├── docs/                 # Documentation
├── scripts/              # Utility scripts
└── deployment/           # Deployment configurations
```

## 🔍 Pull Request Guidelines

### Before Submitting

- [ ] Code follows project style guidelines
- [ ] Tests pass locally
- [ ] New functionality includes tests
- [ ] Documentation is updated
- [ ] Commit messages follow conventional format
- [ ] PR description clearly explains changes

### PR Template

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
- [ ] Unit tests added/updated
- [ ] Integration tests added/updated
- [ ] Manual testing performed

## Checklist
- [ ] Code follows style guidelines
- [ ] Self-review completed
- [ ] Documentation updated
- [ ] Tests pass
```

## 🏷️ Issue Labels

- `bug`: Something isn't working
- `enhancement`: New feature or request
- `documentation`: Improvements to documentation
- `good first issue`: Good for newcomers
- `help wanted`: Extra attention needed
- `question`: Further information requested
- `wontfix`: This will not be worked on

## 📚 Resources

- [Model Context Protocol Specification](https://modelcontextprotocol.io/)
- [Python Async Programming](https://docs.python.org/3/library/asyncio.html)
- [MongoDB Python Driver](https://pymongo.readthedocs.io/)
- [Sentence Transformers](https://www.sbert.net/)

## 🆘 Getting Help

- **GitHub Discussions**: For questions and general discussion
- **GitHub Issues**: For bug reports and feature requests
- **Documentation**: Check the wiki for detailed guides

## 🎉 Recognition

Contributors will be recognized in:
- README acknowledgments
- Release notes
- GitHub contributors page

Thank you for contributing to MCP Memory Server! 🚀 