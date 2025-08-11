"""
Production-ready embedding service with sentence transformers and memory triggers
"""

import asyncio
import logging
import time
from typing import List, Optional, Dict, Any, Union
from pathlib import Path
import numpy as np

from ..config import get_config
from ..utils.exceptions import EmbeddingError, ConfigurationError
from ..utils.retry import retry_async

logger = logging.getLogger(__name__)


class EmbeddingService:
    """Production embedding service with sentence transformers and auto-triggers"""
    
    def __init__(self):
        self.config = get_config()
        self.model = None
        self._initialized = False
        self._model_lock = asyncio.Lock()
        
        # Metrics
        self._embedding_count = 0
        self._total_embedding_time = 0.0
        self._error_count = 0
        
        # Memory trigger settings
        self.trigger_threshold = self.config.memory.trigger_threshold
        self.min_text_length = self.config.memory.min_text_length
        self.auto_save_enabled = self.config.memory.auto_save_enabled
    
    async def initialize(self) -> None:
        """Initialize the embedding model"""
        if self._initialized:
            return
        
        async with self._model_lock:
            if self._initialized:
                return
            
            try:
                await self._load_model()
                self._initialized = True
                logger.info(f"Embedding service initialized with model: {self.config.embedding.model_name}")
                
            except Exception as e:
                logger.error(f"Failed to initialize embedding service: {e}")
                raise EmbeddingError(f"Embedding service initialization failed: {e}")
    
    async def _load_model(self) -> None:
        """Load the sentence transformer model"""
        try:
            # Import sentence transformers
            try:
                from sentence_transformers import SentenceTransformer
            except ImportError:
                raise ConfigurationError(
                    "sentence-transformers package not installed. "
                    "Install with: pip install sentence-transformers"
                )
            
            # Create model cache directory
            cache_dir = Path(self.config.embedding.model_cache_dir)
            cache_dir.mkdir(parents=True, exist_ok=True)
            
            # Load model in thread pool to avoid blocking
            loop = asyncio.get_event_loop()
            self.model = await loop.run_in_executor(
                None,
                lambda: SentenceTransformer(
                    self.config.embedding.model_name,
                    cache_folder=str(cache_dir),
                    device=self.config.embedding.device
                )
            )
            
            logger.info(f"Loaded sentence transformer model: {self.config.embedding.model_name}")
            
        except Exception as e:
            logger.error(f"Failed to load embedding model: {e}")
            raise EmbeddingError(f"Model loading failed: {e}")
    
    async def _ensure_initialized(self) -> None:
        """Ensure the service is initialized"""
        if not self._initialized:
            await self.initialize()
    
    @retry_async(max_attempts=3, delay=1.0)
    async def generate_embedding(self, text: str) -> List[float]:
        """Generate embedding for a single text"""
        await self._ensure_initialized()
        
        if not text or not text.strip():
            raise EmbeddingError("Text cannot be empty")
        
        try:
            start_time = time.time()
            
            # Truncate text if too long
            if len(text) > self.config.embedding.max_text_length:
                text = text[:self.config.embedding.max_text_length]
                logger.warning(f"Text truncated to {self.config.embedding.max_text_length} characters")
            
            # Generate embedding in thread pool
            loop = asyncio.get_event_loop()
            embedding = await loop.run_in_executor(
                None,
                lambda: self.model.encode(
                    text,
                    normalize_embeddings=self.config.embedding.normalize_embeddings,
                    convert_to_numpy=True
                )
            )
            
            # Convert to list and update metrics
            embedding_list = embedding.tolist()
            embedding_time = time.time() - start_time
            
            self._embedding_count += 1
            self._total_embedding_time += embedding_time
            
            logger.debug(f"Generated embedding for text ({len(text)} chars) in {embedding_time:.3f}s")
            return embedding_list
            
        except Exception as e:
            self._error_count += 1
            logger.error(f"Failed to generate embedding: {e}")
            raise EmbeddingError(f"Embedding generation failed: {e}")
    
    @retry_async(max_attempts=3, delay=1.0)
    async def generate_embeddings_batch(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for multiple texts"""
        await self._ensure_initialized()
        
        if not texts:
            return []
        
        # Filter and truncate texts
        processed_texts = []
        for text in texts:
            if text and text.strip():
                if len(text) > self.config.embedding.max_text_length:
                    text = text[:self.config.embedding.max_text_length]
                processed_texts.append(text)
        
        if not processed_texts:
            raise EmbeddingError("No valid texts provided")
        
        try:
            start_time = time.time()
            
            # Process in batches
            batch_size = self.config.embedding.batch_size
            all_embeddings = []
            
            for i in range(0, len(processed_texts), batch_size):
                batch = processed_texts[i:i + batch_size]
                
                # Generate embeddings in thread pool
                loop = asyncio.get_event_loop()
                batch_embeddings = await loop.run_in_executor(
                    None,
                    lambda: self.model.encode(
                        batch,
                        normalize_embeddings=self.config.embedding.normalize_embeddings,
                        convert_to_numpy=True,
                        batch_size=len(batch)
                    )
                )
                
                # Convert to list
                all_embeddings.extend([emb.tolist() for emb in batch_embeddings])
            
            # Update metrics
            embedding_time = time.time() - start_time
            self._embedding_count += len(processed_texts)
            self._total_embedding_time += embedding_time
            
            logger.debug(f"Generated {len(processed_texts)} embeddings in {embedding_time:.3f}s")
            return all_embeddings
            
        except Exception as e:
            self._error_count += 1
            logger.error(f"Failed to generate batch embeddings: {e}")
            raise EmbeddingError(f"Batch embedding generation failed: {e}")
    
    def calculate_similarity(self, embedding1: List[float], embedding2: List[float]) -> float:
        """Calculate cosine similarity between two embeddings"""
        try:
            # Convert to numpy arrays
            vec1 = np.array(embedding1)
            vec2 = np.array(embedding2)
            
            # Calculate cosine similarity
            dot_product = np.dot(vec1, vec2)
            norm1 = np.linalg.norm(vec1)
            norm2 = np.linalg.norm(vec2)
            
            if norm1 == 0 or norm2 == 0:
                return 0.0
            
            similarity = dot_product / (norm1 * norm2)
            return float(similarity)
            
        except Exception as e:
            logger.error(f"Failed to calculate similarity: {e}")
            return 0.0
    
    async def should_trigger_memory_save(self, text: str, context: Optional[Dict[str, Any]] = None) -> bool:
        """
        Determine if text should trigger automatic memory saving
        This is the core sentence transformer memory trigger functionality
        """
        if not self.auto_save_enabled:
            return False
        
        # Check minimum text length
        if len(text.strip()) < self.min_text_length:
            return False
        
        try:
            # Generate embedding for the text
            embedding = await self.generate_embedding(text)
            
            # Simple heuristic: trigger if text contains important keywords
            important_keywords = [
                "remember", "important", "note", "save", "store",
                "decision", "conclusion", "result", "outcome",
                "error", "warning", "issue", "problem", "solution",
                "learned", "discovered", "found", "realized"
            ]
            
            text_lower = text.lower()
            keyword_score = sum(1 for keyword in important_keywords if keyword in text_lower)
            keyword_threshold = 0.1  # At least 10% of keywords should be present
            
            # Calculate trigger score based on multiple factors
            trigger_score = 0.0
            
            # Factor 1: Keyword presence
            if keyword_score > 0:
                trigger_score += min(keyword_score / len(important_keywords), 0.3)
            
            # Factor 2: Text length (longer texts are more likely to be important)
            length_score = min(len(text) / 1000, 0.2)  # Max 0.2 for length
            trigger_score += length_score
            
            # Factor 3: Context-based scoring
            if context:
                # Higher importance if it's a function call result
                if context.get("type") == "function_result":
                    trigger_score += 0.3
                
                # Higher importance if it contains structured data
                if any(key in context for key in ["data", "result", "output"]):
                    trigger_score += 0.2
                
                # Higher importance if it's an error or warning
                if context.get("level") in ["error", "warning"]:
                    trigger_score += 0.4
            
            # Factor 4: Sentence complexity (more complex sentences might be more important)
            sentence_count = text.count('.') + text.count('!') + text.count('?')
            if sentence_count > 1:
                trigger_score += min(sentence_count / 10, 0.1)
            
            # Decision: trigger if score exceeds threshold
            should_trigger = trigger_score >= self.trigger_threshold
            
            logger.debug(f"Memory trigger analysis: score={trigger_score:.3f}, threshold={self.trigger_threshold}, trigger={should_trigger}")
            return should_trigger
            
        except Exception as e:
            logger.error(f"Error in memory trigger analysis: {e}")
            return False
    
    async def analyze_memory_importance(self, text: str, context: Optional[Dict[str, Any]] = None) -> float:
        """Analyze the importance level of a memory based on content and context"""
        try:
            # Base importance
            importance = 0.5
            
            # Analyze text content
            text_lower = text.lower()
            
            # High importance indicators
            high_importance_keywords = ["critical", "urgent", "important", "error", "failure", "security"]
            for keyword in high_importance_keywords:
                if keyword in text_lower:
                    importance += 0.1
            
            # Medium importance indicators
            medium_importance_keywords = ["warning", "note", "remember", "decision", "result"]
            for keyword in medium_importance_keywords:
                if keyword in text_lower:
                    importance += 0.05
            
            # Context-based importance
            if context:
                if context.get("level") == "error":
                    importance += 0.3
                elif context.get("level") == "warning":
                    importance += 0.2
                elif context.get("type") == "function_result":
                    importance += 0.1
            
            # Normalize to [0, 1] range
            importance = max(0.0, min(1.0, importance))
            
            return importance
            
        except Exception as e:
            logger.error(f"Error analyzing memory importance: {e}")
            return 0.5  # Default importance
    
    async def get_metrics(self) -> Dict[str, Any]:
        """Get embedding service metrics"""
        avg_embedding_time = (
            self._total_embedding_time / self._embedding_count 
            if self._embedding_count > 0 else 0.0
        )
        
        return {
            "embedding_count": self._embedding_count,
            "total_embedding_time": self._total_embedding_time,
            "avg_embedding_time_ms": avg_embedding_time * 1000,
            "error_count": self._error_count,
            "model_name": self.config.embedding.model_name,
            "device": self.config.embedding.device,
            "auto_save_enabled": self.auto_save_enabled,
            "trigger_threshold": self.trigger_threshold
        }
    
    async def health_check(self) -> Dict[str, Any]:
        """Perform health check"""
        try:
            if not self._initialized:
                return {"status": "not_initialized"}
            
            # Test embedding generation
            start_time = time.time()
            await self.generate_embedding("health check test")
            response_time = (time.time() - start_time) * 1000
            
            return {
                "status": "healthy",
                "response_time_ms": response_time,
                "model_loaded": self.model is not None
            }
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e)
            }


# Global embedding service instance
embedding_service = EmbeddingService()
