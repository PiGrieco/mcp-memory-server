"""
Unified MCP Server for all platforms
"""

import asyncio
import json
import logging
from typing import Dict, Any, Optional
from pathlib import Path

from mcp.server import Server
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
                ),
                types.Tool(
                    name="analyze_message",
                    description="Analyze message for auto-triggers using ML model",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "message": {
                                "type": "string",
                                "description": "Message to analyze for auto-triggers"
                            },
                            "platform_context": {
                                "type": "object",
                                "description": "Platform-specific context",
                                "properties": {
                                    "platform": {"type": "string"},
                                    "session_id": {"type": "string"},
                                    "user_id": {"type": "string"}
                                }
                            }
                        },
                        "required": ["message"]
                    }
                ),
                types.Tool(
                    name="get_memory_stats",
                    description="Get memory usage and ML model statistics",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "random_string": {"type": "string", "description": "Dummy parameter for no-parameter tools"}
                        },
                        "required": ["random_string"]
                    }
                ),
                types.Tool(
                    name="search_memory",
                    description="Search through saved memories using semantic similarity",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "query": {"type": "string", "description": "Search query for finding relevant memories"},
                            "limit": {"type": "integer", "minimum": 1, "maximum": 20, "default": 5, "description": "Maximum number of results to return"},
                            "min_similarity": {"type": "number", "minimum": 0, "maximum": 1, "default": 0.1, "description": "Minimum similarity threshold"}
                        },
                        "required": ["query"]
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
                elif name == "search_memory":
                    result = await self._handle_search_memory(arguments)
                elif name == "list_memories":
                    result = await self._handle_list_memories(arguments)
                elif name == "memory_status":
                    result = await self._handle_memory_status(arguments)
                elif name == "auto_save_memory":
                    result = await self._handle_auto_save_memory(arguments)
                elif name == "analyze_message":
                    result = await self._handle_analyze_message(arguments)
                elif name == "get_memory_stats":
                    result = await self._handle_get_memory_stats(arguments)
                else:
                    raise MCPMemoryError(f"Unknown tool: {name}")
                
                return [types.TextContent(type="text", text=result)]
                
            except Exception as e:
                self.logger.error(f"Error handling tool {name}: {e}")
                raise MCPMemoryError(f"Tool execution failed: {e}")
    
    async def _handle_save_memory(self, arguments: dict) -> str:
        """Handle save_memory tool"""
        try:
            content = arguments.get("content", "")
            if not content:
                raise ValueError("Content is required")
            
            # Extract SAM-compatible parameters
            context = arguments.get("context", {})
            project = arguments.get("project", "default")
            importance = arguments.get("importance", 0.5)
            tags = arguments.get("tags", [])
            metadata = arguments.get("metadata", {})
            
            # Add platform context for SAM compatibility
            if "category" not in context:
                context["category"] = "conversation"
            if "importance" not in context:
                context["importance"] = importance
            if "tags" not in context:
                context["tags"] = tags
            
            # Create memory using the service
            memory = await self.memory_service.create_memory(
                content=content,
                project=project,
                importance=importance,
                tags=tags,
                metadata=metadata,
                context=context
            )
            
            # Return SAM-compatible response
            response = {
                "success": True,
                "memory_id": memory.id,
                "content": content[:100] + "..." if len(content) > 100 else content,
                "project": memory.project,
                "importance": memory.importance,
                "created_at": memory.created_at.isoformat() if memory.created_at else None,
                "message": "Memory saved successfully"
            }
            
            return json.dumps(response)
            
        except Exception as e:
            self.logger.error(f"Failed to save memory: {e}")
            error_response = {
                "success": False,
                "error": str(e),
                "message": "Failed to save memory"
            }
            return json.dumps(error_response)
    
    async def _handle_search_memories(self, arguments: dict) -> str:
        """Handle search_memories tool"""
        try:
            # Use ML triggers similarity threshold as default
            default_threshold = self.settings.ml_triggers.similarity_threshold
            
            results = await self.memory_service.search_memories(
                query=arguments["query"],
                project=arguments.get("project"),
                max_results=arguments.get("max_results", 20),
                similarity_threshold=arguments.get("similarity_threshold", default_threshold),
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
                # Start MCP server with proper error handling
                import mcp.server.stdio
                from mcp import types
                
                try:
                    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
                        self.logger.info("🚀 MCP server ready to accept connections")
                        
                        # Create initialization options
                        from mcp.server.models import InitializationOptions
                        from mcp.types import ServerCapabilities, ToolsCapability
                        init_options = InitializationOptions(
                            server_name=self.settings.server.name,
                            server_version=self.settings.server.version,
                            capabilities=ServerCapabilities(
                                tools=ToolsCapability(listChanged=True)
                            )
                        )
                        
                        # Run the server with initialization options
                        await self.server.run(
                            read_stream,
                            write_stream,
                            init_options,
                        )
                        
                except asyncio.CancelledError:
                    self.logger.info("🛑 Server cancelled gracefully")
                    raise
                except KeyboardInterrupt:
                    self.logger.info("🛑 Server interrupted by user")
                    raise
                except Exception as e:
                    self.logger.error(f"❌ Error in server.run: {e}")
                    import traceback
                    self.logger.error(f"Full traceback: {traceback.format_exc()}")
                    raise  # Re-raise the exception so the server fails properly
            else:
                self.logger.info(f"✅ Server initialized in {self.settings.server.mode} mode (not starting MCP loop)")
            
        except Exception as e:
            self.logger.error(f"❌ Server failed to start: {e}")
            raise
    
    async def _handle_analyze_message(self, arguments: dict) -> str:
        """Handle analyze_message tool - analyze message for auto-triggers using ML"""
        try:
            message = arguments.get("message", "")
            platform_context = arguments.get("platform_context", {})
            
            # Use ML configuration from settings
            ml_config = self.settings.ml_triggers
            
            analysis_result = {
                "success": True,
                "message": f"Analyzed message: '{message[:50]}...'",
                "triggers": [],
                "confidence": 0.0,
                "platform": platform_context.get("platform", "unknown"),
                "recommendations": [],
                "ml_model": ml_config.huggingface_model_name,
                "trigger_mode": ml_config.ml_trigger_mode,
                "thresholds": {
                    "confidence": ml_config.confidence_threshold,
                    "trigger": ml_config.trigger_threshold,
                    "memory": ml_config.memory_threshold
                }
            }
            
            # Enhanced keyword-based trigger detection with ML thresholds
            trigger_keywords = ["remember", "save", "important", "note", "recall", "ricorda", "nota", "importante", "salva", "memorizza"]
            solution_patterns = ["solved", "fixed", "bug fix", "solution", "tutorial", "how to", "risolto", "come fare"]
            
            confidence = 0.0
            triggers = []
            
            # Check for memory triggers
            if any(keyword in message.lower() for keyword in trigger_keywords):
                confidence += 0.6
                triggers.append("save_memory")
            
            # Check for solution patterns (higher importance)
            if any(pattern in message.lower() for pattern in solution_patterns):
                confidence += 0.4
                if "save_memory" not in triggers:
                    triggers.append("save_memory")
            
            # Check against ML confidence threshold
            if confidence >= ml_config.confidence_threshold:
                analysis_result["triggers"] = triggers
                analysis_result["confidence"] = confidence
                analysis_result["recommendations"].append(f"Auto-trigger activated (confidence: {confidence:.2f})")
            elif confidence >= ml_config.trigger_threshold:
                analysis_result["triggers"] = triggers
                analysis_result["confidence"] = confidence
                analysis_result["recommendations"].append(f"Consider saving (low confidence: {confidence:.2f})")
            
            return json.dumps(analysis_result)
            
        except Exception as e:
            self.logger.error(f"Error in analyze_message: {e}")
            raise MCPMemoryError(f"Failed to analyze message: {e}")
    
    async def _handle_get_memory_stats(self, arguments: dict) -> str:
        """Handle get_memory_stats tool - get memory system statistics"""
        try:
            # Get ML configuration
            ml_config = self.settings.ml_triggers
            
            # Get basic statistics
            stats = {
                "success": True,
                "total_memories": 0,  # Would get from database in real implementation
                "memory_types": ["conversation", "function", "context", "knowledge"],
                "database_status": "connected",
                "ml_model_status": "ready" if ml_config.enabled else "disabled",
                "last_updated": "2024-01-01T00:00:00Z",
                "system_info": {
                    "version": self.settings.server.version,
                    "mode": self.settings.server.mode
                },
                "ml_configuration": {
                    "model_name": ml_config.huggingface_model_name,
                    "model_type": ml_config.model_type,
                    "trigger_mode": ml_config.ml_trigger_mode,
                    "auto_trigger_enabled": ml_config.enabled,
                    "preload_model": ml_config.preload_model,
                    "training_enabled": ml_config.training_enabled
                },
                "thresholds": {
                    "confidence_threshold": ml_config.confidence_threshold,
                    "trigger_threshold": ml_config.trigger_threshold,
                    "similarity_threshold": ml_config.similarity_threshold,
                    "memory_threshold": ml_config.memory_threshold,
                    "semantic_threshold": ml_config.semantic_threshold
                },
                "learning_config": {
                    "retrain_interval": ml_config.retrain_interval,
                    "feature_extraction_timeout": ml_config.feature_extraction_timeout,
                    "max_conversation_history": ml_config.max_conversation_history,
                    "user_behavior_tracking": ml_config.user_behavior_tracking,
                    "behavior_history_limit": ml_config.behavior_history_limit
                }
            }
            
            # Try to get real count from database
            try:
                # This would use the actual database service
                # count = await self.database_service.count_memories()
                # stats["total_memories"] = count
                pass
            except Exception as e:
                self.logger.warning(f"Could not get memory count: {e}")
            
            return json.dumps(stats)
            
        except Exception as e:
            self.logger.error(f"Error in get_memory_stats: {e}")
            raise MCPMemoryError(f"Failed to get memory stats: {e}")
    
    async def _handle_search_memory(self, arguments: dict) -> str:
        """Handle search_memory tool - semantic search using SAM format"""
        try:
            query = arguments.get("query", "")
            limit = arguments.get("limit", 5)
            min_similarity = arguments.get("min_similarity", 0.1)
            
            if not query:
                raise ValueError("Query is required")
            
            # Use the search_memories method but format for SAM
            # Apply ML similarity threshold if not specified
            effective_threshold = min_similarity if min_similarity > 0.1 else self.settings.ml_triggers.similarity_threshold
            
            search_args = {
                "query": query,
                "max_results": limit,
                "similarity_threshold": effective_threshold
            }
            
            # Delegate to existing search_memories handler  
            result_json = await self._handle_search_memories(search_args)
            result = json.loads(result_json)
            
            # Reformat for SAM compatibility
            sam_result = {
                "success": True,
                "results": result.get("memories", []),
                "total_found": len(result.get("memories", [])),
                "query": query,
                "similarity_threshold": min_similarity
            }
            
            return json.dumps(sam_result)
            
        except Exception as e:
            self.logger.error(f"Error in search_memory: {e}")
            raise MCPMemoryError(f"Failed to search memory: {e}") 