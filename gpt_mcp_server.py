#!/usr/bin/env python3
"""
GPT/OpenAI MCP Server - True MCP Protocol Implementation
Supports OpenAI API, ChatGPT, and browser integrations via MCP
"""

import asyncio
import json
import os
import sys
from pathlib import Path
from typing import Dict, List, Any
from datetime import datetime

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

# Import base MCP server
from mcp_base_server import MCPMemoryServer, run_mcp_server
from mcp.types import Tool, TextContent

# Set environment
os.environ.setdefault("ML_MODEL_TYPE", "huggingface")
os.environ.setdefault("HUGGINGFACE_MODEL_NAME", "PiGrieco/mcp-memory-auto-trigger-model")
os.environ.setdefault("AUTO_TRIGGER_ENABLED", "true")
os.environ.setdefault("GPT_MODE", "true")


class GPTMCPServer(MCPMemoryServer):
    """MCP Server optimized for GPT/OpenAI integration"""
    
    def __init__(self):
        super().__init__("gpt")
        self.gpt_stats = {
            'conversations_tracked': 0,
            'api_calls_logged': 0,
            'openai_interactions': 0
        }
        
        # Add GPT-specific tools
        self._add_gpt_tools()
        
        print("🤖 GPT MCP Server initialized with OpenAI optimization")
    
    def _add_gpt_tools(self):
        """Add GPT-specific MCP tools"""
        
        @self.server.list_tools()
        async def handle_gpt_tools() -> List[Tool]:
            """Extended tool list for GPT/OpenAI"""
            base_tools = await super(GPTMCPServer, self).server._list_tools_handler()
            
            gpt_tools = [
                Tool(
                    name="track_conversation",
                    description="Track important parts of GPT/ChatGPT conversations",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "conversation_id": {
                                "type": "string",
                                "description": "Unique conversation identifier"
                            },
                            "user_message": {
                                "type": "string",
                                "description": "User's message to GPT"
                            },
                            "gpt_response": {
                                "type": "string",
                                "description": "GPT's response"
                            },
                            "importance": {
                                "type": "number",
                                "minimum": 0,
                                "maximum": 1,
                                "description": "Importance score (0-1)"
                            },
                            "tags": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": "Tags for the conversation"
                            }
                        },
                        "required": ["user_message", "gpt_response"]
                    }
                ),
                Tool(
                    name="save_prompt_template",
                    description="Save reusable prompt templates for GPT",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "template_name": {
                                "type": "string",
                                "description": "Name of the prompt template"
                            },
                            "prompt_text": {
                                "type": "string",
                                "description": "The prompt template text"
                            },
                            "use_case": {
                                "type": "string",
                                "description": "Description of when to use this prompt"
                            },
                            "variables": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": "Variables that can be substituted in the prompt"
                            }
                        },
                        "required": ["template_name", "prompt_text", "use_case"]
                    }
                ),
                Tool(
                    name="log_api_usage",
                    description="Log OpenAI API usage and costs",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "model": {
                                "type": "string",
                                "description": "GPT model used (gpt-4, gpt-3.5-turbo, etc.)"
                            },
                            "tokens_used": {
                                "type": "integer",
                                "description": "Number of tokens consumed"
                            },
                            "cost": {
                                "type": "number",
                                "description": "Estimated cost in USD"
                            },
                            "request_type": {
                                "type": "string",
                                "enum": ["completion", "chat", "embedding", "fine_tuning"],
                                "description": "Type of API request"
                            },
                            "purpose": {
                                "type": "string",
                                "description": "Purpose of the API call"
                            }
                        },
                        "required": ["model", "tokens_used", "request_type"]
                    }
                ),
                Tool(
                    name="search_conversations",
                    description="Search through saved GPT conversations",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "query": {
                                "type": "string",
                                "description": "Search query for conversations"
                            },
                            "conversation_id": {
                                "type": "string",
                                "description": "Specific conversation ID to search in"
                            },
                            "date_from": {
                                "type": "string",
                                "description": "Start date (YYYY-MM-DD)"
                            },
                            "date_to": {
                                "type": "string",
                                "description": "End date (YYYY-MM-DD)"
                            },
                            "min_importance": {
                                "type": "number",
                                "minimum": 0,
                                "maximum": 1,
                                "description": "Minimum importance score"
                            }
                        },
                        "required": ["query"]
                    }
                )
            ]
            
            return base_tools + gpt_tools
        
        @self.server.call_tool()
        async def handle_gpt_tools(name: str, arguments: Dict[str, Any]) -> List[TextContent]:
            """Handle GPT-specific tool calls"""
            
            if name == "track_conversation":
                return await self._handle_track_conversation(arguments)
            elif name == "save_prompt_template":
                return await self._handle_save_prompt_template(arguments)
            elif name == "log_api_usage":
                return await self._handle_log_api_usage(arguments)
            elif name == "search_conversations":
                return await self._handle_search_conversations(arguments)
            else:
                # Call parent handler for base tools
                return await super(GPTMCPServer, self).server._call_tool_handler(name, arguments)
    
    async def _handle_track_conversation(self, arguments: Dict[str, Any]) -> List[TextContent]:
        """Handle track_conversation tool call"""
        conversation_id = arguments.get("conversation_id", f"conv_{int(datetime.now().timestamp())}")
        user_message = arguments.get("user_message", "")
        gpt_response = arguments.get("gpt_response", "")
        importance = arguments.get("importance", 0.7)
        tags = arguments.get("tags", [])
        
        if not user_message.strip() or not gpt_response.strip():
            return [TextContent(type="text", text="❌ Both user message and GPT response are required")]
        
        # Create conversation content
        content = f"GPT Conversation ({conversation_id}):\n\n"
        content += f"**User:** {user_message}\n\n"
        content += f"**GPT:** {gpt_response}\n"
        
        # Enhanced context for conversations
        context = {
            "category": "gpt_conversation",
            "importance": importance,
            "tags": tags + ["gpt_conversation", "openai"],
            "conversation_id": conversation_id,
            "timestamp": datetime.now().isoformat(),
            "gpt_type": "conversation"
        }
        
        # Save using base functionality
        await self._handle_save_memory({
            "content": content,
            "context": context
        })
        
        self.gpt_stats['conversations_tracked'] += 1
        
        result = f"🤖 GPT conversation tracked!\n"
        result += f"   Conversation ID: {conversation_id}\n"
        result += f"   User message length: {len(user_message)} chars\n"
        result += f"   GPT response length: {len(gpt_response)} chars\n"
        result += f"   Importance: {importance}\n"
        result += f"   Tags: {', '.join(tags)}\n"
        
        return [TextContent(type="text", text=result)]
    
    async def _handle_save_prompt_template(self, arguments: Dict[str, Any]) -> List[TextContent]:
        """Handle save_prompt_template tool call"""
        template_name = arguments.get("template_name", "")
        prompt_text = arguments.get("prompt_text", "")
        use_case = arguments.get("use_case", "")
        variables = arguments.get("variables", [])
        
        if not template_name.strip() or not prompt_text.strip():
            return [TextContent(type="text", text="❌ Template name and prompt text are required")]
        
        # Create template content
        content = f"GPT Prompt Template: {template_name}\n\n"
        content += f"**Use Case:** {use_case}\n\n"
        content += f"**Template:**\n{prompt_text}\n"
        
        if variables:
            content += f"\n**Variables:** {', '.join(variables)}\n"
        
        # Template context
        context = {
            "category": "prompt_template",
            "importance": 0.8,  # Templates are generally important
            "tags": ["prompt_template", "gpt", "template"] + variables,
            "template_name": template_name,
            "use_case": use_case,
            "variables": variables,
            "gpt_type": "prompt_template"
        }
        
        # Save template
        await self._handle_save_memory({
            "content": content,
            "context": context
        })
        
        result = f"🤖 Prompt template saved!\n"
        result += f"   Name: {template_name}\n"
        result += f"   Use case: {use_case}\n"
        result += f"   Variables: {len(variables)}\n"
        result += f"   Template length: {len(prompt_text)} chars\n"
        
        return [TextContent(type="text", text=result)]
    
    async def _handle_log_api_usage(self, arguments: Dict[str, Any]) -> List[TextContent]:
        """Handle log_api_usage tool call"""
        model = arguments.get("model", "")
        tokens_used = arguments.get("tokens_used", 0)
        cost = arguments.get("cost", 0.0)
        request_type = arguments.get("request_type", "")
        purpose = arguments.get("purpose", "")
        
        self.gpt_stats['api_calls_logged'] += 1
        
        # Create API usage content
        content = f"OpenAI API Usage Log:\n\n"
        content += f"**Model:** {model}\n"
        content += f"**Request Type:** {request_type}\n"
        content += f"**Tokens Used:** {tokens_used:,}\n"
        content += f"**Estimated Cost:** ${cost:.4f}\n"
        content += f"**Purpose:** {purpose}\n"
        content += f"**Timestamp:** {datetime.now().isoformat()}\n"
        
        # API usage context
        context = {
            "category": "api_usage",
            "importance": 0.5,
            "tags": ["api_usage", "openai", f"model_{model}", request_type],
            "model": model,
            "tokens_used": tokens_used,
            "cost": cost,
            "request_type": request_type,
            "gpt_type": "api_usage"
        }
        
        # Save usage log
        await self._handle_save_memory({
            "content": content,
            "context": context
        })
        
        result = f"🤖 API usage logged!\n"
        result += f"   Model: {model}\n"
        result += f"   Tokens: {tokens_used:,}\n"
        result += f"   Cost: ${cost:.4f}\n"
        result += f"   Total API calls logged: {self.gpt_stats['api_calls_logged']}\n"
        
        return [TextContent(type="text", text=result)]
    
    async def _handle_search_conversations(self, arguments: Dict[str, Any]) -> List[TextContent]:
        """Handle search_conversations tool call"""
        query = arguments.get("query", "")
        conversation_id = arguments.get("conversation_id")
        date_from = arguments.get("date_from")
        date_to = arguments.get("date_to")
        min_importance = arguments.get("min_importance", 0.0)
        
        if not query.strip():
            return [TextContent(type="text", text="❌ Search query is required")]
        
        # Filter memories by GPT conversations
        filtered_memories = []
        for memory in self.memories.values():
            # Check if it's a GPT conversation
            if memory.get('context', {}).get('category') != 'gpt_conversation':
                continue
            
            # Apply filters
            if conversation_id and memory.get('context', {}).get('conversation_id') != conversation_id:
                continue
            
            if min_importance and memory.get('context', {}).get('importance', 0) < min_importance:
                continue
            
            # Date filtering would require parsing timestamp
            # For now, just add to filtered list
            filtered_memories.append(memory)
        
        # Perform search on filtered memories
        query_lower = query.lower()
        results = []
        
        for memory in filtered_memories:
            content_lower = memory['content'].lower()
            
            # Calculate similarity
            query_words = set(query_lower.split())
            content_words = set(content_lower.split())
            common_words = query_words.intersection(content_words)
            
            if common_words:
                similarity = len(common_words) / len(query_words.union(content_words))
                importance_boost = memory.get('context', {}).get('importance', 0.5) * 0.2
                final_score = similarity + importance_boost
                
                if final_score > 0.1:
                    results.append({
                        "memory": memory,
                        "score": final_score
                    })
        
        # Sort by score
        results.sort(key=lambda x: x['score'], reverse=True)
        results = results[:5]  # Top 5
        
        if not results:
            return [TextContent(type="text", text=f"🤖 No GPT conversations found for query: '{query}'")]
        
        result = f"🤖 Found {len(results)} GPT conversations for query: '{query}'\n\n"
        
        for i, item in enumerate(results, 1):
            memory = item['memory']
            score = item['score']
            conv_id = memory.get('context', {}).get('conversation_id', 'Unknown')
            importance = memory.get('context', {}).get('importance', 0.5)
            
            result += f"{i}. **Conversation {conv_id}** (score: {score:.3f}, importance: {importance:.2f})\n"
            content_preview = memory['content'][:200] + "..." if len(memory['content']) > 200 else memory['content']
            result += f"   {content_preview}\n\n"
        
        return [TextContent(type="text", text=result)]
    
    def _check_deterministic_triggers(self, message: str) -> Dict:
        """Enhanced deterministic triggers for GPT"""
        base_result = super()._check_deterministic_triggers(message)
        
        message_lower = message.lower()
        gpt_triggers = []
        
        # GPT-specific triggers
        gpt_words = [
            'prompt', 'template', 'chatgpt', 'openai', 'gpt',
            'conversation', 'api call', 'tokens', 'model'
        ]
        
        for word in gpt_words:
            if word in message_lower:
                gpt_triggers.append(f"gpt_{word.replace(' ', '_')}")
        
        # Technical assistance triggers
        tech_words = [
            'explain', 'help', 'how to', 'tutorial', 'guide',
            'example', 'code', 'function', 'debug', 'error'
        ]
        
        for word in tech_words:
            if word in message_lower:
                gpt_triggers.append(f"tech_{word.replace(' ', '_')}")
        
        # Combine with base triggers
        all_triggers = base_result['triggers'] + gpt_triggers
        
        # Enhanced save logic for GPT content
        should_save = base_result['should_save'] or len(gpt_triggers) > 0
        
        return {
            "triggers": all_triggers,
            "should_save": should_save,
            "should_search": base_result['should_search'],
            "confidence": 0.9 if all_triggers else 0.1,
            "gpt_triggers": gpt_triggers
        }


async def main():
    """Main entry point for GPT MCP Server"""
    print("🤖 GPT/OPENAI - TRUE MCP SERVER")
    print("=" * 50)
    print("✅ Implementing standard MCP protocol")
    print("🤖 ML auto-triggers with OpenAI optimization")
    print("💬 Conversation tracking and prompt templates")
    print("📡 Native MCP integration ready")
    
    await run_mcp_server("gpt")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 GPT MCP Server stopped")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
