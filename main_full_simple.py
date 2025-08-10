#!/usr/bin/env python3
"""
Full MCP Memory Server with all tools but using in-memory database
Perfect balance: All MCP tools visible + No external dependencies
"""

import asyncio
import json
import logging
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

# MCP imports
from mcp.server import Server, NotificationOptions
from mcp.server.models import InitializationOptions
import mcp.server.stdio
import mcp.types as types

# Simple in-memory storage
MEMORY_STORE = []
NEXT_ID = 1

class InMemoryMemoryService:
    """Full memory service using in-memory storage"""
    
    def __init__(self):
        self.memories = []
        self.next_id = 1
        print("✅ In-memory memory service initialized")
    
    async def save_memory(self, content: str, project: str = "default", 
                         memory_type: str = "conversation", importance: float = 0.5,
                         tags: List[str] = None, metadata: Dict = None,
                         user_id: str = None, session_id: str = None) -> Dict:
        """Save memory to in-memory store"""
        memory_id = f"mem_{self.next_id:03d}"
        self.next_id += 1
        
        memory = {
            'id': memory_id,
            'content': content,
            'project': project,
            'memory_type': memory_type,
            'importance': importance,
            'tags': tags or [],
            'metadata': metadata or {},
            'user_id': user_id,
            'session_id': session_id,
            'timestamp': datetime.now().isoformat(),
            'created_at': time.time()
        }
        
        self.memories.append(memory)
        print(f"💾 Saved memory: {memory_id} - {content[:50]}...")
        return memory
    
    async def search_memories(self, query: str, project: str = None,
                            memory_types: List[str] = None, min_importance: float = 0.0,
                            max_results: int = 20, similarity_threshold: float = 0.3,
                            tags: List[str] = None, user_id: str = None,
                            session_id: str = None) -> List[Dict]:
        """Search memories using simple text matching"""
        results = []
        query_lower = query.lower()
        
        for memory in self.memories:
            # Filter by project
            if project and memory.get('project') != project:
                continue
                
            # Filter by memory types
            if memory_types and memory.get('memory_type') not in memory_types:
                continue
                
            # Filter by importance
            if memory.get('importance', 0) < min_importance:
                continue
                
            # Filter by tags
            if tags and not any(tag in memory.get('tags', []) for tag in tags):
                continue
                
            # Simple text search
            content_lower = memory['content'].lower()
            if query_lower in content_lower:
                # Calculate simple similarity
                similarity = len(query_lower) / len(content_lower) if content_lower else 0
                if similarity >= similarity_threshold:
                    memory['similarity'] = similarity
                    results.append(memory)
        
        # Sort by similarity and limit results
        results.sort(key=lambda x: x.get('similarity', 0), reverse=True)
        results = results[:max_results]
        
        print(f"🔍 Found {len(results)} memories for query: '{query}'")
        return results
    
    async def get_memory_context(self, project: str = "default", limit: int = 10) -> Dict:
        """Get recent context for a project"""
        project_memories = [m for m in self.memories if m.get('project') == project]
        recent_memories = sorted(project_memories, key=lambda x: x['created_at'], reverse=True)[:limit]
        
        return {
            'project': project,
            'total_memories': len(project_memories),
            'recent_memories': recent_memories,
            'summary': f"Found {len(project_memories)} memories in project '{project}'"
        }
    
    async def delete_memory(self, memory_id: str, user_id: str = None) -> bool:
        """Delete a specific memory"""
        for i, memory in enumerate(self.memories):
            if memory['id'] == memory_id:
                if user_id and memory.get('user_id') != user_id:
                    return False  # User can only delete their own memories
                del self.memories[i]
                print(f"🗑️ Deleted memory: {memory_id}")
                return True
        return False

# Initialize services
memory_service = InMemoryMemoryService()

def create_mcp_server():
    """Create MCP server with all tools"""
    server = Server("mcp-memory-server-full")
    
    @server.list_tools()
    async def handle_list_tools() -> List[types.Tool]:
        """List all available MCP tools"""
        return [
            types.Tool(
                name="save_memory",
                description="💾 Save important information to memory",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "content": {"type": "string", "description": "The information to remember"},
                        "project": {"type": "string", "description": "Project name", "default": "default"},
                        "memory_type": {"type": "string", "description": "Type of memory", "default": "conversation"},
                        "importance": {"type": "number", "description": "Importance level (0-1)", "default": 0.5},
                        "tags": {"type": "array", "items": {"type": "string"}, "description": "Tags for categorization", "default": []},
                        "metadata": {"type": "object", "description": "Additional metadata", "default": {}},
                        "user_id": {"type": "string", "description": "User identifier"},
                        "session_id": {"type": "string", "description": "Session identifier"}
                    },
                    "required": ["content"]
                }
            ),
            types.Tool(
                name="search_memories",
                description="🔍 Search through saved memories",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "query": {"type": "string", "description": "What to search for"},
                        "project": {"type": "string", "description": "Project to search in"},
                        "memory_types": {"type": "array", "items": {"type": "string"}, "description": "Types of memories to search", "default": []},
                        "min_importance": {"type": "number", "description": "Minimum importance level", "default": 0.0},
                        "max_results": {"type": "integer", "description": "Maximum number of results", "default": 20},
                        "similarity_threshold": {"type": "number", "description": "Similarity threshold", "default": 0.3},
                        "tags": {"type": "array", "items": {"type": "string"}, "description": "Filter by tags", "default": []},
                        "user_id": {"type": "string", "description": "User identifier"},
                        "session_id": {"type": "string", "description": "Session identifier"}
                    },
                    "required": ["query"]
                }
            ),
            types.Tool(
                name="get_memory_context",
                description="📋 Get recent memory context for a project",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "project": {"type": "string", "description": "Project name", "default": "default"},
                        "limit": {"type": "integer", "description": "Number of recent memories", "default": 10},
                        "user_id": {"type": "string", "description": "User identifier"},
                        "session_id": {"type": "string", "description": "Session identifier"}
                    },
                    "required": []
                }
            ),
            types.Tool(
                name="delete_memory",
                description="🗑️ Delete a specific memory",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "memory_id": {"type": "string", "description": "ID of memory to delete"},
                        "user_id": {"type": "string", "description": "User identifier"}
                    },
                    "required": ["memory_id"]
                }
            )
        ]
    
    @server.call_tool()
    async def handle_call_tool(name: str, arguments: Dict[str, Any]) -> List[types.TextContent]:
        """Handle tool calls"""
        try:
            if name == "save_memory":
                result = await memory_service.save_memory(**arguments)
                return [types.TextContent(
                    type="text",
                    text=f"✅ Memory saved successfully!\n\n**ID:** {result['id']}\n**Content:** {result['content']}\n**Project:** {result['project']}\n**Type:** {result['memory_type']}\n**Importance:** {result['importance']}"
                )]
            
            elif name == "search_memories":
                results = await memory_service.search_memories(**arguments)
                if not results:
                    return [types.TextContent(
                        type="text",
                        text=f"🔍 No memories found for query: '{arguments['query']}'"
                    )]
                
                text = f"🔍 Found {len(results)} memories for: '{arguments['query']}'\n\n"
                for i, memory in enumerate(results, 1):
                    similarity = memory.get('similarity', 0)
                    text += f"**{i}. {memory['id']}** (similarity: {similarity:.2f})\n"
                    text += f"   📅 {memory['timestamp']}\n"
                    text += f"   📝 {memory['content']}\n"
                    text += f"   🏷️ Project: {memory['project']} | Type: {memory['memory_type']}\n\n"
                
                return [types.TextContent(type="text", text=text)]
            
            elif name == "get_memory_context":
                context = await memory_service.get_memory_context(**arguments)
                text = f"📋 **Memory Context for Project: {context['project']}**\n\n"
                text += f"Total memories: {context['total_memories']}\n\n"
                
                if context['recent_memories']:
                    text += "**Recent Memories:**\n"
                    for memory in context['recent_memories']:
                        text += f"• **{memory['id']}**: {memory['content'][:100]}...\n"
                else:
                    text += "No recent memories found.\n"
                
                return [types.TextContent(type="text", text=text)]
            
            elif name == "delete_memory":
                success = await memory_service.delete_memory(**arguments)
                if success:
                    return [types.TextContent(
                        type="text",
                        text=f"✅ Memory {arguments['memory_id']} deleted successfully!"
                    )]
                else:
                    return [types.TextContent(
                        type="text",
                        text=f"❌ Failed to delete memory {arguments['memory_id']} (not found or no permission)"
                    )]
            
            else:
                return [types.TextContent(
                    type="text",
                    text=f"❌ Unknown tool: {name}"
                )]
                
        except Exception as e:
            return [types.TextContent(
                type="text",
                text=f"❌ Error executing {name}: {str(e)}"
            )]
    
    return server

async def main():
    """Main entry point"""
    print("🚀 Starting Full MCP Memory Server (In-Memory)")
    print("=" * 50)
    print("✅ All MCP tools available")
    print("✅ No external dependencies required")
    print("✅ Ready for Cursor integration")
    print("=" * 50)
    
    # Create and run server
    server = create_mcp_server()
    
    # Run stdio server
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="mcp-memory-server-full",
                server_version="2.0.0",
                capabilities=server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={},
                ),
            ),
        )

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Server shutdown gracefully")
    except Exception as e:
        print(f"❌ Server error: {e}")
        sys.exit(1)
