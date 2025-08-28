"""
Unit tests for Database Service
"""

import pytest
from unittest.mock import Mock, AsyncMock, patch
from datetime import datetime
from bson import ObjectId

from src.services.database_service import DatabaseService
from src.config.settings import get_settings
from src.models.memory import Memory, MemoryType


class TestDatabaseService:
    """Test cases for DatabaseService"""
    
    @pytest.fixture
    async def database_service(self):
        """Create database service instance for testing"""
        settings = get_settings()
        service = DatabaseService(settings)
        return service
    
    @pytest.fixture
    def mock_memory(self):
        """Create mock memory object"""
        return Memory(
            id="test_memory_123",
            project="test_project",
            content="Test memory content for database testing",
            memory_type=MemoryType.NOTE,
            importance=0.8,
            tags=["test", "database", "unit"],
            metadata={"test": "value"},
            context={"user_id": "test_user"},
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
            access_count=0,
            last_accessed=None,
            embedding=[0.1, 0.2, 0.3, 0.4, 0.5]
        )
    
    @pytest.mark.asyncio
    async def test_initialize_success(self, database_service):
        """Test successful database initialization"""
        # Arrange
        with patch('pymongo.MongoClient') as mock_client:
            mock_db = Mock()
            mock_collection = Mock()
            mock_client.return_value.__getitem__.return_value = mock_db
            mock_db.__getitem__.return_value = mock_collection
            
            # Act
            await database_service.initialize()
            
            # Assert
            assert database_service._initialized is True
            mock_client.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_initialize_connection_error(self, database_service):
        """Test database initialization with connection error"""
        # Arrange
        with patch('pymongo.MongoClient', side_effect=Exception("Connection failed")):
            # Act & Assert
            with pytest.raises(Exception):
                await database_service.initialize()
            
            assert database_service._initialized is False
    
    @pytest.mark.asyncio
    async def test_create_memory_success(self, database_service, mock_memory):
        """Test successful memory creation"""
        # Arrange
        database_service._initialized = True
        database_service.collection = AsyncMock()
        database_service.collection.insert_one.return_value = Mock(inserted_id=ObjectId())
        
        # Act
        result = await database_service.create_memory(mock_memory)
        
        # Assert
        assert result is True
        database_service.collection.insert_one.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_create_memory_not_initialized(self, database_service, mock_memory):
        """Test memory creation when service not initialized"""
        # Arrange
        database_service._initialized = False
        
        # Act & Assert
        with pytest.raises(Exception):
            await database_service.create_memory(mock_memory)
    
    @pytest.mark.asyncio
    async def test_get_memory_success(self, database_service):
        """Test successful memory retrieval"""
        # Arrange
        memory_id = "test_memory_123"
        database_service._initialized = True
        database_service.collection = AsyncMock()
        
        mock_doc = {
            "_id": ObjectId(),
            "id": memory_id,
            "project": "test_project",
            "content": "Test content",
            "memory_type": "note",
            "importance": 0.8,
            "tags": ["test"],
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        
        database_service.collection.find_one.return_value = mock_doc
        
        # Act
        result = await database_service.get_memory(memory_id)
        
        # Assert
        assert result is not None
        assert result["id"] == memory_id
        database_service.collection.find_one.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_get_memory_not_found(self, database_service):
        """Test memory retrieval when not found"""
        # Arrange
        memory_id = "non_existent_id"
        database_service._initialized = True
        database_service.collection = AsyncMock()
        database_service.collection.find_one.return_value = None
        
        # Act
        result = await database_service.get_memory(memory_id)
        
        # Assert
        assert result is None
    
    @pytest.mark.asyncio
    async def test_update_memory_success(self, database_service):
        """Test successful memory update"""
        # Arrange
        memory_id = "test_memory_123"
        update_data = {
            "content": "Updated content",
            "importance": 0.9,
            "tags": ["updated", "test"]
        }
        
        database_service._initialized = True
        database_service.collection = AsyncMock()
        database_service.collection.update_one.return_value = Mock(modified_count=1)
        
        # Act
        result = await database_service.update_memory(memory_id, update_data)
        
        # Assert
        assert result is True
        database_service.collection.update_one.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_delete_memory_success(self, database_service):
        """Test successful memory deletion"""
        # Arrange
        memory_id = "test_memory_123"
        database_service._initialized = True
        database_service.collection = AsyncMock()
        database_service.collection.delete_one.return_value = Mock(deleted_count=1)
        
        # Act
        result = await database_service.delete_memory(memory_id)
        
        # Assert
        assert result is True
        database_service.collection.delete_one.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_list_memories_success(self, database_service):
        """Test successful memory listing"""
        # Arrange
        project = "test_project"
        limit = 10
        offset = 0
        
        database_service._initialized = True
        database_service.collection = AsyncMock()
        
        mock_docs = [
            {
                "_id": ObjectId(),
                "id": f"memory_{i}",
                "project": project,
                "content": f"Test content {i}",
                "memory_type": "note",
                "importance": 0.8,
                "tags": ["test"],
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            }
            for i in range(5)
        ]
        
        database_service.collection.find.return_value.skip.return_value.limit.return_value = mock_docs
        
        # Act
        result = await database_service.list_memories(project, limit, offset)
        
        # Assert
        assert len(result) == 5
        assert all(doc["project"] == project for doc in result)
        database_service.collection.find.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_search_memories_success(self, database_service):
        """Test successful memory search"""
        # Arrange
        query_embedding = [0.1, 0.2, 0.3, 0.4, 0.5]
        project = "test_project"
        max_results = 10
        
        database_service._initialized = True
        database_service.collection = AsyncMock()
        
        mock_docs = [
            {
                "_id": ObjectId(),
                "id": f"memory_{i}",
                "project": project,
                "content": f"Test content {i}",
                "memory_type": "note",
                "importance": 0.8,
                "tags": ["test"],
                "embedding": [0.1, 0.2, 0.3, 0.4, 0.5],
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            }
            for i in range(3)
        ]
        
        database_service.collection.aggregate.return_value = mock_docs
        
        # Act
        result = await database_service.search_memories(query_embedding, project, max_results)
        
        # Assert
        assert len(result) == 3
        assert all(doc["project"] == project for doc in result)
        database_service.collection.aggregate.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_get_memory_stats_success(self, database_service):
        """Test successful memory statistics retrieval"""
        # Arrange
        project = "test_project"
        database_service._initialized = True
        database_service.collection = AsyncMock()
        
        mock_stats = {
            "total_memories": 100,
            "total_size": 1024,
            "avg_importance": 0.75,
            "most_used_tags": ["test", "important"]
        }
        
        database_service.collection.aggregate.return_value = [mock_stats]
        
        # Act
        result = await database_service.get_memory_stats(project)
        
        # Assert
        assert result is not None
        assert result["total_memories"] == 100
        database_service.collection.aggregate.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_create_indexes_success(self, database_service):
        """Test successful index creation"""
        # Arrange
        database_service._initialized = True
        database_service.collection = AsyncMock()
        
        # Act
        await database_service._create_indexes()
        
        # Assert
        # Should create multiple indexes
        assert database_service.collection.create_index.call_count >= 1
    
    @pytest.mark.asyncio
    async def test_health_check_success(self, database_service):
        """Test successful health check"""
        # Arrange
        database_service._initialized = True
        database_service.client = AsyncMock()
        database_service.client.admin.command.return_value = {"ok": 1}
        
        # Act
        result = await database_service.health_check()
        
        # Assert
        assert result["status"] == "healthy"
        assert "database" in result
        assert "connection" in result
    
    @pytest.mark.asyncio
    async def test_health_check_not_initialized(self, database_service):
        """Test health check when not initialized"""
        # Arrange
        database_service._initialized = False
        
        # Act
        result = await database_service.health_check()
        
        # Assert
        assert result["status"] == "not_initialized"
    
    @pytest.mark.asyncio
    async def test_health_check_connection_error(self, database_service):
        """Test health check with connection error"""
        # Arrange
        database_service._initialized = True
        database_service.client = AsyncMock()
        database_service.client.admin.command.side_effect = Exception("Connection failed")
        
        # Act
        result = await database_service.health_check()
        
        # Assert
        assert result["status"] == "unhealthy"
        assert "error" in result
    
    @pytest.mark.asyncio
    async def test_close_connection_success(self, database_service):
        """Test successful connection close"""
        # Arrange
        database_service._initialized = True
        database_service.client = AsyncMock()
        
        # Act
        await database_service.close()
        
        # Assert
        database_service.client.close.assert_called_once()
        assert database_service._initialized is False
    
    @pytest.mark.asyncio
    async def test_get_status_success(self, database_service):
        """Test successful status retrieval"""
        # Arrange
        database_service._initialized = True
        database_service.collection = AsyncMock()
        database_service.collection.count_documents.return_value = 100
        
        # Act
        result = await database_service.get_status()
        
        # Assert
        assert result["status"] == "healthy"
        assert result["total_memories"] == 100
        assert "database_info" in result


if __name__ == "__main__":
    pytest.main([__file__]) 