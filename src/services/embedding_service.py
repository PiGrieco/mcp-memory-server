"""
Embedding service for MCP Memory Server
"""

import asyncio
import logging
import numpy as np
from typing import List, Optional, Dict, Any
from pathlib import Path

from sentence_transformers import SentenceTransformer
from transformers import AutoTokenizer, AutoModel
import torch

from ..config.settings import EmbeddingConfig
from ..utils.exceptions import EmbeddingServiceError

logger = logging.getLogger(__name__)


class EmbeddingService:
    """Embedding service for text vectorization"""
    
    def __init__(self, settings: EmbeddingConfig):
        self.settings = settings
        self.model: Optional[SentenceTransformer] = None
        self.tokenizer: Optional[AutoTokenizer] = None
        self.transformer_model: Optional[AutoModel] = None
        self._initialized = False
        
        # Metrics
        self._embedding_count = 0
        self._total_embedding_time = 0.0
        self._error_count = 0
    
    async def initialize(self) -> None:
        """Initialize embedding service"""
        if self._initialized:
            return
        
        try:
            # Create model cache directory
            cache_dir = Path(self.settings.model_cache_dir)
            cache_dir.mkdir(parents=True, exist_ok=True)
            
            # Load model based on provider
            if self.settings.provider == "sentence_transformers":
                await self._load_sentence_transformer()
            elif self.settings.provider == "huggingface":
                await self._load_huggingface_model()
            else:
                raise EmbeddingServiceError(f"Unsupported embedding provider: {self.settings.provider}")
            
            self._initialized = True
            logger.info(f"Embedding service initialized with {self.settings.provider}")
            
        except Exception as e:
            logger.error(f"Failed to initialize embedding service: {e}")
            raise EmbeddingServiceError(f"Embedding service initialization failed: {e}")
    
    async def _load_sentence_transformer(self) -> None:
        """Load SentenceTransformer model"""
        try:
            self.model = SentenceTransformer(
                self.settings.model_name,
                cache_folder=self.settings.model_cache_dir,
                device=self.settings.device
            )
            
            # Test the model
            test_embedding = self.model.encode("test", normalize_embeddings=self.settings.normalize_embeddings)
            logger.info(f"Loaded SentenceTransformer model: {self.settings.model_name}")
            logger.info(f"Embedding dimensions: {len(test_embedding)}")
            
        except Exception as e:
            logger.error(f"Failed to load SentenceTransformer model: {e}")
            raise
    
    async def _load_huggingface_model(self) -> None:
        """Load HuggingFace model"""
        try:
            self.tokenizer = AutoTokenizer.from_pretrained(
                self.settings.model_name,
                cache_dir=self.settings.model_cache_dir
            )
            
            self.transformer_model = AutoModel.from_pretrained(
                self.settings.model_name,
                cache_dir=self.settings.model_cache_dir
            )
            
            if self.settings.device != "cpu":
                self.transformer_model = self.transformer_model.to(self.settings.device)
            
            # Test the model
            test_embedding = await self._generate_huggingface_embedding("test")
            logger.info(f"Loaded HuggingFace model: {self.settings.model_name}")
            logger.info(f"Embedding dimensions: {len(test_embedding)}")
            
        except Exception as e:
            logger.error(f"Failed to load HuggingFace model: {e}")
            raise
    
    async def _ensure_initialized(self) -> None:
        """Ensure service is initialized"""
        if not self._initialized:
            await self.initialize()
    
    def _update_metrics(self, success: bool = True, duration: float = 0.0) -> None:
        """Update operation metrics"""
        if success:
            self._embedding_count += 1
            self._total_embedding_time += duration
        else:
            self._error_count += 1
    
    async def generate_embedding(self, text: str) -> List[float]:
        """Generate embedding for text"""
        await self._ensure_initialized()
        
        try:
            import time
            start_time = time.time()
            
            # Truncate text if too long
            if len(text) > self.settings.max_text_length:
                text = text[:self.settings.max_text_length]
            
            # Generate embedding based on provider
            if self.settings.provider == "sentence_transformers":
                embedding = self.model.encode(
                    text, 
                    normalize_embeddings=self.settings.normalize_embeddings
                )
            elif self.settings.provider == "huggingface":
                embedding = await self._generate_huggingface_embedding(text)
            else:
                raise EmbeddingServiceError(f"Unsupported provider: {self.settings.provider}")
            
            duration = time.time() - start_time
            self._update_metrics(success=True, duration=duration)
            
            # Convert to list
            if isinstance(embedding, np.ndarray):
                embedding = embedding.tolist()
            
            logger.debug(f"Generated embedding in {duration:.3f}s")
            return embedding
            
        except Exception as e:
            self._update_metrics(success=False)
            logger.error(f"Failed to generate embedding: {e}")
            raise EmbeddingServiceError(f"Failed to generate embedding: {e}")
    
    async def _generate_huggingface_embedding(self, text: str) -> np.ndarray:
        """Generate embedding using HuggingFace model"""
        try:
            # Tokenize
            inputs = self.tokenizer(
                text,
                return_tensors="pt",
                max_length=self.settings.max_text_length,
                truncation=True,
                padding=True
            )
            
            # Move to device
            if self.settings.device != "cpu":
                inputs = {k: v.to(self.settings.device) for k, v in inputs.items()}
            
            # Generate embeddings
            with torch.no_grad():
                outputs = self.transformer_model(**inputs)
                # Use mean pooling
                embeddings = outputs.last_hidden_state.mean(dim=1)
                
                # Move back to CPU and convert to numpy
                embeddings = embeddings.cpu().numpy()
                
                # Normalize if requested
                if self.settings.normalize_embeddings:
                    embeddings = embeddings / np.linalg.norm(embeddings, axis=1, keepdims=True)
                
                return embeddings[0]  # Return first (and only) embedding
                
        except Exception as e:
            logger.error(f"Failed to generate HuggingFace embedding: {e}")
            raise
    
    def calculate_similarity(self, embedding1: List[float], embedding2: List[float]) -> float:
        """Calculate cosine similarity between two embeddings"""
        try:
            # Convert to numpy arrays
            if isinstance(embedding1, list):
                embedding1 = np.array(embedding1)
            if isinstance(embedding2, list):
                embedding2 = np.array(embedding2)
            
            # Calculate cosine similarity
            similarity = np.dot(embedding1, embedding2) / (
                np.linalg.norm(embedding1) * np.linalg.norm(embedding2)
            )
            
            return float(similarity)
            
        except Exception as e:
            logger.error(f"Failed to calculate similarity: {e}")
            return 0.0
    
    async def should_trigger_memory_save(self, content: str, context: Optional[Dict[str, Any]] = None) -> bool:
        """Determine if content should trigger memory save"""
        try:
            # Basic length check
            if len(content) < self.settings.min_text_length:
                return False
            
            # Check for important keywords
            important_keywords = [
                "error", "warning", "bug", "fix", "solution", "problem",
                "decision", "choice", "important", "remember", "note",
                "knowledge", "fact", "information", "learned", "discovered"
            ]
            
            content_lower = content.lower()
            keyword_matches = sum(1 for keyword in important_keywords if keyword in content_lower)
            
            # Simple heuristic: if multiple important keywords, likely worth saving
            if keyword_matches >= 2:
                return True
            
            # Check context for triggers
            if context:
                if context.get("type") == "error":
                    return True
                if context.get("importance", 0) > self.settings.trigger_threshold:
                    return True
            
            # Default: don't trigger
            return False
            
        except Exception as e:
            logger.error(f"Error in should_trigger_memory_save: {e}")
            return False
    
    async def analyze_memory_importance(self, content: str, context: Optional[Dict[str, Any]] = None) -> float:
        """Analyze the importance of content for memory storage"""
        try:
            importance = 0.5  # Default importance
            
            # Length factor
            length_factor = min(len(content) / 1000, 1.0)  # Normalize to 0-1
            importance += length_factor * 0.1
            
            # Keyword importance
            high_importance_keywords = ["error", "bug", "fix", "solution", "decision", "important"]
            medium_importance_keywords = ["warning", "note", "remember", "learned", "discovered"]
            
            content_lower = content.lower()
            
            for keyword in high_importance_keywords:
                if keyword in content_lower:
                    importance += 0.2
            
            for keyword in medium_importance_keywords:
                if keyword in content_lower:
                    importance += 0.1
            
            # Context importance
            if context:
                if context.get("type") == "error":
                    importance += 0.3
                elif context.get("type") == "warning":
                    importance += 0.2
                elif context.get("type") == "decision":
                    importance += 0.25
                
                # User-provided importance
                if "importance" in context:
                    importance = max(importance, context["importance"])
            
            # Cap at 1.0
            return min(importance, 1.0)
            
        except Exception as e:
            logger.error(f"Error in analyze_memory_importance: {e}")
            return 0.5
    
    async def get_metrics(self) -> Dict[str, Any]:
        """Get embedding service metrics"""
        try:
            avg_embedding_time = (
                self._total_embedding_time / self._embedding_count 
                if self._embedding_count > 0 else 0.0
            )
            
            return {
                "provider": self.settings.provider,
                "model_name": self.settings.model_name,
                "embedding_count": self._embedding_count,
                "avg_embedding_time_ms": avg_embedding_time * 1000,
                "error_count": self._error_count,
                "device": self.settings.device,
                "max_text_length": self.settings.max_text_length,
                "normalize_embeddings": self.settings.normalize_embeddings
            }
            
        except Exception as e:
            logger.error(f"Failed to get embedding metrics: {e}")
            return {
                "error": str(e),
                "provider": self.settings.provider,
                "embedding_count": self._embedding_count,
                "error_count": self._error_count
            }
    
    async def health_check(self) -> Dict[str, Any]:
        """Perform health check"""
        try:
            if not self._initialized:
                return {"status": "not_initialized"}
            
            # Test embedding generation
            test_embedding = await self.generate_embedding("health check")
            
            return {
                "status": "healthy",
                "provider": self.settings.provider,
                "model_name": self.settings.model_name,
                "embedding_dimensions": len(test_embedding),
                "device": self.settings.device
            }
            
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e),
                "provider": self.settings.provider
            }
