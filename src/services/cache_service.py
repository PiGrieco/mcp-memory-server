"""
Cache service for MCP Memory Server
"""

import asyncio
import logging
import json
import hashlib
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List, Union
from dataclasses import dataclass, asdict

import redis.asyncio as redis
from pydantic import BaseModel

from ..config.settings import Settings
from ..utils.exceptions import CacheServiceError


@dataclass
class CacheEntry:
    """Cache entry with metadata"""
    key: str
    value: Any
    created_at: datetime
    expires_at: Optional[datetime] = None
    access_count: int = 0
    last_accessed: Optional[datetime] = None
    
    def is_expired(self) -> bool:
        """Check if entry is expired"""
        if self.expires_at is None:
            return False
        return datetime.utcnow() > self.expires_at
    
    def touch(self) -> None:
        """Update access metadata"""
        self.access_count += 1
        self.last_accessed = datetime.utcnow()


class CacheService:
    """Distributed cache service with Redis backend"""
    
    def __init__(self, settings: Settings):
        self.settings = settings
        self.redis_client: Optional[redis.Redis] = None
        self.local_cache: Dict[str, CacheEntry] = {}
        self._initialized = False
        
        self.logger = logging.getLogger(__name__)
    
    async def initialize(self) -> None:
        """Initialize cache service"""
        if self._initialized:
            return
        
        try:
            # Initialize Redis connection
            if self.settings.cache.redis_enabled:
                await self._initialize_redis()
            
            # Start cache cleanup task
            asyncio.create_task(self._cache_cleanup_task())
            
            self._initialized = True
            self.logger.info("Cache service initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize cache service: {e}")
            raise CacheServiceError(f"Cache service initialization failed: {e}")
    
    async def _initialize_redis(self) -> None:
        """Initialize Redis connection"""
        try:
            self.redis_client = redis.Redis(
                host=self.settings.cache.redis["host"],
                port=self.settings.cache.redis["port"],
                db=self.settings.cache.redis["db"],
                password=self.settings.cache.redis.get("password"),
                decode_responses=True,
                socket_connect_timeout=5,
                socket_timeout=5,
                retry_on_timeout=True
            )
            
            # Test connection
            await self.redis_client.ping()
            
            self.logger.info(f"Redis cache connected to {self.settings.cache.redis['host']}:{self.settings.cache.redis['port']}")
            
        except Exception as e:
            self.logger.warning(f"Failed to connect to Redis: {e}")
            self.redis_client = None
    
    async def _cache_cleanup_task(self) -> None:
        """Background task to clean up expired cache entries"""
        while True:
            try:
                await asyncio.sleep(self.settings.cache.cleanup_interval)
                await self._cleanup_expired_entries()
            except Exception as e:
                self.logger.error(f"Cache cleanup task error: {e}")
    
    async def _cleanup_expired_entries(self) -> None:
        """Clean up expired cache entries"""
        try:
            # Clean local cache
            expired_keys = [
                key for key, entry in self.local_cache.items()
                if entry.is_expired()
            ]
            
            for key in expired_keys:
                del self.local_cache[key]
            
            if expired_keys:
                self.logger.debug(f"Cleaned up {len(expired_keys)} expired local cache entries")
            
            # Clean Redis cache (Redis handles expiration automatically)
            if self.redis_client:
                # Optional: Add custom cleanup logic for Redis if needed
                pass
                
        except Exception as e:
            self.logger.error(f"Failed to cleanup expired entries: {e}")
    
    def _generate_key(self, prefix: str, *args, **kwargs) -> str:
        """Generate cache key from prefix and arguments"""
        # Create a hash of the arguments
        key_data = {
            "args": args,
            "kwargs": sorted(kwargs.items())
        }
        
        key_hash = hashlib.md5(
            json.dumps(key_data, sort_keys=True).encode()
        ).hexdigest()
        
        return f"{prefix}:{key_hash}"
    
    async def get(self, key: str, default: Any = None) -> Any:
        """Get value from cache"""
        try:
            # Try local cache first
            if key in self.local_cache:
                entry = self.local_cache[key]
                if not entry.is_expired():
                    entry.touch()
                    return entry.value
                else:
                    del self.local_cache[key]
            
            # Try Redis cache
            if self.redis_client:
                try:
                    value = await self.redis_client.get(key)
                    if value is not None:
                        # Parse JSON value
                        parsed_value = json.loads(value)
                        
                        # Store in local cache for faster access
                        await self.set_local(key, parsed_value, ttl=300)  # 5 minutes local cache
                        
                        return parsed_value
                except Exception as e:
                    self.logger.debug(f"Redis get failed for key {key}: {e}")
            
            return default
            
        except Exception as e:
            self.logger.error(f"Failed to get cache key {key}: {e}")
            return default
    
    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Set value in cache"""
        try:
            # Set in local cache
            await self.set_local(key, value, ttl)
            
            # Set in Redis cache
            if self.redis_client:
                try:
                    json_value = json.dumps(value)
                    if ttl:
                        await self.redis_client.setex(key, ttl, json_value)
                    else:
                        await self.redis_client.set(key, json_value)
                except Exception as e:
                    self.logger.debug(f"Redis set failed for key {key}: {e}")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to set cache key {key}: {e}")
            return False
    
    async def set_local(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """Set value in local cache only"""
        try:
            expires_at = None
            if ttl:
                expires_at = datetime.utcnow() + timedelta(seconds=ttl)
            
            entry = CacheEntry(
                key=key,
                value=value,
                created_at=datetime.utcnow(),
                expires_at=expires_at
            )
            
            self.local_cache[key] = entry
            
        except Exception as e:
            self.logger.error(f"Failed to set local cache key {key}: {e}")
    
    async def delete(self, key: str) -> bool:
        """Delete value from cache"""
        try:
            # Delete from local cache
            if key in self.local_cache:
                del self.local_cache[key]
            
            # Delete from Redis cache
            if self.redis_client:
                try:
                    await self.redis_client.delete(key)
                except Exception as e:
                    self.logger.debug(f"Redis delete failed for key {key}: {e}")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to delete cache key {key}: {e}")
            return False
    
    async def exists(self, key: str) -> bool:
        """Check if key exists in cache"""
        try:
            # Check local cache
            if key in self.local_cache:
                entry = self.local_cache[key]
                if not entry.is_expired():
                    return True
                else:
                    del self.local_cache[key]
            
            # Check Redis cache
            if self.redis_client:
                try:
                    return await self.redis_client.exists(key) > 0
                except Exception as e:
                    self.logger.debug(f"Redis exists failed for key {key}: {e}")
            
            return False
            
        except Exception as e:
            self.logger.error(f"Failed to check cache key {key}: {e}")
            return False
    
    async def clear(self, pattern: Optional[str] = None) -> bool:
        """Clear cache entries"""
        try:
            # Clear local cache
            if pattern:
                keys_to_delete = [
                    key for key in self.local_cache.keys()
                    if pattern in key
                ]
                for key in keys_to_delete:
                    del self.local_cache[key]
            else:
                self.local_cache.clear()
            
            # Clear Redis cache
            if self.redis_client:
                try:
                    if pattern:
                        keys = await self.redis_client.keys(pattern)
                        if keys:
                            await self.redis_client.delete(*keys)
                    else:
                        await self.redis_client.flushdb()
                except Exception as e:
                    self.logger.debug(f"Redis clear failed: {e}")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to clear cache: {e}")
            return False
    
    async def get_memory_cache_key(self, memory_id: str) -> str:
        """Get cache key for memory"""
        return f"memory:{memory_id}"
    
    async def get_search_cache_key(self, query: str, project: str, max_results: int) -> str:
        """Get cache key for search results"""
        return self._generate_key("search", query, project, max_results)
    
    async def get_embedding_cache_key(self, text: str) -> str:
        """Get cache key for embedding"""
        return self._generate_key("embedding", text)
    
    async def cache_memory(self, memory: Any) -> bool:
        """Cache a memory object"""
        try:
            # Handle both Memory objects and dictionaries
            if hasattr(memory, 'id'):
                memory_id = memory.id
                memory_data = asdict(memory)
            elif isinstance(memory, dict) and 'id' in memory:
                memory_id = memory['id']
                memory_data = memory
            else:
                self.logger.warning(f"Invalid memory object for caching: {type(memory)}")
                return False
            
            key = await self.get_memory_cache_key(memory_id)
            return await self.set(key, memory_data, ttl=self.settings.cache.memory_ttl)
        except Exception as e:
            memory_id = getattr(memory, 'id', str(memory)) if hasattr(memory, 'id') else str(memory)
            self.logger.error(f"Failed to cache memory {memory_id}: {e}")
            return False
    
    async def get_cached_memory(self, memory_id: str) -> Optional[Any]:
        """Get cached memory"""
        try:
            key = await self.get_memory_cache_key(memory_id)
            return await self.get(key)
        except Exception as e:
            self.logger.error(f"Failed to get cached memory {memory_id}: {e}")
            return None
    
    async def cache_search_results(self, query: str, project: str, max_results: int, results: List[Any]) -> bool:
        """Cache search results"""
        try:
            key = await self.get_search_cache_key(query, project, max_results)
            return await self.set(key, results, ttl=self.settings.cache.search_ttl)
        except Exception as e:
            self.logger.error(f"Failed to cache search results: {e}")
            return False
    
    async def get_cached_search_results(self, query: str, project: str, max_results: int) -> Optional[List[Any]]:
        """Get cached search results"""
        try:
            key = await self.get_search_cache_key(query, project, max_results)
            return await self.get(key)
        except Exception as e:
            self.logger.error(f"Failed to get cached search results: {e}")
            return None
    
    async def cache_embedding(self, text: str, embedding: List[float]) -> bool:
        """Cache embedding"""
        try:
            key = await self.get_embedding_cache_key(text)
            return await self.set(key, embedding, ttl=self.settings.cache.embedding_ttl)
        except Exception as e:
            self.logger.error(f"Failed to cache embedding: {e}")
            return False
    
    async def get_cached_embedding(self, text: str) -> Optional[List[float]]:
        """Get cached embedding"""
        try:
            key = await self.get_embedding_cache_key(text)
            return await self.get(key)
        except Exception as e:
            self.logger.error(f"Failed to get cached embedding: {e}")
            return None
    
    async def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        try:
            stats = {
                "local_cache_size": len(self.local_cache),
                "local_cache_keys": list(self.local_cache.keys()),
                "redis_enabled": self.redis_client is not None,
                "status": "healthy" if self._initialized else "not_initialized"
            }
            
            if self.redis_client:
                try:
                    redis_info = await self.redis_client.info()
                    stats["redis_info"] = {
                        "used_memory": redis_info.get("used_memory_human"),
                        "connected_clients": redis_info.get("connected_clients"),
                        "total_commands_processed": redis_info.get("total_commands_processed")
                    }
                except Exception as e:
                    stats["redis_error"] = str(e)
            
            return stats
            
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
            
            # Test local cache
            test_key = "health_check"
            test_value = {"timestamp": datetime.utcnow().isoformat()}
            
            await self.set_local(test_key, test_value, ttl=60)
            retrieved_value = await self.get(test_key)
            
            local_cache_ok = retrieved_value == test_value
            
            # Test Redis cache
            redis_ok = False
            if self.redis_client:
                try:
                    await self.redis_client.ping()
                    redis_ok = True
                except Exception as e:
                    redis_ok = False
            
            overall_status = "healthy" if local_cache_ok else "unhealthy"
            
            return {
                "status": overall_status,
                "local_cache": "healthy" if local_cache_ok else "unhealthy",
                "redis_cache": "healthy" if redis_ok else "unhealthy",
                "local_cache_size": len(self.local_cache)
            }
            
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e)
            } 