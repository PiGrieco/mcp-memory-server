"""
Production MCP Server implementation with enhanced features
"""

import asyncio
import json
import logging
from typing import Any, Dict, List, Optional
import time

from mcp.server import Server, NotificationOptions
from mcp.server.models import InitializationOptions
import mcp.server.stdio
import mcp.types as types

from ..config import get_config
from ..models import (
    MemoryCreate, MemoryUpdate, MemorySearchQuery, MemoryContext,
    MemoryType, MemoryImportance, SuccessResponse, ErrorResponse
)
from ..services import memory_service, database_service, embedding_service
from ..utils.exceptions import MCPMemoryError, ValidationError

logger = logging.getLogger(__name__)


class MCPServer:
    """Production MCP Server for memory management with auto-triggers"""
    
    def __init__(self):
        self.config = get_config()
        self.server = Server(self.config.server.name)
        self.start_time = time.time()
        self._setup_handlers()
    
    def _setup_handlers(self):
        """Setup MCP protocol handlers"""
        
        # Tool handlers
        @self.server.list_tools()
        async def handle_list_tools() -> List[types.Tool]:
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
                            "memory_type": {"type": "string", "enum": [t.value for t in MemoryType], "default": "conversation"},
                            "importance": {"type": "number", "minimum": 0, "maximum": 1, "default": 0.5},
                            "tags": {"type": "array", "items": {"type": "string"}, "default": []},
                            "metadata": {"type": "object", "default": {}},
                            "context": {"type": "object", "default": {}},
                            "user_id": {"type": "string"},
                            "session_id": {"type": "string"}
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
                            "memory_types": {"type": "array", "items": {"type": "string"}, "default": []},
                            "min_importance": {"type": "number", "minimum": 0, "maximum": 1, "default": 0.0},
                            "max_results": {"type": "integer", "minimum": 1, "maximum": 100, "default": 20},
                            "similarity_threshold": {"type": "number", "minimum": 0, "maximum": 1, "default": 0.3},
                            "tags": {"type": "array", "items": {"type": "string"}, "default": []},
                            "user_id": {"type": "string"},
                            "session_id": {"type": "string"}
                        },
                        "required": ["query"]
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
                            "project": {"type": "string", "description": "Project name", "default": "default"},
                            "user_id": {"type": "string"},
                            "session_id": {"type": "string"}
                        },
                        "required": ["content"]
                    }
                ),
                types.Tool(
                    name="get_memory_context",
                    description="Get memory context for a project",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "project": {"type": "string", "description": "Project name"},
                            "types": {"type": "array", "items": {"type": "string"}, "description": "Memory types to include"},
                            "limit": {"type": "integer", "minimum": 1, "maximum": 200, "default": 50},
                            "min_importance": {"type": "number", "minimum": 0, "maximum": 1, "default": 0.0},
                            "user_id": {"type": "string"},
                            "session_id": {"type": "string"}
                        },
                        "required": ["project", "types"]
                    }
                ),
                types.Tool(
                    name="get_memory",
                    description="Get a specific memory by ID",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "memory_id": {"type": "string", "description": "Memory ID"}
                        },
                        "required": ["memory_id"]
                    }
                ),
                types.Tool(
                    name="update_memory",
                    description="Update an existing memory",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "memory_id": {"type": "string", "description": "Memory ID"},
                            "content": {"type": "string", "description": "New content"},
                            "memory_type": {"type": "string", "enum": [t.value for t in MemoryType]},
                            "importance": {"type": "number", "minimum": 0, "maximum": 1},
                            "tags": {"type": "array", "items": {"type": "string"}},
                            "metadata": {"type": "object"},
                            "context": {"type": "object"}
                        },
                        "required": ["memory_id"]
                    }
                ),
                types.Tool(
                    name="delete_memory",
                    description="Delete a memory",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "memory_id": {"type": "string", "description": "Memory ID"}
                        },
                        "required": ["memory_id"]
                    }
                ),
                types.Tool(
                    name="health_check",
                    description="Check system health",
                    inputSchema={
                        "type": "object",
                        "properties": {}
                    }
                ),
                types.Tool(
                    name="get_metrics",
                    description="Get system metrics",
                    inputSchema={
                        "type": "object",
                        "properties": {}
                    }
                )
            ]
        
        @self.server.call_tool()
        async def handle_call_tool(name: str, arguments: Dict[str, Any]) -> List[types.TextContent]:
            """Handle tool calls"""
            try:
                if name == "save_memory":
                    return await self._handle_save_memory(arguments)
                elif name == "search_memories":
                    return await self._handle_search_memories(arguments)
                elif name == "auto_save_memory":
                    return await self._handle_auto_save_memory(arguments)
                elif name == "get_memory_context":
                    return await self._handle_get_memory_context(arguments)
                elif name == "get_memory":
                    return await self._handle_get_memory(arguments)
                elif name == "update_memory":
                    return await self._handle_update_memory(arguments)
                elif name == "delete_memory":
                    return await self._handle_delete_memory(arguments)
                elif name == "health_check":
                    return await self._handle_health_check(arguments)
                elif name == "get_metrics":
                    return await self._handle_get_metrics(arguments)
                else:
                    raise ValueError(f"Unknown tool: {name}")
                    
            except Exception as e:
                logger.error(f"Tool call failed: {name} - {e}")
                error_response = ErrorResponse(
                    error=str(e),
                    error_code="TOOL_ERROR",
                    details={"tool": name, "arguments": arguments}
                )
                return [types.TextContent(type="text", text=error_response.to_json())]
        
        # Resource handlers
        @self.server.list_resources()
        async def handle_list_resources() -> List[types.Resource]:
            """List available resources"""
            return [
                types.Resource(
                    uri="memory://health",
                    name="System Health",
                    description="Current system health status",
                    mimeType="application/json"
                ),
                types.Resource(
                    uri="memory://metrics",
                    name="System Metrics", 
                    description="Current system metrics",
                    mimeType="application/json"
                ),
                types.Resource(
                    uri="memory://config",
                    name="Configuration",
                    description="Current system configuration",
                    mimeType="application/json"
                )
            ]
        
        @self.server.read_resource()
        async def handle_read_resource(uri: str) -> str:
            """Handle resource reads"""
            try:
                if uri == "memory://health":
                    health = await self._get_system_health()
                    return json.dumps(health, indent=2)
                elif uri == "memory://metrics":
                    metrics = await memory_service.get_metrics()
                    return json.dumps(metrics, indent=2)
                elif uri == "memory://config":
                    config_dict = {
                        "server": {
                            "name": self.config.server.name,
                            "version": self.config.server.version,
                            "environment": self.config.environment.value
                        },
                        "memory": {
                            "auto_save_enabled": self.config.memory.auto_save_enabled,
                            "trigger_threshold": self.config.memory.trigger_threshold,
                            "default_project": self.config.memory.default_project
                        }
                    }
                    return json.dumps(config_dict, indent=2)
                else:
                    raise ValueError(f"Unknown resource: {uri}")
                    
            except Exception as e:
                logger.error(f"Resource read failed: {uri} - {e}")
                raise

    async def _handle_save_memory(self, arguments: Dict[str, Any]) -> List[types.TextContent]:
        """Handle save memory tool call"""
        try:
            memory_create = MemoryCreate(
                content=arguments["content"],
                project=arguments.get("project", self.config.memory.default_project),
                memory_type=MemoryType(arguments.get("memory_type", "conversation")),
                importance=arguments.get("importance", 0.5),
                tags=arguments.get("tags", []),
                metadata=arguments.get("metadata", {}),
                context=arguments.get("context", {}),
                user_id=arguments.get("user_id"),
                session_id=arguments.get("session_id")
            )

            memory = await memory_service.create_memory(memory_create)

            response = SuccessResponse(
                message="Memory saved successfully",
                data={
                    "memory_id": memory.id,
                    "project": memory.project,
                    "importance": memory.importance,
                    "memory_type": memory.memory_type.value
                }
            )

            return [types.TextContent(type="text", text=response.to_json())]

        except Exception as e:
            raise MCPMemoryError(f"Failed to save memory: {e}")

    async def _handle_search_memories(self, arguments: Dict[str, Any]) -> List[types.TextContent]:
        """Handle search memories tool call"""
        try:
            search_query = MemorySearchQuery(
                query=arguments["query"],
                project=arguments.get("project"),
                memory_types=[MemoryType(t) for t in arguments.get("memory_types", [])],
                min_importance=arguments.get("min_importance", 0.0),
                max_results=arguments.get("max_results", 20),
                similarity_threshold=arguments.get("similarity_threshold", 0.3),
                tags=arguments.get("tags", []),
                user_id=arguments.get("user_id"),
                session_id=arguments.get("session_id")
            )

            result = await memory_service.search_memories(search_query)

            # Convert memories to serializable format
            memories_data = []
            for memory in result.memories:
                memories_data.append({
                    "id": memory.id,
                    "content": memory.content,
                    "project": memory.project,
                    "memory_type": memory.memory_type.value,
                    "importance": memory.importance,
                    "similarity_score": memory.similarity_score,
                    "tags": memory.tags,
                    "created_at": memory.created_at.isoformat(),
                    "metadata": memory.metadata
                })

            response = SuccessResponse(
                message=f"Found {len(memories_data)} memories",
                data={
                    "memories": memories_data,
                    "total_count": result.total_count,
                    "search_time_ms": result.search_time_ms,
                    "query": result.query
                }
            )

            return [types.TextContent(type="text", text=response.to_json())]

        except Exception as e:
            raise MCPMemoryError(f"Failed to search memories: {e}")

    async def _handle_auto_save_memory(self, arguments: Dict[str, Any]) -> List[types.TextContent]:
        """Handle auto save memory tool call"""
        try:
            memory = await memory_service.auto_save_memory(
                content=arguments["content"],
                context=arguments.get("context", {}),
                project=arguments.get("project"),
                user_id=arguments.get("user_id"),
                session_id=arguments.get("session_id")
            )

            if memory:
                response = SuccessResponse(
                    message="Memory auto-saved successfully",
                    data={
                        "memory_id": memory.id,
                        "project": memory.project,
                        "importance": memory.importance,
                        "memory_type": memory.memory_type.value,
                        "triggered": True
                    }
                )
            else:
                response = SuccessResponse(
                    message="Content did not trigger memory save threshold",
                    data={"triggered": False}
                )

            return [types.TextContent(type="text", text=response.to_json())]

        except Exception as e:
            raise MCPMemoryError(f"Failed to auto-save memory: {e}")

    async def _handle_get_memory_context(self, arguments: Dict[str, Any]) -> List[types.TextContent]:
        """Handle get memory context tool call"""
        try:
            context_query = MemoryContext(
                project=arguments["project"],
                types=[MemoryType(t) for t in arguments["types"]],
                limit=arguments.get("limit", 50),
                min_importance=arguments.get("min_importance", 0.0),
                user_id=arguments.get("user_id"),
                session_id=arguments.get("session_id")
            )

            result = await memory_service.get_memory_context(context_query)

            # Convert context to serializable format
            context_data = {}
            for memory_type, memories in result.context.items():
                context_data[memory_type] = [
                    {
                        "id": memory.id,
                        "content": memory.content,
                        "importance": memory.importance,
                        "created_at": memory.created_at.isoformat(),
                        "tags": memory.tags
                    }
                    for memory in memories
                ]

            response = SuccessResponse(
                message=f"Retrieved context for project {result.project}",
                data={
                    "project": result.project,
                    "context": context_data,
                    "total_memories": result.total_memories,
                    "retrieval_time_ms": result.retrieval_time_ms
                }
            )

            return [types.TextContent(type="text", text=response.to_json())]

        except Exception as e:
            raise MCPMemoryError(f"Failed to get memory context: {e}")

    async def _handle_get_memory(self, arguments: Dict[str, Any]) -> List[types.TextContent]:
        """Handle get memory tool call"""
        try:
            memory = await memory_service.get_memory(arguments["memory_id"])

            if not memory:
                response = ErrorResponse(
                    error="Memory not found",
                    error_code="NOT_FOUND"
                )
            else:
                response = SuccessResponse(
                    message="Memory retrieved successfully",
                    data={
                        "id": memory.id,
                        "content": memory.content,
                        "project": memory.project,
                        "memory_type": memory.memory_type.value,
                        "importance": memory.importance,
                        "tags": memory.tags,
                        "metadata": memory.metadata,
                        "context": memory.context,
                        "created_at": memory.created_at.isoformat(),
                        "updated_at": memory.updated_at.isoformat(),
                        "access_count": memory.access_count
                    }
                )

            return [types.TextContent(type="text", text=response.to_json())]

        except Exception as e:
            raise MCPMemoryError(f"Failed to get memory: {e}")

    async def _handle_update_memory(self, arguments: Dict[str, Any]) -> List[types.TextContent]:
        """Handle update memory tool call"""
        try:
            updates = MemoryUpdate()

            if "content" in arguments:
                updates.content = arguments["content"]
            if "memory_type" in arguments:
                updates.memory_type = MemoryType(arguments["memory_type"])
            if "importance" in arguments:
                updates.importance = arguments["importance"]
            if "tags" in arguments:
                updates.tags = arguments["tags"]
            if "metadata" in arguments:
                updates.metadata = arguments["metadata"]
            if "context" in arguments:
                updates.context = arguments["context"]

            memory = await memory_service.update_memory(arguments["memory_id"], updates)

            if not memory:
                response = ErrorResponse(
                    error="Memory not found",
                    error_code="NOT_FOUND"
                )
            else:
                response = SuccessResponse(
                    message="Memory updated successfully",
                    data={
                        "memory_id": memory.id,
                        "updated_at": memory.updated_at.isoformat()
                    }
                )

            return [types.TextContent(type="text", text=response.to_json())]

        except Exception as e:
            raise MCPMemoryError(f"Failed to update memory: {e}")

    async def _handle_delete_memory(self, arguments: Dict[str, Any]) -> List[types.TextContent]:
        """Handle delete memory tool call"""
        try:
            deleted = await memory_service.delete_memory(arguments["memory_id"])

            if deleted:
                response = SuccessResponse(
                    message="Memory deleted successfully",
                    data={"memory_id": arguments["memory_id"]}
                )
            else:
                response = ErrorResponse(
                    error="Memory not found",
                    error_code="NOT_FOUND"
                )

            return [types.TextContent(type="text", text=response.to_json())]

        except Exception as e:
            raise MCPMemoryError(f"Failed to delete memory: {e}")

    async def _handle_health_check(self, arguments: Dict[str, Any]) -> List[types.TextContent]:
        """Handle health check tool call"""
        try:
            health = await self._get_system_health()

            response = SuccessResponse(
                message="Health check completed",
                data=health
            )

            return [types.TextContent(type="text", text=response.to_json())]

        except Exception as e:
            raise MCPMemoryError(f"Health check failed: {e}")

    async def _handle_get_metrics(self, arguments: Dict[str, Any]) -> List[types.TextContent]:
        """Handle get metrics tool call"""
        try:
            metrics = await memory_service.get_metrics()

            # Add server metrics
            uptime = time.time() - self.start_time
            metrics["server"] = {
                "uptime_seconds": uptime,
                "version": self.config.server.version,
                "environment": self.config.environment.value
            }

            response = SuccessResponse(
                message="Metrics retrieved successfully",
                data=metrics
            )

            return [types.TextContent(type="text", text=response.to_json())]

        except Exception as e:
            raise MCPMemoryError(f"Failed to get metrics: {e}")

    async def _get_system_health(self) -> Dict[str, Any]:
        """Get overall system health"""
        try:
            # Check all services
            memory_health = await memory_service.health_check()
            db_health = await database_service.health_check()
            embedding_health = await embedding_service.health_check()

            # Determine overall status
            all_healthy = all(
                health.get("status") == "healthy"
                for health in [memory_health, db_health, embedding_health]
            )

            uptime = time.time() - self.start_time

            return {
                "status": "healthy" if all_healthy else "unhealthy",
                "uptime_seconds": uptime,
                "version": self.config.server.version,
                "environment": self.config.environment.value,
                "services": {
                    "memory_service": memory_health,
                    "database_service": db_health,
                    "embedding_service": embedding_health
                }
            }

        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return {
                "status": "unhealthy",
                "error": str(e),
                "uptime_seconds": time.time() - self.start_time
            }

    async def run(self):
        """Run the MCP server"""
        try:
            async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
                # Initialize services
                await memory_service.initialize()

                # Setup initialization options
                init_options = InitializationOptions(
                    server_name=self.config.server.name,
                    server_version=self.config.server.version,
                    capabilities=self.server.get_capabilities(
                        notification_options=NotificationOptions(),
                        experimental_capabilities={},
                    )
                )

                logger.info(f"Starting MCP Server: {self.config.server.name} v{self.config.server.version}")
                logger.info(f"Environment: {self.config.environment.value}")

                # Run the server
                await self.server.run(
                    read_stream,
                    write_stream,
                    init_options
                )

        except Exception as e:
            logger.error(f"MCP Server error: {e}")
            raise
