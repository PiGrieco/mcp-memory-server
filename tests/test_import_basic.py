"""
Basic import tests - these should always pass
"""

import sys
import os

# Add project root to path
project_root = os.path.dirname(os.path.dirname(__file__))
sys.path.insert(0, project_root)


def test_core_imports():
    """Test that core modules can be imported"""
    from src.config.settings import get_settings  # noqa: E402
    from src.models.memory import Memory  # noqa: E402
    from src.services.memory_service import MemoryService  # noqa: E402
    from src.services.database_service import DatabaseService  # noqa: E402
    from src.services.embedding_service import EmbeddingService  # noqa: E402
    
    # Test that we can get settings
    settings = get_settings()
    assert settings is not None
    
    print("✅ All core modules imported successfully")


def test_optional_imports():
    """Test that optional imports work with graceful fallback"""
    from src.services.cache_service import CacheService, REDIS_AVAILABLE  # noqa: E402
    from src.services.backup_service import BackupService, SCHEDULE_AVAILABLE  # noqa: E402
    
    # These should not fail even if dependencies are missing
    assert CacheService is not None
    assert BackupService is not None
    
    print(f"✅ Cache service available: Redis={REDIS_AVAILABLE}")
    print(f"✅ Backup service available: Schedule={SCHEDULE_AVAILABLE}")


def test_server_imports():
    """Test that server modules can be imported"""
    from src.core.server import MCPServer  # noqa: E402
    from src.core.auto_trigger_system import AutoTriggerSystem  # noqa: E402
    
    assert MCPServer is not None
    assert AutoTriggerSystem is not None
    
    print("✅ Server modules imported successfully")


def test_watchdog_import():
    """Test that watchdog service can be imported"""
    from src.services.watchdog_service import WatchdogService  # noqa: E402
    
    assert WatchdogService is not None
    
    print("✅ Watchdog service imported successfully")


if __name__ == "__main__":
    test_core_imports()
    test_optional_imports()
    test_server_imports()
    test_watchdog_import()
    print("🎉 All import tests passed!")
