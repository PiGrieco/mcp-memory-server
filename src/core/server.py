"""
Unified MCP Server for all platforms
"""

import asyncio
import logging
from typing import Dict, Any, Optional
from pathlib import Path

from mcp.server import Server
from mcp.server.models import InitializationOptions
import mcp.server.stdio
import mcp.types as types

from ..config.settings import Settings
from ..services.memory_service import MemoryService
from ..services.embedding_service import EmbeddingService
from ..services.database_service import DatabaseService
from ..utils.exceptions import MCPMemoryError


class MCPServer:
    """Unified MCP Server for all platforms"""
    
    def __init__(self, settings: Settings):
        self.settings = settings
        self.server = Server(settings.server.name)
        self.memory_service = MemoryService(settings)
        self.embedding_service = EmbeddingService(settings.embedding)
        self.database_service = DatabaseService(settings.database)
        
        # Setup logging
        self._setup_logging()
        
        # Setup handlers
        self._setup_handlers()
        
        self.logger = logging.getLogger(__name__)
    
    def _setup_logging(self):
        """Setup logging configuration"""
        logging.basicConfig(
            level=getattr(logging, self.settings.logging.level),
            format=self.settings.logging.format,
            handlers=[
                logging.FileHandler(self.settings.logging.file),
                logging.StreamHandler()
            ]
        )
    
    def _setup_handlers(self):
        """Setup MCP protocol handlers"""
        
        @self.server.list_tools()
        async def handle_list_tools() -> list[types.Tool]:
            """List available tools"""
            return [
                types.Tool(
                    name="save_memory",
                    description="Save a memory with automatic embedding and importance analysis",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "content": {"type": "string", "description": "Memory content"},
                            "project": {"type": "string", "description": "Project name", "default": "default"},
                            "importance": {"type": "number", "minimum": 0, "maximum": 1, "default": 0.5},
                            "tags": {"type": "array", "items": {"type": "string"}, "default": []},
                            "metadata": {"type": "object", "default": {}},
                            "context": {"type": "object", "default": {}}
                        },
                        "required": ["content"]
                    }
                ),
                types.Tool(
                    name="search_memories",
                    description="Search memories using semantic similarity",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "query": {"type": "string", "description": "Search query"},
                            "project": {"type": "string", "description": "Project to search in"},
                            "max_results": {"type": "integer", "minimum": 1, "maximum": 100, "default": 20},
                            "similarity_threshold": {"type": "number", "minimum": 0, "maximum": 1, "default": 0.3},
                            "tags": {"type": "array", "items": {"type": "string"}, "default": []}
                        },
                        "required": ["query"]
                    }
                ),
                types.Tool(
                    name="list_memories",
                    description="List all memories for a project",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "project": {"type": "string", "description": "Project name", "default": "default"},
                            "limit": {"type": "integer", "minimum": 1, "maximum": 100, "default": 50},
                            "offset": {"type": "integer", "minimum": 0, "default": 0}
                        }
                    }
                ),
                types.Tool(
                    name="memory_status",
                    description="Get memory system status and statistics",
                    inputSchema={
                        "type": "object",
                        "properties": {}
                    }
                ),
                types.Tool(
                    name="auto_save_memory",
                    description="Automatically save memory if content triggers the threshold",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "content": {"type": "string", "description": "Content to analyze"},
                            "context": {"type": "object", "description": "Context information", "default": {}},
                            "project": {"type": "string", "description": "Project name", "default": "default"}
                        },
                        "required": ["content"]
                    }
                )
            ]
        
        @self.server.call_tool()
        async def handle_call_tool(name: str, arguments: dict) -> list[types.TextContent]:
            """Handle tool calls"""
            try:
                if name == "save_memory":
                    result = await self._handle_save_memory(arguments)
                elif name == "search_memories":
                    result = await self._handle_search_memories(arguments)
                elif name == "list_memories":
                    result = await self._handle_list_memories(arguments)
                elif name == "memory_status":
                    result = await self._handle_memory_status(arguments)
                elif name == "auto_save_memory":
                    result = await self._handle_auto_save_memory(arguments)
                else:
                    raise MCPMemoryError(f"Unknown tool: {name}")
                
                return [types.TextContent(type="text", text=result)]
                
            except Exception as e:
                self.logger.error(f"Error handling tool {name}: {e}")
                raise MCPMemoryError(f"Tool execution failed: {e}")
    
    async def _handle_save_memory(self, arguments: dict) -> str:
        """Handle save_memory tool"""
        try:
            memory = await self.memory_service.create_memory(
                content=arguments["content"],
                project=arguments.get("project", "default"),
                importance=arguments.get("importance", 0.5),
                tags=arguments.get("tags", []),
                metadata=arguments.get("metadata", {}),
                context=arguments.get("context", {})
            )
            
            return f"✅ Memory saved successfully with ID: {memory.id}"
            
        except Exception as e:
            self.logger.error(f"Failed to save memory: {e}")
            raise MCPMemoryError(f"Failed to save memory: {e}")
    
    async def _handle_search_memories(self, arguments: dict) -> str:
        """Handle search_memories tool"""
        try:
            results = await self.memory_service.search_memories(
                query=arguments["query"],
                project=arguments.get("project"),
                max_results=arguments.get("max_results", 20),
                similarity_threshold=arguments.get("similarity_threshold", 0.3),
                tags=arguments.get("tags", [])
            )
            
            if not results:
                return "🔍 No memories found matching your query."
            
            response = f"🔍 Found {len(results)} memories:\n\n"
            for i, memory in enumerate(results, 1):
                response += f"{i}. **{memory.project}** - {memory.content[:100]}...\n"
                response += f"   Similarity: {memory.similarity_score:.2f}\n\n"
            
            return response
            
        except Exception as e:
            self.logger.error(f"Failed to search memories: {e}")
            raise MCPMemoryError(f"Failed to search memories: {e}")
    
    async def _handle_list_memories(self, arguments: dict) -> str:
        """Handle list_memories tool"""
        try:
            memories = await self.memory_service.list_memories(
                project=arguments.get("project", "default"),
                limit=arguments.get("limit", 50),
                offset=arguments.get("offset", 0)
            )
            
            if not memories:
                return f"📝 No memories found for project: {arguments.get('project', 'default')}"
            
            response = f"📝 Found {len(memories)} memories:\n\n"
            for i, memory in enumerate(memories, 1):
                response += f"{i}. **{memory.project}** - {memory.content[:100]}...\n"
                response += f"   Created: {memory.created_at.strftime('%Y-%m-%d %H:%M')}\n\n"
            
            return response
            
        except Exception as e:
            self.logger.error(f"Failed to list memories: {e}")
            raise MCPMemoryError(f"Failed to list memories: {e}")
    
    async def _handle_memory_status(self, arguments: dict) -> str:
        """Handle memory_status tool"""
        try:
            status = await self.memory_service.get_status()
            
            response = "📊 **Memory System Status**\n\n"
            response += f"• **Total Memories**: {status['total_memories']}\n"
            response += f"• **Projects**: {status['total_projects']}\n"
            response += f"• **Storage**: {status['storage_type']}\n"
            response += f"• **Auto-save**: {'✅ Enabled' if status['auto_save_enabled'] else '❌ Disabled'}\n"
            response += f"• **ML Triggers**: {'✅ Enabled' if status['ml_triggers_enabled'] else '❌ Disabled'}\n"
            response += f"• **Last Activity**: {status['last_activity']}\n"
            
            return response
            
        except Exception as e:
            self.logger.error(f"Failed to get memory status: {e}")
            raise MCPMemoryError(f"Failed to get memory status: {e}")
    
    async def _handle_auto_save_memory(self, arguments: dict) -> str:
        """Handle auto_save_memory tool"""
        try:
            result = await self.memory_service.auto_save_memory(
                content=arguments["content"],
                context=arguments.get("context", {}),
                project=arguments.get("project", "default")
            )
            
            if result["saved"]:
                return f"💾 Memory auto-saved! Trigger: {result['trigger_type']}"
            else:
                return f"⏭️ Content did not meet auto-save criteria (threshold: {result['threshold']})"
                
        except Exception as e:
            self.logger.error(f"Failed to auto-save memory: {e}")
            raise MCPMemoryError(f"Failed to auto-save memory: {e}")
    
    async def initialize(self):
        """Initialize the server and all services"""
        try:
            self.logger.info("🚀 Initializing MCP Memory Server...")
            
            # Initialize services
            await self.database_service.initialize()
            await self.embedding_service.initialize()
            await self.memory_service.initialize()
            
            self.logger.info("✅ MCP Memory Server initialized successfully")
            
        except Exception as e:
            self.logger.error(f"❌ Failed to initialize server: {e}")
            raise
    
    async def start(self):
        """Start the MCP server"""
        try:
            await self.initialize()
            
            self.logger.info(f"🎯 Starting MCP server in {self.settings.server.mode} mode")
            
            if self.settings.server.mode in ["universal", "mcp_only"]:
                # Start MCP server
                async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
                    await self.server.run(
                        read_stream,
                        write_stream,
                        InitializationOptions(
                            server_name=self.settings.server.name,
                            server_version=self.settings.server.version,
                            capabilities=self.server.get_capabilities(
                                experimental_capabilities={},
                            ),
                        ),
                    )
            
        except Exception as e:
            self.logger.error(f"❌ Server failed to start: {e}")
            raise 