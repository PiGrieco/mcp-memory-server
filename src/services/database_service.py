"""
Database service for MCP Memory Server
"""

import asyncio
import logging
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, timedelta
from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase, AsyncIOMotorCollection
from pymongo import ASCENDING, DESCENDING
from pymongo.errors import PyMongoError, DuplicateKeyError, ConnectionFailure
import time

from ..config import config
from ..models import Memory, MemoryCreate, MemoryUpdate, MemorySearchQuery, MemoryStats

logger = logging.getLogger(__name__)

class DatabaseService:
    """Service for MongoDB operations"""
    
    def __init__(self):
        self.client: Optional[AsyncIOMotorClient] = None
        self.db: Optional[AsyncIOMotorDatabase] = None
        self.collection: Optional[AsyncIOMotorCollection] = None
        self._initialized = False
        self._lock = asyncio.Lock()
    
    async def initialize(self) -> None:
        """Initialize database connection and create indexes"""
        async with self._lock:
            if self._initialized:
                return
            
            try:
                logger.info(f"Connecting to MongoDB: {config.database.url}")
                
                # Create client with connection pooling
                self.client = AsyncIOMotorClient(
                    config.database.url,
                    maxPoolSize=config.database.max_pool_size,
                    minPoolSize=config.database.min_pool_size,
                    maxIdleTimeMS=config.database.max_idle_time_ms,
                    serverSelectionTimeoutMS=config.database.server_selection_timeout_ms
                )
                
                # Get database and collection
                self.db = self.client[config.database.database_name]
                self.collection = self.db[config.database.collection_name]
                
                # Test connection
                await self.client.admin.command('ping')
                logger.info("MongoDB connection established successfully")
                
                # Create indexes
                await self._create_indexes()
                
                self._initialized = True
                
            except Exception as e:
                logger.error(f"Failed to initialize database: {e}")
                raise
    
    async def _create_indexes(self) -> None:
        """Create necessary database indexes"""
        try:
            # Text search index
            await self.collection.create_index([
                ("text", "text")
            ], name="text_search")
            
            # Project and type index
            await self.collection.create_index([
                ("project", ASCENDING),
                ("type", ASCENDING)
            ], name="project_type")
            
            # Timestamp index
            await self.collection.create_index([
                ("created_at", DESCENDING)
            ], name="created_at")
            
            # Importance index
            await self.collection.create_index([
                ("importance", DESCENDING)
            ], name="importance")
            
            # Project and importance index
            await self.collection.create_index([
                ("project", ASCENDING),
                ("importance", DESCENDING),
                ("created_at", DESCENDING)
            ], name="project_importance_time")
            
            # Embedding index (for vector search)
            await self.collection.create_index([
                ("embedding", "2dsphere")
            ], name="embedding_vector")
            
            logger.info("Database indexes created successfully")
            
        except Exception as e:
            logger.error(f"Failed to create indexes: {e}")
            raise
    
    async def create_memory(self, memory_data: MemoryCreate, embedding: List[float]) -> Memory:
        """Create a new memory"""
        await self._ensure_initialized()
        
        try:
            # Prepare document
            document = {
                "_id": ObjectId(),
                "text": memory_data.text,
                "type": memory_data.type.value,
                "project": memory_data.project,
                "metadata": memory_data.metadata,
                "importance": memory_data.importance,
                "embedding": embedding,
                "created_at": datetime.utcnow(),
                "updated_at": None
            }
            
            # Insert document
            result = await self.collection.insert_one(document)
            
            # Convert to Memory model
            memory = Memory(
                id=str(result.inserted_id),
                text=memory_data.text,
                type=memory_data.type,
                project=memory_data.project,
                metadata=memory_data.metadata,
                importance=memory_data.importance,
                embedding=embedding,
                created_at=document["created_at"]
            )
            
            logger.info(f"Created memory: {memory.id} (project={memory.project}, type={memory.type})")
            return memory
            
        except DuplicateKeyError as e:
            logger.error(f"Duplicate key error creating memory: {e}")
            raise
        except PyMongoError as e:
            logger.error(f"Database error creating memory: {e}")
            raise
    
    async def get_memory(self, memory_id: str) -> Optional[Memory]:
        """Get a memory by ID"""
        await self._ensure_initialized()
        
        try:
            document = await self.collection.find_one({"_id": ObjectId(memory_id)})
            
            if not document:
                return None
            
            return self._document_to_memory(document)
            
        except PyMongoError as e:
            logger.error(f"Database error getting memory {memory_id}: {e}")
            raise
    
    async def update_memory(self, memory_id: str, updates: MemoryUpdate, embedding: Optional[List[float]] = None) -> Optional[Memory]:
        """Update an existing memory"""
        await self._ensure_initialized()
        
        try:
            # Prepare update document
            update_doc = {"updated_at": datetime.utcnow()}
            
            if updates.text is not None:
                update_doc["text"] = updates.text
            if updates.type is not None:
                update_doc["type"] = updates.type.value
            if updates.metadata is not None:
                update_doc["metadata"] = updates.metadata
            if updates.importance is not None:
                update_doc["importance"] = updates.importance
            if embedding is not None:
                update_doc["embedding"] = embedding
            
            # Update document
            result = await self.collection.update_one(
                {"_id": ObjectId(memory_id)},
                {"$set": update_doc}
            )
            
            if result.modified_count == 0:
                return None
            
            # Get updated document
            return await self.get_memory(memory_id)
            
        except PyMongoError as e:
            logger.error(f"Database error updating memory {memory_id}: {e}")
            raise
    
    async def delete_memory(self, memory_id: str) -> bool:
        """Delete a memory"""
        await self._ensure_initialized()
        
        try:
            result = await self.collection.delete_one({"_id": ObjectId(memory_id)})
            deleted = result.deleted_count > 0
            
            if deleted:
                logger.info(f"Deleted memory: {memory_id}")
            
            return deleted
            
        except PyMongoError as e:
            logger.error(f"Database error deleting memory {memory_id}: {e}")
            raise
    
    async def search_memories(
        self, 
        query_embedding: List[float], 
        search_query: MemorySearchQuery
    ) -> List[Tuple[Memory, float]]:
        """Search memories by similarity"""
        await self._ensure_initialized()
        
        try:
            start_time = time.time()
            
            # Build filter
            filter_query = {"project": search_query.project}
            
            if search_query.type != "all":
                filter_query["type"] = search_query.type.value
            
            if search_query.min_importance is not None:
                filter_query["importance"] = {"$gte": search_query.min_importance}
            
            # Build aggregation pipeline for similarity search
            pipeline = [
                {"$match": filter_query},
                {
                    "$addFields": {
                        "similarity": {
                            "$let": {
                                "vars": {
                                    "dot_product": {
                                        "$reduce": {
                                            "input": {"$zip": {"inputs": ["$embedding", query_embedding]}},
                                            "initialValue": 0,
                                            "in": {
                                                "$add": [
                                                    "$$value",
                                                    {"$multiply": [
                                                        {"$arrayElemAt": ["$$this", 0]},
                                                        {"$arrayElemAt": ["$$this", 1]}
                                                    ]}
                                                ]
                                            }
                                        }
                                    }
                                },
                                "in": "$$dot_product"
                            }
                        }
                    }
                },
                {"$match": {"similarity": {"$gte": search_query.min_similarity or 0.0}}},
                {"$sort": {"similarity": DESCENDING}},
                {"$limit": search_query.limit}
            ]
            
            # Execute search
            cursor = self.collection.aggregate(pipeline)
            documents = await cursor.to_list(None)
            
            # Convert to Memory objects with similarity scores
            results = []
            for doc in documents:
                memory = self._document_to_memory(doc)
                similarity = doc.get("similarity", 0.0)
                results.append((memory, similarity))
            
            search_time = time.time() - start_time
            logger.info(f"Search completed in {search_time:.3f}s: {len(results)} results")
            
            return results
            
        except PyMongoError as e:
            logger.error(f"Database error searching memories: {e}")
            raise
    
    async def get_project_memories(
        self, 
        project: str, 
        memory_types: Optional[List[str]] = None,
        limit: int = 50,
        min_importance: Optional[float] = None
    ) -> List[Memory]:
        """Get memories for a specific project"""
        await self._ensure_initialized()
        
        try:
            # Build filter
            filter_query = {"project": project}
            
            if memory_types:
                filter_query["type"] = {"$in": memory_types}
            
            if min_importance is not None:
                filter_query["importance"] = {"$gte": min_importance}
            
            # Execute query
            cursor = self.collection.find(filter_query).sort([
                ("importance", DESCENDING),
                ("created_at", DESCENDING)
            ]).limit(limit)
            
            documents = await cursor.to_list(None)
            
            # Convert to Memory objects
            memories = [self._document_to_memory(doc) for doc in documents]
            
            logger.info(f"Retrieved {len(memories)} memories for project: {project}")
            return memories
            
        except PyMongoError as e:
            logger.error(f"Database error getting project memories: {e}")
            raise
    
    async def get_memory_stats(self, project: str) -> MemoryStats:
        """Get statistics for a project"""
        await self._ensure_initialized()
        
        try:
            # Total count
            total_count = await self.collection.count_documents({"project": project})
            
            # Count by type
            pipeline = [
                {"$match": {"project": project}},
                {"$group": {"_id": "$type", "count": {"$sum": 1}}}
            ]
            
            cursor = self.collection.aggregate(pipeline)
            type_counts = await cursor.to_list(None)
            
            memories_by_type = {item["_id"]: item["count"] for item in type_counts}
            
            # Average importance
            pipeline = [
                {"$match": {"project": project}},
                {"$group": {"_id": None, "avg_importance": {"$avg": "$importance"}}}
            ]
            
            cursor = self.collection.aggregate(pipeline)
            avg_result = await cursor.to_list(None)
            avg_importance = avg_result[0]["avg_importance"] if avg_result else 0.0
            
            # Oldest and newest
            oldest_doc = await self.collection.find_one(
                {"project": project},
                sort=[("created_at", ASCENDING)]
            )
            
            newest_doc = await self.collection.find_one(
                {"project": project},
                sort=[("created_at", DESCENDING)]
            )
            
            return MemoryStats(
                project=project,
                total_memories=total_count,
                memories_by_type=memories_by_type,
                avg_importance=avg_importance,
                oldest_memory=oldest_doc["created_at"] if oldest_doc else None,
                newest_memory=newest_doc["created_at"] if newest_doc else None
            )
            
        except PyMongoError as e:
            logger.error(f"Database error getting memory stats: {e}")
            raise
    
    async def cleanup_old_memories(self, days_old: int = 30) -> int:
        """Clean up old memories"""
        await self._ensure_initialized()
        
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=days_old)
            
            result = await self.collection.delete_many({
                "created_at": {"$lt": cutoff_date},
                "importance": {"$lt": 0.3}  # Only delete low importance memories
            })
            
            deleted_count = result.deleted_count
            logger.info(f"Cleaned up {deleted_count} old memories (older than {days_old} days)")
            
            return deleted_count
            
        except PyMongoError as e:
            logger.error(f"Database error cleaning up old memories: {e}")
            raise
    
    def _document_to_memory(self, document: Dict[str, Any]) -> Memory:
        """Convert MongoDB document to Memory model"""
        return Memory(
            id=str(document["_id"]),
            text=document["text"],
            type=document["type"],
            project=document["project"],
            metadata=document.get("metadata", {}),
            importance=document.get("importance", 0.5),
            embedding=document.get("embedding"),
            created_at=document["created_at"],
            updated_at=document.get("updated_at")
        )
    
    async def _ensure_initialized(self) -> None:
        """Ensure the service is initialized"""
        if not self._initialized:
            await self.initialize()
    
    async def close(self) -> None:
        """Close database connection"""
        if self.client:
            self.client.close()
            logger.info("Database connection closed")
    
    def is_initialized(self) -> bool:
        """Check if the service is initialized"""
        return self._initialized

# Global database service instance
database_service = DatabaseService() 