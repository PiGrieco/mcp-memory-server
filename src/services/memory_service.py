"""
Main memory service for MCP Memory Server
"""

import asyncio
import logging
from typing import List, Dict, Any, Optional, Tuple
import time

from ..config import config
from ..models import (
    Memory, MemoryCreate, MemoryUpdate, MemorySearchQuery, 
    MemorySearchResult, MemoryContext, MemoryContextResult, MemoryStats
)
from .database_service import database_service
from .embedding_service import embedding_service

logger = logging.getLogger(__name__)

class MemoryService:
    """Main service for memory operations"""
    
    def __init__(self):
        self._initialized = False
        self._lock = asyncio.Lock()
    
    async def initialize(self) -> None:
        """Initialize all services"""
        async with self._lock:
            if self._initialized:
                return
            
            try:
                logger.info("Initializing Memory Service...")
                
                # Initialize services in parallel
                await asyncio.gather(
                    database_service.initialize(),
                    embedding_service.initialize()
                )
                
                self._initialized = True
                logger.info("Memory Service initialized successfully")
                
            except Exception as e:
                logger.error(f"Failed to initialize Memory Service: {e}")
                raise
    
    async def create_memory(self, memory_data: MemoryCreate) -> Memory:
        """Create a new memory with embedding"""
        await self._ensure_initialized()
        
        try:
            # Generate embedding
            embedding = await embedding_service.generate_embedding(memory_data.text)
            
            # Create memory in database
            memory = await database_service.create_memory(memory_data, embedding)
            
            logger.info(f"Created memory: {memory.id} (type={memory.type}, project={memory.project})")
            return memory
            
        except Exception as e:
            logger.error(f"Failed to create memory: {e}")
            raise
    
    async def get_memory(self, memory_id: str) -> Optional[Memory]:
        """Get a memory by ID"""
        await self._ensure_initialized()
        
        try:
            return await database_service.get_memory(memory_id)
        except Exception as e:
            logger.error(f"Failed to get memory {memory_id}: {e}")
            raise
    
    async def update_memory(self, memory_id: str, updates: MemoryUpdate) -> Optional[Memory]:
        """Update an existing memory"""
        await self._ensure_initialized()
        
        try:
            # Generate new embedding if text is updated
            embedding = None
            if updates.text is not None:
                embedding = await embedding_service.generate_embedding(updates.text)
            
            # Update memory in database
            memory = await database_service.update_memory(memory_id, updates, embedding)
            
            if memory:
                logger.info(f"Updated memory: {memory_id}")
            else:
                logger.warning(f"Memory not found for update: {memory_id}")
            
            return memory
            
        except Exception as e:
            logger.error(f"Failed to update memory {memory_id}: {e}")
            raise
    
    async def delete_memory(self, memory_id: str) -> bool:
        """Delete a memory"""
        await self._ensure_initialized()
        
        try:
            deleted = await database_service.delete_memory(memory_id)
            return deleted
        except Exception as e:
            logger.error(f"Failed to delete memory {memory_id}: {e}")
            raise
    
    async def search_memories(self, search_query: MemorySearchQuery) -> MemorySearchResult:
        """Search memories by similarity"""
        await self._ensure_initialized()
        
        try:
            start_time = time.time()
            
            # Generate embedding for search query
            query_embedding = await embedding_service.generate_embedding(search_query.query)
            
            # Search in database
            results = await database_service.search_memories(query_embedding, search_query)
            
            # Prepare memories with similarity scores
            memories = []
            for memory, similarity in results:
                memory.similarity = similarity
                memories.append(memory)
            
            search_time = (time.time() - start_time) * 1000  # Convert to milliseconds
            
            result = MemorySearchResult(
                memories=memories,
                total_count=len(memories),
                query=search_query.query,
                search_time_ms=search_time
            )
            
            logger.info(f"Search completed: {len(memories)} results in {search_time:.2f}ms")
            return result
            
        except Exception as e:
            logger.error(f"Failed to search memories: {e}")
            raise
    
    async def get_context(self, context_query: MemoryContext) -> MemoryContextResult:
        """Get context for a project"""
        await self._ensure_initialized()
        
        try:
            start_time = time.time()
            
            # Get memories by type
            context = {}
            total_memories = 0
            
            for memory_type in context_query.types:
                memories = await database_service.get_project_memories(
                    project=context_query.project,
                    memory_types=[memory_type.value],
                    limit=context_query.limit,
                    min_importance=context_query.min_importance
                )
                
                context[memory_type.value] = memories
                total_memories += len(memories)
            
            retrieval_time = (time.time() - start_time) * 1000  # Convert to milliseconds
            
            result = MemoryContextResult(
                project=context_query.project,
                context=context,
                total_memories=total_memories,
                retrieval_time_ms=retrieval_time
            )
            
            logger.info(f"Context retrieved: {total_memories} memories in {retrieval_time:.2f}ms")
            return result
            
        except Exception as e:
            logger.error(f"Failed to get context: {e}")
            raise
    
    async def get_memory_stats(self, project: str) -> MemoryStats:
        """Get statistics for a project"""
        await self._ensure_initialized()
        
        try:
            return await database_service.get_memory_stats(project)
        except Exception as e:
            logger.error(f"Failed to get memory stats: {e}")
            raise
    
    async def batch_create_memories(self, memories: List[MemoryCreate]) -> List[Memory]:
        """Create multiple memories efficiently"""
        await self._ensure_initialized()
        
        try:
            # Generate embeddings in batch
            texts = [memory.text for memory in memories]
            embeddings = await embedding_service.generate_embeddings_batch(texts)
            
            # Create memories in database
            created_memories = []
            for memory_data, embedding in zip(memories, embeddings):
                memory = await database_service.create_memory(memory_data, embedding)
                created_memories.append(memory)
            
            logger.info(f"Batch created {len(created_memories)} memories")
            return created_memories
            
        except Exception as e:
            logger.error(f"Failed to batch create memories: {e}")
            raise
    
    async def cleanup_old_memories(self, days_old: int = 30) -> int:
        """Clean up old, low-importance memories"""
        await self._ensure_initialized()
        
        try:
            deleted_count = await database_service.cleanup_old_memories(days_old)
            return deleted_count
        except Exception as e:
            logger.error(f"Failed to cleanup old memories: {e}")
            raise
    
    async def get_embedding_model_info(self) -> Dict[str, Any]:
        """Get information about the embedding model"""
        await self._ensure_initialized()
        
        try:
            return await embedding_service.get_model_info()
        except Exception as e:
            logger.error(f"Failed to get embedding model info: {e}")
            raise
    
    async def health_check(self) -> Dict[str, Any]:
        """Perform health check on all services"""
        try:
            health_status = {
                "status": "healthy",
                "services": {},
                "timestamp": time.time()
            }
            
            # Check database
            try:
                await database_service._ensure_initialized()
                health_status["services"]["database"] = "healthy"
            except Exception as e:
                health_status["services"]["database"] = f"unhealthy: {e}"
                health_status["status"] = "unhealthy"
            
            # Check embedding service
            try:
                await embedding_service._ensure_initialized()
                health_status["services"]["embedding"] = "healthy"
            except Exception as e:
                health_status["services"]["embedding"] = f"unhealthy: {e}"
                health_status["status"] = "unhealthy"
            
            return health_status
            
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return {
                "status": "unhealthy",
                "error": str(e),
                "timestamp": time.time()
            }
    
    async def _ensure_initialized(self) -> None:
        """Ensure the service is initialized"""
        if not self._initialized:
            await self.initialize()
    
    async def close(self) -> None:
        """Close all services"""
        try:
            await database_service.close()
            logger.info("Memory Service closed")
        except Exception as e:
            logger.error(f"Error closing Memory Service: {e}")
    
    def is_initialized(self) -> bool:
        """Check if the service is initialized"""
        return self._initialized

# Global memory service instance
memory_service = MemoryService() 