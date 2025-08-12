"""
Unit tests for Embedding Service
"""

import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch, MagicMock
import numpy as np
from typing import List

from src.services.embedding_service import EmbeddingService
from src.config.settings import get_settings


class TestEmbeddingService:
    """Test cases for EmbeddingService"""
    
    @pytest.fixture
    async def embedding_service(self):
        """Create embedding service instance for testing"""
        settings = get_settings()
        service = EmbeddingService(settings)
        return service
    
    @pytest.fixture
    def mock_texts(self):
        """Create mock texts for testing"""
        return [
            "This is a test sentence for embedding generation.",
            "Another test sentence with different content.",
            "Third sentence to test batch processing."
        ]
    
    @pytest.fixture
    def mock_embeddings(self):
        """Create mock embeddings for testing"""
        return [
            [0.1, 0.2, 0.3, 0.4, 0.5],
            [0.6, 0.7, 0.8, 0.9, 1.0],
            [0.2, 0.3, 0.4, 0.5, 0.6]
        ]
    
    @pytest.mark.asyncio
    async def test_initialize_success(self, embedding_service):
        """Test successful embedding service initialization"""
        # Arrange
        with patch('sentence_transformers.SentenceTransformer') as mock_transformer:
            mock_model = Mock()
            mock_transformer.return_value = mock_model
            
            # Act
            await embedding_service.initialize()
            
            # Assert
            assert embedding_service._initialized is True
            assert embedding_service.model is not None
            mock_transformer.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_initialize_model_loading_error(self, embedding_service):
        """Test embedding service initialization with model loading error"""
        # Arrange
        with patch('sentence_transformers.SentenceTransformer', side_effect=Exception("Model loading failed")):
            # Act & Assert
            with pytest.raises(Exception):
                await embedding_service.initialize()
            
            assert embedding_service._initialized is False
    
    @pytest.mark.asyncio
    async def test_generate_embedding_success(self, embedding_service, mock_texts, mock_embeddings):
        """Test successful single embedding generation"""
        # Arrange
        text = mock_texts[0]
        expected_embedding = mock_embeddings[0]
        
        embedding_service._initialized = True
        embedding_service.model = Mock()
        embedding_service.model.encode.return_value = np.array(expected_embedding)
        
        # Act
        result = await embedding_service.generate_embedding(text)
        
        # Assert
        assert result is not None
        assert len(result) == len(expected_embedding)
        assert all(abs(a - b) < 1e-6 for a, b in zip(result, expected_embedding))
        embedding_service.model.encode.assert_called_once_with(text)
    
    @pytest.mark.asyncio
    async def test_generate_embedding_not_initialized(self, embedding_service, mock_texts):
        """Test embedding generation when service not initialized"""
        # Arrange
        text = mock_texts[0]
        embedding_service._initialized = False
        
        # Act & Assert
        with pytest.raises(Exception):
            await embedding_service.generate_embedding(text)
    
    @pytest.mark.asyncio
    async def test_generate_embeddings_batch_success(self, embedding_service, mock_texts, mock_embeddings):
        """Test successful batch embedding generation"""
        # Arrange
        embedding_service._initialized = True
        embedding_service.model = Mock()
        embedding_service.model.encode.return_value = np.array(mock_embeddings)
        
        # Act
        result = await embedding_service.generate_embeddings_batch(mock_texts)
        
        # Assert
        assert result is not None
        assert len(result) == len(mock_texts)
        assert all(len(emb) == len(mock_embeddings[0]) for emb in result)
        embedding_service.model.encode.assert_called_once_with(mock_texts)
    
    @pytest.mark.asyncio
    async def test_generate_embeddings_batch_empty_list(self, embedding_service):
        """Test batch embedding generation with empty list"""
        # Arrange
        texts = []
        embedding_service._initialized = True
        
        # Act
        result = await embedding_service.generate_embeddings_batch(texts)
        
        # Assert
        assert result == []
    
    @pytest.mark.asyncio
    async def test_generate_embeddings_batch_large_list(self, embedding_service):
        """Test batch embedding generation with large list"""
        # Arrange
        texts = [f"Test sentence {i}" for i in range(100)]
        mock_embeddings = [[0.1] * 384 for _ in range(100)]  # 384-dim embeddings
        
        embedding_service._initialized = True
        embedding_service.model = Mock()
        embedding_service.model.encode.return_value = np.array(mock_embeddings)
        
        # Act
        result = await embedding_service.generate_embeddings_batch(texts)
        
        # Assert
        assert len(result) == 100
        assert all(len(emb) == 384 for emb in result)
    
    @pytest.mark.asyncio
    async def test_get_embedding_dimension_success(self, embedding_service):
        """Test successful embedding dimension retrieval"""
        # Arrange
        embedding_service._initialized = True
        embedding_service.model = Mock()
        embedding_service.model.get_sentence_embedding_dimension.return_value = 384
        
        # Act
        result = await embedding_service.get_embedding_dimension()
        
        # Assert
        assert result == 384
        embedding_service.model.get_sentence_embedding_dimension.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_get_embedding_dimension_not_initialized(self, embedding_service):
        """Test embedding dimension retrieval when not initialized"""
        # Arrange
        embedding_service._initialized = False
        
        # Act & Assert
        with pytest.raises(Exception):
            await embedding_service.get_embedding_dimension()
    
    @pytest.mark.asyncio
    async def test_calculate_similarity_success(self, embedding_service, mock_embeddings):
        """Test successful similarity calculation"""
        # Arrange
        embedding1 = mock_embeddings[0]
        embedding2 = mock_embeddings[1]
        
        embedding_service._initialized = True
        
        # Act
        result = await embedding_service.calculate_similarity(embedding1, embedding2)
        
        # Assert
        assert isinstance(result, float)
        assert 0.0 <= result <= 1.0
    
    @pytest.mark.asyncio
    async def test_calculate_similarity_identical_embeddings(self, embedding_service, mock_embeddings):
        """Test similarity calculation with identical embeddings"""
        # Arrange
        embedding = mock_embeddings[0]
        embedding_service._initialized = True
        
        # Act
        result = await embedding_service.calculate_similarity(embedding, embedding)
        
        # Assert
        assert abs(result - 1.0) < 1e-6  # Should be very close to 1.0
    
    @pytest.mark.asyncio
    async def test_calculate_similarity_orthogonal_embeddings(self, embedding_service):
        """Test similarity calculation with orthogonal embeddings"""
        # Arrange
        embedding1 = [1.0, 0.0, 0.0]
        embedding2 = [0.0, 1.0, 0.0]
        embedding_service._initialized = True
        
        # Act
        result = await embedding_service.calculate_similarity(embedding1, embedding2)
        
        # Assert
        assert abs(result) < 1e-6  # Should be very close to 0.0
    
    @pytest.mark.asyncio
    async def test_cache_embedding_success(self, embedding_service, mock_texts, mock_embeddings):
        """Test successful embedding caching"""
        # Arrange
        text = mock_texts[0]
        embedding = mock_embeddings[0]
        
        embedding_service._initialized = True
        embedding_service.cache = {}
        
        # Act
        await embedding_service._cache_embedding(text, embedding)
        
        # Assert
        assert text in embedding_service.cache
        assert embedding_service.cache[text] == embedding
    
    @pytest.mark.asyncio
    async def test_get_cached_embedding_success(self, embedding_service, mock_texts, mock_embeddings):
        """Test successful cached embedding retrieval"""
        # Arrange
        text = mock_texts[0]
        embedding = mock_embeddings[0]
        
        embedding_service._initialized = True
        embedding_service.cache = {text: embedding}
        
        # Act
        result = await embedding_service._get_cached_embedding(text)
        
        # Assert
        assert result == embedding
    
    @pytest.mark.asyncio
    async def test_get_cached_embedding_not_found(self, embedding_service, mock_texts):
        """Test cached embedding retrieval when not found"""
        # Arrange
        text = mock_texts[0]
        embedding_service._initialized = True
        embedding_service.cache = {}
        
        # Act
        result = await embedding_service._get_cached_embedding(text)
        
        # Assert
        assert result is None
    
    @pytest.mark.asyncio
    async def test_clear_cache_success(self, embedding_service, mock_texts, mock_embeddings):
        """Test successful cache clearing"""
        # Arrange
        embedding_service._initialized = True
        embedding_service.cache = {
            mock_texts[0]: mock_embeddings[0],
            mock_texts[1]: mock_embeddings[1]
        }
        
        # Act
        await embedding_service.clear_cache()
        
        # Assert
        assert len(embedding_service.cache) == 0
    
    @pytest.mark.asyncio
    async def test_get_cache_stats_success(self, embedding_service, mock_texts, mock_embeddings):
        """Test successful cache statistics retrieval"""
        # Arrange
        embedding_service._initialized = True
        embedding_service.cache = {
            mock_texts[0]: mock_embeddings[0],
            mock_texts[1]: mock_embeddings[1]
        }
        
        # Act
        result = await embedding_service.get_cache_stats()
        
        # Assert
        assert result["cache_size"] == 2
        assert result["cache_hits"] >= 0
        assert result["cache_misses"] >= 0
        assert "hit_rate" in result
    
    @pytest.mark.asyncio
    async def test_health_check_success(self, embedding_service):
        """Test successful health check"""
        # Arrange
        embedding_service._initialized = True
        embedding_service.model = Mock()
        embedding_service.model.get_sentence_embedding_dimension.return_value = 384
        
        # Act
        result = await embedding_service.health_check()
        
        # Assert
        assert result["status"] == "healthy"
        assert "model_info" in result
        assert "cache_info" in result
    
    @pytest.mark.asyncio
    async def test_health_check_not_initialized(self, embedding_service):
        """Test health check when not initialized"""
        # Arrange
        embedding_service._initialized = False
        
        # Act
        result = await embedding_service.health_check()
        
        # Assert
        assert result["status"] == "not_initialized"
    
    @pytest.mark.asyncio
    async def test_health_check_model_error(self, embedding_service):
        """Test health check with model error"""
        # Arrange
        embedding_service._initialized = True
        embedding_service.model = Mock()
        embedding_service.model.get_sentence_embedding_dimension.side_effect = Exception("Model error")
        
        # Act
        result = await embedding_service.health_check()
        
        # Assert
        assert result["status"] == "unhealthy"
        assert "error" in result
    
    @pytest.mark.asyncio
    async def test_get_model_info_success(self, embedding_service):
        """Test successful model information retrieval"""
        # Arrange
        embedding_service._initialized = True
        embedding_service.model = Mock()
        embedding_service.model.get_sentence_embedding_dimension.return_value = 384
        
        # Act
        result = await embedding_service.get_model_info()
        
        # Assert
        assert result["embedding_dimension"] == 384
        assert "model_name" in result
        assert "model_path" in result
    
    @pytest.mark.asyncio
    async def test_get_model_info_not_initialized(self, embedding_service):
        """Test model information retrieval when not initialized"""
        # Arrange
        embedding_service._initialized = False
        
        # Act & Assert
        with pytest.raises(Exception):
            await embedding_service.get_model_info()
    
    @pytest.mark.asyncio
    async def test_generate_embedding_with_cache(self, embedding_service, mock_texts, mock_embeddings):
        """Test embedding generation with cache hit"""
        # Arrange
        text = mock_texts[0]
        embedding = mock_embeddings[0]
        
        embedding_service._initialized = True
        embedding_service.cache = {text: embedding}
        
        # Act
        result = await embedding_service.generate_embedding(text)
        
        # Assert
        assert result == embedding
        # Model should not be called since we have a cache hit
        assert not hasattr(embedding_service.model, 'encode') or not embedding_service.model.encode.called
    
    @pytest.mark.asyncio
    async def test_generate_embedding_cache_miss(self, embedding_service, mock_texts, mock_embeddings):
        """Test embedding generation with cache miss"""
        # Arrange
        text = mock_texts[0]
        embedding = mock_embeddings[0]
        
        embedding_service._initialized = True
        embedding_service.cache = {}
        embedding_service.model = Mock()
        embedding_service.model.encode.return_value = np.array(embedding)
        
        # Act
        result = await embedding_service.generate_embedding(text)
        
        # Assert
        assert result == embedding
        embedding_service.model.encode.assert_called_once_with(text)
        assert text in embedding_service.cache


if __name__ == "__main__":
    pytest.main([__file__]) 