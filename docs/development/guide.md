# 🔧 **Development Guide - MCP Memory Server**

## 📖 **Introduction**

This guide provides detailed information for developers who want to contribute to the MCP Memory Server or understand how the project works internally.

## 🚀 **Development Environment Setup**

### **1. Prerequisites**
```bash
# Python 3.8+
python3 --version

# Git
git --version

# MongoDB (local or Atlas)
mongod --version

# Redis (optional)
redis-server --version
```

### **2. Environment Setup**
```bash
# Clone repository
git clone https://github.com/your-repo/mcp-memory-server.git
cd mcp-memory-server

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # Linux/macOS
# or
venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt

# Install development dependencies
pip install pytest pytest-asyncio pytest-cov black isort mypy
```

### **3. Development Configuration**
```bash
# Copy example configuration
cp config/settings.yaml.example config/settings.yaml
cp env.example .env

# Edit configuration for development
nano config/settings.yaml
nano .env
```

### **4. Database Configuration**
```bash
# Local MongoDB
mongod --dbpath ./data/db

# Or use MongoDB Atlas
# Update MONGODB_URI in .env
```

## 🏗️ **Code Structure**

### **Module Organization**
```
src/
├── core/                    # Core server logic
│   ├── server.py           # Main MCP server
│   └── __init__.py
├── services/               # Business services
│   ├── memory_service.py   # Memory management
│   ├── database_service.py # Database operations
│   ├── embedding_service.py # Embedding generation
│   ├── cache_service.py    # Distributed cache
│   ├── plugin_service.py   # Plugin system
│   ├── backup_service.py   # Automatic backup
│   ├── notification_service.py # Notifications
│   ├── export_service.py   # Data export
│   └── __init__.py
├── models/                 # Data models
│   ├── memory.py          # Memory model
│   └── __init__.py
├── config/                 # Configuration
│   ├── settings.py        # Configuration management
│   └── __init__.py
└── utils/                  # Utilities
    ├── exceptions.py      # Custom exceptions
    └── __init__.py
```

### **Code Conventions**

#### **1. Naming**
```python
# Classes: PascalCase
class MemoryService:
    pass

# Functions and variables: snake_case
def create_memory():
    pass

# Constants: UPPER_SNAKE_CASE
MAX_MEMORY_SIZE = 10000
```

#### **2. File Organization**
```python
# Standard imports first
import os
import sys
from typing import Optional, List

# Third-party imports
import pymongo
from pydantic import BaseModel

# Local imports
from src.models.memory import Memory
from src.utils.exceptions import MemoryServiceError
```

#### **3. Documentation**
```python
class MemoryService:
    """Service for managing memories in the MCP Memory Server.
    
    This service handles all memory-related operations including
    creation, retrieval, updating, and deletion of memories.
    
    Attributes:
        database_service: Service for database operations
        embedding_service: Service for embedding generation
        cache_service: Service for caching operations
    """
    
    def __init__(self, settings: Settings):
        """Initialize the MemoryService.
        
        Args:
            settings: Application settings containing configuration
            
        Raises:
            MemoryServiceError: If initialization fails
        """
        pass
```

## 🔧 **Development Workflow**

### **1. Setting Up Development**
```bash
# Fork the repository
# Clone your fork
git clone https://github.com/your-username/mcp-memory-server.git

# Add upstream remote
git remote add upstream https://github.com/original-repo/mcp-memory-server.git

# Create development branch
git checkout -b feature/your-feature-name
```

### **2. Making Changes**
```bash
# Make your changes
# Follow coding conventions
# Add tests for new functionality

# Format code
black src/
isort src/

# Type checking
mypy src/

# Run tests
pytest tests/ -v
```

### **3. Testing**
```bash
# Run all tests
pytest tests/ -v

# Run specific test file
pytest tests/test_memory_service.py -v

# Run with coverage
pytest tests/ --cov=src --cov-report=html

# Run integration tests
pytest tests/integration/ -v
```

### **4. Code Quality**
```bash
# Linting
flake8 src/

# Type checking
mypy src/

# Security check
bandit -r src/

# Complexity check
radon cc src/
```

## 🧪 **Testing Strategy**

### **1. Unit Tests**
```python
# tests/unit/test_memory_service.py
import pytest
from unittest.mock import Mock, patch
from src.services.memory_service import MemoryService
from src.models.memory import Memory

class TestMemoryService:
    @pytest.fixture
    def memory_service(self):
        """Create MemoryService instance for testing."""
        settings = Mock()
        return MemoryService(settings)
    
    @pytest.mark.asyncio
    async def test_create_memory(self, memory_service):
        """Test memory creation."""
        memory_data = {
            "content": "Test memory content",
            "project": "test_project",
            "user_id": "test_user"
        }
        
        result = await memory_service.create_memory(**memory_data)
        
        assert result is not None
        assert result.content == memory_data["content"]
        assert result.project == memory_data["project"]
```

### **2. Integration Tests**
```python
# tests/integration/test_full_workflow.py
import pytest
from src.services.memory_service import MemoryService
from src.config.settings import get_settings

class TestFullWorkflow:
    @pytest.mark.asyncio
    async def test_memory_workflow(self):
        """Test complete memory workflow."""
        settings = get_settings()
        memory_service = MemoryService(settings)
        
        # Create memory
        memory = await memory_service.create_memory(
            content="Test content",
            project="test_project"
        )
        
        # Search memory
        results = await memory_service.search_memories("test")
        
        # Verify results
        assert len(results) > 0
        assert memory.id in [r.id for r in results]
```

### **3. Performance Tests**
```python
# tests/performance/test_performance.py
import pytest
import time
from src.services.memory_service import MemoryService

class TestPerformance:
    @pytest.mark.asyncio
    async def test_memory_creation_performance(self):
        """Test memory creation performance."""
        settings = get_settings()
        memory_service = MemoryService(settings)
        
        start_time = time.time()
        
        # Create multiple memories
        for i in range(100):
            await memory_service.create_memory(
                content=f"Memory {i}",
                project="performance_test"
            )
        
        end_time = time.time()
        duration = end_time - start_time
        
        # Should complete within 10 seconds
        assert duration < 10.0
```

## 🔌 **Plugin Development**

### **1. Creating a Plugin**
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
    """Called when a new memory is created."""
    print(f"New memory created: {memory.id}")
    
async def search_performed(query, results, context):
    """Called when a search is performed."""
    print(f"Search performed: {query} -> {len(results)} results")
```

### **2. Testing Plugins**
```python
# tests/unit/test_my_plugin.py
import pytest
from plugins.my_plugin.plugin import memory_created, search_performed

@pytest.mark.asyncio
async def test_memory_created_hook():
    """Test memory_created hook."""
    memory = Mock()
    memory.id = "test123"
    context = {"logger": Mock()}
    
    await memory_created(memory, context)
    
    # Add assertions based on expected behavior
    assert True
```

## 📊 **Monitoring and Debugging**

### **1. Logging**
```python
import logging

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

# Use in code
logger.debug("Debug message")
logger.info("Info message")
logger.warning("Warning message")
logger.error("Error message")
```

### **2. Performance Monitoring**
```python
import time
from functools import wraps

def timing_decorator(func):
    """Decorator to measure function execution time."""
    @wraps(func)
    async def wrapper(*args, **kwargs):
        start_time = time.time()
        result = await func(*args, **kwargs)
        end_time = time.time()
        print(f"{func.__name__} took {end_time - start_time:.2f} seconds")
        return result
    return wrapper

@timing_decorator
async def slow_function():
    """Example slow function."""
    await asyncio.sleep(1)
```

### **3. Memory Profiling**
```python
import tracemalloc

# Start memory tracking
tracemalloc.start()

# Your code here
memory_service = MemoryService(settings)
await memory_service.create_memory(content="Test")

# Get memory snapshot
snapshot = tracemalloc.take_snapshot()
top_stats = snapshot.statistics('lineno')

print("[ Top 10 memory users ]")
for stat in top_stats[:10]:
    print(stat)
```

## 🚀 **Deployment**

### **1. Development Deployment**
```bash
# Start development server
./scripts/main.sh server http

# Or start MCP server
./scripts/main.sh server mcp
```

### **2. Production Deployment**
```bash
# Build Docker image
docker build -t mcp-memory-server .

# Run with Docker Compose
docker-compose up -d

# Or deploy to Kubernetes
kubectl apply -f deployment/kubernetes/
```

### **3. Environment Management**
```bash
# Switch to production environment
./scripts/utils/manage_environments.sh switch production

# Check current environment
./scripts/utils/manage_environments.sh current
```

## 📚 **API Development**

### **1. Adding New Endpoints**
```python
# servers/http_server.py
from fastapi import APIRouter, HTTPException
from src.models.memory import Memory

router = APIRouter()

@router.post("/memories/", response_model=Memory)
async def create_memory(memory: MemoryCreate):
    """Create a new memory."""
    try:
        result = await memory_service.create_memory(**memory.dict())
        return result
    except MemoryServiceError as e:
        raise HTTPException(status_code=400, detail=str(e))
```

### **2. Error Handling**
```python
from src.utils.exceptions import (
    MemoryServiceError,
    DatabaseServiceError,
    EmbeddingServiceError
)

async def handle_memory_operation():
    """Handle memory operations with proper error handling."""
    try:
        result = await memory_service.create_memory(content="test")
        return result
    except MemoryServiceError as e:
        logger.error(f"Memory service error: {e}")
        raise HTTPException(status_code=500, detail="Memory service error")
    except DatabaseServiceError as e:
        logger.error(f"Database error: {e}")
        raise HTTPException(status_code=503, detail="Database unavailable")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
```

## 🔒 **Security Considerations**

### **1. Input Validation**
```python
from pydantic import BaseModel, validator
from typing import Optional

class MemoryCreate(BaseModel):
    content: str
    project: Optional[str] = "default"
    user_id: Optional[str] = None
    
    @validator('content')
    def validate_content(cls, v):
        if len(v.strip()) < 10:
            raise ValueError('Content must be at least 10 characters')
        if len(v) > 10000:
            raise ValueError('Content must be less than 10000 characters')
        return v.strip()
```

### **2. Authentication and Authorization**
```python
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer

security = HTTPBearer()

async def get_current_user(token: str = Depends(security)):
    """Validate user token and return user information."""
    try:
        # Validate token
        user = validate_token(token.credentials)
        return user
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials"
        )

@router.post("/memories/")
async def create_memory(
    memory: MemoryCreate,
    current_user: User = Depends(get_current_user)
):
    """Create memory with user authentication."""
    memory.user_id = current_user.id
    return await memory_service.create_memory(**memory.dict())
```

## 📈 **Performance Optimization**

### **1. Database Optimization**
```python
# Use indexes for frequently queried fields
await collection.create_index([("content", "text")])
await collection.create_index([("project", 1)])
await collection.create_index([("user_id", 1)])

# Use projection to limit returned fields
result = await collection.find_one(
    {"_id": memory_id},
    projection={"content": 1, "project": 1, "_id": 0}
)
```

### **2. Caching Strategy**
```python
# Cache frequently accessed data
async def get_memory(memory_id: str):
    """Get memory with caching."""
    cache_key = f"memory:{memory_id}"
    
    # Try cache first
    cached = await cache_service.get(cache_key)
    if cached:
        return cached
    
    # Get from database
    memory = await database_service.get_memory(memory_id)
    
    # Cache for 1 hour
    await cache_service.set(cache_key, memory, ttl=3600)
    
    return memory
```

### **3. Async Operations**
```python
# Use asyncio.gather for parallel operations
async def process_multiple_memories(memory_ids: List[str]):
    """Process multiple memories in parallel."""
    tasks = [get_memory(memory_id) for memory_id in memory_ids]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    # Filter out exceptions
    valid_results = [r for r in results if not isinstance(r, Exception)]
    return valid_results
```

## 🤝 **Contributing Guidelines**

### **1. Code Review Process**
1. **Create feature branch** from main
2. **Write tests** for new functionality
3. **Follow coding standards** (black, isort, mypy)
4. **Update documentation** if needed
5. **Submit pull request** with clear description
6. **Address review comments** promptly

### **2. Commit Messages**
```bash
# Use conventional commit format
feat: add new memory search endpoint
fix: resolve database connection issue
docs: update installation guide
test: add unit tests for memory service
refactor: improve error handling in cache service
```

### **3. Pull Request Template**
```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
- [ ] Unit tests pass
- [ ] Integration tests pass
- [ ] Manual testing completed

## Checklist
- [ ] Code follows style guidelines
- [ ] Self-review completed
- [ ] Documentation updated
- [ ] No breaking changes
```

## 📞 **Getting Help**

### **Development Resources**
- **Documentation**: `docs/`
- **API Reference**: `docs/development/api.md`
- **Architecture**: `docs/ARCHITECTURE_COMPLETE.md`
- **Testing Guide**: `docs/development/testing.md`

### **Community Support**
- **GitHub Issues**: [Issues](https://github.com/your-repo/mcp-memory-server/issues)
- **Discord**: [Development Channel]
- **Stack Overflow**: Tag with `mcp-memory-server`

### **Code Examples**
- **Service Examples**: `src/services/`
- **Test Examples**: `tests/`
- **Plugin Examples**: `plugins/`

---

**Happy coding! 🚀** 