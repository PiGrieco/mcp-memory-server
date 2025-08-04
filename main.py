#!/usr/bin/env python3
"""
MCP Memory Server - Main Entry Point
"""

import asyncio
import logging
import logging.config
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.config import config
from src.core import MCPServer

def setup_logging():
    """Setup logging configuration"""
    logging_config = config.get_logging_config()
    logging.config.dictConfig(logging_config)

async def main():
    """Main entry point"""
    try:
        # Setup logging
        setup_logging()
        logger = logging.getLogger(__name__)
        
        logger.info("Starting MCP Memory Server...")
        logger.info(f"Version: {config.server.version}")
        logger.info(f"Environment: {config.environment}")
        
        # Create and run MCP server
        server = MCPServer()
        await server.run()
        
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    except Exception as e:
        logger.error(f"Server error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main()) 