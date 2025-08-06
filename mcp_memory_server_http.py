#!/usr/bin/env python3
"""
MCP Memory Server - HTTP/Network Mode
Serves the MCP Memory Server over HTTP for remote access
"""

import asyncio
import json
import logging
import os
import sys
from datetime import datetime
from typing import Any, Dict

# Add the src directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from aiohttp import web, web_request
from aiohttp.web import middleware
import aiohttp_cors

# Import the original MCP server functionality
from mcp_memory_server import async_main as mcp_main, initialize_full_memory_server

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Global MCP server instance
mcp_server = None
full_server = None

async def initialize_mcp_server():
    """Initialize the MCP server for HTTP mode"""
    global mcp_server, full_server
    
    try:
        # Initialize full server
        full_server, has_full_server = initialize_full_memory_server()
        if not has_full_server:
            raise Exception("Failed to initialize full server")
        
        logger.info("✅ MCP Memory Server initialized for HTTP mode")
        return True
    except Exception as e:
        logger.error(f"❌ Failed to initialize MCP server: {e}")
        return False

async def handle_mcp_request(request_data: Dict[str, Any]) -> Dict[str, Any]:
    """Handle MCP requests and return responses"""
    global full_server
    
    try:
        method = request_data.get("method")
        params = request_data.get("params", {})
        request_id = request_data.get("id")
        
        logger.info(f"🔄 Processing MCP request: {method}")
        
        if method == "initialize":
            return {
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
                        "name": "memory-server-http",
                        "version": "1.0.0",
                        "description": "Memory server for remote access (HTTP)"
                    }
                }
            }
        
        elif method == "tools/list":
            return {
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
                                    "content": {"type": "string"},
                                    "project": {"type": "string"},
                                    "importance": {"type": "number"}
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
                                    "query": {"type": "string"},
                                    "max_results": {"type": "number"},
                                    "similarity_threshold": {"type": "number"}
                                },
                                "required": ["query"]
                            }
                        },
                        {
                            "name": "list_memories",
                            "description": "List all saved memories",
                            "inputSchema": {"type": "object", "properties": {}}
                        },
                        {
                            "name": "memory_status",
                            "description": "Check memory system status",
                            "inputSchema": {"type": "object", "properties": {}}
                        }
                    ]
                }
            }
        
        elif method == "tools/call":
            tool_name = params.get("name")
            arguments = params.get("arguments", {})
            
            # Handle tool calls using the full server
            if tool_name == "save_memory":
                result = await full_server._handle_save_memory(arguments)
            elif tool_name == "search_memories":
                result = await full_server._handle_search_memories(arguments)
            elif tool_name == "list_memories":
                # Use the same method as the working search_memories with a broad query
                result = await full_server._handle_search_memories({
                    "query": "*",
                    "max_results": arguments.get("limit", 50),
                    "similarity_threshold": 0.0
                })
            elif tool_name == "memory_status":
                # Get memory count using the working search method
                try:
                    # Get memory count by searching with wildcard query
                    count_result = await full_server._handle_search_memories({
                        "query": "*",
                        "max_results": 1000,
                        "similarity_threshold": 0.0
                    })

                    # Parse the result to get memory count
                    if count_result and len(count_result) > 0:
                        result_text = count_result[0].text
                        import json
                        result_data = json.loads(result_text)
                        total_memories = len(result_data.get("data", {}).get("memories", []))
                    else:
                        total_memories = 0

                    # Create status response
                    default_project = os.getenv("PROJECT_NAME", os.getenv("DEFAULT_PROJECT", "default"))
                    status = {
                        "success": True,
                        "message": "Memory system status",
                        "data": {
                            "total_memories": total_memories,
                            "project": default_project,
                            "database_connected": True,
                            "embedding_model": os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2"),
                            "server_mode": os.getenv("ENVIRONMENT", "production")
                        }
                    }
                    result = [type('Result', (), {'text': str(status)})()]
                except Exception as e:
                    status = {
                        "success": False,
                        "message": f"Status check failed: {str(e)}",
                        "data": {
                            "total_memories": 0,
                            "database_connected": False
                        }
                    }
                    result = [type('Result', (), {'text': str(status)})()]
            else:
                raise Exception(f"Unknown tool: {tool_name}")
            
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "result": {
                    "content": result[0].text if result else "Operation completed"
                }
            }
        
        else:
            raise Exception(f"Unknown method: {method}")
    
    except Exception as e:
        logger.error(f"❌ Error handling MCP request: {e}")
        return {
            "jsonrpc": "2.0",
            "id": request_data.get("id"),
            "error": {
                "code": -32603,
                "message": str(e)
            }
        }

async def mcp_handler(request):
    """HTTP handler for MCP requests"""
    try:
        # Parse JSON request
        request_data = await request.json()
        logger.info(f"📥 Received request: {request_data.get('method', 'unknown')}")
        
        # Process MCP request
        response = await handle_mcp_request(request_data)
        
        # Return JSON response
        return web.json_response(response)
    
    except Exception as e:
        logger.error(f"❌ HTTP handler error: {e}")
        return web.json_response({
            "jsonrpc": "2.0",
            "id": None,
            "error": {
                "code": -32700,
                "message": f"Parse error: {str(e)}"
            }
        }, status=400)

async def health_handler(request):
    """Health check endpoint"""
    return web.json_response({
        "status": "healthy",
        "service": "mcp-memory-server",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0"
    })

async def info_handler(request):
    """Server info endpoint"""
    return web.json_response({
        "name": "MCP Memory Server",
        "version": "1.0.0",
        "mode": "HTTP",
        "endpoints": {
            "mcp": "/mcp",
            "health": "/health",
            "info": "/info"
        },
        "project": os.getenv("PROJECT_NAME", os.getenv("DEFAULT_PROJECT", "default")),
        "database": os.getenv("DATABASE_NAME", "mcp_memory_production"),
        "environment": os.getenv("ENVIRONMENT", "production"),
        "embedding_model": os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")
    })

@middleware
async def cors_middleware(request, handler):
    """CORS middleware for cross-origin requests"""
    response = await handler(request)
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
    return response

async def create_app():
    """Create the HTTP application"""
    app = web.Application(middlewares=[cors_middleware])
    
    # Add routes
    app.router.add_post('/mcp', mcp_handler)
    app.router.add_get('/health', health_handler)
    app.router.add_get('/info', info_handler)
    app.router.add_options('/mcp', lambda r: web.Response())
    
    return app

async def main():
    """Main HTTP server function"""
    print("🌐 Starting MCP Memory Server - HTTP Mode")
    print("=" * 50)
    
    # Initialize MCP server
    if not await initialize_mcp_server():
        print("❌ Failed to initialize MCP server")
        sys.exit(1)
    
    # Create web application
    app = await create_app()
    
    # Start HTTP server
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "8000"))
    
    print(f"🚀 Starting HTTP server on {host}:{port}")
    print(f"📡 MCP endpoint: http://{host}:{port}/mcp")
    print(f"🏥 Health check: http://{host}:{port}/health")
    print(f"ℹ️  Server info: http://{host}:{port}/info")
    print("=" * 50)
    
    runner = web.AppRunner(app)
    await runner.setup()
    
    site = web.TCPSite(runner, host, port)
    await site.start()
    
    print("✅ MCP Memory Server is running!")
    print("Press Ctrl+C to stop")
    
    # Keep the server running
    try:
        await asyncio.Future()  # Run forever
    except KeyboardInterrupt:
        print("\n🛑 Shutting down server...")
        await runner.cleanup()

if __name__ == "__main__":
    asyncio.run(main())
