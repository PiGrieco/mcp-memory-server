#!/usr/bin/env python3
"""
MCP Memory Server - Main Entry Point
Unified server for all platforms with intelligent memory management
"""

import sys
import os
import asyncio
from pathlib import Path

# Add src to path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

from src.core.server import MCPServer
from src.config.settings import get_settings


async def main():
    """Main entry point"""
    try:
        # Load settings
        settings = get_settings()
        
        # Create and start server
        server = MCPServer(settings)
        await server.start()
        
    except KeyboardInterrupt:
        print("\n🛑 Server stopped by user")
    except Exception as e:
        print(f"❌ Error starting server: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main()) 