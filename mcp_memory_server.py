#!/usr/bin/env python3
"""
MCP Memory Server for Cursor IDE
Production-ready memory management with intelligent storage and retrieval
"""

import json
import sys
import os
import asyncio
import logging
import traceback
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional

# Load environment variables first
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# Setup comprehensive logging system
def setup_logging():
    """Setup professional logging system for MCP Memory Server"""
    # Create logs directory
    logs_dir = Path("logs")
    logs_dir.mkdir(exist_ok=True)

    # Create log filename with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = logs_dir / f"mcp_memory_server_{timestamp}.log"

    # Configure logging format
    log_format = (
        "%(asctime)s | %(levelname)-8s | %(name)-20s | "
        "%(funcName)-15s:%(lineno)-4d | %(message)s"
    )

    # Configure root logger
    logging.basicConfig(
        level=logging.DEBUG,
        format=log_format,
        handlers=[
            # File handler for all logs
            logging.FileHandler(log_file, encoding='utf-8'),
            # Console handler for errors only
            logging.StreamHandler(sys.stderr)
        ]
    )

    # Set console handler to only show errors
    console_handler = logging.getLogger().handlers[1]
    console_handler.setLevel(logging.ERROR)

    # Create logger for this module
    logger = logging.getLogger("mcp_memory_server")
    logger.info("=" * 80)
    logger.info("MCP Memory Server Starting")
    logger.info(f"Log file: {log_file}")
    logger.info(f"Python version: {sys.version}")
    logger.info(f"Working directory: {os.getcwd()}")
    logger.info("=" * 80)

    return logger

# Initialize logging
logger = setup_logging()

# Environment-based configuration
PROJECT_NAME = os.getenv("PROJECT_NAME", "default")
DATABASE_NAME = os.getenv("DATABASE_NAME", "mcp_memory")

def initialize_full_memory_server():
    """Initialize the full memory server with environment variables"""
    try:
        # Set environment variables for production
        os.environ.setdefault("ENVIRONMENT", "production")
        os.environ.setdefault("MONGODB_URI", "mongodb://localhost:27017")
        os.environ.setdefault("MONGODB_DATABASE", DATABASE_NAME)
        os.environ.setdefault("MONGODB_COLLECTION", "memories")
        os.environ.setdefault("EMBEDDING_MODEL", "all-MiniLM-L6-v2")

        # Add src to path
        current_dir = Path(__file__).parent
        src_path = current_dir / "src"
        if src_path.exists():
            sys.path.insert(0, str(src_path))

        # Try to import
        from src.core.mcp_server import MCPServer
        server = MCPServer()
        return server, True
    except Exception as e:
        print(f"Full server initialization failed: {e}", file=sys.stderr)
        return None, False

async def async_main():
    # Initialize full server (required)
    full_server, has_full_server = initialize_full_memory_server()
    if not has_full_server:
        print("❌ CRITICAL ERROR: Full server initialization failed. Cannot continue.", file=sys.stderr)
        sys.exit(1)
    print(f"✅ Full server initialized successfully", file=sys.stderr)

    # Initialize memory service if using full server
    if has_full_server:
        try:
            from src.services.memory_service import memory_service
            print("Initializing memory service...", file=sys.stderr)
            await memory_service.initialize()
            print("Memory service initialized successfully", file=sys.stderr)
        except Exception as e:
            print(f"Failed to initialize memory service: {e}", file=sys.stderr)
            has_full_server = False

    try:
        logger.info("📡 Starting MCP message processing loop")
        for line in sys.stdin:
            try:
                request = json.loads(line.strip())
                method = request.get("method")
                request_id = request.get("id")

                logger.debug(f"📨 Received MCP request: {method} (ID: {request_id})")

                if method == "initialize":
                    logger.info(f"🚀 INITIALIZE request received")
                    logger.info(f"   Request ID: {request_id}")
                    logger.info(f"   Full server available: {has_full_server}")
                    response = {
                        "jsonrpc": "2.0",
                        "id": request_id,
                        "result": {
                            "protocolVersion": "2024-11-05",
                            "capabilities": {
                                "tools": {},
                                "resources": {},
                                "prompts": {}
                            },
                            "serverInfo": {
                                "name": "memory-server",
                                "version": "1.0.0",
                                "description": "Memory server for Cursor IDE" + (" (Full)" if has_full_server else " (Simple)")
                            }
                        }
                    }
                    
                elif method == "tools/list":
                    response = {
                        "jsonrpc": "2.0",
                        "id": request_id,
                        "result": {
                            "tools": [
                                {
                                    "name": "save_memory",
                                    "description": "Save important information to memory",
                                    "inputSchema": {
                                        "type": "object",
                                        "properties": {
                                            "content": {
                                                "type": "string",
                                                "description": "Information to save"
                                            },
                                            "project": {
                                                "type": "string",
                                                "description": "Project name",
                                                "default": "default"
                                            },
                                            "importance": {
                                                "type": "number",
                                                "description": "Importance (0.0-1.0)",
                                                "default": 0.7
                                            }
                                        },
                                        "required": ["content"]
                                    }
                                },
                                {
                                    "name": "search_memories",
                                    "description": "Search for relevant memories",
                                    "inputSchema": {
                                        "type": "object",
                                        "properties": {
                                            "query": {
                                                "type": "string",
                                                "description": "Search query"
                                            },
                                            "max_results": {
                                                "type": "integer",
                                                "description": "Max results",
                                                "default": 5
                                            }
                                        },
                                        "required": ["query"]
                                    }
                                },
                                {
                                    "name": "list_memories",
                                    "description": "List all saved memories",
                                    "inputSchema": {
                                        "type": "object",
                                        "properties": {},
                                        "additionalProperties": False
                                    }
                                },
                                {
                                    "name": "memory_status",
                                    "description": "Check memory system status",
                                    "inputSchema": {
                                        "type": "object",
                                        "properties": {},
                                        "additionalProperties": False
                                    }
                                }
                            ]
                        }
                    }
                    
                elif method == "prompts/list":
                    response = {
                        "jsonrpc": "2.0",
                        "id": request_id,
                        "result": {
                            "prompts": []
                        }
                    }
                    
                elif method == "tools/call":
                    params = request.get("params", {})
                    tool_name = params.get("name")
                    arguments = params.get("arguments", {})

                    # Log tool call start
                    logger.info(f"🔧 MCP TOOL CALL START")
                    logger.info(f"   Tool: {tool_name}")
                    logger.info(f"   Arguments: {json.dumps(arguments, indent=2)}")
                    logger.info(f"   Request ID: {request_id}")
                    logger.info(f"   Full Server Mode: {has_full_server}")

                    start_time = datetime.now()
                    
                    if tool_name == "save_memory":
                        content = arguments.get("content", "")
                        project = arguments.get("project", PROJECT_NAME)
                        importance = arguments.get("importance", 0.7)

                        logger.info(f"💾 SAVE_MEMORY Processing")
                        logger.info(f"   Content length: {len(content)} chars")
                        logger.info(f"   Content preview: {content[:100]}{'...' if len(content) > 100 else ''}")
                        logger.info(f"   Project: {project}")
                        logger.info(f"   Importance: {importance}")

                        try:
                            logger.info("   Using FULL SERVER mode")
                            # Use full server (required)
                            result = await full_server._handle_save_memory(arguments)
                            result_text = result[0].text if result else "Memory saved with full server"
                            logger.info(f"   ✅ Full server SUCCESS")
                            logger.info(f"   Result: {result_text[:200]}{'...' if len(result_text) > 200 else ''}")
                        except Exception as e:
                            # No fallback - full server is required
                            logger.error(f"   ❌ Full server FAILED: {str(e)}")
                            logger.error(f"   Traceback: {traceback.format_exc()}")
                            result_text = f"❌ Error saving memory: {str(e)}"
                        
                    elif tool_name == "search_memories":
                        query = arguments.get("query", "")
                        max_results = arguments.get("max_results", 5)
                        similarity_threshold = arguments.get("similarity_threshold", 0.3)
                        project = arguments.get("project", PROJECT_NAME)

                        logger.info(f"🔍 SEARCH_MEMORIES Processing")
                        logger.info(f"   Query: '{query}'")
                        logger.info(f"   Max results: {max_results}")
                        logger.info(f"   Similarity threshold: {similarity_threshold}")
                        logger.info(f"   Project filter: {project}")

                        try:
                            logger.info("   Using FULL SERVER mode")
                            # Use full server (required)
                            result = await full_server._handle_search_memories(arguments)
                            result_text = result[0].text if result else "Search completed with full server"
                            logger.info(f"   ✅ Full server SUCCESS")
                            logger.info(f"   Result: {result_text[:300]}{'...' if len(result_text) > 300 else ''}")
                        except Exception as e:
                            # No fallback - full server is required
                            logger.error(f"   ❌ Full server FAILED: {str(e)}")
                            logger.error(f"   Traceback: {traceback.format_exc()}")
                            result_text = f"❌ Error searching memories: {str(e)}"
                        
                    elif tool_name == "list_memories":
                        logger.info(f"📚 LIST_MEMORIES Processing")

                        try:
                            logger.info("   Using FULL SERVER mode")
                            # Use full server to list memories
                            from src.services.database_service import database_service

                            # Get all memories directly from database
                            memories = await database_service.get_project_memories(
                                project=PROJECT_NAME,  # Use environment project name
                                limit=1000  # Increased limit to show all memories
                            )

                            logger.info(f"   Retrieved {len(memories)} memories from database")

                            if memories:
                                memories_text = []
                                embeddings_count = 0
                                for memory in memories:
                                    content_preview = memory.content[:100] + "..." if len(memory.content) > 100 else memory.content
                                    has_embedding = "✅" if memory.embedding else "❌"
                                    if memory.embedding:
                                        embeddings_count += 1
                                    embedding_info = f" (embedding: {has_embedding})"
                                    memories_text.append(f"- {memory.id}: {content_preview}{embedding_info}")
                                result_text = f"📚 {len(memories)} memories stored:\n" + "\n".join(memories_text)
                                logger.info(f"   ✅ Full server SUCCESS: {len(memories)} memories, {embeddings_count} with embeddings")
                            else:
                                result_text = "📚 No memories stored yet"
                                logger.info("   ✅ Full server SUCCESS: No memories found")
                        except Exception as e:
                            result_text = f"📚 Error listing memories: {str(e)}"
                            logger.error(f"   ❌ Full server FAILED: {str(e)}")
                            logger.error(f"   Traceback: {traceback.format_exc()}")
                        
                    elif tool_name == "memory_status":
                        logger.info(f"🧠 MEMORY_STATUS Processing")
                        try:
                            from src.services.database_service import database_service
                            memory_count = await database_service.get_memory_count(project=PROJECT_NAME)
                            result_text = f"🧠 Memory System Status:\n- Mode: Full Server\n- Project: {PROJECT_NAME}\n- Database: {DATABASE_NAME}\n- Memories stored: {memory_count}\n- Working directory: {os.getcwd()}"
                        except Exception as e:
                            result_text = f"🧠 Memory System Status:\n- Mode: Full Server\n- Project: {PROJECT_NAME}\n- Database: {DATABASE_NAME}\n- Error getting count: {str(e)}\n- Working directory: {os.getcwd()}"
                        logger.info(f"   ✅ Status retrieved successfully")

                    else:
                        logger.warning(f"❓ UNKNOWN TOOL: {tool_name}")
                        result_text = f"Unknown tool: {tool_name}"

                    # Calculate execution time
                    end_time = datetime.now()
                    execution_time = (end_time - start_time).total_seconds() * 1000  # ms

                    # Log completion
                    logger.info(f"🏁 MCP TOOL CALL COMPLETE")
                    logger.info(f"   Tool: {tool_name}")
                    logger.info(f"   Execution time: {execution_time:.2f}ms")
                    logger.info(f"   Response length: {len(result_text)} chars")
                    logger.info(f"   Response preview: {result_text[:150]}{'...' if len(result_text) > 150 else ''}")

                    response = {
                        "jsonrpc": "2.0",
                        "id": request_id,
                        "result": {
                            "content": [
                                {
                                    "type": "text",
                                    "text": result_text
                                }
                            ]
                        }
                    }
                    
                elif method.startswith("notifications/"):
                    # Handle notifications (Cursor sends these)
                    if request_id is not None:
                        response = {
                            "jsonrpc": "2.0",
                            "id": request_id,
                            "result": {}
                        }
                    else:
                        # Notification without ID - no response needed
                        response = None
                        
                else:
                    response = {
                        "jsonrpc": "2.0",
                        "id": request_id,
                        "error": {
                            "code": -32601,
                            "message": f"Method not found: {method}"
                        }
                    }
                
                # Send response only if we have one
                if response is not None:
                    logger.debug(f"📤 Sending response for {method} (ID: {request_id})")
                    logger.debug(f"   Response size: {len(json.dumps(response))} bytes")
                    print(json.dumps(response), flush=True)
                else:
                    logger.debug(f"📭 No response needed for {method}")
                    
            except Exception as e:
                logger.error(f"💥 REQUEST PROCESSING ERROR")
                logger.error(f"   Error: {str(e)}")
                logger.error(f"   Request: {request if 'request' in locals() else 'Unknown'}")
                logger.error(f"   Traceback: {traceback.format_exc()}")

                error_response = {
                    "jsonrpc": "2.0",
                    "id": request.get("id") if 'request' in locals() else None,
                    "error": {
                        "code": -32603,
                        "message": f"Internal error: {str(e)}"
                    }
                }
                print(json.dumps(error_response), flush=True)

    except KeyboardInterrupt:
        logger.info("🛑 Server shutdown requested (Ctrl+C)")
        # Handle Ctrl+C gracefully
        pass
    except BrokenPipeError:
        logger.info("🔌 Client disconnected (broken pipe)")
        # Handle broken pipe when Cursor disconnects
        pass
    except Exception as e:
        logger.critical(f"💀 FATAL SERVER ERROR")
        logger.critical(f"   Error: {str(e)}")
        logger.critical(f"   Traceback: {traceback.format_exc()}")

        # Handle any other errors
        error_response = {
            "jsonrpc": "2.0",
            "id": None,
            "error": {"code": -32603, "message": f"Fatal error: {str(e)}"}
        }
        print(json.dumps(error_response), flush=True)

    finally:
        logger.info("🏁 MCP Memory Server shutting down")
        logger.info("=" * 80)

def main():
    """Wrapper to run async main"""
    try:
        # Note: logging is initialized in setup_logging() which is called at module level
        asyncio.run(async_main())
    except Exception as e:
        print(f"FATAL: Failed to start MCP Memory Server: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
