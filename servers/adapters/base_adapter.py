"""
Base adapter for all platforms
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
from dataclasses import dataclass

from ...src.config.settings import Settings
from ...src.services.memory_service import MemoryService


@dataclass
class PlatformContext:
    """Context information for platform-specific operations"""
    platform: str
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    project: str = "default"
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


class BaseAdapter(ABC):
    """Base adapter for all platforms"""
    
    def __init__(self, settings: Settings, memory_service: MemoryService):
        self.settings = settings
        self.memory_service = memory_service
        self.platform_config = self._get_platform_config()
    
    @abstractmethod
    def _get_platform_config(self) -> Dict[str, Any]:
        """Get platform-specific configuration"""
        pass
    
    @abstractmethod
    async def process_message(self, content: str, context: PlatformContext) -> Dict[str, Any]:
        """Process a message from the platform"""
        pass
    
    @abstractmethod
    async def should_auto_save(self, content: str, context: PlatformContext) -> bool:
        """Determine if content should be auto-saved"""
        pass
    
    @abstractmethod
    async def get_relevant_memories(self, query: str, context: PlatformContext) -> List[Any]:
        """Get relevant memories for the current context"""
        pass
    
    async def create_memory(self, content: str, context: PlatformContext) -> Dict[str, Any]:
        """Create a memory with platform-specific context"""
        try:
            # Add platform-specific metadata
            enhanced_context = {
                **context.metadata,
                "platform": context.platform,
                "user_id": context.user_id,
                "session_id": context.session_id,
                "source": "platform_adapter"
            }
            
            memory = await self.memory_service.create_memory(
                content=content,
                project=context.project,
                importance=0.5,  # Default importance
                context=enhanced_context
            )
            
            return {
                "success": True,
                "memory_id": memory.id,
                "message": f"Memory saved successfully: {memory.id}"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": f"Failed to save memory: {e}"
            }
    
    async def auto_save_memory(self, content: str, context: PlatformContext) -> Dict[str, Any]:
        """Auto-save memory if it meets criteria"""
        try:
            # Check if content should be auto-saved
            should_save = await self.should_auto_save(content, context)
            
            if not should_save:
                return {
                    "saved": False,
                    "reason": "Content did not meet auto-save criteria",
                    "message": "Content not saved automatically"
                }
            
            # Add platform-specific context
            enhanced_context = {
                **context.metadata,
                "platform": context.platform,
                "user_id": context.user_id,
                "session_id": context.session_id,
                "source": "auto_save"
            }
            
            result = await self.memory_service.auto_save_memory(
                content=content,
                context=enhanced_context,
                project=context.project
            )
            
            return result
            
        except Exception as e:
            return {
                "saved": False,
                "error": str(e),
                "message": f"Auto-save failed: {e}"
            }
    
    async def search_memories(self, query: str, context: PlatformContext) -> Dict[str, Any]:
        """Search memories with platform-specific context"""
        try:
            memories = await self.memory_service.search_memories(
                query=query,
                project=context.project,
                max_results=20,
                similarity_threshold=0.3
            )
            
            # Format results for platform
            formatted_memories = []
            for memory in memories:
                formatted_memories.append({
                    "id": memory.id,
                    "content": memory.content,
                    "project": memory.project,
                    "importance": memory.importance,
                    "similarity": memory.similarity_score,
                    "created_at": memory.created_at.isoformat(),
                    "tags": memory.tags
                })
            
            return {
                "success": True,
                "memories": formatted_memories,
                "count": len(formatted_memories),
                "query": query
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": f"Search failed: {e}"
            }
    
    async def get_context_memories(self, context: PlatformContext) -> Dict[str, Any]:
        """Get context-relevant memories for the platform"""
        try:
            memories = await self.memory_service.list_memories(
                project=context.project,
                limit=10,
                offset=0
            )
            
            # Filter by relevance to current context
            relevant_memories = await self.get_relevant_memories(
                query="",  # Empty query to get all context memories
                context=context
            )
            
            return {
                "success": True,
                "context_memories": relevant_memories,
                "total_memories": len(memories),
                "project": context.project
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": f"Failed to get context memories: {e}"
            }
    
    async def get_platform_status(self) -> Dict[str, Any]:
        """Get platform-specific status"""
        try:
            memory_status = await self.memory_service.get_status()
            
            return {
                "platform": self.platform_config.get("name", "unknown"),
                "auto_save_enabled": self.platform_config.get("auto_trigger", False),
                "memory_count": memory_status.get("total_memories", 0),
                "project_count": memory_status.get("total_projects", 0),
                "status": "healthy"
            }
            
        except Exception as e:
            return {
                "platform": self.platform_config.get("name", "unknown"),
                "status": "unhealthy",
                "error": str(e)
            } 