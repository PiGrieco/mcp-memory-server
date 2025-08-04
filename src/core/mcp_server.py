"""
MCP Server implementation for Memory Management
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

from ..config import config
from ..models import (
    MemoryCreate, MemoryUpdate, MemorySearchQuery, MemoryContext,
    MemoryType, MemoryImportance
)
from ..services import memory_service

logger = logging.getLogger(__name__)

class MCPServer:
    """MCP Server for memory management"""
    
    def __init__(self):
        self.server = Server(config.server.name)
        self.setup_handlers()
    
    def setup_handlers(self):
        """Setup MCP protocol handlers"""
        
        @self.server.list_tools()
        async def handle_list_tools() -> list[types.Tool]:
            """List available tools"""
            return [
                types.Tool(
                    name="save_memory",
                    description="Save a memory to the system",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "text": {
                                "type": "string",
                                "description": "Text content to memorize"
                            },
                            "type": {
                                "type": "string",
                                "enum": [t.value for t in MemoryType],
                                "description": "Type of memory"
                            },
                            "project": {
                                "type": "string",
                                "description": "Project identifier",
                                "default": "default"
                            },
                            "metadata": {
                                "type": "object",
                                "description": "Additional metadata",
                                "additionalProperties": True
                            },
                            "importance": {
                                "type": "number",
                                "minimum": 0.0,
                                "maximum": 1.0,
                                "description": "Importance score (0.0-1.0)",
                                "default": 0.5
                            }
                        },
                        "required": ["text", "type"]
                    }
                ),
                types.Tool(
                    name="search_memory",
                    description="Search for relevant memories using semantic similarity",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "query": {
                                "type": "string",
                                "description": "Search query"
                            },
                            "project": {
                                "type": "string",
                                "description": "Project to search in",
                                "default": "default"
                            },
                            "limit": {
                                "type": "integer",
                                "minimum": 1,
                                "maximum": 100,
                                "description": "Maximum number of results",
                                "default": 5
                            },
                            "type": {
                                "type": "string",
                                "enum": ["all"] + [t.value for t in MemoryType],
                                "description": "Filter by memory type",
                                "default": "all"
                            },
                            "min_importance": {
                                "type": "number",
                                "minimum": 0.0,
                                "maximum": 1.0,
                                "description": "Minimum importance threshold"
                            },
                            "min_similarity": {
                                "type": "number",
                                "minimum": 0.0,
                                "maximum": 1.0,
                                "description": "Minimum similarity threshold"
                            }
                        },
                        "required": ["query"]
                    }
                ),
                types.Tool(
                    name="get_context",
                    description="Get contextual memories for a project",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "project": {
                                "type": "string",
                                "description": "Project identifier",
                                "default": "default"
                            },
                            "types": {
                                "type": "array",
                                "items": {"type": "string", "enum": [t.value for t in MemoryType]},
                                "description": "Memory types to include",
                                "default": ["context", "knowledge", "decision"]
                            },
                            "limit": {
                                "type": "integer",
                                "minimum": 1,
                                "maximum": 100,
                                "description": "Maximum memories per type",
                                "default": 10
                            },
                            "min_importance": {
                                "type": "number",
                                "minimum": 0.0,
                                "maximum": 1.0,
                                "description": "Minimum importance threshold"
                            }
                        }
                    }
                ),
                types.Tool(
                    name="update_memory",
                    description="Update an existing memory",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "memory_id": {
                                "type": "string",
                                "description": "ID of the memory to update"
                            },
                            "updates": {
                                "type": "object",
                                "properties": {
                                    "text": {"type": "string"},
                                    "type": {"type": "string", "enum": [t.value for t in MemoryType]},
                                    "metadata": {"type": "object", "additionalProperties": True},
                                    "importance": {"type": "number", "minimum": 0.0, "maximum": 1.0}
                                },
                                "additionalProperties": False
                            }
                        },
                        "required": ["memory_id", "updates"]
                    }
                ),
                types.Tool(
                    name="delete_memory",
                    description="Delete a memory",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "memory_id": {
                                "type": "string",
                                "description": "ID of the memory to delete"
                            }
                        },
                        "required": ["memory_id"]
                    }
                ),
                types.Tool(
                    name="get_memory_stats",
                    description="Get statistics for a project",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "project": {
                                "type": "string",
                                "description": "Project identifier",
                                "default": "default"
                            }
                        }
                    }
                ),
                types.Tool(
                    name="health_check",
                    description="Check system health",
                    inputSchema={
                        "type": "object",
                        "properties": {},
                        "additionalProperties": False
                    }
                )
            ]
        
        @self.server.call_tool()
        async def handle_call_tool(
            name: str, arguments: Optional[Dict[str, Any]]
        ) -> list[types.TextContent]:
            """Handle tool calls"""
            
            if arguments is None:
                arguments = {}
            
            try:
                if name == "save_memory":
                    result = await self._save_memory(arguments)
                elif name == "search_memory":
                    result = await self._search_memory(arguments)
                elif name == "get_context":
                    result = await self._get_context(arguments)
                elif name == "update_memory":
                    result = await self._update_memory(arguments)
                elif name == "delete_memory":
                    result = await self._delete_memory(arguments)
                elif name == "get_memory_stats":
                    result = await self._get_memory_stats(arguments)
                elif name == "health_check":
                    result = await self._health_check(arguments)
                else:
                    raise ValueError(f"Unknown tool: {name}")
                
                return [types.TextContent(
                    type="text",
                    text=json.dumps(result, ensure_ascii=False, default=str)
                )]
                
            except Exception as e:
                logger.error(f"Error in tool {name}: {e}")
                error_result = {
                    "error": str(e),
                    "tool": name,
                    "arguments": arguments
                }
                return [types.TextContent(
                    type="text",
                    text=json.dumps(error_result, ensure_ascii=False)
                )]
        
        @self.server.list_resources()
        async def handle_list_resources() -> list[types.Resource]:
            """List available resources (projects)"""
            try:
                # Get all projects from database
                projects = await memory_service.database_service.collection.distinct("project")
                
                resources = []
                for project in projects:
                    # Get count for each project
                    count = await memory_service.database_service.collection.count_documents({"project": project})
                    
                    resources.append(
                        types.Resource(
                            uri=f"memory://project/{project}",
                            name=f"Project: {project}",
                            description=f"Contains {count} memories",
                            mimeType="application/json"
                        )
                    )
                
                return resources
                
            except Exception as e:
                logger.error(f"Error listing resources: {e}")
                return []
        
        @self.server.read_resource()
        async def handle_read_resource(uri: str) -> str:
            """Read a specific resource"""
            try:
                if uri.startswith("memory://project/"):
                    project = uri.replace("memory://project/", "")
                    
                    # Get memories for the project
                    memories = await memory_service.database_service.get_project_memories(
                        project=project,
                        limit=50
                    )
                    
                    # Convert to JSON-serializable format
                    memory_data = []
                    for memory in memories:
                        memory_dict = memory.dict()
                        memory_dict["id"] = str(memory.id)
                        memory_data.append(memory_dict)
                    
                    return json.dumps(memory_data, ensure_ascii=False, default=str)
                
                raise ValueError(f"Unknown resource URI: {uri}")
                
            except Exception as e:
                logger.error(f"Error reading resource {uri}: {e}")
                return json.dumps({"error": str(e)})
    
    async def _save_memory(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Save a memory"""
        memory_data = MemoryCreate(
            text=arguments["text"],
            type=MemoryType(arguments["type"]),
            project=arguments.get("project", "default"),
            metadata=arguments.get("metadata", {}),
            importance=arguments.get("importance", 0.5)
        )
        
        memory = await memory_service.create_memory(memory_data)
        
        return {
            "status": "success",
            "memory_id": memory.id,
            "message": f"Memory saved successfully"
        }
    
    async def _search_memory(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Search memories"""
        search_query = MemorySearchQuery(
            query=arguments["query"],
            project=arguments.get("project", "default"),
            limit=arguments.get("limit", 5),
            type=arguments.get("type", "all"),
            min_importance=arguments.get("min_importance"),
            min_similarity=arguments.get("min_similarity")
        )
        
        result = await memory_service.search_memories(search_query)
        
        return {
            "status": "success",
            "memories": [memory.dict() for memory in result.memories],
            "total_count": result.total_count,
            "search_time_ms": result.search_time_ms
        }
    
    async def _get_context(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Get context for a project"""
        context_query = MemoryContext(
            project=arguments.get("project", "default"),
            types=[MemoryType(t) for t in arguments.get("types", ["context", "knowledge", "decision"])],
            limit=arguments.get("limit", 10),
            min_importance=arguments.get("min_importance")
        )
        
        result = await memory_service.get_context(context_query)
        
        # Convert memories to dict format
        context_dict = {}
        for memory_type, memories in result.context.items():
            context_dict[memory_type] = [memory.dict() for memory in memories]
        
        return {
            "status": "success",
            "project": result.project,
            "context": context_dict,
            "total_memories": result.total_memories,
            "retrieval_time_ms": result.retrieval_time_ms
        }
    
    async def _update_memory(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Update a memory"""
        memory_id = arguments["memory_id"]
        updates_data = arguments["updates"]
        
        updates = MemoryUpdate(**updates_data)
        memory = await memory_service.update_memory(memory_id, updates)
        
        if memory:
            return {
                "status": "success",
                "memory_id": memory.id,
                "message": "Memory updated successfully"
            }
        else:
            return {
                "status": "error",
                "message": "Memory not found"
            }
    
    async def _delete_memory(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Delete a memory"""
        memory_id = arguments["memory_id"]
        deleted = await memory_service.delete_memory(memory_id)
        
        if deleted:
            return {
                "status": "success",
                "message": "Memory deleted successfully"
            }
        else:
            return {
                "status": "error",
                "message": "Memory not found"
            }
    
    async def _get_memory_stats(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Get memory statistics"""
        project = arguments.get("project", "default")
        stats = await memory_service.get_memory_stats(project)
        
        return {
            "status": "success",
            "stats": stats.dict()
        }
    
    async def _health_check(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Check system health"""
        health = await memory_service.health_check()
        
        return {
            "status": "success",
            "health": health
        }
    
    async def run(self):
        """Run the MCP server"""
        async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
            # Initialize memory service
            await memory_service.initialize()
            
            # Setup initialization options
            init_options = InitializationOptions(
                server_name=config.server.name,
                server_version=config.server.version,
                capabilities=self.server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={},
                )
            )
            
            logger.info(f"Starting MCP Server: {config.server.name} v{config.server.version}")
            
            # Run the server
            await self.server.run(
                read_stream,
                write_stream,
                init_options
            ) 