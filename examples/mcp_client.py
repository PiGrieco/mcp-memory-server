#!/usr/bin/env python3
"""
Example MCP Client for Memory Server
"""

import asyncio
import json
from typing import Any, Dict, List, Optional
from contextlib import asynccontextmanager

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

class MemoryClient:
    """Client for interacting with the Memory MCP Server"""
    
    def __init__(self, server_script_path: str = "main.py"):
        self.server_script_path = server_script_path
    
    @asynccontextmanager
    async def connect(self):
        """Context manager for server connection"""
        server_params = StdioServerParameters(
            command="python",
            args=[self.server_script_path],
            env=None
        )
        
        read_stream, write_stream = await stdio_client(server_params)
        client = ClientSession(read_stream, write_stream)
        await client.initialize()
        
        try:
            self._client = client
            yield self
        finally:
            await client.close()
    
    async def save_memory(self, text: str, memory_type: str = "conversation", 
                         metadata: Optional[Dict[str, Any]] = None, project: str = "default",
                         importance: float = 0.5):
        """Save a memory"""
        result = await self._client.call_tool(
            "save_memory",
            arguments={
                "text": text,
                "type": memory_type,
                "project": project,
                "metadata": metadata or {},
                "importance": importance
            }
        )
        return json.loads(result.content[0].text)
    
    async def search_memory(self, query: str, project: str = "default", 
                           limit: int = 5, memory_type: str = "all"):
        """Search for relevant memories"""
        result = await self._client.call_tool(
            "search_memory",
            arguments={
                "query": query,
                "project": project,
                "limit": limit,
                "type": memory_type
            }
        )
        return json.loads(result.content[0].text)
    
    async def get_context(self, project: str = "default", 
                         types: List[str] = None, limit: int = 10):
        """Get context for a project"""
        if types is None:
            types = ["context", "knowledge", "decision"]
        
        result = await self._client.call_tool(
            "get_context",
            arguments={
                "project": project,
                "types": types,
                "limit": limit
            }
        )
        return json.loads(result.content[0].text)
    
    async def get_memory_stats(self, project: str = "default"):
        """Get memory statistics"""
        result = await self._client.call_tool(
            "get_memory_stats",
            arguments={"project": project}
        )
        return json.loads(result.content[0].text)
    
    async def health_check(self):
        """Check system health"""
        result = await self._client.call_tool(
            "health_check",
            arguments={}
        )
        return json.loads(result.content[0].text)

async def demo():
    """Demonstration of the memory system"""
    print("🚀 MCP Memory Server Demo")
    print("=" * 50)
    
    async with MemoryClient().connect() as client:
        # Health check
        print("\n1. Health Check:")
        health = await client.health_check()
        print(f"   Status: {health['health']['status']}")
        
        # Save some memories
        print("\n2. Saving Memories:")
        memories_to_save = [
            {
                "text": "Python is excellent for machine learning and data science",
                "type": "knowledge",
                "metadata": {"topic": "programming", "language": "python"}
            },
            {
                "text": "Always use virtual environments for Python projects",
                "type": "knowledge", 
                "metadata": {"topic": "best_practices"}
            },
            {
                "text": "The user wants to build a memory system for AI agents",
                "type": "context",
                "metadata": {"project": "ai_memory"}
            }
        ]
        
        for mem in memories_to_save:
            result = await client.save_memory(**mem)
            print(f"   Saved: {mem['text'][:50]}... (ID: {result['memory_id']})")
        
        # Search memories
        print("\n3. Searching Memories:")
        search_results = await client.search_memory(
            query="Python programming best practices",
            limit=3
        )
        
        print(f"   Found {len(search_results['memories'])} relevant memories:")
        for i, memory in enumerate(search_results['memories'], 1):
            print(f"   {i}. {memory['text'][:60]}... (similarity: {memory.get('similarity', 0):.3f})")
        
        # Get context
        print("\n4. Getting Context:")
        context = await client.get_context(types=["knowledge", "context"])
        print(f"   Retrieved {context['total_memories']} contextual memories")
        
        # Get stats
        print("\n5. Memory Statistics:")
        stats = await client.get_memory_stats()
        print(f"   Total memories: {stats['stats']['total_memories']}")
        print(f"   Average importance: {stats['stats']['avg_importance']:.2f}")
        
        print("\n✅ Demo completed successfully!")

if __name__ == "__main__":
    asyncio.run(demo()) 