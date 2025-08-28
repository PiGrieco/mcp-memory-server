#!/usr/bin/env python3
"""
Enhanced MCP Server with Automatic Triggering System
Adds intelligent auto-triggering capabilities to the standard MCP server
"""

import asyncio
import json
import time
from typing import Any, Dict, List
from datetime import datetime, timezone

from mcp.server import Server, NotificationOptions
from mcp.server.models import InitializationOptions
import mcp.server.stdio
import mcp.types as types

from ..config import get_config
from ..services.memory_service import MemoryService
from ..services.database_service import DatabaseService
from ..services.embedding_service import EmbeddingService
from .auto_trigger_system import create_auto_trigger_system
from ..utils.logging import get_logger


logger = get_logger(__name__)


class EnhancedMCPServer:
    """
    Enhanced MCP Server with automatic triggering capabilities
    """
    
    def __init__(self):
        self.config = get_config()
        self.server = Server(self.config.server.name)
        self.start_time = time.time()
        
        # Services
        self.memory_service = None
        self.embedding_service = None
        self.database_service = None
        
        # Auto-trigger system
        self.auto_trigger_system = None
        
        # Conversation tracking
        self.conversation_buffer = {}  # platform -> messages
        self.last_interaction_time = {}  # platform -> timestamp
        
        # Auto-trigger configuration
        self.auto_trigger_enabled = True
        self.auto_trigger_platforms = ["cursor", "claude", "chatgpt", "browser"]
        
        self._setup_handlers()
    
    async def initialize_services(self):
        """Initialize all services"""
        try:
            # Initialize database service
            self.database_service = DatabaseService()
            await self.database_service.initialize()
            
            # Initialize embedding service
            self.embedding_service = EmbeddingService()
            await self.embedding_service.initialize()
            
            # Initialize memory service
            self.memory_service = MemoryService(self.database_service, self.embedding_service)
            
            # Initialize auto-trigger system
            if self.auto_trigger_enabled:
                self.auto_trigger_system = create_auto_trigger_system(
                    self.memory_service, 
                    self.embedding_service
                )
                logger.info("Auto-trigger system initialized")
            
            logger.info("All services initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize services: {e}")
            raise
    
    def _setup_handlers(self):
        """Setup MCP protocol handlers with auto-trigger support"""
        
        @self.server.list_tools()
        async def handle_list_tools() -> List[types.Tool]:
            """List available tools including auto-trigger tools"""
            base_tools = [
                types.Tool(
                    name="save_memory",
                    description="Save a memory with automatic embedding and importance analysis",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "content": {"type": "string", "description": "Memory content"},
                            "importance": {"type": "number", "minimum": 0, "maximum": 1, "description": "Importance score"},
                            "memory_type": {"type": "string", "description": "Type of memory"},
                            "metadata": {"type": "object", "description": "Additional metadata"},
                            "project": {"type": "string", "description": "Project name"}
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
                            "limit": {"type": "integer", "description": "Maximum results"},
                            "similarity_threshold": {"type": "number", "description": "Minimum similarity"},
                            "project": {"type": "string", "description": "Project filter"}
                        },
                        "required": ["query"]
                    }
                ),
                types.Tool(
                    name="get_memory_context",
                    description="Get relevant memory context for current conversation",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "context": {"type": "string", "description": "Current conversation context"},
                            "limit": {"type": "integer", "description": "Maximum memories to return"}
                        },
                        "required": ["context"]
                    }
                )
            ]
            
            # Add auto-trigger specific tools
            if self.auto_trigger_enabled:
                auto_tools = [
                    types.Tool(
                        name="register_conversation",
                        description="Register conversation for automatic triggering (used internally)",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "messages": {"type": "array", "description": "Conversation messages"},
                                "platform": {"type": "string", "description": "Platform identifier"},
                                "context": {"type": "object", "description": "Additional context"}
                            },
                            "required": ["messages", "platform"]
                        }
                    ),
                    types.Tool(
                        name="trigger_auto_analysis",
                        description="Manually trigger automatic analysis of conversation",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "messages": {"type": "array", "description": "Messages to analyze"},
                                "platform": {"type": "string", "description": "Platform identifier"}
                            },
                            "required": ["messages"]
                        }
                    ),
                    types.Tool(
                        name="configure_triggers",
                        description="Configure automatic trigger settings",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "enabled": {"type": "boolean", "description": "Enable/disable auto-triggers"},
                                "platforms": {"type": "array", "description": "Enabled platforms"},
                                "rules": {"type": "object", "description": "Trigger rules configuration"}
                            }
                        }
                    )
                ]
                base_tools.extend(auto_tools)
            
            return base_tools
        
        @self.server.call_tool()
        async def handle_call_tool(name: str, arguments: Dict[str, Any]) -> List[types.TextContent]:
            """Handle tool calls with auto-trigger support"""
            try:
                # Ensure services are initialized
                if not self.memory_service:
                    await self.initialize_services()
                
                # Standard tool handlers
                if name == "save_memory":
                    return await self._handle_save_memory(arguments)
                elif name == "search_memories":
                    return await self._handle_search_memories(arguments)
                elif name == "get_memory_context":
                    return await self._handle_get_memory_context(arguments)
                
                # Auto-trigger tool handlers
                elif name == "register_conversation" and self.auto_trigger_enabled:
                    return await self._handle_register_conversation(arguments)
                elif name == "trigger_auto_analysis" and self.auto_trigger_enabled:
                    return await self._handle_trigger_auto_analysis(arguments)
                elif name == "configure_triggers" and self.auto_trigger_enabled:
                    return await self._handle_configure_triggers(arguments)
                
                else:
                    raise ValueError(f"Unknown tool: {name}")
                    
            except Exception as e:
                logger.error(f"Tool call failed: {name} - {e}")
                return [types.TextContent(
                    type="text",
                    text=json.dumps({
                        "success": False,
                        "error": str(e),
                        "tool": name
                    })
                )]
    
    # Standard tool handlers (same as before)
    async def _handle_save_memory(self, arguments: Dict[str, Any]) -> List[types.TextContent]:
        """Handle save_memory tool call"""
        try:
            content = arguments.get("content")
            importance = arguments.get("importance", 0.5)
            memory_type = arguments.get("memory_type", "conversation")
            metadata = arguments.get("metadata", {})
            project = arguments.get("project", "default")
            
            if not content:
                raise ValueError("Content is required")
            
            # Add auto-trigger metadata if this was triggered automatically
            if metadata.get("auto_triggered"):
                metadata["trigger_timestamp"] = datetime.now(timezone.utc).isoformat()
            
            result = await self.memory_service.create_memory(
                content=content,
                importance=importance,
                memory_type=memory_type,
                metadata=metadata,
                project=project
            )
            
            return [types.TextContent(
                type="text",
                text=json.dumps({
                    "success": True,
                    "memory_id": result.get("id"),
                    "message": "Memory saved successfully",
                    "auto_triggered": metadata.get("auto_triggered", False)
                })
            )]
            
        except Exception as e:
            logger.error(f"Save memory failed: {e}")
            raise
    
    async def _handle_search_memories(self, arguments: Dict[str, Any]) -> List[types.TextContent]:
        """Handle search_memories tool call"""
        try:
            query = arguments.get("query")
            limit = arguments.get("limit", 10)
            similarity_threshold = arguments.get("similarity_threshold", 0.3)
            project = arguments.get("project", "default")
            
            if not query:
                raise ValueError("Query is required")
            
            memories = await self.memory_service.search_memories(
                query=query,
                limit=limit,
                similarity_threshold=similarity_threshold,
                project=project
            )
            
            return [types.TextContent(
                type="text",
                text=json.dumps({
                    "success": True,
                    "memories": memories,
                    "count": len(memories),
                    "query": query,
                    "auto_triggered": arguments.get("metadata", {}).get("auto_triggered", False)
                })
            )]
            
        except Exception as e:
            logger.error(f"Search memories failed: {e}")
            raise
    
    async def _handle_get_memory_context(self, arguments: Dict[str, Any]) -> List[types.TextContent]:
        """Handle get_memory_context tool call"""
        try:
            context = arguments.get("context")
            limit = arguments.get("limit", 5)
            
            if not context:
                raise ValueError("Context is required")
            
            # Search for relevant memories
            memories = await self.memory_service.search_memories(
                query=context,
                limit=limit,
                similarity_threshold=0.4
            )
            
            # Format context
            context_info = {
                "relevant_memories": memories,
                "context_summary": context[:200] + "..." if len(context) > 200 else context,
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
            
            return [types.TextContent(
                type="text",
                text=json.dumps({
                    "success": True,
                    "context": context_info,
                    "auto_triggered": arguments.get("metadata", {}).get("auto_triggered", False)
                })
            )]
            
        except Exception as e:
            logger.error(f"Get memory context failed: {e}")
            raise
    
    # Auto-trigger specific handlers
    async def _handle_register_conversation(self, arguments: Dict[str, Any]) -> List[types.TextContent]:
        """Handle conversation registration for auto-triggering"""
        try:
            messages = arguments.get("messages", [])
            platform = arguments.get("platform", "unknown")
            arguments.get("context", {})
            
            # Store conversation in buffer
            self.conversation_buffer[platform] = messages
            self.last_interaction_time[platform] = time.time()
            
            # Check if auto-triggering should occur
            triggered_actions = []
            if platform in self.auto_trigger_platforms and self.auto_trigger_system:
                triggered_actions = await self.auto_trigger_system.check_triggers(messages, platform)
            
            # Execute triggered actions
            execution_results = []
            for action, params in triggered_actions:
                try:
                    if action == "save_memory":
                        result = await self._handle_save_memory(params)
                        execution_results.append({"action": action, "result": "success", "details": result})
                    elif action == "search_memories":
                        result = await self._handle_search_memories(params)
                        execution_results.append({"action": action, "result": "success", "details": result})
                    elif action == "get_memory_context":
                        result = await self._handle_get_memory_context(params)
                        execution_results.append({"action": action, "result": "success", "details": result})
                except Exception as e:
                    execution_results.append({"action": action, "result": "error", "error": str(e)})
            
            return [types.TextContent(
                type="text",
                text=json.dumps({
                    "success": True,
                    "platform": platform,
                    "messages_registered": len(messages),
                    "triggered_actions": len(triggered_actions),
                    "execution_results": execution_results,
                    "timestamp": datetime.now(timezone.utc).isoformat()
                })
            )]
            
        except Exception as e:
            logger.error(f"Register conversation failed: {e}")
            raise
    
    async def _handle_trigger_auto_analysis(self, arguments: Dict[str, Any]) -> List[types.TextContent]:
        """Handle manual trigger of auto-analysis"""
        try:
            messages = arguments.get("messages", [])
            platform = arguments.get("platform", "manual")
            
            if not self.auto_trigger_system:
                raise ValueError("Auto-trigger system not initialized")
            
            # Force analysis
            triggered_actions = await self.auto_trigger_system.check_triggers(messages, platform)
            
            # Return analysis results without executing
            analysis = await self.auto_trigger_system.analyze_conversation(messages)
            
            return [types.TextContent(
                type="text",
                text=json.dumps({
                    "success": True,
                    "analysis": {
                        "importance_score": analysis.importance_score,
                        "keywords": analysis.keywords[:10],  # Limit output
                        "intent": analysis.intent,
                        "characteristics": {
                            "code_content": analysis.code_content,
                            "question_asked": analysis.question_asked,
                            "solution_provided": analysis.solution_provided,
                            "error_mentioned": analysis.error_mentioned,
                            "decision_made": analysis.decision_made
                        }
                    },
                    "triggered_actions": [{"action": action, "params": params} for action, params in triggered_actions],
                    "platform": platform
                })
            )]
            
        except Exception as e:
            logger.error(f"Trigger auto analysis failed: {e}")
            raise
    
    async def _handle_configure_triggers(self, arguments: Dict[str, Any]) -> List[types.TextContent]:
        """Handle trigger configuration"""
        try:
            enabled = arguments.get("enabled")
            platforms = arguments.get("platforms")
            rules = arguments.get("rules")
            
            config_updated = {}
            
            if enabled is not None:
                self.auto_trigger_enabled = enabled
                config_updated["auto_trigger_enabled"] = enabled
            
            if platforms is not None:
                self.auto_trigger_platforms = platforms
                config_updated["auto_trigger_platforms"] = platforms
            
            if rules is not None:
                # Update trigger rules in auto-trigger system
                if self.auto_trigger_system:
                    # This would require implementing rule updates in AutoTriggerSystem
                    config_updated["rules_updated"] = "Feature not yet implemented"
            
            return [types.TextContent(
                type="text",
                text=json.dumps({
                    "success": True,
                    "configuration_updated": config_updated,
                    "current_config": {
                        "auto_trigger_enabled": self.auto_trigger_enabled,
                        "auto_trigger_platforms": self.auto_trigger_platforms
                    }
                })
            )]
            
        except Exception as e:
            logger.error(f"Configure triggers failed: {e}")
            raise
    
    async def start_server(self):
        """Start the enhanced MCP server"""
        try:
            await self.initialize_services()
            
            logger.info(f"Starting Enhanced MCP Server with auto-triggers: {self.auto_trigger_enabled}")
            
            async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
                await self.server.run(
                    read_stream,
                    write_stream,
                    InitializationOptions(
                        server_name=self.config.server.name,
                        server_version=self.config.server.version,
                        capabilities=self.server.get_capabilities(
                            notification_options=NotificationOptions(),
                            experimental_capabilities={}
                        ),
                    ),
                )
                
        except Exception as e:
            logger.error(f"Server startup failed: {e}")
            raise
    
    async def shutdown(self):
        """Shutdown the server gracefully"""
        try:
            if self.database_service:
                await self.database_service.close()
            
            logger.info("Enhanced MCP Server shut down gracefully")
            
        except Exception as e:
            logger.error(f"Shutdown error: {e}")


# Factory function for easy creation
def create_enhanced_mcp_server() -> EnhancedMCPServer:
    """Create and configure enhanced MCP server"""
    return EnhancedMCPServer()


# Main entry point
async def main():
    """Main entry point for enhanced MCP server"""
    server = create_enhanced_mcp_server()
    
    try:
        await server.start_server()
    except KeyboardInterrupt:
        logger.info("Server interrupted by user")
    except Exception as e:
        logger.error(f"Server error: {e}")
    finally:
        await server.shutdown()


if __name__ == "__main__":
    asyncio.run(main())

