"""
Unit tests for Memory Service
"""

import pytest
import sys
import os
from unittest.mock import AsyncMock
from datetime import datetime

# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
sys.path.insert(0, project_root)

from src.services.memory_service import MemoryService  # noqa: E402
from src.config.settings import get_settings  # noqa: E402
from src.models.memory import Memory, MemoryCreate, MemoryUpdate  # noqa: E402


class TestMemoryService:
    """Test cases for MemoryService"""
    
    @pytest.fixture
    async def memory_service(self):
        """Create memory service instance for testing"""
        settings = get_settings()
        service = MemoryService(settings)
        await service.initialize()
        return service
    
    @pytest.fixture
    def mock_memory(self):
        """Create mock memory object"""
        return Memory(
            id="test_memory_123",
            project="test_project",
            content="Test memory content",
            memory_type="note",
            importance=0.8,
            tags=["test", "unit"],
            metadata={"test": "value"},
            context={"user_id": "test_user"},
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
            access_count=0,
            last_accessed=None,
            embedding=[0.1, 0.2, 0.3]
        )
    
    @pytest.mark.asyncio
    async def test_create_memory_success(self, memory_service):
        """Test successful memory creation"""
        # Arrange
        memory_data = MemoryCreate(
            content="Test memory content",
            project="test_project",
            importance=0.8,
            tags=["test", "unit"]
        )
        
        # Act
        result = await memory_service.create_memory(
            content=memory_data.content,
            project=memory_data.project,
            importance=memory_data.importance,
            tags=memory_data.tags
        )
        
        # Assert
        assert result is not None
        assert result.content == memory_data.content
        assert result.project == memory_data.project
        assert result.importance == memory_data.importance
        assert result.tags == memory_data.tags
        assert result.id is not None
    
    @pytest.mark.asyncio
    async def test_create_memory_invalid_content(self, memory_service):
        """Test memory creation with invalid content"""
        # Arrange
        invalid_content = ""  # Empty content
        
        # Act & Assert
        with pytest.raises(ValueError):
            await memory_service.create_memory(
                content=invalid_content,
                project="test_project"
            )
    
    @pytest.mark.asyncio
    async def test_get_memory_success(self, memory_service, mock_memory):
        """Test successful memory retrieval"""
        # Arrange
        memory_id = mock_memory.id
        
        # Mock database service
        memory_service.database_service.get_memory = AsyncMock(return_value=mock_memory)
        
        # Act
        result = await memory_service.get_memory(memory_id)
        
        # Assert
        assert result is not None
        assert result.id == memory_id
        memory_service.database_service.get_memory.assert_called_once_with(memory_id)
    
    @pytest.mark.asyncio
    async def test_get_memory_not_found(self, memory_service):
        """Test memory retrieval when not found"""
        # Arrange
        memory_id = "non_existent_id"
        memory_service.database_service.get_memory = AsyncMock(return_value=None)
        
        # Act & Assert
        with pytest.raises(ValueError):
            await memory_service.get_memory(memory_id)
    
    @pytest.mark.asyncio
    async def test_update_memory_success(self, memory_service, mock_memory):
        """Test successful memory update"""
        # Arrange
        memory_id = mock_memory.id
        update_data = MemoryUpdate(
            content="Updated content",
            importance=0.9,
            tags=["updated", "test"]
        )
        
        updated_memory = Memory(
            **{**mock_memory.__dict__, **update_data.dict()}
        )
        
        memory_service.database_service.update_memory = AsyncMock(return_value=updated_memory)
        
        # Act
        result = await memory_service.update_memory(memory_id, update_data)
        
        # Assert
        assert result is not None
        assert result.content == update_data.content
        assert result.importance == update_data.importance
        assert result.tags == update_data.tags
    
    @pytest.mark.asyncio
    async def test_delete_memory_success(self, memory_service):
        """Test successful memory deletion"""
        # Arrange
        memory_id = "test_memory_123"
        memory_service.database_service.delete_memory = AsyncMock(return_value=True)
        
        # Act
        result = await memory_service.delete_memory(memory_id)
        
        # Assert
        assert result is True
        memory_service.database_service.delete_memory.assert_called_once_with(memory_id)
    
    @pytest.mark.asyncio
    async def test_search_memories_success(self, memory_service, mock_memory):
        """Test successful memory search"""
        # Arrange
        query = "test query"
        project = "test_project"
        max_results = 10
        
        mock_results = [mock_memory]
        memory_service.database_service.search_memories = AsyncMock(return_value=mock_results)
        
        # Act
        results = await memory_service.search_memories(
            query=query,
            project=project,
            max_results=max_results
        )
        
        # Assert
        assert results is not None
        assert len(results) == 1
        assert results[0].id == mock_memory.id
        memory_service.database_service.search_memories.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_list_memories_success(self, memory_service, mock_memory):
        """Test successful memory listing"""
        # Arrange
        project = "test_project"
        limit = 10
        offset = 0
        
        mock_results = [mock_memory]
        memory_service.database_service.list_memories = AsyncMock(return_value=mock_results)
        
        # Act
        results = await memory_service.list_memories(
            project=project,
            limit=limit,
            offset=offset
        )
        
        # Assert
        assert results is not None
        assert len(results) == 1
        assert results[0].id == mock_memory.id
        memory_service.database_service.list_memories.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_auto_save_memory_success(self, memory_service, mock_memory):
        """Test successful auto-save memory"""
        # Arrange
        content = "Auto-save test content"
        project = "test_project"
        context = {"user_id": "test_user"}
        
        memory_service.embedding_service.should_trigger_memory_save = AsyncMock(return_value=True)
        memory_service.embedding_service.analyze_memory_importance = AsyncMock(return_value=0.8)
        memory_service.create_memory = AsyncMock(return_value=mock_memory)
        
        # Act
        result = await memory_service.auto_save_memory(
            content=content,
            project=project,
            context=context
        )
        
        # Assert
        assert result is not None
        assert result.id == mock_memory.id
        memory_service.embedding_service.should_trigger_memory_save.assert_called_once()
        memory_service.embedding_service.analyze_memory_importance.assert_called_once()
        memory_service.create_memory.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_auto_save_memory_no_trigger(self, memory_service):
        """Test auto-save memory when trigger is false"""
        # Arrange
        content = "Auto-save test content"
        project = "test_project"
        context = {"user_id": "test_user"}
        
        memory_service.embedding_service.should_trigger_memory_save = AsyncMock(return_value=False)
        
        # Act
        result = await memory_service.auto_save_memory(
            content=content,
            project=project,
            context=context
        )
        
        # Assert
        assert result is None
        memory_service.embedding_service.should_trigger_memory_save.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_get_memory_stats_success(self, memory_service):
        """Test successful memory statistics retrieval"""
        # Arrange
        project = "test_project"
        mock_stats = {
            "total_memories": 100,
            "total_size": 1024,
            "avg_importance": 0.75,
            "most_used_tags": ["test", "important"]
        }
        
        memory_service.database_service.get_memory_stats = AsyncMock(return_value=mock_stats)
        
        # Act
        result = await memory_service.get_memory_stats(project)
        
        # Assert
        assert result is not None
        assert result["total_memories"] == 100
        assert result["total_size"] == 1024
        memory_service.database_service.get_memory_stats.assert_called_once_with(project)
    
    @pytest.mark.asyncio
    async def test_get_status_success(self, memory_service):
        """Test successful status retrieval"""
        # Arrange
        _mock_status = {
            "status": "healthy",
            "total_memories": 100,
            "database_connected": True,
            "embedding_service_ready": True
        }
        
        memory_service.database_service.health_check = AsyncMock(return_value={"status": "healthy"})
        memory_service.embedding_service.health_check = AsyncMock(return_value={"status": "healthy"})
        memory_service.database_service.get_memory_stats = AsyncMock(return_value={"total_memories": 100})
        
        # Act
        result = await memory_service.get_status()
        
        # Assert
        assert result is not None
        assert result["status"] == "healthy"
        assert result["total_memories"] == 100
        assert result["database_connected"] is True
        assert result["embedding_service_ready"] is True


if __name__ == "__main__":
    pytest.main([__file__]) 