#!/usr/bin/env python3
"""
Production-Ready Integration Manager for MCP Memory Server
Manages all AI agent integrations with unified configuration and monitoring
"""

import asyncio
import json
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional, Any, Type
from dataclasses import dataclass, asdict

from .ai-agents import (
    BaseAIIntegration,
    ClaudeMemoryIntegration,
    GPTMemoryIntegration,
    CursorMemoryIntegration
)
from ..src.config.settings import get_config
from ..src.utils.logging import get_logger, log_performance
from ..src.utils.exceptions import MCPMemoryError


logger = get_logger(__name__)


@dataclass
class IntegrationStatus:
    """Status of an integration"""
    name: str
    active: bool
    initialized: bool
    last_activity: datetime
    error_count: int
    memory_count: int
    metadata: Dict[str, Any]


class IntegrationManager:
    """
    Manages all AI integrations with unified configuration and monitoring
    """
    
    def __init__(self, config_override: Optional[Dict] = None):
        self.config = get_config()
        self.integrations: Dict[str, BaseAIIntegration] = {}
        self.integration_configs = {}
        self.manager_config = self._load_manager_config(config_override)
        
        # Available integration classes
        self.available_integrations = {
            'cursor': CursorMemoryIntegration,
            'claude': ClaudeMemoryIntegration,
            'gpt': GPTMemoryIntegration
        }
        
        # Status tracking
        self.status_cache = {}
        self.last_status_update = None
        
    def _load_manager_config(self, config_override: Optional[Dict] = None) -> Dict:
        """Load integration manager configuration"""
        default_config = {
            'auto_start_integrations': ['cursor'],
            'health_check_interval': 300,  # 5 minutes
            'max_concurrent_integrations': 5,
            'integration_timeout': 30,
            'enable_cross_platform_sync': True,
            'unified_project_namespace': True
        }
        
        # Load from file if exists
        config_path = Path.home() / ".mcp_memory" / "integration_manager.json"
        if config_path.exists():
            try:
                with open(config_path, 'r') as f:
                    file_config = json.load(f)
                default_config.update(file_config)
            except Exception as e:
                logger.warning(f"Failed to load manager config: {e}")
        
        if config_override:
            default_config.update(config_override)
        
        return default_config
    
    async def initialize_all_integrations(self, platforms: Optional[List[str]] = None) -> Dict[str, bool]:
        """Initialize specified or all available integrations"""
        platforms = platforms or self.manager_config.get('auto_start_integrations', [])
        results = {}
        
        logger.info(f"Initializing integrations: {platforms}")
        
        for platform in platforms:
            try:
                result = await self.add_integration(platform)
                results[platform] = result
            except Exception as e:
                logger.error(f"Failed to initialize {platform} integration: {e}")
                results[platform] = False
        
        logger.info(f"Integration initialization results: {results}")
        return results
    
    async def add_integration(
        self, 
        platform: str, 
        config_override: Optional[Dict] = None
    ) -> bool:
        """Add and initialize a specific integration"""
        try:
            if platform in self.integrations:
                logger.warning(f"Integration {platform} already exists")
                return True
            
            if platform not in self.available_integrations:
                raise ValueError(f"Unknown integration platform: {platform}")
            
            # Create integration instance
            integration_class = self.available_integrations[platform]
            integration = integration_class(config_override)
            
            # Initialize integration
            success = await integration.start_integration()
            
            if success:
                self.integrations[platform] = integration
                logger.info(f"Successfully added {platform} integration")
                
                # Setup cross-platform hooks if enabled
                if self.manager_config.get('enable_cross_platform_sync', True):
                    await self._setup_cross_platform_hooks(integration)
                
                return True
            else:
                logger.error(f"Failed to initialize {platform} integration")
                return False
                
        except Exception as e:
            logger.error(f"Error adding {platform} integration: {e}")
            return False
    
    async def _setup_cross_platform_hooks(self, integration: BaseAIIntegration):
        """Setup hooks for cross-platform memory synchronization"""
        try:
            async def sync_memory_across_platforms(memory_data):
                """Sync memory to other active integrations"""
                if not self.manager_config.get('enable_cross_platform_sync', True):
                    return
                
                for platform, other_integration in self.integrations.items():
                    if other_integration != integration:
                        try:
                            # Notify other integrations of new memory
                            await other_integration._trigger_hook('cross_platform_memory', memory_data)
                        except Exception as e:
                            logger.debug(f"Cross-platform sync to {platform} failed: {e}")
            
            # Add the sync hook
            integration.add_hook('post_save', sync_memory_across_platforms)
            
        except Exception as e:
            logger.warning(f"Failed to setup cross-platform hooks: {e}")
    
    async def remove_integration(self, platform: str) -> bool:
        """Remove an integration"""
        try:
            if platform not in self.integrations:
                logger.warning(f"Integration {platform} not found")
                return False
            
            integration = self.integrations[platform]
            await integration.shutdown()
            
            del self.integrations[platform]
            logger.info(f"Removed {platform} integration")
            return True
            
        except Exception as e:
            logger.error(f"Failed to remove {platform} integration: {e}")
            return False
    
    @log_performance("integration_status_check")
    async def get_integration_status(self, platform: Optional[str] = None) -> Dict[str, IntegrationStatus]:
        """Get status of integrations"""
        statuses = {}
        
        platforms = [platform] if platform else list(self.integrations.keys())
        
        for platform_name in platforms:
            if platform_name not in self.integrations:
                continue
                
            integration = self.integrations[platform_name]
            
            try:
                stats = await integration.get_integration_stats()
                
                status = IntegrationStatus(
                    name=platform_name,
                    active=True,
                    initialized=True,
                    last_activity=datetime.fromtimestamp(stats.get('last_memory_time', 0)),
                    error_count=0,  # Could be tracked by integration
                    memory_count=stats.get('session_memory_count', 0),
                    metadata=stats
                )
                
                statuses[platform_name] = status
                
            except Exception as e:
                logger.warning(f"Failed to get status for {platform_name}: {e}")
                statuses[platform_name] = IntegrationStatus(
                    name=platform_name,
                    active=False,
                    initialized=False,
                    last_activity=datetime.now(timezone.utc),
                    error_count=1,
                    memory_count=0,
                    metadata={'error': str(e)}
                )
        
        self.status_cache = statuses
        self.last_status_update = datetime.now(timezone.utc)
        
        return statuses
    
    async def process_unified_conversation(
        self, 
        conversation_data: Dict[str, Any],
        target_platforms: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Process conversation across multiple platforms"""
        target_platforms = target_platforms or list(self.integrations.keys())
        results = {}
        
        for platform in target_platforms:
            if platform not in self.integrations:
                continue
                
            try:
                integration = self.integrations[platform]
                result = await integration.process_conversation(conversation_data)
                results[platform] = result
                
            except Exception as e:
                logger.error(f"Failed to process conversation on {platform}: {e}")
                results[platform] = {'error': str(e)}
        
        return results
    
    async def search_across_platforms(
        self, 
        query: str,
        limit_per_platform: int = 5
    ) -> Dict[str, List[Dict]]:
        """Search memories across all active integrations"""
        results = {}
        
        for platform, integration in self.integrations.items():
            try:
                memories = await integration.search_relevant_memories(
                    query, 
                    limit=limit_per_platform
                )
                results[platform] = memories
                
            except Exception as e:
                logger.error(f"Search failed on {platform}: {e}")
                results[platform] = []
        
        return results
    
    async def export_integration_configs(self, output_path: Optional[str] = None) -> str:
        """Export all integration configurations"""
        try:
            if not output_path:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                output_path = f"mcp_integrations_config_{timestamp}.json"
            
            config_data = {
                'manager_config': self.manager_config,
                'integrations': {},
                'status': {},
                'exported_at': datetime.now(timezone.utc).isoformat()
            }
            
            # Get integration configs and status
            for platform, integration in self.integrations.items():
                config_data['integrations'][platform] = integration.integration_config
                
                try:
                    stats = await integration.get_integration_stats()
                    config_data['status'][platform] = stats
                except:
                    config_data['status'][platform] = {'error': 'Failed to get stats'}
            
            # Save to file
            with open(output_path, 'w') as f:
                json.dump(config_data, f, indent=2, default=str)
            
            logger.info(f"Integration configurations exported to {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"Failed to export integration configs: {e}")
            raise
    
    async def health_check(self) -> Dict[str, Any]:
        """Perform health check on all integrations"""
        health_status = {
            'overall_status': 'healthy',
            'integrations': {},
            'checked_at': datetime.now(timezone.utc).isoformat(),
            'manager_status': 'active'
        }
        
        issues = []
        
        for platform, integration in self.integrations.items():
            try:
                # Basic connectivity check
                stats = await integration.get_integration_stats()
                
                integration_health = {
                    'status': 'healthy',
                    'memory_client_available': stats.get('memory_client_available', False),
                    'session_memory_count': stats.get('session_memory_count', 0),
                    'last_activity': stats.get('last_memory_time', 0)
                }
                
                # Check for issues
                if not stats.get('memory_client_available'):
                    integration_health['status'] = 'degraded'
                    issues.append(f"{platform}: Memory client not available")
                
                health_status['integrations'][platform] = integration_health
                
            except Exception as e:
                health_status['integrations'][platform] = {
                    'status': 'error',
                    'error': str(e)
                }
                issues.append(f"{platform}: {str(e)}")
        
        # Determine overall status
        if issues:
            health_status['overall_status'] = 'degraded' if len(issues) < len(self.integrations) else 'unhealthy'
            health_status['issues'] = issues
        
        return health_status
    
    async def shutdown_all(self):
        """Shutdown all integrations"""
        logger.info("Shutting down all integrations...")
        
        shutdown_tasks = []
        for platform, integration in self.integrations.items():
            shutdown_tasks.append(integration.shutdown())
        
        # Wait for all shutdowns to complete
        if shutdown_tasks:
            await asyncio.gather(*shutdown_tasks, return_exceptions=True)
        
        self.integrations.clear()
        logger.info("All integrations shut down")


# Standalone utility functions
async def create_integration_manager(
    platforms: Optional[List[str]] = None,
    config: Optional[Dict] = None
) -> IntegrationManager:
    """Create and initialize integration manager"""
    manager = IntegrationManager(config)
    
    if platforms:
        await manager.initialize_all_integrations(platforms)
    
    return manager


def setup_all_integrations_cli():
    """CLI function to setup all integrations"""
    async def main():
        try:
            print("🚀 Setting up MCP Memory integrations...")
            
            manager = IntegrationManager()
            platforms = ['cursor', 'claude', 'gpt']
            
            results = await manager.initialize_all_integrations(platforms)
            
            print("\n📊 Integration Results:")
            for platform, success in results.items():
                status = "✅ Success" if success else "❌ Failed"
                print(f"  {platform}: {status}")
            
            # Export configuration
            config_file = await manager.export_integration_configs()
            print(f"\n📄 Configuration exported to: {config_file}")
            
            # Health check
            health = await manager.health_check()
            print(f"\n🏥 Health Status: {health['overall_status']}")
            
            if health.get('issues'):
                print("⚠️  Issues found:")
                for issue in health['issues']:
                    print(f"  • {issue}")
            
            await manager.shutdown_all()
            print("\n✅ Setup completed!")
            
        except Exception as e:
            print(f"❌ Setup failed: {e}")
            import sys
            sys.exit(1)
    
    asyncio.run(main())


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "setup":
        setup_all_integrations_cli()
    
    elif len(sys.argv) > 1 and sys.argv[1] == "health":
        async def health_check():
            manager = IntegrationManager()
            await manager.initialize_all_integrations()
            health = await manager.health_check()
            print(json.dumps(health, indent=2, default=str))
            await manager.shutdown_all()
        
        asyncio.run(health_check())
    
    else:
        print("Usage:")
        print("  python integration_manager.py setup")
        print("  python integration_manager.py health")
