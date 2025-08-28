"""
Production memory service with auto-triggers and advanced features
"""

import logging
import time
from datetime import datetime
from typing import List, Optional, Dict, Any

from ..config.settings import Settings
from ..models.memory import (
    Memory, MemoryCreate, MemoryUpdate, MemoryType
)
from ..utils.exceptions import MemoryServiceError
from .database_service import DatabaseService
from .embedding_service import EmbeddingService

logger = logging.getLogger(__name__)


class MemoryService:
    """Production memory service with intelligent triggers and management"""
    
    def __init__(self, settings: Settings):
        self.settings = settings
        self.database_service = DatabaseService(settings.database)
        self.embedding_service = EmbeddingService(settings.embedding)
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
            # Initialize dependencies
            await self.database_service.initialize()
            await self.embedding_service.initialize()
            
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
    
    async def create_memory(
        self, 
        content: str,
        project: str = "default",
        importance: float = 0.5,
        tags: List[str] = None,
        metadata: Dict[str, Any] = None,
        context: Dict[str, Any] = None
    ) -> Memory:
        """Create a new memory with optional automatic embedding"""
        await self._ensure_initialized()
        
        try:
            start_time = time.time()
            
            # Generate embedding
            embedding = await self.embedding_service.generate_embedding(content)
            
            # Create memory object
            memory_create = MemoryCreate(
                project=project,
                content=content,
                memory_type=MemoryType.CONVERSATION,
                importance=importance,
                tags=tags or [],
                metadata=metadata or {},
                context=context or {},
                embedding=embedding
            )
            
            # Create memory in database
            memory = await self.database_service.create_memory(memory_create)
            
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
        project: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Automatically save memory if content triggers the threshold
        This is the core auto-trigger functionality
        """
        await self._ensure_initialized()
        
        try:
            # Check if content should trigger memory save
            should_save = await self.embedding_service.should_trigger_memory_save(content, context)
            
            if not should_save:
                logger.debug("Content did not trigger memory save threshold")
                return {
                    "saved": False,
                    "threshold": self.settings.memory.trigger_threshold,
                    "trigger_type": "none"
                }
            
            # Analyze importance
            importance = await self.embedding_service.analyze_memory_importance(content, context)
            
            # Determine memory type from context
            trigger_type = "ml_trigger"
            
            if context:
                if context.get("type") == "function_result":
                    trigger_type = "function_result"
                elif context.get("level") == "error":
                    trigger_type = "error"
                elif context.get("level") == "warning":
                    trigger_type = "warning"
                elif "decision" in content.lower():
                    trigger_type = "decision"
                elif any(keyword in content.lower() for keyword in ["knowledge", "fact", "information"]):
                    trigger_type = "knowledge"
            
            # Create memory
            memory = await self.create_memory(
                content=content,
                project=project or self.settings.memory.default_project,
                importance=importance,
                context=context or {}
            )
            
            self._update_metrics("auto_save", success=True)
            
            logger.info(f"Auto-saved memory {memory.id} with importance {importance:.2f}")
            return {
                "saved": True,
                "memory_id": memory.id,
                "importance": importance,
                "trigger_type": trigger_type,
                "threshold": self.settings.memory.trigger_threshold
            }
            
        except Exception as e:
            self._update_metrics("auto_save", success=False)
            logger.error(f"Auto-save failed: {e}")
            return {
                "saved": False,
                "error": str(e),
                "trigger_type": "error"
            }
    
    async def search_memories(
        self,
        query: str,
        project: Optional[str] = None,
        max_results: int = 20,
        similarity_threshold: float = 0.3,
        tags: List[str] = None
    ) -> List[Memory]:
        """Search memories with semantic similarity"""
        await self._ensure_initialized()
        
        try:
            start_time = time.time()
            
            # Generate embedding for search query
            query_embedding = await self.embedding_service.generate_embedding(query)
            
            # Get candidate memories from database
            candidates = await self.database_service.search_memories(
                project=project,
                limit=max_results * 2,  # Get more candidates for similarity filtering
                text_query=query,
                tags=tags or []
            )
            
            # Calculate similarity scores
            scored_memories = []
            for memory in candidates:
                if memory.embedding:
                    similarity = self.embedding_service.calculate_similarity(
                        query_embedding, memory.embedding
                    )
                    if similarity >= similarity_threshold:
                        memory.similarity_score = similarity
                        scored_memories.append(memory)
            
            # Sort by similarity and limit results
            scored_memories.sort(key=lambda m: m.similarity_score or 0, reverse=True)
            final_memories = scored_memories[:max_results]
            
            search_time = time.time() - start_time
            self._update_metrics("search", success=True, duration=search_time)
            
            logger.debug(f"Search completed: {len(final_memories)} results in {search_time:.3f}s")
            return final_memories
            
        except Exception as e:
            self._update_metrics("search", success=False)
            logger.error(f"Memory search failed: {e}")
            raise MemoryServiceError(f"Memory search failed: {e}")
    
    async def list_memories(
        self,
        project: str = "default",
        limit: int = 50,
        offset: int = 0
    ) -> List[Memory]:
        """List memories for a project"""
        await self._ensure_initialized()
        
        try:
            return await self.database_service.list_memories(
                project=project,
                limit=limit,
                offset=offset
            )
        except Exception as e:
            logger.error(f"Failed to list memories: {e}")
            raise MemoryServiceError(f"Failed to list memories: {e}")
    
    async def get_memory(self, memory_id: str) -> Optional[Memory]:
        """Get a memory by ID"""
        await self._ensure_initialized()
        
        try:
            return await self.database_service.get_memory(memory_id)
        except Exception as e:
            logger.error(f"Failed to get memory {memory_id}: {e}")
            raise MemoryServiceError(f"Failed to get memory: {e}")
    
    async def update_memory(self, memory_id: str, updates: MemoryUpdate) -> Optional[Memory]:
        """Update a memory"""
        await self._ensure_initialized()
        
        try:
            # Re-generate embedding if content changed
            if updates.content is not None:
                embedding = await self.embedding_service.generate_embedding(updates.content)
                updates.embedding = embedding
            
            return await self.database_service.update_memory(memory_id, updates)
        except Exception as e:
            logger.error(f"Failed to update memory {memory_id}: {e}")
            raise MemoryServiceError(f"Failed to update memory: {e}")
    
    async def delete_memory(self, memory_id: str) -> bool:
        """Delete a memory"""
        await self._ensure_initialized()
        
        try:
            return await self.database_service.delete_memory(memory_id)
        except Exception as e:
            logger.error(f"Failed to delete memory {memory_id}: {e}")
            raise MemoryServiceError(f"Failed to delete memory: {e}")
    
    async def get_status(self) -> Dict[str, Any]:
        """Get memory service status"""
        try:
            if not self._initialized:
                return {
                    "status": "not_initialized",
                    "total_memories": 0,
                    "total_projects": 0,
                    "storage_type": self.settings.memory.storage,
                    "auto_save_enabled": self.settings.memory.auto_save,
                    "ml_triggers_enabled": self.settings.memory.ml_triggers,
                    "last_activity": "never"
                }
            
            # Get basic stats
            total_memories = await self.database_service.count_memories()
            total_projects = await self.database_service.count_projects()
            
            return {
                "status": "healthy",
                "total_memories": total_memories,
                "total_projects": total_projects,
                "storage_type": self.settings.memory.storage,
                "auto_save_enabled": self.settings.memory.auto_save,
                "ml_triggers_enabled": self.settings.memory.ml_triggers,
                "last_activity": datetime.now().isoformat()
            }
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e),
                "total_memories": 0,
                "total_projects": 0,
                "storage_type": self.settings.memory.storage,
                "auto_save_enabled": self.settings.memory.auto_save,
                "ml_triggers_enabled": self.settings.memory.ml_triggers,
                "last_activity": "error"
            }
    
    async def get_metrics(self) -> Dict[str, Any]:
        """Get memory service metrics"""
        try:
            db_metrics = await self.database_service.get_metrics()
            embedding_metrics = await self.embedding_service.get_metrics()
            
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
        except Exception as e:
            logger.error(f"Failed to get metrics: {e}")
            return {
                "error": str(e),
                "operation_count": self._operation_count,
                "search_count": self._search_count,
                "auto_save_count": self._auto_save_count,
                "error_count": self._error_count
            }
    
    async def health_check(self) -> Dict[str, Any]:
        """Perform health check"""
        try:
            if not self._initialized:
                return {"status": "not_initialized"}
            
            # Check dependencies
            db_health = await self.database_service.health_check()
            embedding_health = await self.embedding_service.health_check()
            
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
