#!/usr/bin/env python3
"""
Test server for the new architecture
"""

import asyncio
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.config.settings import get_settings  # noqa: E402
from src.services.memory_service import MemoryService  # noqa: E402
from src.services.database_service import DatabaseService  # noqa: E402
from src.services.embedding_service import EmbeddingService  # noqa: E402


async def test_architecture():
    """Test the new architecture"""
    print("🧪 Testing new architecture...")
    
    try:
        # Load settings
        settings = get_settings()
        print("✅ Settings loaded successfully")
        
        # Test database service
        db_service = DatabaseService(settings)
        await db_service.initialize()
        print("✅ Database service initialized")
        
        # Test embedding service
        embedding_service = EmbeddingService(settings)
        await embedding_service.initialize()
        print("✅ Embedding service initialized")
        
        # Test memory service
        memory_service = MemoryService(settings)
        await memory_service.initialize()
        print("✅ Memory service initialized")
        
        # Test memory creation
        memory = await memory_service.create_memory(
            content="Test memory from new architecture",
            project="test",
            importance=0.8,
            tags=["test", "architecture"]
        )
        print(f"✅ Memory created: {memory.id}")
        
        # Test memory search
        results = await memory_service.search_memories(
            query="test architecture",
            project="test"
        )
        print(f"✅ Memory search found {len(results)} results")
        
        # Test memory listing
        memories = await memory_service.list_memories(project="test")
        print(f"✅ Memory listing found {len(memories)} memories")
        
        # Test status
        status = await memory_service.get_status()
        print(f"✅ Memory status: {status['total_memories']} total memories")
        
        print("\n🎉 All tests passed! New architecture is working correctly!")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True


if __name__ == "__main__":
    success = asyncio.run(test_architecture())
    sys.exit(0 if success else 1) 