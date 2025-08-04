"""
Embedding service for MCP Memory Server
"""

import asyncio
import logging
from typing import List, Optional, Dict, Any
import numpy as np
from sentence_transformers import SentenceTransformer
from functools import lru_cache
import time

from ..config import config

logger = logging.getLogger(__name__)

class EmbeddingService:
    """Service for generating and managing text embeddings"""
    
    def __init__(self):
        self.model: Optional[SentenceTransformer] = None
        self.embedding_dim: Optional[int] = None
        self._initialized = False
        self._lock = asyncio.Lock()
    
    async def initialize(self) -> None:
        """Initialize the embedding model"""
        async with self._lock:
            if self._initialized:
                return
            
            try:
                logger.info(f"Loading embedding model: {config.embedding.model_name}")
                start_time = time.time()
                
                # Load model with configuration
                model_kwargs = {}
                if config.embedding.cache_dir:
                    model_kwargs['cache_folder'] = config.embedding.cache_dir
                
                self.model = SentenceTransformer(
                    config.embedding.model_name,
                    device=config.embedding.device,
                    **model_kwargs
                )
                
                # Get embedding dimension
                self.embedding_dim = self.model.get_sentence_embedding_dimension()
                
                load_time = time.time() - start_time
                logger.info(f"Model loaded successfully in {load_time:.2f}s (dim={self.embedding_dim})")
                
                self._initialized = True
                
            except Exception as e:
                logger.error(f"Failed to load embedding model: {e}")
                raise
    
    async def generate_embedding(self, text: str) -> List[float]:
        """Generate embedding for a single text"""
        await self._ensure_initialized()
        
        try:
            # Generate embedding
            embedding = self.model.encode(
                text,
                normalize_embeddings=config.embedding.normalize_embeddings
            )
            
            # Convert to list of floats
            return embedding.tolist()
            
        except Exception as e:
            logger.error(f"Failed to generate embedding for text: {e}")
            raise
    
    async def generate_embeddings_batch(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for multiple texts efficiently"""
        await self._ensure_initialized()
        
        if not texts:
            return []
        
        try:
            # Generate embeddings in batch
            embeddings = self.model.encode(
                texts,
                normalize_embeddings=config.embedding.normalize_embeddings,
                show_progress_bar=False
            )
            
            # Convert to list of lists
            return embeddings.tolist()
            
        except Exception as e:
            logger.error(f"Failed to generate batch embeddings: {e}")
            raise
    
    async def compute_similarity(self, embedding1: List[float], embedding2: List[float]) -> float:
        """Compute cosine similarity between two embeddings"""
        try:
            # Convert to numpy arrays
            vec1 = np.array(embedding1, dtype=np.float32)
            vec2 = np.array(embedding2, dtype=np.float32)
            
            # Compute cosine similarity
            similarity = np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2))
            
            # Ensure result is in [0, 1] range
            return max(0.0, min(1.0, float(similarity)))
            
        except Exception as e:
            logger.error(f"Failed to compute similarity: {e}")
            return 0.0
    
    async def compute_similarities_batch(
        self, 
        query_embedding: List[float], 
        embeddings: List[List[float]]
    ) -> List[float]:
        """Compute similarities between query and multiple embeddings"""
        try:
            # Convert to numpy arrays
            query_vec = np.array(query_embedding, dtype=np.float32)
            embedding_matrix = np.array(embeddings, dtype=np.float32)
            
            # Compute cosine similarities
            similarities = np.dot(embedding_matrix, query_vec) / (
                np.linalg.norm(embedding_matrix, axis=1) * np.linalg.norm(query_vec)
            )
            
            # Ensure results are in [0, 1] range
            similarities = np.clip(similarities, 0.0, 1.0)
            
            return similarities.tolist()
            
        except Exception as e:
            logger.error(f"Failed to compute batch similarities: {e}")
            return [0.0] * len(embeddings)
    
    async def get_embedding_dimension(self) -> int:
        """Get the embedding dimension"""
        await self._ensure_initialized()
        return self.embedding_dim
    
    async def get_model_info(self) -> Dict[str, Any]:
        """Get information about the embedding model"""
        await self._ensure_initialized()
        
        return {
            "model_name": config.embedding.model_name,
            "embedding_dimension": self.embedding_dim,
            "device": config.embedding.device,
            "normalize_embeddings": config.embedding.normalize_embeddings,
            "cache_dir": config.embedding.cache_dir
        }
    
    async def _ensure_initialized(self) -> None:
        """Ensure the service is initialized"""
        if not self._initialized:
            await self.initialize()
    
    def is_initialized(self) -> bool:
        """Check if the service is initialized"""
        return self._initialized

# Global embedding service instance
embedding_service = EmbeddingService() 