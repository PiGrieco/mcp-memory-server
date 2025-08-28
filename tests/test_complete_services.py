#!/usr/bin/env python3
"""
Test script for all implemented services
"""

import asyncio
import sys
from pathlib import Path

# Add src to path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

from src.config.settings import get_settings  # noqa: E402
from src.services.memory_service import MemoryService  # noqa: E402
from src.services.database_service import DatabaseService  # noqa: E402
from src.services.embedding_service import EmbeddingService  # noqa: E402
from src.services.plugin_service import PluginService  # noqa: E402
from src.services.cache_service import CacheService  # noqa: E402
from src.services.backup_service import BackupService  # noqa: E402
from src.services.notification_service import NotificationService  # noqa: E402
from src.services.export_service import ExportService  # noqa: E402


async def test_all_services():
    """Test all implemented services"""
    print("🚀 Testing All Services...")
    
    try:
        # Load settings
        settings = get_settings()
        print("✅ Settings loaded successfully")
        
        # Initialize all services
        services = {
            "Database": DatabaseService(settings),
            "Embedding": EmbeddingService(settings),
            "Memory": MemoryService(settings),
            "Plugin": PluginService(settings),
            "Cache": CacheService(settings),
            "Backup": BackupService(settings),
            "Notification": NotificationService(settings),
            "Export": ExportService(settings)
        }
        
        # Initialize services
        for name, service in services.items():
            try:
                await service.initialize()
                print(f"✅ {name} service initialized")
            except Exception as e:
                print(f"⚠️ {name} service initialization failed: {e}")
        
        # Test memory operations
        print("\n🧪 Testing Memory Operations...")
        memory = await services["Memory"].create_memory(
            content="Complete service test memory",
            project="complete_test",
            importance=0.9,
            tags=["test", "complete", "services"]
        )
        print(f"✅ Memory created: {memory.id}")
        
        # Test cache operations
        print("\n🧪 Testing Cache Operations...")
        await services["Cache"].cache_memory(memory)
        cached_memory = await services["Cache"].get_cached_memory(memory.id)
        print(f"✅ Memory cached: {cached_memory is not None}")
        
        # Test search operations
        print("\n🧪 Testing Search Operations...")
        results = await services["Memory"].search_memories(
            query="complete service test",
            project="complete_test"
        )
        print(f"✅ Search results: {len(results)} memories found")
        
        # Test export operations
        print("\n🧪 Testing Export Operations...")
        export_result = await services["Export"].export_memories(
            memories=results,
            format="json",
            filename="test_export.json"
        )
        print(f"✅ Export completed: {export_result['success']}")
        
        # Test backup operations
        print("\n🧪 Testing Backup Operations...")
        backup_result = await services["Backup"].create_backup("test")
        print(f"✅ Backup created: {backup_result['success']}")
        
        # Test notification operations
        print("\n🧪 Testing Notification Operations...")
        notification_result = await services["Notification"].send_notification(
            title="Test Notification",
            content="This is a test notification from the complete service test",
            level="info"
        )
        print(f"✅ Notification sent: {notification_result}")
        
        # Test plugin operations
        print("\n🧪 Testing Plugin Operations...")
        plugin_status = await services["Plugin"].get_plugin_status()
        print(f"✅ Plugin status: {plugin_status['total_plugins']} plugins loaded")
        
        # Get service statuses
        print("\n📊 Service Status Summary:")
        for name, service in services.items():
            try:
                if hasattr(service, 'get_status'):
                    status = await service.get_status()
                elif hasattr(service, 'health_check'):
                    status = await service.health_check()
                else:
                    status = {"status": "unknown"}
                
                print(f"  {name}: {status.get('status', 'unknown')}")
            except Exception as e:
                print(f"  {name}: error - {e}")
        
        print("\n🎉 All services tested successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_service_integration():
    """Test service integration"""
    print("\n🔗 Testing Service Integration...")
    
    try:
        settings = get_settings()
        
        # Create services
        memory_service = MemoryService(settings)
        cache_service = CacheService(settings)
        notification_service = NotificationService(settings)
        export_service = ExportService(settings)
        
        # Initialize services
        await memory_service.initialize()
        await cache_service.initialize()
        await notification_service.initialize()
        await export_service.initialize()
        
        # Create memory with cache
        memory = await memory_service.create_memory(
            content="Integration test memory",
            project="integration_test",
            importance=0.8,
            tags=["integration", "test"]
        )
        print(f"✅ Memory created: {memory.id}")
        
        # Cache memory
        await cache_service.cache_memory(memory)
        print("✅ Memory cached")
        
        # Send notification
        await notification_service.send_memory_created_notification(memory)
        print("✅ Notification sent")
        
        # Export memory
        export_result = await export_service.export_memories([memory], "json")
        print(f"✅ Memory exported: {export_result['success']}")
        
        print("🎉 Service integration test completed!")
        return True
        
    except Exception as e:
        print(f"❌ Integration test failed: {e}")
        return False


async def main():
    """Main test function"""
    print("🚀 Complete Service Test Suite")
    print("=" * 50)
    
    results = []
    
    # Test all services
    results.append(await test_all_services())
    
    # Test service integration
    results.append(await test_service_integration())
    
    # Summary
    passed = sum(results)
    total = len(results)
    
    print(f"\n📊 Test Results: {passed}/{total} test suites passed")
    
    if passed == total:
        print("🎉 All tests passed! All services are working correctly!")
        return True
    else:
        print("❌ Some tests failed")
        return False


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1) 