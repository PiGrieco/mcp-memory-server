#!/usr/bin/env python3
"""
Test script for advanced services (plugins and cache)
"""

import asyncio
import sys
from pathlib import Path

# Add src to path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

from src.config.settings import get_settings  # noqa: E402
from src.services.plugin_service import PluginService  # noqa: E402
from src.services.cache_service import CacheService  # noqa: E402
from src.services.memory_service import MemoryService  # noqa: E402


async def test_plugin_service():
    """Test plugin service"""
    print("🧪 Testing Plugin Service...")
    
    try:
        # Load settings
        settings = get_settings()
        print("✅ Settings loaded successfully")
        
        # Create plugin service
        plugin_service = PluginService(settings)
        await plugin_service.initialize()
        print("✅ Plugin service initialized")
        
        # Test plugin status
        status = await plugin_service.get_plugin_status()
        print(f"✅ Plugin status: {status['total_plugins']} plugins loaded")
        
        # Test listing plugins
        plugins = await plugin_service.list_plugins()
        print(f"✅ Found {len(plugins)} plugins")
        
        # Test hook calling (even if no plugins are loaded)
        hook_results = await plugin_service.call_hook("test_hook", "test_data")
        print(f"✅ Hook call test completed: {len(hook_results)} results")
        
        return True
        
    except Exception as e:
        print(f"❌ Plugin service test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_cache_service():
    """Test cache service"""
    print("\n🧪 Testing Cache Service...")
    
    try:
        # Load settings
        settings = get_settings()
        print("✅ Settings loaded successfully")
        
        # Create cache service
        cache_service = CacheService(settings)
        await cache_service.initialize()
        print("✅ Cache service initialized")
        
        # Test basic cache operations
        test_key = "test_key"
        test_value = {"message": "Hello from cache!", "timestamp": "2024-01-01"}
        
        # Set value
        success = await cache_service.set(test_key, test_value, ttl=60)
        print(f"✅ Cache set: {success}")
        
        # Get value
        retrieved_value = await cache_service.get(test_key)
        print(f"✅ Cache get: {retrieved_value == test_value}")
        
        # Test exists
        exists = await cache_service.exists(test_key)
        print(f"✅ Cache exists: {exists}")
        
        # Test memory-specific cache
        memory_data = {
            "id": "test_memory_123",
            "content": "Test memory content",
            "project": "test",
            "importance": 0.8
        }
        
        await cache_service.get_memory_cache_key("test_memory_123")
        await cache_service.cache_memory(memory_data)
        cached_memory = await cache_service.get_cached_memory("test_memory_123")
        print(f"✅ Memory cache: {cached_memory is not None}")
        
        # Test search cache
        search_results = [{"id": "1", "content": "result 1"}, {"id": "2", "content": "result 2"}]
        await cache_service.cache_search_results("test query", "test", 10, search_results)
        cached_search = await cache_service.get_cached_search_results("test query", "test", 10)
        print(f"✅ Search cache: {cached_search is not None}")
        
        # Test embedding cache
        embedding = [0.1, 0.2, 0.3, 0.4, 0.5]
        await cache_service.cache_embedding("test text", embedding)
        cached_embedding = await cache_service.get_cached_embedding("test text")
        print(f"✅ Embedding cache: {cached_embedding == embedding}")
        
        # Get cache stats
        stats = await cache_service.get_cache_stats()
        print(f"✅ Cache stats: {stats['local_cache_size']} local entries")
        
        # Health check
        health = await cache_service.health_check()
        print(f"✅ Cache health: {health['status']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Cache service test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_integration():
    """Test integration between services"""
    print("\n🧪 Testing Service Integration...")
    
    try:
        # Load settings
        settings = get_settings()
        print("✅ Settings loaded successfully")
        
        # Create services
        memory_service = MemoryService(settings)
        cache_service = CacheService(settings)
        plugin_service = PluginService(settings)
        
        # Initialize services
        await memory_service.initialize()
        await cache_service.initialize()
        await plugin_service.initialize()
        print("✅ All services initialized")
        
        # Test memory creation with cache
        memory = await memory_service.create_memory(
            content="Integration test memory",
            project="integration_test",
            importance=0.9,
            tags=["test", "integration"]
        )
        print(f"✅ Memory created: {memory.id}")
        
        # Test cache integration
        cached_memory = await cache_service.get_cached_memory(memory.id)
        print(f"✅ Memory cached: {cached_memory is not None}")
        
        # Test search with cache
        results = await memory_service.search_memories(
            query="integration test",
            project="integration_test"
        )
        print(f"✅ Search results: {len(results)} memories found")
        
        # Test plugin hooks (if any plugins are loaded)
        hook_results = await plugin_service.call_hook("memory_created", memory)
        print(f"✅ Plugin hooks called: {len(hook_results)} results")
        
        # Test service status
        memory_status = await memory_service.get_status()
        cache_status = await cache_service.get_cache_stats()
        plugin_status = await plugin_service.get_plugin_status()
        
        print(f"✅ Memory status: {memory_status['status']}")
        print(f"✅ Cache status: {cache_status['status']}")
        print(f"✅ Plugin status: {plugin_status['status']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Integration test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def main():
    """Main test function"""
    print("🚀 Testing Advanced Services...")
    
    results = []
    
    # Test plugin service
    results.append(await test_plugin_service())
    
    # Test cache service
    results.append(await test_cache_service())
    
    # Test integration
    results.append(await test_integration())
    
    # Summary
    passed = sum(results)
    total = len(results)
    
    print(f"\n📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All advanced services tests passed!")
        return True
    else:
        print("❌ Some tests failed")
        return False


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1) 