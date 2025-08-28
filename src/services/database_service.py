"""
Database service for MCP Memory Server
"""

import logging
from datetime import datetime
from typing import List, Optional, Dict, Any
from bson import ObjectId

import motor.motor_asyncio
from pymongo import ASCENDING, DESCENDING

from ..config.settings import DatabaseConfig
from ..models.memory import Memory, MemoryCreate, MemoryUpdate
from ..utils.exceptions import DatabaseServiceError

logger = logging.getLogger(__name__)


class DatabaseService:
    """Database service for MongoDB operations"""
    
    def __init__(self, settings: DatabaseConfig):
        self.settings = settings
        self.client: Optional[motor.motor_asyncio.AsyncIOMotorClient] = None
        self.db: Optional[motor.motor_asyncio.AsyncIOMotorDatabase] = None
        self.collection: Optional[motor.motor_asyncio.AsyncIOMotorCollection] = None
        self._initialized = False
    
    async def initialize(self) -> None:
        """Initialize database connection"""
        if self._initialized:
            return
        
        try:
            # Create MongoDB client
            self.client = motor.motor_asyncio.AsyncIOMotorClient(
                self.settings.mongodb["uri"],
                maxPoolSize=self.settings.mongodb["max_pool_size"],
                minPoolSize=self.settings.mongodb["min_pool_size"],
                maxIdleTimeMS=self.settings.mongodb["max_idle_time_ms"],
                serverSelectionTimeoutMS=self.settings.mongodb["server_selection_timeout_ms"]
            )
            
            # Get database and collection
            self.db = self.client[self.settings.mongodb["database"]]
            self.collection = self.db[self.settings.mongodb["collection"]]
            
            # Setup indexes
            await self._setup_indexes()
            
            # Test connection
            await self.client.admin.command('ping')
            
            self._initialized = True
            logger.info("Database service initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize database service: {e}")
            raise DatabaseServiceError(f"Database initialization failed: {e}")
    
    async def _setup_indexes(self) -> None:
        """Setup database indexes"""
        try:
            # Text search index
            await self.collection.create_index([
                ("content", "text"),
                ("project", ASCENDING)
            ])
            
            # Project and timestamp index
            await self.collection.create_index([
                ("project", ASCENDING),
                ("created_at", DESCENDING)
            ])
            
            # Tags index
            await self.collection.create_index("tags")
            
            # Memory type index
            await self.collection.create_index("memory_type")
            
            # Importance index
            await self.collection.create_index("importance")
            
            logger.info("Database indexes created successfully")
            
        except Exception as e:
            logger.warning(f"Failed to create indexes: {e}")
    
    async def _ensure_initialized(self) -> None:
        """Ensure service is initialized"""
        if not self._initialized:
            await self.initialize()
    
    async def create_memory(self, memory_create: MemoryCreate) -> Memory:
        """Create a new memory"""
        await self._ensure_initialized()
        
        try:
            # Convert to document
            doc = {
                "project": memory_create.project,
                "content": memory_create.content,
                "memory_type": memory_create.memory_type.value,
                "importance": memory_create.importance,
                "tags": memory_create.tags,
                "metadata": memory_create.metadata,
                "context": memory_create.context,
                "embedding": memory_create.embedding,
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow(),
                "access_count": 0,
                "last_accessed": None
            }
            
            result = await self.collection.insert_one(doc)
            
            # Create memory object
            memory = Memory(
                id=str(result.inserted_id),
                project=memory_create.project,
                content=memory_create.content,
                memory_type=memory_create.memory_type,
                importance=memory_create.importance,
                tags=memory_create.tags,
                metadata=memory_create.metadata,
                context=memory_create.context,
                embedding=memory_create.embedding,
                created_at=doc["created_at"],
                updated_at=doc["updated_at"],
                access_count=0,
                last_accessed=None
            )
            
            logger.debug(f"Created memory {memory.id}")
            return memory
            
        except Exception as e:
            logger.error(f"Failed to create memory: {e}")
            raise DatabaseServiceError(f"Failed to create memory: {e}")
    
    async def get_memory(self, memory_id: str) -> Optional[Memory]:
        """Get a memory by ID"""
        await self._ensure_initialized()
        
        try:
            doc = await self.collection.find_one({"_id": ObjectId(memory_id)})
            if not doc:
                return None
            
            return self._doc_to_memory(doc)
            
        except Exception as e:
            logger.error(f"Failed to get memory {memory_id}: {e}")
            raise DatabaseServiceError(f"Failed to get memory: {e}")
    
    async def update_memory(self, memory_id: str, updates: MemoryUpdate) -> Optional[Memory]:
        """Update a memory"""
        await self._ensure_initialized()
        
        try:
            # Build update document
            update_doc = {"updated_at": datetime.utcnow()}
            
            if updates.content is not None:
                update_doc["content"] = updates.content
            if updates.memory_type is not None:
                update_doc["memory_type"] = updates.memory_type.value
            if updates.importance is not None:
                update_doc["importance"] = updates.importance
            if updates.tags is not None:
                update_doc["tags"] = updates.tags
            if updates.metadata is not None:
                update_doc["metadata"] = updates.metadata
            if updates.context is not None:
                update_doc["context"] = updates.context
            if updates.embedding is not None:
                update_doc["embedding"] = updates.embedding
            
            result = await self.collection.update_one(
                {"_id": ObjectId(memory_id)},
                {"$set": update_doc}
            )
            
            if result.matched_count == 0:
                return None
            
            # Return updated memory
            return await self.get_memory(memory_id)
            
        except Exception as e:
            logger.error(f"Failed to update memory {memory_id}: {e}")
            raise DatabaseServiceError(f"Failed to update memory: {e}")
    
    async def delete_memory(self, memory_id: str) -> bool:
        """Delete a memory"""
        await self._ensure_initialized()
        
        try:
            result = await self.collection.delete_one({"_id": ObjectId(memory_id)})
            return result.deleted_count > 0
            
        except Exception as e:
            logger.error(f"Failed to delete memory {memory_id}: {e}")
            raise DatabaseServiceError(f"Failed to delete memory: {e}")
    
    async def search_memories(
        self,
        project: Optional[str] = None,
        limit: int = 20,
        text_query: Optional[str] = None,
        tags: Optional[List[str]] = None
    ) -> List[Memory]:
        """Search memories"""
        await self._ensure_initialized()
        
        try:
            # Build query
            query = {}
            
            if project:
                query["project"] = project
            
            if tags:
                query["tags"] = {"$in": tags}
            
            if text_query:
                query["$text"] = {"$search": text_query}
            
            # Execute query
            cursor = self.collection.find(query).limit(limit)
            docs = await cursor.to_list(length=limit)
            
            # Convert to memory objects
            memories = [self._doc_to_memory(doc) for doc in docs]
            
            return memories
            
        except Exception as e:
            logger.error(f"Failed to search memories: {e}")
            raise DatabaseServiceError(f"Failed to search memories: {e}")
    
    async def list_memories(
        self,
        project: str = "default",
        limit: int = 50,
        offset: int = 0
    ) -> List[Memory]:
        """List memories for a project"""
        await self._ensure_initialized()
        
        try:
            cursor = self.collection.find(
                {"project": project}
            ).sort("created_at", DESCENDING).skip(offset).limit(limit)
            
            docs = await cursor.to_list(length=limit)
            memories = [self._doc_to_memory(doc) for doc in docs]
            
            return memories
            
        except Exception as e:
            logger.error(f"Failed to list memories: {e}")
            raise DatabaseServiceError(f"Failed to list memories: {e}")
    
    async def count_memories(self, project: Optional[str] = None) -> int:
        """Count total memories"""
        await self._ensure_initialized()
        
        try:
            query = {}
            if project:
                query["project"] = project
            
            return await self.collection.count_documents(query)
            
        except Exception as e:
            logger.error(f"Failed to count memories: {e}")
            return 0
    
    async def count_projects(self) -> int:
        """Count total projects"""
        await self._ensure_initialized()
        
        try:
            return len(await self.collection.distinct("project"))
            
        except Exception as e:
            logger.error(f"Failed to count projects: {e}")
            return 0
    
    def _doc_to_memory(self, doc: Dict[str, Any]) -> Memory:
        """Convert database document to Memory object"""
        from ..models.memory import MemoryType
        
        return Memory(
            id=str(doc["_id"]),
            project=doc["project"],
            content=doc["content"],
            memory_type=MemoryType(doc["memory_type"]),
            importance=doc["importance"],
            tags=doc.get("tags", []),
            metadata=doc.get("metadata", {}),
            context=doc.get("context", {}),
            embedding=doc.get("embedding"),
            created_at=doc["created_at"],
            updated_at=doc["updated_at"],
            access_count=doc.get("access_count", 0),
            last_accessed=doc.get("last_accessed")
        )
    
    async def get_metrics(self) -> Dict[str, Any]:
        """Get database metrics"""
        try:
            if not self._initialized:
                return {"status": "not_initialized"}
            
            # Basic stats
            total_memories = await self.count_memories()
            total_projects = await self.count_projects()
            
            # Memory types distribution
            pipeline = [
                {"$group": {"_id": "$memory_type", "count": {"$sum": 1}}}
            ]
            type_stats = await self.collection.aggregate(pipeline).to_list(None)
            
            return {
                "status": "healthy",
                "total_memories": total_memories,
                "total_projects": total_projects,
                "memory_types": {stat["_id"]: stat["count"] for stat in type_stats},
                "database_name": self.settings.mongodb["database"],
                "collection_name": self.settings.mongodb["collection"]
            }
            
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e)
            }
    
    async def health_check(self) -> Dict[str, Any]:
        """Perform health check"""
        try:
            if not self._initialized:
                return {"status": "not_initialized"}
            
            # Test connection
            await self.client.admin.command('ping')
            
            return {
                "status": "healthy",
                "database": self.settings.mongodb["database"],
                "collection": self.settings.mongodb["collection"]
            }
            
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e)
            }
    
    async def close(self) -> None:
        """Close database connection"""
        if self.client:
            self.client.close()
            self._initialized = False
            logger.info("Database connection closed")
