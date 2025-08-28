import pytest
import sys
import os

# Add project root to path
project_root = os.path.dirname(os.path.dirname(__file__))
sys.path.insert(0, project_root)

@pytest.mark.skip_ci
def test_import_mcp_server():
    """Test that the MCP server module can be imported"""
    try:
        import mcp_memory_server
        assert hasattr(mcp_memory_server, 'async_main')
    except ImportError as e:
        pytest.fail(f"Failed to import MCP server: {e}")

@pytest.mark.skip_ci
def test_import_http_server():
    """Test that the HTTP server module can be imported"""
    try:
        import mcp_memory_server_http
        assert hasattr(mcp_memory_server_http, 'main')
        assert hasattr(mcp_memory_server_http, 'health_handler')
    except ImportError as e:
        pytest.fail(f"Failed to import HTTP server: {e}")

def test_core_services_available():
    """Test that core services can be imported"""
    try:
        from src.services import memory_service, database_service, embedding_service
        assert memory_service is not None
        assert database_service is not None
        assert embedding_service is not None
    except ImportError as e:
        pytest.fail(f"Failed to import core services: {e}")
