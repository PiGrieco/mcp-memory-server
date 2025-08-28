#!/usr/bin/env python3
"""
Base MCP Server Implementation
Implements the standard MCP protocol for all integrations
"""

import asyncio
import os
import sys
import time
from typing import Any, Dict, List
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

# MCP Protocol imports
try:
    from mcp.server import Server
    from mcp.types import Tool, TextContent
    from mcp.server.stdio import stdio_server
    from mcp.server.models import InitializationOptions
except ImportError:
    print("⚠️ MCP library not found. Installing...")
    import subprocess
    subprocess.run([sys.executable, "-m", "pip", "install", "mcp"], check=True)
    from mcp.server import Server
    from mcp.types import Tool, TextContent
    from mcp.server.stdio import stdio_server
    from mcp.server.models import InitializationOptions


class ProgressBar:
    """Simple progress bar for console"""
    
    def __init__(self, total: int, description: str = "Progress"):
        self.total = total
        self.current = 0
        self.description = description
        self.start_time = time.time()
    
    def update(self, increment: int = 1):
        self.current += increment
        self._display()
    
    def _display(self):
        percentage = min(100, (self.current / self.total) * 100)
        bar_length = 30
        filled_length = int(bar_length * self.current // self.total)
        
        bar = '█' * filled_length + '░' * (bar_length - filled_length)
        elapsed = time.time() - self.start_time
        
        print(f'\r🔄 {self.description}: [{bar}] {percentage:.1f}% ({elapsed:.1f}s)', end='', flush=True)
        
        if self.current >= self.total:
            print()  # New line when complete


class MCPMemoryServer:
    """Base MCP Memory Server with ML Auto-Triggers"""
    
    def __init__(self, platform_name: str = "generic"):
        self.platform_name = platform_name
        self.server = Server(f"mcp-memory-{platform_name}")
        self.memories = {}
        self.memory_counter = 0
        self.ml_model = None
        self._model_loading = False
        self.stats = {
            'requests': 0,
            'saves': 0,
            'searches': 0,
            'ml_predictions': 0
        }
        
        # Setup MCP tools
        self._setup_mcp_tools()
        
        print(f"✅ MCP Memory Server for {platform_name} initialized")
    
    def _setup_mcp_tools(self):
        """Setup MCP protocol tools"""
        
        @self.server.list_tools()
        async def handle_list_tools() -> List[Tool]:
            """List available MCP tools"""
            return [
                Tool(
                    name="save_memory",
                    description="Save important information to memory with ML auto-detection",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "content": {
                                "type": "string",
                                "description": "Content to save to memory"
                            },
                            "context": {
                                "type": "object",
                                "description": "Additional context information",
                                "properties": {
                                    "importance": {"type": "number", "minimum": 0, "maximum": 1},
                                    "tags": {"type": "array", "items": {"type": "string"}},
                                    "category": {"type": "string"}
                                }
                            }
                        },
                        "required": ["content"]
                    }
                ),
                Tool(
                    name="search_memory",
                    description="Search through saved memories using semantic similarity",
                    inputSchema={
                        "type": "object", 
                        "properties": {
                            "query": {
                                "type": "string",
                                "description": "Search query for finding relevant memories"
                            },
                            "limit": {
                                "type": "integer",
                                "description": "Maximum number of results to return",
                                "default": 5,
                                "minimum": 1,
                                "maximum": 20
                            },
                            "min_similarity": {
                                "type": "number",
                                "description": "Minimum similarity threshold",
                                "default": 0.1,
                                "minimum": 0,
                                "maximum": 1
                            }
                        },
                        "required": ["query"]
                    }
                ),
                Tool(
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
                Tool(
                    name="get_memory_stats",
                    description="Get memory usage and ML model statistics",
                    inputSchema={
                        "type": "object",
                        "properties": {}
                    }
                ),
                Tool(
                    name="list_memories",
                    description="List all saved memories with optional filtering",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "limit": {
                                "type": "integer",
                                "default": 10,
                                "minimum": 1,
                                "maximum": 100
                            },
                            "category": {
                                "type": "string",
                                "description": "Filter by category"
                            },
                            "tag": {
                                "type": "string", 
                                "description": "Filter by tag"
                            }
                        }
                    }
                )
            ]
        
        @self.server.call_tool()
        async def handle_call_tool(name: str, arguments: Dict[str, Any]) -> List[TextContent]:
            """Handle MCP tool calls"""
            self.stats['requests'] += 1
            
            try:
                if name == "save_memory":
                    return await self._handle_save_memory(arguments)
                elif name == "search_memory":
                    return await self._handle_search_memory(arguments)
                elif name == "analyze_message":
                    return await self._handle_analyze_message(arguments)
                elif name == "get_memory_stats":
                    return await self._handle_get_stats(arguments)
                elif name == "list_memories":
                    return await self._handle_list_memories(arguments)
                else:
                    return [TextContent(type="text", text=f"Unknown tool: {name}")]
                    
            except Exception as e:
                error_msg = f"Error in {name}: {str(e)}"
                print(f"❌ {error_msg}")
                return [TextContent(type="text", text=error_msg)]
    
    async def _load_ml_model_lazy(self):
        """Load ML model only when needed with progress"""
        if self.ml_model is not None or self._model_loading:
            return True
        
        self._model_loading = True
        
        try:
            print(f"\n🤖 [{self.platform_name.upper()}] Caricamento modello ML da Hugging Face...")
            progress = ProgressBar(5, f"{self.platform_name} ML Loading")
            
            # Step 1: Import libraries
            progress.update()
            from transformers import pipeline
            
            # Step 2: Check model availability
            progress.update()
            from huggingface_hub import model_info
            model_name = "PiGrieco/mcp-memory-auto-trigger-model"
            
            try:
                info = model_info(model_name)
                progress.update()
                print(f"\n✅ [{self.platform_name.upper()}] Modello trovato: {model_name}")
                print(f"   📊 Dimensione: ~{info.safetensors.total // (1024*1024) if hasattr(info, 'safetensors') and info.safetensors else 'N/A'}MB")
            except Exception as e:
                print(f"\n⚠️ [{self.platform_name.upper()}] Problema accesso modello: {e}")
                print("🔄 Uso modello generico di backup...")
                model_name = "cardiffnlp/twitter-roberta-base-sentiment-latest"
            
            # Step 3: Initialize pipeline
            progress.update()
            print(f"\n🧠 [{self.platform_name.upper()}] Inizializzazione pipeline ML...")
            
            self.ml_model = pipeline(
                "text-classification",
                model=model_name,
                return_all_scores=True,
                device=-1,  # CPU for compatibility
                model_kwargs={"torch_dtype": "auto"}
            )
            
            # Step 4: Test prediction
            progress.update()
            self.ml_model(f"Test message for {self.platform_name} initialization")
            
            progress.update()
            print(f"\n✅ [{self.platform_name.upper()}] Modello ML caricato e testato!")
            print(f"   🎯 Ottimizzato per: {self.platform_name}")
            print("   ⚡ Device: CPU (compatibility)")
            print("   📡 MCP Protocol: Ready")
            
            self._model_loading = False
            return True
            
        except Exception as e:
            print(f"\n❌ [{self.platform_name.upper()}] Errore caricamento ML: {e}")
            print("🔄 Continuando con trigger deterministici...")
            self._model_loading = False
            return False
    
    async def _handle_save_memory(self, arguments: Dict[str, Any]) -> List[TextContent]:
        """Handle save_memory tool call"""
        content = arguments.get("content", "")
        context = arguments.get("context", {})
        
        if not content.strip():
            return [TextContent(type="text", text="❌ Cannot save empty content")]
        
        # Generate memory ID
        self.memory_counter += 1
        memory_id = f"{self.platform_name}_mem_{self.memory_counter:03d}"
        
        # Save memory
        self.memories[memory_id] = {
            "id": memory_id,
            "content": content,
            "context": context,
            "timestamp": time.time(),
            "platform": self.platform_name,
            "importance": context.get("importance", 0.5),
            "tags": context.get("tags", []),
            "category": context.get("category", "general")
        }
        
        self.stats['saves'] += 1
        
        result = "💾 Memory saved successfully!\n"
        result += f"   ID: {memory_id}\n"
        result += f"   Content: {content[:100]}{'...' if len(content) > 100 else ''}\n"
        result += f"   Platform: {self.platform_name}\n"
        result += f"   Tags: {', '.join(context.get('tags', []))}\n"
        
        return [TextContent(type="text", text=result)]
    
    async def _handle_search_memory(self, arguments: Dict[str, Any]) -> List[TextContent]:
        """Handle search_memory tool call"""
        query = arguments.get("query", "")
        limit = arguments.get("limit", 5)
        min_similarity = arguments.get("min_similarity", 0.1)
        
        if not query.strip():
            return [TextContent(type="text", text="❌ Cannot search with empty query")]
        
        # Simple text-based search
        results = []
        query_lower = query.lower()
        
        for memory in self.memories.values():
            content_lower = memory['content'].lower()
            
            # Calculate simple similarity
            query_words = set(query_lower.split())
            content_words = set(content_lower.split())
            common_words = query_words.intersection(content_words)
            
            if common_words:
                similarity = len(common_words) / len(query_words.union(content_words))
                
                # Apply importance boost
                importance_boost = memory.get('importance', 0.5) * 0.2
                final_score = similarity + importance_boost
                
                if final_score >= min_similarity:
                    results.append({
                        "memory": memory,
                        "similarity": similarity,
                        "final_score": final_score
                    })
        
        # Sort by final score
        results.sort(key=lambda x: x['final_score'], reverse=True)
        results = results[:limit]
        
        self.stats['searches'] += 1
        
        if not results:
            return [TextContent(type="text", text=f"🔍 No memories found for query: '{query}'")]
        
        result = f"🔍 Found {len(results)} memories for query: '{query}'\n\n"
        
        for i, item in enumerate(results, 1):
            memory = item['memory']
            score = item['final_score']
            result += f"{i}. **{memory['id']}** (score: {score:.3f})\n"
            result += f"   Content: {memory['content'][:150]}{'...' if len(memory['content']) > 150 else ''}\n"
            result += f"   Tags: {', '.join(memory.get('tags', []))}\n"
            result += f"   Category: {memory.get('category', 'general')}\n\n"
        
        return [TextContent(type="text", text=result)]
    
    async def _handle_analyze_message(self, arguments: Dict[str, Any]) -> List[TextContent]:
        """Handle analyze_message tool call"""
        message = arguments.get("message", "")
        arguments.get("platform_context", {})
        
        if not message.strip():
            return [TextContent(type="text", text="❌ Cannot analyze empty message")]
        
        # Deterministic triggers
        deterministic_triggers = self._check_deterministic_triggers(message)
        
        # ML triggers
        ml_result = {}
        if deterministic_triggers['triggers'] or len(message) > 15:
            ml_available = await self._load_ml_model_lazy()
            
            if ml_available and self.ml_model:
                try:
                    predictions = self.ml_model(message)
                    self.stats['ml_predictions'] += 1
                    
                    if isinstance(predictions, list) and len(predictions) > 0:
                        if isinstance(predictions[0], list):
                            predictions = predictions[0]
                        best_pred = max(predictions, key=lambda x: x['score'])
                    else:
                        best_pred = {"label": "NO_ACTION", "score": 0.5}
                    
                    ml_result = {
                        "available": True,
                        "prediction": best_pred,
                        "should_save": best_pred['label'] == 'SAVE_MEMORY' and best_pred['score'] > 0.6,
                        "should_search": best_pred['label'] == 'SEARCH_MEMORY' and best_pred['score'] > 0.5
                    }
                except Exception as e:
                    ml_result = {"available": False, "error": str(e)}
        
        # Combine results
        should_save = deterministic_triggers.get('should_save', False) or ml_result.get('should_save', False)
        should_search = deterministic_triggers.get('should_search', False) or ml_result.get('should_search', False)
        
        result = f"🤖 Message Analysis for {self.platform_name}:\n\n"
        result += f"**Message:** {message[:100]}{'...' if len(message) > 100 else ''}\n\n"
        result += f"**Deterministic Triggers:** {len(deterministic_triggers['triggers'])} found\n"
        result += f"**ML Analysis:** {'✅ Available' if ml_result.get('available') else '❌ Not available'}\n"
        
        if ml_result.get('available'):
            pred = ml_result['prediction']
            result += f"   Prediction: {pred['label']} ({pred['score']:.3f})\n"
        
        result += "\n**Recommended Actions:**\n"
        result += f"   💾 Save: {'✅ Yes' if should_save else '❌ No'}\n"
        result += f"   🔍 Search: {'✅ Yes' if should_search else '❌ No'}\n"
        
        return [TextContent(type="text", text=result)]
    
    async def _handle_get_stats(self, arguments: Dict[str, Any]) -> List[TextContent]:
        """Handle get_memory_stats tool call"""
        result = f"📊 MCP Memory Server Stats - {self.platform_name}\n\n"
        result += "**API Statistics:**\n"
        result += f"   📡 Total requests: {self.stats['requests']}\n"
        result += f"   💾 Memories saved: {self.stats['saves']}\n"
        result += f"   🔍 Searches performed: {self.stats['searches']}\n"
        result += f"   🤖 ML predictions: {self.stats['ml_predictions']}\n\n"
        
        result += "**Memory Database:**\n"
        result += f"   📚 Total memories: {len(self.memories)}\n"
        result += f"   🎯 Platform: {self.platform_name}\n"
        result += f"   🤖 ML Model loaded: {'✅ Yes' if self.ml_model else '❌ No'}\n\n"
        
        # Category breakdown
        categories = {}
        for memory in self.memories.values():
            cat = memory.get('category', 'general')
            categories[cat] = categories.get(cat, 0) + 1
        
        if categories:
            result += "**Categories:**\n"
            for cat, count in categories.items():
                result += f"   {cat}: {count} memories\n"
        
        return [TextContent(type="text", text=result)]
    
    async def _handle_list_memories(self, arguments: Dict[str, Any]) -> List[TextContent]:
        """Handle list_memories tool call"""
        limit = arguments.get("limit", 10)
        category_filter = arguments.get("category")
        tag_filter = arguments.get("tag")
        
        memories = list(self.memories.values())
        
        # Apply filters
        if category_filter:
            memories = [m for m in memories if m.get('category') == category_filter]
        
        if tag_filter:
            memories = [m for m in memories if tag_filter in m.get('tags', [])]
        
        # Sort by timestamp (newest first)
        memories.sort(key=lambda x: x.get('timestamp', 0), reverse=True)
        memories = memories[:limit]
        
        if not memories:
            return [TextContent(type="text", text="📚 No memories found matching the criteria")]
        
        result = f"📚 {len(memories)} memories found:\n\n"
        
        for i, memory in enumerate(memories, 1):
            result += f"{i}. **{memory['id']}**\n"
            result += f"   Content: {memory['content'][:100]}{'...' if len(memory['content']) > 100 else ''}\n"
            result += f"   Category: {memory.get('category', 'general')}\n"
            result += f"   Tags: {', '.join(memory.get('tags', []))}\n"
            result += f"   Importance: {memory.get('importance', 0.5):.2f}\n\n"
        
        return [TextContent(type="text", text=result)]
    
    def _check_deterministic_triggers(self, message: str) -> Dict:
        """Check deterministic triggers"""
        message_lower = message.lower()
        triggers = []
        
        # Standard keywords
        keywords = [
            'ricorda', 'importante', 'nota', 'salva', 'memorizza',
            'remember', 'save', 'note', 'important', 'store'
        ]
        
        for keyword in keywords:
            if keyword in message_lower:
                triggers.append(f"keyword_{keyword}")
        
        # Patterns
        patterns = [
            'risolto', 'solved', 'fixed', 'bug fix', 'solution',
            'tutorial', 'how to', 'guide', 'best practice'
        ]
        
        for pattern in patterns:
            if pattern in message_lower:
                triggers.append(f"pattern_{pattern}")
        
        # Questions
        question_words = ['come', 'cosa', 'perché', 'how', 'what', 'why', '?']
        if any(q in message_lower for q in question_words):
            triggers.append("question_detected")
        
        return {
            "triggers": triggers,
            "should_save": len([t for t in triggers if 'keyword' in t or 'pattern' in t]) > 0,
            "should_search": "question_detected" in triggers,
            "confidence": 0.9 if triggers else 0.1
        }


def create_mcp_server(platform_name: str) -> MCPMemoryServer:
    """Factory function to create platform-specific MCP servers"""
    return MCPMemoryServer(platform_name)


async def run_mcp_server(platform_name: str):
    """Run MCP server with stdio transport"""
    memory_server = create_mcp_server(platform_name)
    
    # Run with stdio transport (standard for MCP)
    async with stdio_server() as (read_stream, write_stream):
        await memory_server.server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name=f"mcp-memory-{platform_name}",
                server_version="1.0.0",
                capabilities={
                    "tools": {}
                }
            )
        )


if __name__ == "__main__":
    # Get platform name from command line or environment
    platform = sys.argv[1] if len(sys.argv) > 1 else os.environ.get("MCP_PLATFORM", "generic")
    
    print(f"🚀 Starting MCP Memory Server for {platform}")
    try:
        asyncio.run(run_mcp_server(platform))
    except KeyboardInterrupt:
        print(f"\n👋 MCP Server for {platform} stopped")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
