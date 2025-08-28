#!/usr/bin/env python3
"""
Simple MCP Memory Server per Cursor IDE - Con Tools MCP
Funziona in memoria senza database esterno
"""

import asyncio
import sys
from pathlib import Path
from typing import Dict, List
import time
from datetime import datetime

# MCP imports
from mcp import types, server
from mcp.server import Server
from mcp.server.models import InitializationOptions
import mcp.server.stdio

# Add src to path se presente
src_path = Path(__file__).parent / "src"
if src_path.exists():
    sys.path.insert(0, str(src_path))

# Simple in-memory storage
MEMORY_STORE = []
EMBEDDING_CACHE = {}

class InMemoryDatabase:
    """Simple in-memory database for testing"""
    
    def __init__(self):
        self.memories = []
        self.next_id = 1
    
    async def save_memory(self, content: str, importance: float = 0.5, 
                         memory_type: str = "conversation", metadata: Dict = None) -> Dict:
        """Save memory to in-memory store"""
        memory_id = f"mem_{self.next_id:03d}"
        self.next_id += 1
        
        memory = {
            'id': memory_id,
            'content': content,
            'importance': importance,
            'memory_type': memory_type,
            'metadata': metadata or {},
            'timestamp': datetime.now().isoformat(),
            'created_at': time.time()
        }
        
        self.memories.append(memory)
        return memory
    
    async def search_memories(self, query: str, limit: int = 5) -> List[Dict]:
        """Simple text-based search"""
        query_lower = query.lower()
        results = []
        
        for memory in self.memories:
            if query_lower in memory['content'].lower():
                # Simulate similarity score
                similarity = 0.5 + (query_lower.count(' ') * 0.1)
                memory_result = memory.copy()
                memory_result['similarity'] = min(similarity, 1.0)
                results.append(memory_result)
        
        # Sort by similarity and return top results
        results.sort(key=lambda x: x['similarity'], reverse=True)
        return results[:limit]

class AutoTriggerProcessor:
    """Simple auto-trigger system"""
    
    def __init__(self, db):
        self.db = db
        self.keywords = ['ricorda', 'nota', 'importante', 'salva', 'memorizza', 'remember', 'save', 'note']
        self.patterns = ['risolto', 'solved', 'fixed', 'bug fix', 'solution', 'tutorial']
    
    def analyze_for_auto_trigger(self, content: str) -> List[Dict]:
        """Analyze content for auto-trigger patterns"""
        actions = []
        content_lower = content.lower()
        
        # Check for save keywords
        for keyword in self.keywords:
            if keyword in content_lower:
                actions.append({
                    'type': 'save_memory',
                    'trigger': 'keyword',
                    'confidence': 0.8,
                    'reason': f'Keyword detected: {keyword}'
                })
                break
        
        # Check for solution patterns
        for pattern in self.patterns:
            if pattern in content_lower:
                actions.append({
                    'type': 'save_memory',
                    'trigger': 'pattern',
                    'confidence': 0.7,
                    'reason': f'Solution pattern detected: {pattern}'
                })
                break
        
        return actions

class SimpleCursorMCPServer:
    """Simple MCP Server for Cursor with proper tools"""
    
    def __init__(self):
        self.db = InMemoryDatabase()
        self.auto_trigger = AutoTriggerProcessor(self.db)
        self.server = Server("mcp-memory-cursor")
        self._setup_handlers()
        
        print("🎯 Simple Cursor MCP Server initialized")
        print("✅ Auto-trigger system enabled")
        print(f"✅ Keywords: {self.auto_trigger.keywords}")
        print(f"✅ Patterns: {self.auto_trigger.patterns}")
    
    def _setup_handlers(self):
        """Setup MCP handlers"""
        
        @self.server.list_tools()
        async def handle_list_tools() -> List[types.Tool]:
            """Return available tools"""
            return [
                types.Tool(
                    name="save_memory",
                    description="Save important information to memory with auto-trigger detection",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "content": {
                                "type": "string",
                                "description": "The content to save to memory"
                            },
                            "importance": {
                                "type": "number",
                                "description": "Importance level (0.0 to 1.0)",
                                "minimum": 0.0,
                                "maximum": 1.0,
                                "default": 0.5
                            },
                            "memory_type": {
                                "type": "string",
                                "description": "Type of memory",
                                "enum": ["conversation", "code", "solution", "note"],
                                "default": "conversation"
                            },
                            "metadata": {
                                "type": "object",
                                "description": "Additional metadata",
                                "default": {}
                            }
                        },
                        "required": ["content"]
                    }
                ),
                types.Tool(
                    name="search_memories",
                    description="Search for relevant memories using text similarity",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "query": {
                                "type": "string",
                                "description": "Search query"
                            },
                            "limit": {
                                "type": "integer",
                                "description": "Maximum number of results",
                                "minimum": 1,
                                "maximum": 20,
                                "default": 5
                            }
                        },
                        "required": ["query"]
                    }
                ),
                types.Tool(
                    name="analyze_auto_trigger",
                    description="Analyze text for automatic memory trigger patterns",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "text": {
                                "type": "string",
                                "description": "Text to analyze for auto-trigger patterns"
                            }
                        },
                        "required": ["text"]
                    }
                ),
                types.Tool(
                    name="list_memories",
                    description="List all saved memories",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "limit": {
                                "type": "integer",
                                "description": "Maximum number of memories to return",
                                "minimum": 1,
                                "maximum": 50,
                                "default": 10
                            }
                        }
                    }
                )
            ]
        
        @self.server.call_tool()
        async def handle_call_tool(name: str, arguments: dict) -> List[types.TextContent]:
            """Handle tool calls"""
            
            try:
                if name == "save_memory":
                    content = arguments.get("content", "")
                    importance = arguments.get("importance", 0.5)
                    memory_type = arguments.get("memory_type", "conversation")
                    metadata = arguments.get("metadata", {})
                    
                    # Auto-trigger analysis
                    triggers = self.auto_trigger.analyze_for_auto_trigger(content)
                    if triggers:
                        metadata["auto_triggered"] = True
                        metadata["triggers"] = triggers
                        importance = max(importance, 0.7)  # Boost importance for auto-triggered
                    
                    # Save memory
                    memory = await self.db.save_memory(content, importance, memory_type, metadata)
                    
                    result = {
                        "success": True,
                        "memory_id": memory["id"],
                        "content": content,
                        "importance": importance,
                        "auto_triggered": bool(triggers),
                        "triggers_detected": len(triggers)
                    }
                    
                    return [types.TextContent(
                        type="text",
                        text=f"✅ Memory saved: {memory['id']}\n📝 Content: {content[:100]}{'...' if len(content) > 100 else ''}\n⭐ Importance: {importance}\n🤖 Auto-triggered: {'Yes' if triggers else 'No'}"
                    )]
                
                elif name == "search_memories":
                    query = arguments.get("query", "")
                    limit = arguments.get("limit", 5)
                    
                    memories = await self.db.search_memories(query, limit)
                    
                    if not memories:
                        return [types.TextContent(
                            type="text",
                            text=f"🔍 No memories found for query: '{query}'"
                        )]
                    
                    result_text = f"🔍 Found {len(memories)} memories for '{query}':\n\n"
                    for i, memory in enumerate(memories, 1):
                        result_text += f"{i}. *{memory['id']}* (similarity: {memory['similarity']:.2f})\n"
                        result_text += f"   📝 {memory['content'][:100]}{'...' if len(memory['content']) > 100 else ''}\n"
                        result_text += f"   📅 {memory['timestamp']}\n\n"
                    
                    return [types.TextContent(type="text", text=result_text)]
                
                elif name == "analyze_auto_trigger":
                    text = arguments.get("text", "")
                    triggers = self.auto_trigger.analyze_for_auto_trigger(text)
                    
                    if not triggers:
                        return [types.TextContent(
                            type="text",
                            text=f"🔍 No auto-trigger patterns detected in: '{text[:100]}{'...' if len(text) > 100 else ''}'"
                        )]
                    
                    result_text = f"⚡ Detected {len(triggers)} auto-trigger pattern(s):\n\n"
                    for trigger in triggers:
                        result_text += f"• *{trigger['type']}* ({trigger['trigger']})\n"
                        result_text += f"  Confidence: {trigger['confidence']:.1%}\n"
                        result_text += f"  Reason: {trigger['reason']}\n\n"
                    
                    return [types.TextContent(type="text", text=result_text)]
                
                elif name == "list_memories":
                    limit = arguments.get("limit", 10)
                    all_memories = self.db.memories[-limit:]  # Get latest memories
                    
                    if not all_memories:
                        return [types.TextContent(
                            type="text",
                            text="📝 No memories saved yet."
                        )]
                    
                    result_text = f"📚 Latest {len(all_memories)} memories:\n\n"
                    for memory in reversed(all_memories):  # Show newest first
                        result_text += f"*{memory['id']}* ({memory['memory_type']})\n"
                        result_text += f"📝 {memory['content'][:80]}{'...' if len(memory['content']) > 80 else ''}\n"
                        result_text += f"⭐ Importance: {memory['importance']:.1f} | 📅 {memory['timestamp']}\n\n"
                    
                    return [types.TextContent(type="text", text=result_text)]
                
                else:
                    return [types.TextContent(
                        type="text",
                        text=f"❌ Unknown tool: {name}"
                    )]
            except Exception as e:
                print(f"Error in tool call {name}: {e}")
                return [types.TextContent(
                    type="text",
                    text=f"❌ Error: {str(e)}"
                )]

async def main():
    """Main entry point"""
    try:
        # Create server instance
        mcp_server = SimpleCursorMCPServer()
        
        print("\n🚀 Starting Simple Cursor MCP Server...")
        print("=" * 50)
        print("✅ In-memory database ready")
        print("✅ Auto-trigger system enabled")
        print("✅ MCP Tools available:")
        print("   • save_memory")
        print("   • search_memories") 
        print("   • analyze_auto_trigger")
        print("   • list_memories")
        print("\n📡 Server ready for MCP connections")
        
        # Run the server using stdio
        async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
            await mcp_server.server.run(
                read_stream,
                write_stream,
                InitializationOptions(
                    server_name="mcp-memory-cursor",
                    server_version="1.0.0",
                    capabilities=mcp_server.server.get_capabilities(
                        notification_options=server.NotificationOptions(),
                        experimental_capabilities={}
                    )
                )
            )
            
    except Exception as e:
        print(f"\n❌ Server error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    try:
        # Set up asyncio with proper error handling
        if sys.platform == "win32":
            asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
        
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Server stopped by user")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1) 