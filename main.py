#!/usr/bin/env python3
"""
MCP Memory Server - Production Ready Main Entry Point
"""

import asyncio
import logging
import signal
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.config import setup_logging, get_config
from src.core import MCPServer
from src.services import database_service, embedding_service, memory_service


class GracefulShutdown:
    """Handle graceful shutdown of the server"""
    
    def __init__(self):
        self.shutdown = False
        self.tasks = []
    
    def exit_gracefully(self, signum, frame):
        """Handle shutdown signal"""
        logging.info(f"Received signal {signum}, initiating graceful shutdown...")
        self.shutdown = True
        
        # Cancel all running tasks
        for task in self.tasks:
            if not task.done():
                task.cancel()


async def initialize_services():
    """Initialize all services"""
    logger = logging.getLogger(__name__)
    
    try:
        logger.info("Initializing services...")
        
        # Initialize database service
        logger.info("Initializing database service...")
        await database_service.initialize()
        
        # Initialize embedding service
        logger.info("Initializing embedding service...")
        await embedding_service.initialize()
        
        # Initialize memory service
        logger.info("Initializing memory service...")
        await memory_service.initialize()
        
        logger.info("All services initialized successfully")
        
    except Exception as e:
        logger.error(f"Failed to initialize services: {e}")
        raise


async def shutdown_services():
    """Shutdown all services gracefully"""
    logger = logging.getLogger(__name__)
    
    try:
        logger.info("Shutting down services...")
        
        # Close database connection
        await database_service.close()
        
        logger.info("All services shut down successfully")
        
    except Exception as e:
        logger.error(f"Error during service shutdown: {e}")


async def health_check():
    """Perform initial health check"""
    logger = logging.getLogger(__name__)
    
    try:
        logger.info("Performing health check...")
        
        # Check database
        db_health = await database_service.health_check()
        logger.info(f"Database health: {db_health['status']}")
        
        # Check embedding service
        embedding_health = await embedding_service.health_check()
        logger.info(f"Embedding service health: {embedding_health['status']}")
        
        # Check memory service
        memory_health = await memory_service.health_check()
        logger.info(f"Memory service health: {memory_health['status']}")
        
        # Overall health
        all_healthy = all(
            health['status'] == 'healthy' 
            for health in [db_health, embedding_health, memory_health]
        )
        
        if all_healthy:
            logger.info("All services are healthy")
        else:
            logger.warning("Some services are not healthy")
            
        return all_healthy
        
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return False


async def main():
    """Main entry point"""
    # Setup logging first
    setup_logging()
    logger = logging.getLogger(__name__)
    
    # Get configuration
    config = get_config()
    
    logger.info("=" * 60)
    logger.info("Starting MCP Memory Server (Production)")
    logger.info("=" * 60)
    logger.info(f"Version: {config.server.version}")
    logger.info(f"Environment: {config.environment.value}")
    logger.info(f"Debug mode: {config.env_config.get('debug', False)}")
    logger.info("=" * 60)
    
    # Setup graceful shutdown
    shutdown_handler = GracefulShutdown()
    signal.signal(signal.SIGINT, shutdown_handler.exit_gracefully)
    signal.signal(signal.SIGTERM, shutdown_handler.exit_gracefully)
    
    try:
        # Initialize services
        await initialize_services()
        
        # Perform health check
        if not await health_check():
            logger.error("Health check failed, exiting...")
            sys.exit(1)
        
        # Create and run MCP server
        logger.info("Starting MCP server...")
        server = MCPServer()
        
        # Run server
        server_task = asyncio.create_task(server.run())
        shutdown_handler.tasks.append(server_task)
        
        logger.info(f"MCP Memory Server started successfully on {config.server.host}:{config.server.port}")
        logger.info("Server is ready to accept connections")
        
        # Wait for server or shutdown signal
        while not shutdown_handler.shutdown:
            try:
                await asyncio.sleep(1)
                if server_task.done():
                    break
            except asyncio.CancelledError:
                break
        
        logger.info("Shutdown signal received, stopping server...")
        
    except KeyboardInterrupt:
        logger.info("Server stopped by user (Ctrl+C)")
    except Exception as e:
        logger.error(f"Server error: {e}")
        sys.exit(1)
    finally:
        # Cleanup
        try:
            await shutdown_services()
        except Exception as e:
            logger.error(f"Error during cleanup: {e}")
        
        logger.info("MCP Memory Server stopped")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nServer stopped by user")
    except Exception as e:
        print(f"Fatal error: {e}")
        sys.exit(1)
