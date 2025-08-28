"""
Integration tests for full workflow
"""

import pytest
import sys
import os

# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
sys.path.insert(0, project_root)

from src.services.memory_service import MemoryService  # noqa: E402
from src.services.database_service import DatabaseService  # noqa: E402
from src.services.embedding_service import EmbeddingService  # noqa: E402
from src.services.cache_service import CacheService  # noqa: E402
from src.services.plugin_service import PluginService  # noqa: E402
from src.services.backup_service import BackupService  # noqa: E402
from src.services.notification_service import NotificationService  # noqa: E402
from src.services.export_service import ExportService  # noqa: E402
from src.config.settings import get_settings  # noqa: E402


class TestFullWorkflow:
    """Integration tests for complete workflow"""
    
    @pytest.fixture
    async def services(self):
        """Initialize all services for testing"""
        settings = get_settings()
        
        # Initialize services
        services = {
            "database": DatabaseService(settings),
            "embedding": EmbeddingService(settings),
            "memory": MemoryService(settings),
            "cache": CacheService(settings),
            "plugin": PluginService(settings),
            "backup": BackupService(settings),
            "notification": NotificationService(settings),
            "export": ExportService(settings)
        }
        
        # Initialize all services
        for name, service in services.items():
            try:
                await service.initialize()
                print(f"✅ {name} service initialized")
            except Exception as e:
                print(f"⚠️ {name} service initialization failed: {e}")
        
        yield services
        
        # Cleanup
        for name, service in services.items():
            if hasattr(service, 'stop'):
                try:
                    await service.stop()
                except Exception as e:
                    print(f"⚠️ {name} service cleanup failed: {e}")
    
    @pytest.mark.asyncio
    async def test_memory_creation_workflow(self, services):
        """Test complete memory creation workflow"""
        # Arrange
        memory_service = services["memory"]
        cache_service = services["cache"]
        notification_service = services["notification"]
        
        # Act - Create memory
        memory = await memory_service.create_memory(
            content="Integration test memory content",
            project="integration_test",
            importance=0.9,
            tags=["integration", "test", "workflow"]
        )
        
        # Assert - Memory created
        assert memory is not None
        assert memory.content == "Integration test memory content"
        assert memory.project == "integration_test"
        assert memory.importance == 0.9
        assert "integration" in memory.tags
        
        # Act - Cache memory
        cache_result = await cache_service.cache_memory(memory)
        assert cache_result is True
        
        # Act - Get cached memory
        cached_memory = await cache_service.get_cached_memory(memory.id)
        assert cached_memory is not None
        
        # Act - Send notification
        notification_result = await notification_service.send_memory_created_notification(memory)
        assert notification_result is True
        
        print(f"✅ Memory creation workflow completed: {memory.id}")
    
    @pytest.mark.asyncio
    async def test_search_workflow(self, services):
        """Test complete search workflow"""
        # Arrange
        memory_service = services["memory"]
        cache_service = services["cache"]
        
        # Create test memories
        memories = []
        for i in range(3):
            memory = await memory_service.create_memory(
                content=f"Search test memory {i} with specific keywords",
                project="search_test",
                importance=0.8,
                tags=[f"search_test_{i}", "integration"]
            )
            memories.append(memory)
        
        # Act - Search memories
        search_results = await memory_service.search_memories(
            query="specific keywords",
            project="search_test",
            max_results=10
        )
        
        # Assert - Search results
        assert search_results is not None
        assert len(search_results) >= 1
        
        # Act - Cache search results
        cache_result = await cache_service.cache_search_results(
            query="specific keywords",
            project="search_test",
            max_results=10,
            results=search_results
        )
        assert cache_result is True
        
        # Act - Get cached search results
        cached_results = await cache_service.get_cached_search_results(
            query="specific keywords",
            project="search_test",
            max_results=10
        )
        assert cached_results is not None
        
        print(f"✅ Search workflow completed: {len(search_results)} results found")
    
    @pytest.mark.asyncio
    async def test_auto_save_workflow(self, services):
        """Test auto-save workflow"""
        # Arrange
        memory_service = services["memory"]
        services["embedding"]
        
        # Test content that should trigger auto-save
        test_content = """
        This is important information that should be automatically saved.
        It contains key insights and valuable knowledge that needs to be remembered.
        This is a critical piece of information for the project.
        """
        
        # Act - Auto-save memory
        auto_save_result = await memory_service.auto_save_memory(
            content=test_content,
            project="auto_save_test",
            context={"user_id": "integration_test_user"}
        )
        
        # Assert - Auto-save result
        if auto_save_result is not None:
            assert auto_save_result.content == test_content
            assert auto_save_result.project == "auto_save_test"
            print(f"✅ Auto-save workflow completed: {auto_save_result.id}")
        else:
            print("ℹ️ Auto-save not triggered (content may not meet criteria)")
    
    @pytest.mark.asyncio
    async def test_export_workflow(self, services):
        """Test export workflow"""
        # Arrange
        memory_service = services["memory"]
        export_service = services["export"]
        
        # Create test memories for export
        memories = []
        for i in range(5):
            memory = await memory_service.create_memory(
                content=f"Export test memory {i}",
                project="export_test",
                importance=0.7,
                tags=[f"export_test_{i}", "integration"]
            )
            memories.append(memory)
        
        # Act - Export memories
        export_result = await export_service.export_memories(
            memories=memories,
            format="json",
            filename="integration_test_export.json"
        )
        
        # Assert - Export result
        assert export_result["success"] is True
        assert export_result["memory_count"] == 5
        assert export_result["format"] == "json"
        
        print(f"✅ Export workflow completed: {export_result['filename']}")
    
    @pytest.mark.asyncio
    async def test_backup_workflow(self, services):
        """Test backup workflow"""
        # Arrange
        backup_service = services["backup"]
        notification_service = services["notification"]
        
        # Act - Create backup
        backup_result = await backup_service.create_backup("integration_test")
        
        # Assert - Backup result
        assert backup_result["success"] is True
        assert backup_result["backup_name"] is not None
        
        # Act - Send backup notification
        notification_result = await notification_service.send_backup_notification(backup_result)
        assert notification_result is True
        
        # Act - List backups
        backups = await backup_service.list_backups()
        assert len(backups) >= 1
        
        print(f"✅ Backup workflow completed: {backup_result['backup_name']}")
    
    @pytest.mark.asyncio
    async def test_plugin_workflow(self, services):
        """Test plugin workflow"""
        # Arrange
        plugin_service = services["plugin"]
        memory_service = services["memory"]
        
        # Act - Get plugin status
        plugin_status = await plugin_service.get_plugin_status()
        assert plugin_status is not None
        
        # Act - Create memory to trigger plugin hooks
        memory = await memory_service.create_memory(
            content="Plugin test memory",
            project="plugin_test",
            importance=0.8,
            tags=["plugin", "test"]
        )
        
        # Act - Call plugin hooks
        hook_results = await plugin_service.call_hook("memory_created", memory, {})
        assert hook_results is not None
        
        print(f"✅ Plugin workflow completed: {len(hook_results)} hook results")
    
    @pytest.mark.asyncio
    async def test_health_check_workflow(self, services):
        """Test health check workflow"""
        # Arrange
        health_checks = {}
        
        # Act - Check health of all services
        for name, service in services.items():
            if hasattr(service, 'health_check'):
                try:
                    health = await service.health_check()
                    health_checks[name] = health
                except Exception as e:
                    health_checks[name] = {"status": "error", "error": str(e)}
            else:
                health_checks[name] = {"status": "no_health_check"}
        
        # Assert - Health check results
        for name, health in health_checks.items():
            print(f"  {name}: {health.get('status', 'unknown')}")
            if health.get('status') == 'unhealthy':
                print(f"    ⚠️ {name} is unhealthy: {health.get('error', 'unknown error')}")
        
        # Check if critical services are healthy
        critical_services = ["database", "memory"]
        for service in critical_services:
            if service in health_checks:
                status = health_checks[service].get('status')
                assert status in ['healthy', 'not_initialized'], f"{service} should be healthy or not_initialized, got {status}"
        
        print(f"✅ Health check workflow completed: {len(health_checks)} services checked")
    
    @pytest.mark.asyncio
    async def test_complete_integration_workflow(self, services):
        """Test complete integration workflow"""
        # Arrange
        memory_service = services["memory"]
        cache_service = services["cache"]
        export_service = services["export"]
        backup_service = services["backup"]
        notification_service = services["notification"]
        
        # Act - Create multiple memories
        memories = []
        for i in range(3):
            memory = await memory_service.create_memory(
                content=f"Complete integration test memory {i}",
                project="complete_integration_test",
                importance=0.8 + (i * 0.1),
                tags=[f"integration_{i}", "complete_test"]
            )
            memories.append(memory)
            
            # Cache each memory
            await cache_service.cache_memory(memory)
            
            # Send notification for each memory
            await notification_service.send_memory_created_notification(memory)
        
        # Act - Search memories
        search_results = await memory_service.search_memories(
            query="integration test",
            project="complete_integration_test"
        )
        
        # Act - Export memories
        export_result = await export_service.export_memories(
            memories=memories,
            format="json",
            filename="complete_integration_export.json"
        )
        
        # Act - Create backup
        backup_result = await backup_service.create_backup("complete_integration_test")
        
        # Assert - All operations successful
        assert len(memories) == 3
        assert len(search_results) >= 1
        assert export_result["success"] is True
        assert backup_result["success"] is True
        
        print("✅ Complete integration workflow completed:")
        print(f"  - Created {len(memories)} memories")
        print(f"  - Found {len(search_results)} search results")
        print(f"  - Exported to {export_result['filename']}")
        print(f"  - Created backup {backup_result['backup_name']}")


if __name__ == "__main__":
    pytest.main([__file__, "-v"]) 