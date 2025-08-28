"""
Plugin service for MCP Memory Server
"""

import asyncio
import logging
import importlib
from typing import Dict, Any, List, Optional, Callable
from pathlib import Path
from dataclasses import dataclass

from ..config.settings import Settings
from ..utils.exceptions import PluginServiceError


@dataclass
class PluginInfo:
    """Plugin information"""
    name: str
    version: str
    description: str
    author: str
    hooks: List[str]
    enabled: bool = True
    config: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.config is None:
            self.config = {}


@dataclass
class PluginHook:
    """Plugin hook definition"""
    name: str
    plugin: str
    function: Callable
    priority: int = 0
    async_func: bool = False


class PluginService:
    """Plugin service for extensibility"""
    
    def __init__(self, settings: Settings):
        self.settings = settings
        self.plugins: Dict[str, PluginInfo] = {}
        self.hooks: Dict[str, List[PluginHook]] = {}
        self.plugin_modules: Dict[str, Any] = {}
        self._initialized = False
        
        self.logger = logging.getLogger(__name__)
    
    async def initialize(self) -> None:
        """Initialize plugin service"""
        if self._initialized:
            return
        
        try:
            # Create plugins directory if it doesn't exist
            plugins_dir = Path(self.settings.plugins.directory)
            plugins_dir.mkdir(parents=True, exist_ok=True)
            
            # Load plugins
            await self._load_plugins()
            
            # Initialize enabled plugins
            await self._initialize_plugins()
            
            self._initialized = True
            self.logger.info(f"Plugin service initialized with {len(self.plugins)} plugins")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize plugin service: {e}")
            raise PluginServiceError(f"Plugin service initialization failed: {e}")
    
    async def _load_plugins(self) -> None:
        """Load plugins from plugins directory"""
        try:
            plugins_dir = Path(self.settings.plugins.directory)
            
            if not plugins_dir.exists():
                self.logger.info("Plugins directory does not exist, skipping plugin loading")
                return
            
            # Load built-in plugins
            await self._load_builtin_plugins()
            
            # Load external plugins
            await self._load_external_plugins(plugins_dir)
            
        except Exception as e:
            self.logger.error(f"Failed to load plugins: {e}")
            raise
    
    async def _load_builtin_plugins(self) -> None:
        """Load built-in plugins"""
        try:
            builtin_plugins = [
                "memory_analytics",
                "backup_manager", 
                "notification_service",
                "export_service"
            ]
            
            for plugin_name in builtin_plugins:
                try:
                    await self._load_plugin_module(f"plugins.{plugin_name}")
                except Exception as e:
                    self.logger.warning(f"Failed to load builtin plugin {plugin_name}: {e}")
                    
        except Exception as e:
            self.logger.error(f"Failed to load builtin plugins: {e}")
    
    async def _load_external_plugins(self, plugins_dir: Path) -> None:
        """Load external plugins from directory"""
        try:
            for plugin_file in plugins_dir.glob("*.py"):
                if plugin_file.name.startswith("_"):
                    continue
                
                try:
                    plugin_name = plugin_file.stem
                    await self._load_plugin_from_file(plugin_file, plugin_name)
                except Exception as e:
                    self.logger.warning(f"Failed to load plugin {plugin_file.name}: {e}")
                    
        except Exception as e:
            self.logger.error(f"Failed to load external plugins: {e}")
    
    async def _load_plugin_from_file(self, plugin_file: Path, plugin_name: str) -> None:
        """Load plugin from file"""
        try:
            # Import plugin module
            spec = importlib.util.spec_from_file_location(plugin_name, plugin_file)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            
            # Get plugin info
            plugin_info = getattr(module, "PLUGIN_INFO", None)
            if not plugin_info:
                self.logger.warning(f"Plugin {plugin_name} missing PLUGIN_INFO")
                return
            
            # Create plugin info object
            plugin = PluginInfo(
                name=plugin_info.get("name", plugin_name),
                version=plugin_info.get("version", "1.0.0"),
                description=plugin_info.get("description", ""),
                author=plugin_info.get("author", "Unknown"),
                hooks=plugin_info.get("hooks", []),
                enabled=plugin_info.get("enabled", True),
                config=plugin_info.get("config", {})
            )
            
            # Store plugin
            self.plugins[plugin_name] = plugin
            self.plugin_modules[plugin_name] = module
            
            self.logger.info(f"Loaded plugin: {plugin.name} v{plugin.version}")
            
        except Exception as e:
            self.logger.error(f"Failed to load plugin {plugin_name}: {e}")
            raise
    
    async def _load_plugin_module(self, module_path: str) -> None:
        """Load plugin module by path"""
        try:
            module = importlib.import_module(module_path)
            plugin_name = module_path.split(".")[-1]
            
            # Get plugin info
            plugin_info = getattr(module, "PLUGIN_INFO", None)
            if not plugin_info:
                return
            
            # Create plugin info object
            plugin = PluginInfo(
                name=plugin_info.get("name", plugin_name),
                version=plugin_info.get("version", "1.0.0"),
                description=plugin_info.get("description", ""),
                author=plugin_info.get("author", "Unknown"),
                hooks=plugin_info.get("hooks", []),
                enabled=plugin_info.get("enabled", True),
                config=plugin_info.get("config", {})
            )
            
            # Store plugin
            self.plugins[plugin_name] = plugin
            self.plugin_modules[plugin_name] = module
            
            self.logger.info(f"Loaded builtin plugin: {plugin.name} v{plugin.version}")
            
        except Exception as e:
            self.logger.error(f"Failed to load plugin module {module_path}: {e}")
            raise
    
    async def _initialize_plugins(self) -> None:
        """Initialize enabled plugins"""
        try:
            for plugin_name, plugin in self.plugins.items():
                if not plugin.enabled:
                    continue
                
                try:
                    await self._initialize_plugin(plugin_name, plugin)
                except Exception as e:
                    self.logger.error(f"Failed to initialize plugin {plugin_name}: {e}")
                    
        except Exception as e:
            self.logger.error(f"Failed to initialize plugins: {e}")
            raise
    
    async def _initialize_plugin(self, plugin_name: str, plugin: PluginInfo) -> None:
        """Initialize a specific plugin"""
        try:
            module = self.plugin_modules[plugin_name]
            
            # Call plugin initialize function if it exists
            if hasattr(module, "initialize"):
                init_func = getattr(module, "initialize")
                if asyncio.iscoroutinefunction(init_func):
                    await init_func(self.settings, plugin.config)
                else:
                    init_func(self.settings, plugin.config)
            
            # Register hooks
            await self._register_plugin_hooks(plugin_name, plugin, module)
            
            self.logger.info(f"Initialized plugin: {plugin.name}")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize plugin {plugin_name}: {e}")
            raise
    
    async def _register_plugin_hooks(self, plugin_name: str, plugin: PluginInfo, module: Any) -> None:
        """Register plugin hooks"""
        try:
            for hook_name in plugin.hooks:
                hook_func = getattr(module, hook_name, None)
                if hook_func and callable(hook_func):
                    hook = PluginHook(
                        name=hook_name,
                        plugin=plugin_name,
                        function=hook_func,
                        priority=getattr(module, f"{hook_name}_priority", 0),
                        async_func=asyncio.iscoroutinefunction(hook_func)
                    )
                    
                    if hook_name not in self.hooks:
                        self.hooks[hook_name] = []
                    
                    self.hooks[hook_name].append(hook)
                    
                    # Sort by priority
                    self.hooks[hook_name].sort(key=lambda h: h.priority, reverse=True)
                    
                    self.logger.debug(f"Registered hook {hook_name} for plugin {plugin_name}")
                    
        except Exception as e:
            self.logger.error(f"Failed to register hooks for plugin {plugin_name}: {e}")
            raise
    
    async def call_hook(self, hook_name: str, *args, **kwargs) -> List[Any]:
        """Call a hook and return results from all plugins"""
        try:
            if hook_name not in self.hooks:
                return []
            
            results = []
            for hook in self.hooks[hook_name]:
                try:
                    if hook.async_func:
                        result = await hook.function(*args, **kwargs)
                    else:
                        result = hook.function(*args, **kwargs)
                    
                    results.append({
                        "plugin": hook.plugin,
                        "result": result
                    })
                    
                except Exception as e:
                    self.logger.error(f"Hook {hook_name} failed for plugin {hook.plugin}: {e}")
                    results.append({
                        "plugin": hook.plugin,
                        "error": str(e)
                    })
            
            return results
            
        except Exception as e:
            self.logger.error(f"Failed to call hook {hook_name}: {e}")
            return []
    
    async def enable_plugin(self, plugin_name: str) -> bool:
        """Enable a plugin"""
        try:
            if plugin_name not in self.plugins:
                return False
            
            plugin = self.plugins[plugin_name]
            plugin.enabled = True
            
            # Re-initialize plugin
            await self._initialize_plugin(plugin_name, plugin)
            
            self.logger.info(f"Enabled plugin: {plugin.name}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to enable plugin {plugin_name}: {e}")
            return False
    
    async def disable_plugin(self, plugin_name: str) -> bool:
        """Disable a plugin"""
        try:
            if plugin_name not in self.plugins:
                return False
            
            plugin = self.plugins[plugin_name]
            plugin.enabled = False
            
            # Remove hooks
            for hook_name in list(self.hooks.keys()):
                self.hooks[hook_name] = [
                    hook for hook in self.hooks[hook_name] 
                    if hook.plugin != plugin_name
                ]
                
                if not self.hooks[hook_name]:
                    del self.hooks[hook_name]
            
            self.logger.info(f"Disabled plugin: {plugin.name}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to disable plugin {plugin_name}: {e}")
            return False
    
    async def get_plugin_info(self, plugin_name: str) -> Optional[PluginInfo]:
        """Get plugin information"""
        return self.plugins.get(plugin_name)
    
    async def list_plugins(self) -> List[PluginInfo]:
        """List all plugins"""
        return list(self.plugins.values())
    
    async def get_plugin_status(self) -> Dict[str, Any]:
        """Get plugin service status"""
        try:
            enabled_plugins = [p for p in self.plugins.values() if p.enabled]
            disabled_plugins = [p for p in self.plugins.values() if not p.enabled]
            
            return {
                "total_plugins": len(self.plugins),
                "enabled_plugins": len(enabled_plugins),
                "disabled_plugins": len(disabled_plugins),
                "total_hooks": sum(len(hooks) for hooks in self.hooks.values()),
                "hook_types": list(self.hooks.keys()),
                "status": "healthy" if self._initialized else "not_initialized"
            }
            
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e)
            } 