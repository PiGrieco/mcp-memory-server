"""
Production memory service with auto-triggers and advanced features
"""

import asyncio
import logging
import time
from datetime import datetime
from typing import List, Optional, Dict, Any

from ..config import get_config
from ..models import (
    Memory, MemoryCreate, MemoryUpdate, MemorySearchQuery, 
    MemorySearchResult, MemoryContext, MemoryContextResult,
    MemoryType, MemoryImportance
)
from ..utils.exceptions import MemoryServiceError, ValidationError
from .database_service import database_service
from .embedding_service import embedding_service

logger = logging.getLogger(__name__)


class MemoryService:
    """Production memory service with intelligent triggers and management"""
    
    def __init__(self):
        self.config = get_config()
        self._initialized = False
        
        # Metrics
        self._operation_count = 0
        self._search_count = 0
        self._auto_save_count = 0
        self._total_search_time = 0.0
        self._error_count = 0
    
    async def initialize(self) -> None:
        """Initialize memory service"""
        if self._initialized:
            return
        
        try:
            # Ensure dependencies are initialized
            await database_service.initialize()
            await embedding_service.initialize()
            
            self._initialized = True
            logger.info("Memory service initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize memory service: {e}")
            raise MemoryServiceError(f"Memory service initialization failed: {e}")
    
    async def _ensure_initialized(self) -> None:
        """Ensure service is initialized"""
        if not self._initialized:
            await self.initialize()
    
    def _update_metrics(self, operation: str, success: bool = True, duration: float = 0.0) -> None:
        """Update operation metrics"""
        self._operation_count += 1
        
        if operation == "search":
            self._search_count += 1
            self._total_search_time += duration
        elif operation == "auto_save":
            self._auto_save_count += 1
        
        if not success:
            self._error_count += 1
    
    async def create_memory(self, memory_create: MemoryCreate, auto_embed: bool = True) -> Memory:
        """Create a new memory with optional automatic embedding"""
        await self._ensure_initialized()
        
        try:
            start_time = time.time()
            
            # Generate embedding if requested
            if auto_embed:
                try:
                    embedding = await embedding_service.generate_embedding(memory_create.content)
                    memory_create.embedding = embedding
                    logger.info(f"Generated embedding with {len(embedding)} dimensions")
                except Exception as e:
                    logger.error(f"Failed to generate embedding: {e}")
                    # Continue without embedding for now
                    memory_create.embedding = None
            
            # Create memory in database
            memory = await database_service.create_memory(memory_create)
            
            duration = time.time() - start_time
            self._update_metrics("create", success=True, duration=duration)
            
            logger.debug(f"Created memory {memory.id} in {duration:.3f}s")
            return memory
            
        except Exception as e:
            self._update_metrics("create", success=False)
            logger.error(f"Failed to create memory: {e}")
            raise MemoryServiceError(f"Memory creation failed: {e}")
    
    async def auto_save_memory(
        self, 
        content: str, 
        context: Optional[Dict[str, Any]] = None,
        project: Optional[str] = None,
        user_id: Optional[str] = None,
        session_id: Optional[str] = None
    ) -> Optional[Memory]:
        """
        Automatically save memory if content triggers the threshold
        This is the core auto-trigger functionality
        """
        await self._ensure_initialized()
        
        try:
            # Check if content should trigger memory save
            should_save = await embedding_service.should_trigger_memory_save(content, context)
            
            if not should_save:
                logger.debug("Content did not trigger memory save threshold")
                return None
            
            # Analyze importance
            importance = await embedding_service.analyze_memory_importance(content, context)
            
            # Determine memory type from context
            memory_type = MemoryType.CONVERSATION
            if context:
                if context.get("type") == "function_result":
                    memory_type = MemoryType.FUNCTION
                elif context.get("level") == "error":
                    memory_type = MemoryType.ERROR
                elif context.get("level") == "warning":
                    memory_type = MemoryType.WARNING
                elif "decision" in content.lower():
                    memory_type = MemoryType.DECISION
                elif any(keyword in content.lower() for keyword in ["knowledge", "fact", "information"]):
                    memory_type = MemoryType.KNOWLEDGE
            
            # Create memory
            memory_create = MemoryCreate(
                project=project or self.config.memory.default_project,
                content=content,
                memory_type=memory_type,
                importance=importance,
                context=context or {},
                user_id=user_id,
                session_id=session_id,
                source="auto_trigger"
            )
            
            memory = await self.create_memory(memory_create)
            self._update_metrics("auto_save", success=True)
            
            logger.info(f"Auto-saved memory {memory.id} with importance {importance:.2f}")
            return memory
            
        except Exception as e:
            self._update_metrics("auto_save", success=False)
            logger.error(f"Auto-save failed: {e}")
            return None
    
    async def search_memories(self, search_query: MemorySearchQuery) -> MemorySearchResult:
        """Search memories with semantic similarity"""
        await self._ensure_initialized()
        
        try:
            start_time = time.time()
            
            # Generate embedding for search query
            query_embedding = await embedding_service.generate_embedding(search_query.query)
            
            # Get candidate memories from database
            candidates = await database_service.search_memories(
                project=search_query.project,
                memory_types=[mt.value for mt in search_query.memory_types] if search_query.memory_types else None,
                min_importance=search_query.min_importance,
                limit=search_query.max_results * 2,  # Get more candidates for similarity filtering
                text_query=search_query.query,
                tags=search_query.tags,
                user_id=search_query.user_id,
                session_id=search_query.session_id,
                date_from=search_query.date_from,
                date_to=search_query.date_to
            )
            
            # Calculate similarity scores
            scored_memories = []
            for memory in candidates:
                if memory.embedding:
                    similarity = embedding_service.calculate_similarity(
                        query_embedding, memory.embedding
                    )
                    if similarity >= search_query.similarity_threshold:
                        memory.similarity_score = similarity
                        scored_memories.append(memory)
            
            # Sort by similarity and limit results
            scored_memories.sort(key=lambda m: m.similarity_score or 0, reverse=True)
            final_memories = scored_memories[:search_query.max_results]
            
            # Update access counts
            for memory in final_memories:
                memory.increment_access()
                await database_service.update_memory(
                    memory.id, 
                    MemoryUpdate(metadata={"access_count": memory.access_count, "last_accessed": memory.last_accessed})
                )
            
            search_time = time.time() - start_time
            self._update_metrics("search", success=True, duration=search_time)
            
            result = MemorySearchResult(
                memories=final_memories,
                total_count=len(final_memories),
                query=search_query.query,
                search_time_ms=search_time * 1000,
                similarity_scores=[m.similarity_score or 0 for m in final_memories]
            )
            
            logger.debug(f"Search completed: {len(final_memories)} results in {search_time:.3f}s")
            return result
            
        except Exception as e:
            self._update_metrics("search", success=False)
            logger.error(f"Memory search failed: {e}")
            raise MemoryServiceError(f"Memory search failed: {e}")
    
    async def get_memory_context(self, context_query: MemoryContext) -> MemoryContextResult:
        """Get memory context for a project"""
        await self._ensure_initialized()
        
        try:
            start_time = time.time()
            
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
            
            retrieval_time = (time.time() - start_time) * 1000
            
            result = MemoryContextResult(
                project=context_query.project,
                context=context,
                total_memories=total_memories,
                retrieval_time_ms=retrieval_time
            )
            
            logger.debug(f"Context retrieved: {total_memories} memories in {retrieval_time:.2f}ms")
            return result
            
        except Exception as e:
            logger.error(f"Context retrieval failed: {e}")
            raise MemoryServiceError(f"Context retrieval failed: {e}")
    
    async def get_memory(self, memory_id: str) -> Optional[Memory]:
        """Get a memory by ID"""
        await self._ensure_initialized()
        
        try:
            return await database_service.get_memory(memory_id)
        except Exception as e:
            logger.error(f"Failed to get memory {memory_id}: {e}")
            raise MemoryServiceError(f"Failed to get memory: {e}")
    
    async def update_memory(self, memory_id: str, updates: MemoryUpdate) -> Optional[Memory]:
        """Update a memory"""
        await self._ensure_initialized()
        
        try:
            # Re-generate embedding if content changed
            if updates.content is not None:
                embedding = await embedding_service.generate_embedding(updates.content)
                if not hasattr(updates, 'embedding'):
                    updates.embedding = embedding
            
            return await database_service.update_memory(memory_id, updates)
        except Exception as e:
            logger.error(f"Failed to update memory {memory_id}: {e}")
            raise MemoryServiceError(f"Failed to update memory: {e}")
    
    async def delete_memory(self, memory_id: str) -> bool:
        """Delete a memory"""
        await self._ensure_initialized()
        
        try:
            return await database_service.delete_memory(memory_id)
        except Exception as e:
            logger.error(f"Failed to delete memory {memory_id}: {e}")
            raise MemoryServiceError(f"Failed to delete memory: {e}")
    
    async def get_metrics(self) -> Dict[str, Any]:
        """Get memory service metrics"""
        db_metrics = await database_service.get_metrics()
        embedding_metrics = await embedding_service.get_metrics()
        
        avg_search_time = (
            self._total_search_time / self._search_count 
            if self._search_count > 0 else 0.0
        )
        
        return {
            "operation_count": self._operation_count,
            "search_count": self._search_count,
            "auto_save_count": self._auto_save_count,
            "avg_search_time_ms": avg_search_time * 1000,
            "error_count": self._error_count,
            "database_metrics": db_metrics,
            "embedding_metrics": embedding_metrics
        }
    
    async def health_check(self) -> Dict[str, Any]:
        """Perform health check"""
        try:
            if not self._initialized:
                return {"status": "not_initialized"}
            
            # Check dependencies
            db_health = await database_service.health_check()
            embedding_health = await embedding_service.health_check()
            
            overall_status = "healthy" if (
                db_health.get("status") == "healthy" and 
                embedding_health.get("status") == "healthy"
            ) else "unhealthy"
            
            return {
                "status": overall_status,
                "database": db_health,
                "embedding": embedding_health
            }
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e)
            }


# Global memory service instance
memory_service = MemoryService()
