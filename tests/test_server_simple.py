#!/usr/bin/env python3
"""
Simple test script to verify MCP Memory Server services
"""

import asyncio
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.config.settings import get_settings
from src.services.database_service import DatabaseService
from src.services.embedding_service import EmbeddingService
from src.services.memory_service import MemoryService


async def test_services():
    """Test all services individually"""
    print("🧪 Testing MCP Memory Server Services...")
    
    try:
        # Load settings
        settings = get_settings()
        print(f"✅ Settings loaded: {settings.server.name}")
        
        # Test Database Service
        print("\n🗄️ Testing Database Service...")
        db_service = DatabaseService(settings.database)
        await db_service.initialize()
        print("✅ Database service initialized")
        
        # Test Embedding Service
        print("\n🧠 Testing Embedding Service...")
        embedding_service = EmbeddingService(settings.embedding)
        await embedding_service.initialize()
        print("✅ Embedding service initialized")
        
        # Test Memory Service
        print("\n💾 Testing Memory Service...")
        memory_service = MemoryService(settings)
        await memory_service.initialize()
        print("✅ Memory service initialized")
        
        # Test creating a memory
        print("\n📝 Testing Memory Creation...")
        memory = await memory_service.create_memory(
            content="This is a test memory for the MCP Memory Server",
            project="test",
            importance=0.8,
            tags=["test", "demo"],
            metadata={"source": "test_script"}
        )
        print(f"✅ Memory created: {memory.id}")
        
        # Test searching memories
        print("\n🔍 Testing Memory Search...")
        search_results = await memory_service.search_memories(
            query="test memory",
            project="test",
            max_results=5
        )
        print(f"✅ Found {len(search_results)} memories")
        
        # Test getting memory status
        print("\n📊 Testing Memory Status...")
        status = await memory_service.get_status()
        print(f"✅ Status: {status['total_memories']} total memories")
        
        print("\n🎉 All tests passed! Services are working correctly.")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True


async def test_http_endpoints():
    """Test HTTP endpoints if available"""
    print("\n🌐 Testing HTTP Endpoints...")
    
    try:
        import aiohttp
        
        # Test health endpoint
        async with aiohttp.ClientSession() as session:
            async with session.get('http://localhost:8000/health') as response:
                if response.status == 200:
                    print("✅ Health endpoint working")
                else:
                    print(f"⚠️ Health endpoint returned {response.status}")
                    
    except Exception as e:
        print(f"⚠️ HTTP test failed: {e}")


if __name__ == "__main__":
    print("🚀 MCP Memory Server - Service Test")
    print("=" * 50)
    
    # Run tests
    success = asyncio.run(test_services())
    
    if success:
        # Test HTTP endpoints
        asyncio.run(test_http_endpoints())
        
        print("\n" + "=" * 50)
        print("✅ All core services are working!")
        print("💡 The server is ready for use.")
    else:
        print("\n" + "=" * 50)
        print("❌ Some services failed to initialize.")
        print("🔧 Please check the configuration and dependencies.") 