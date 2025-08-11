"""
Database service for MCP Memory Server with production features
"""

import asyncio
import logging
from datetime import datetime
from typing import List, Optional, Dict, Any
from contextlib import asynccontextmanager

from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase, AsyncIOMotorCollection
from pymongo.errors import PyMongoError, DuplicateKeyError, ConnectionFailure
from pymongo import IndexModel, ASCENDING, DESCENDING, TEXT
from bson import ObjectId

from ..config import get_config
from ..models import Memory, MemoryCreate, MemoryUpdate, MemoryType
from ..utils.exceptions import DatabaseError, NotFoundError
from ..utils.retry import retry_async

logger = logging.getLogger(__name__)


class DatabaseService:
    """Production-ready database service with connection pooling, retries, and monitoring"""
    
    def __init__(self):
        self.config = get_config()
        self.client: Optional[AsyncIOMotorClient] = None
        self.db: Optional[AsyncIOMotorDatabase] = None
        self.collection: Optional[AsyncIOMotorCollection] = None
        self._initialized = False
        self._connection_lock = asyncio.Lock()
        
        # Metrics
        self._operation_count = 0
        self._error_count = 0
        self._last_operation_time = None
    
    async def initialize(self) -> None:
        """Initialize database connection with retry logic"""
        if self._initialized:
            return
        
        async with self._connection_lock:
            if self._initialized:
                return
            
            try:
                await self._connect()
                await self._setup_indexes()
                self._initialized = True
                logger.info("Database service initialized successfully")
                
            except Exception as e:
                logger.error(f"Failed to initialize database service: {e}")
                raise DatabaseError(f"Database initialization failed: {e}")
    
    @retry_async(max_attempts=3, delay=1.0, backoff=2.0)
    async def _connect(self) -> None:
        """Connect to MongoDB with retry logic"""
        try:
            logger.info(f"Connecting to MongoDB: {self.config.database.host}:{self.config.database.port}")
            
            # Create client with production settings
            self.client = AsyncIOMotorClient(
                self.config.database.url,
                maxPoolSize=self.config.database.max_pool_size,
                minPoolSize=self.config.database.min_pool_size,
                maxIdleTimeMS=self.config.database.max_idle_time_ms,
                serverSelectionTimeoutMS=self.config.database.server_selection_timeout_ms,
                retryWrites=True,
                retryReads=True,
                w="majority",  # Write concern for data safety
                readPreference="primaryPreferred"
            )
            
            # Get database and collection
            self.db = self.client[self.config.database.database_name]
            self.collection = self.db[self.config.database.collection_name]
            
            # Test connection
            await self.client.admin.command('ping')
            logger.info("MongoDB connection established successfully")
            
        except ConnectionFailure as e:
            logger.error(f"MongoDB connection failed: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error connecting to MongoDB: {e}")
            raise
    
    async def _setup_indexes(self) -> None:
        """Create database indexes for optimal performance"""
        try:
            indexes = [
                # Text search index
                IndexModel([("content", TEXT), ("tags", TEXT)], name="text_search_idx"),
                
                # Project and type queries
                IndexModel([("project", ASCENDING), ("memory_type", ASCENDING)], name="project_type_idx"),
                
                # Importance and timestamp queries
                IndexModel([("importance", DESCENDING), ("created_at", DESCENDING)], name="importance_time_idx"),
                
                # User and session queries
                IndexModel([("user_id", ASCENDING), ("session_id", ASCENDING)], name="user_session_idx"),
                
                # Embedding similarity search (if using vector search)
                IndexModel([("embedding", "2dsphere")], name="embedding_idx", sparse=True),
                
                # Compound index for common queries
                IndexModel([
                    ("project", ASCENDING),
                    ("memory_type", ASCENDING), 
                    ("importance", DESCENDING),
                    ("created_at", DESCENDING)
                ], name="compound_query_idx"),
                
                # TTL index for automatic cleanup (optional)
                # IndexModel([("created_at", ASCENDING)], name="ttl_idx", expireAfterSeconds=31536000)  # 1 year
            ]
            
            await self.collection.create_indexes(indexes)
            logger.info("Database indexes created successfully")
            
        except Exception as e:
            logger.error(f"Failed to create indexes: {e}")
            raise
    
    async def _ensure_initialized(self) -> None:
        """Ensure database is initialized"""
        if not self._initialized:
            await self.initialize()
    
    def _update_metrics(self, success: bool = True) -> None:
        """Update operation metrics"""
        self._operation_count += 1
        self._last_operation_time = datetime.utcnow()
        if not success:
            self._error_count += 1
    
    def _memory_to_document(self, memory: Memory) -> Dict[str, Any]:
        """Convert Memory model to MongoDB document"""
        doc = memory.to_dict()
        
        # Handle ObjectId
        if memory.id:
            doc["_id"] = ObjectId(memory.id)
        else:
            doc.pop("id", None)
        
        # Convert enum to string
        doc["memory_type"] = memory.memory_type.value
        
        return doc
    
    def _document_to_memory(self, doc: Dict[str, Any]) -> Memory:
        """Convert MongoDB document to Memory model"""
        # Handle ObjectId
        doc["id"] = str(doc.pop("_id"))
        
        # Convert string to enum
        if "memory_type" in doc:
            doc["memory_type"] = MemoryType(doc["memory_type"])
        
        return Memory.from_dict(doc)
    
    @asynccontextmanager
    async def _handle_errors(self, operation: str):
        """Context manager for consistent error handling"""
        try:
            yield
            self._update_metrics(success=True)
        except DuplicateKeyError as e:
            self._update_metrics(success=False)
            logger.error(f"Duplicate key error in {operation}: {e}")
            raise DatabaseError(f"Duplicate entry: {e}")
        except PyMongoError as e:
            self._update_metrics(success=False)
            logger.error(f"Database error in {operation}: {e}")
            raise DatabaseError(f"Database operation failed: {e}")
        except Exception as e:
            self._update_metrics(success=False)
            logger.error(f"Unexpected error in {operation}: {e}")
            raise DatabaseError(f"Unexpected database error: {e}")
    
    async def create_memory(self, memory_create: MemoryCreate) -> Memory:
        """Create a new memory"""
        await self._ensure_initialized()
        
        async with self._handle_errors("create_memory"):
            # Create memory object
            memory = Memory(
                project=memory_create.project,
                content=memory_create.content,
                memory_type=memory_create.memory_type,
                importance=memory_create.importance,
                metadata=memory_create.metadata,
                tags=memory_create.tags,
                embedding=memory_create.embedding,
                context=memory_create.context,
                source=memory_create.source,
                user_id=memory_create.user_id,
                session_id=memory_create.session_id
            )
            
            # Convert to document and insert
            doc = self._memory_to_document(memory)
            result = await self.collection.insert_one(doc)
            
            # Set the ID and return
            memory.id = str(result.inserted_id)
            logger.debug(f"Created memory: {memory.id}")
            return memory
    
    async def get_memory(self, memory_id: str) -> Optional[Memory]:
        """Get a memory by ID"""
        await self._ensure_initialized()

        async with self._handle_errors("get_memory"):
            try:
                doc = await self.collection.find_one({"_id": ObjectId(memory_id)})
                if not doc:
                    return None
                return self._document_to_memory(doc)
            except Exception as e:
                if "invalid ObjectId" in str(e):
                    return None
                raise

    async def update_memory(self, memory_id: str, updates: MemoryUpdate) -> Optional[Memory]:
        """Update a memory"""
        await self._ensure_initialized()

        async with self._handle_errors("update_memory"):
            # Build update document
            update_doc = {}
            if updates.content is not None:
                update_doc["content"] = updates.content
            if updates.memory_type is not None:
                update_doc["memory_type"] = updates.memory_type.value
            if updates.importance is not None:
                update_doc["importance"] = updates.importance
            if updates.metadata is not None:
                update_doc["metadata"] = updates.metadata
            if updates.tags is not None:
                update_doc["tags"] = updates.tags
            if updates.context is not None:
                update_doc["context"] = updates.context

            if not update_doc:
                # No updates to apply
                return await self.get_memory(memory_id)

            update_doc["updated_at"] = datetime.utcnow()

            try:
                result = await self.collection.find_one_and_update(
                    {"_id": ObjectId(memory_id)},
                    {"$set": update_doc},
                    return_document=True
                )

                if not result:
                    return None

                return self._document_to_memory(result)
            except Exception as e:
                if "invalid ObjectId" in str(e):
                    return None
                raise

    async def delete_memory(self, memory_id: str) -> bool:
        """Delete a memory"""
        await self._ensure_initialized()

        async with self._handle_errors("delete_memory"):
            try:
                result = await self.collection.delete_one({"_id": ObjectId(memory_id)})
                return result.deleted_count > 0
            except Exception as e:
                if "invalid ObjectId" in str(e):
                    return False
                raise

    async def search_memories(
        self,
        project: Optional[str] = None,
        memory_types: Optional[List[str]] = None,
        min_importance: float = 0.0,
        limit: int = 100,
        skip: int = 0,
        text_query: Optional[str] = None,
        tags: Optional[List[str]] = None,
        user_id: Optional[str] = None,
        session_id: Optional[str] = None,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None
    ) -> List[Memory]:
        """Search memories with various filters"""
        await self._ensure_initialized()

        async with self._handle_errors("search_memories"):
            # Build query
            query = {}

            if project:
                query["project"] = project

            if memory_types:
                query["memory_type"] = {"$in": memory_types}

            if min_importance > 0:
                query["importance"] = {"$gte": min_importance}

            if user_id:
                query["user_id"] = user_id

            if session_id:
                query["session_id"] = session_id

            if tags:
                query["tags"] = {"$in": tags}

            if date_from or date_to:
                date_query = {}
                if date_from:
                    date_query["$gte"] = date_from
                if date_to:
                    date_query["$lte"] = date_to
                query["created_at"] = date_query

            if text_query:
                query["$text"] = {"$search": text_query}

            # Execute query
            cursor = self.collection.find(query).sort("created_at", DESCENDING).skip(skip).limit(limit)
            docs = await cursor.to_list(length=limit)

            return [self._document_to_memory(doc) for doc in docs]

    async def get_project_memories(
        self,
        project: str,
        memory_types: Optional[List[str]] = None,
        limit: int = 100,
        min_importance: float = 0.0
    ) -> List[Memory]:
        """Get memories for a specific project"""
        return await self.search_memories(
            project=project,
            memory_types=memory_types,
            limit=limit,
            min_importance=min_importance
        )

    async def get_memory_count(self, project: Optional[str] = None) -> int:
        """Get total memory count"""
        await self._ensure_initialized()

        async with self._handle_errors("get_memory_count"):
            query = {}
            if project:
                query["project"] = project
            return await self.collection.count_documents(query)

    async def get_metrics(self) -> Dict[str, Any]:
        """Get database metrics"""
        await self._ensure_initialized()

        async with self._handle_errors("get_metrics"):
            # Get collection stats
            stats = await self.db.command("collStats", self.config.database.collection_name)

            # Get memory counts by type and project
            pipeline = [
                {"$group": {
                    "_id": {"type": "$memory_type", "project": "$project"},
                    "count": {"$sum": 1}
                }}
            ]

            aggregation_result = await self.collection.aggregate(pipeline).to_list(None)

            memories_by_type = {}
            memories_by_project = {}

            for item in aggregation_result:
                memory_type = item["_id"]["type"]
                project = item["_id"]["project"]
                count = item["count"]

                memories_by_type[memory_type] = memories_by_type.get(memory_type, 0) + count
                memories_by_project[project] = memories_by_project.get(project, 0) + count

            return {
                "total_memories": stats.get("count", 0),
                "database_size_mb": stats.get("size", 0) / (1024 * 1024),
                "index_size_mb": stats.get("totalIndexSize", 0) / (1024 * 1024),
                "memories_by_type": memories_by_type,
                "memories_by_project": memories_by_project,
                "operation_count": self._operation_count,
                "error_count": self._error_count,
                "last_operation_time": self._last_operation_time
            }

    async def health_check(self) -> Dict[str, Any]:
        """Perform health check"""
        try:
            start_time = datetime.utcnow()
            await self.client.admin.command('ping')
            response_time = (datetime.utcnow() - start_time).total_seconds() * 1000

            return {
                "status": "healthy",
                "response_time_ms": response_time,
                "connections": self.client.nodes
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


# Global database service instance
database_service = DatabaseService()
