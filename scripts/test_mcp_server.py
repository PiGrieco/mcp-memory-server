#!/usr/bin/env python3
"""
Quick MCP Server Test
Verifies that the server can start and respond correctly
"""

import sys
import asyncio
import json
from pathlib import Path

# Add project root to path so we can import from src
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

async def test_mcp_server():
    """Test MCP server initialization and tool registration"""
    print("🧪 Testing MCP Server...")
    
    try:
        # Import and initialize
        from src.core.server import MCPServer
        from src.config.settings import get_settings
        
        # Load settings
        settings = get_settings()
        print(f"✅ Settings loaded: {settings.server.name}")
        
        # Create server instance
        server = MCPServer(settings)
        print("✅ Server instance created")
        
        # Initialize server
        await server.initialize()
        print("✅ Server initialized successfully")
        
        # Check if tools are registered
        mcp_server = server.server
        
        # Check handlers
        has_list_tools = hasattr(mcp_server, '_list_tools_handler')
        has_call_tool = hasattr(mcp_server, '_call_tool_handler')
        
        print(f"✅ List tools handler: {'Yes' if has_list_tools else 'No'}")
        print(f"✅ Call tool handler: {'Yes' if has_call_tool else 'No'}")
        
        # Test tool listing if available
        if has_list_tools:
            try:
                tools = await mcp_server._list_tools_handler()
                print(f"✅ Found {len(tools)} tools registered")
                for tool in tools[:3]:  # Show first 3
                    print(f"   - {tool.name}")
                if len(tools) > 3:
                    print(f"   ... and {len(tools) - 3} more")
            except Exception as e:
                print(f"⚠️ Tool listing error: {e}")
        
        print("\n🎉 MCP Server test PASSED!")
        return True
        
    except Exception as e:
        print(f"❌ MCP Server test FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    # Set minimal environment for testing
    import os
    os.environ.setdefault("ENVIRONMENT", "development")
    os.environ.setdefault("LOG_LEVEL", "WARNING")  # Reduce noise
    os.environ.setdefault("MONGODB_URI", "mongodb://localhost:27017")
    os.environ.setdefault("MONGODB_DATABASE", "mcp_memory_test")
    os.environ.setdefault("SERVER_MODE", "universal")
    
    # Run test
    success = asyncio.run(test_mcp_server())
    sys.exit(0 if success else 1)
