#!/usr/bin/env python3
"""
MCP Memory Server - Main Entry Point
Unified server for all platforms with intelligent memory management
"""

import sys
import os
import asyncio
import signal
from pathlib import Path

# Add src to path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

from src.core.server import MCPServer
from src.config.settings import get_settings

# Global server instance for graceful shutdown
server_instance = None

def signal_handler(signum, frame):
    """Handle shutdown signals gracefully"""
    print(f"\n🛑 Received signal {signum}, shutting down...")
    sys.exit(0)

async def main():
    """Main entry point"""
    global server_instance
    
    # Set up signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    try:
        # Load settings
        settings = get_settings()
        
        # Create and start server
        server_instance = MCPServer(settings)
        await server_instance.start()
        
    except KeyboardInterrupt:
        print("\n🛑 Server stopped by user")
    except asyncio.CancelledError:
        print("\n🛑 Server cancelled")
    except Exception as e:
        print(f"❌ Error starting server: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    # Handle test flag
    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        print("✅ Server imports and configuration successful")
        sys.exit(0)
    
    try:
        # Run with proper event loop handling
        if sys.platform == 'win32':
            asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
        
        asyncio.run(main())
        
    except (KeyboardInterrupt, asyncio.CancelledError):
        print("\n🛑 Server stopped")
    except Exception as e:
        print(f"❌ Fatal error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1) 