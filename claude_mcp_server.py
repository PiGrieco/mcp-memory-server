#!/usr/bin/env python3
"""
Claude Desktop MCP Server - True MCP Protocol Implementation
Optimized for Claude Desktop with native MCP integration
"""

import asyncio
import os
import sys
from pathlib import Path
from typing import Dict, List, Any

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

# Import base MCP server
from mcp_base_server import MCPMemoryServer, run_mcp_server
from mcp.types import Tool, TextContent

# Set environment
os.environ.setdefault("ML_MODEL_TYPE", "huggingface")
os.environ.setdefault("HUGGINGFACE_MODEL_NAME", "PiGrieco/mcp-memory-auto-trigger-model")
os.environ.setdefault("AUTO_TRIGGER_ENABLED", "true")
os.environ.setdefault("CLAUDE_MODE", "true")


class ClaudeMCPServer(MCPMemoryServer):
    """MCP Server optimized for Claude Desktop"""
    
    def __init__(self):
        super().__init__("claude")
        self.claude_stats = {
            'explanations_provided': 0,
            'long_conversations': 0,
            'follow_up_questions': 0
        }
        
        # Add Claude-specific tools
        self._add_claude_tools()
        
        print("🔮 Claude MCP Server initialized with native integration")
    
    def _add_claude_tools(self):
        """Add Claude-specific MCP tools"""
        
        @self.server.list_tools()
        async def handle_claude_tools() -> List[Tool]:
            """Extended tool list for Claude Desktop"""
            base_tools = await super(ClaudeMCPServer, self).server._list_tools_handler()
            
            claude_tools = [
                Tool(
                    name="save_explanation",
                    description="Save detailed explanations provided by Claude",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "topic": {
                                "type": "string",
                                "description": "Main topic of the explanation"
                            },
                            "user_question": {
                                "type": "string",
                                "description": "User's original question"
                            },
                            "explanation": {
                                "type": "string",
                                "description": "Claude's detailed explanation"
                            },
                            "complexity_level": {
                                "type": "string",
                                "enum": ["beginner", "intermediate", "advanced", "expert"],
                                "description": "Complexity level of the explanation"
                            },
                            "related_topics": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": "Related topics mentioned"
                            },
                            "examples_included": {
                                "type": "boolean",
                                "description": "Whether examples were provided"
                            }
                        },
                        "required": ["topic", "user_question", "explanation"]
                    }
                ),
                Tool(
                    name="track_conversation_thread",
                    description="Track long conversation threads with context",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "thread_topic": {
                                "type": "string",
                                "description": "Main topic of the conversation thread"
                            },
                            "messages_count": {
                                "type": "integer",
                                "description": "Number of messages in the thread"
                            },
                            "key_insights": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": "Key insights from the conversation"
                            },
                            "unresolved_questions": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": "Questions that remain unresolved"
                            },
                            "action_items": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": "Action items identified"
                            }
                        },
                        "required": ["thread_topic", "messages_count"]
                    }
                ),
                Tool(
                    name="save_claude_insight",
                    description="Save particularly valuable insights from Claude",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "insight": {
                                "type": "string",
                                "description": "The valuable insight"
                            },
                            "context": {
                                "type": "string",
                                "description": "Context in which the insight was provided"
                            },
                            "insight_type": {
                                "type": "string",
                                "enum": ["analytical", "creative", "problem_solving", "educational", "strategic"],
                                "description": "Type of insight"
                            },
                            "potential_applications": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": "Potential applications of this insight"
                            }
                        },
                        "required": ["insight", "context", "insight_type"]
                    }
                )
            ]
            
            return base_tools + claude_tools
        
        @self.server.call_tool()
        async def handle_claude_tools(name: str, arguments: Dict[str, Any]) -> List[TextContent]:
            """Handle Claude-specific tool calls"""
            
            if name == "save_explanation":
                return await self._handle_save_explanation(arguments)
            elif name == "track_conversation_thread":
                return await self._handle_track_conversation_thread(arguments)
            elif name == "save_claude_insight":
                return await self._handle_save_claude_insight(arguments)
            else:
                # Call parent handler for base tools
                return await super(ClaudeMCPServer, self).server._call_tool_handler(name, arguments)
    
    async def _handle_save_explanation(self, arguments: Dict[str, Any]) -> List[TextContent]:
        """Handle save_explanation tool call"""
        topic = arguments.get("topic", "")
        user_question = arguments.get("user_question", "")
        explanation = arguments.get("explanation", "")
        complexity_level = arguments.get("complexity_level", "intermediate")
        related_topics = arguments.get("related_topics", [])
        examples_included = arguments.get("examples_included", False)
        
        self.claude_stats['explanations_provided'] += 1
        
        # Create explanation content
        content = f"Claude Explanation: {topic}\n\n"
        content += f"**Complexity Level:** {complexity_level}\n"
        content += f"**Examples Included:** {'✅ Yes' if examples_included else '❌ No'}\n\n"
        content += f"**User Question:**\n{user_question}\n\n"
        content += f"**Claude's Explanation:**\n{explanation}\n"
        
        if related_topics:
            content += f"\n**Related Topics:** {', '.join(related_topics)}\n"
        
        # Explanation context
        context = {
            "category": "explanation",
            "importance": 0.8,
            "tags": ["claude_explanation", complexity_level, "educational"] + related_topics,
            "topic": topic,
            "complexity_level": complexity_level,
            "examples_included": examples_included,
            "claude_type": "explanation"
        }
        
        # Save explanation
        await self._handle_save_memory({
            "content": content,
            "context": context
        })
        
        result = f"🔮 Claude explanation saved!\n"
        result += f"   Topic: {topic}\n"
        result += f"   Complexity: {complexity_level}\n"
        result += f"   Related topics: {len(related_topics)}\n"
        result += f"   Examples: {'✅' if examples_included else '❌'}\n"
        result += f"   Total explanations: {self.claude_stats['explanations_provided']}\n"
        
        return [TextContent(type="text", text=result)]
    
    async def _handle_track_conversation_thread(self, arguments: Dict[str, Any]) -> List[TextContent]:
        """Handle track_conversation_thread tool call"""
        thread_topic = arguments.get("thread_topic", "")
        messages_count = arguments.get("messages_count", 0)
        key_insights = arguments.get("key_insights", [])
        unresolved_questions = arguments.get("unresolved_questions", [])
        action_items = arguments.get("action_items", [])
        
        if messages_count > 10:
            self.claude_stats['long_conversations'] += 1
        
        # Create conversation thread log
        content = f"Claude Conversation Thread: {thread_topic}\n\n"
        content += f"**Messages Count:** {messages_count}\n"
        content += f"**Status:** {'Long conversation' if messages_count > 10 else 'Standard conversation'}\n\n"
        
        if key_insights:
            content += f"**Key Insights:**\n"
            for insight in key_insights:
                content += f"  • {insight}\n"
            content += "\n"
        
        if unresolved_questions:
            content += f"**Unresolved Questions:**\n"
            for question in unresolved_questions:
                content += f"  ❓ {question}\n"
            content += "\n"
        
        if action_items:
            content += f"**Action Items:**\n"
            for item in action_items:
                content += f"  📋 {item}\n"
        
        # Thread context
        context = {
            "category": "conversation_thread",
            "importance": 0.7,
            "tags": ["claude_conversation", "thread", "long" if messages_count > 10 else "standard"],
            "thread_topic": thread_topic,
            "messages_count": messages_count,
            "insights_count": len(key_insights),
            "claude_type": "conversation_thread"
        }
        
        # Save thread
        await self._handle_save_memory({
            "content": content,
            "context": context
        })
        
        result = f"🔮 Conversation thread tracked!\n"
        result += f"   Topic: {thread_topic}\n"
        result += f"   Messages: {messages_count}\n"
        result += f"   Insights: {len(key_insights)}\n"
        result += f"   Unresolved: {len(unresolved_questions)}\n"
        result += f"   Action items: {len(action_items)}\n"
        
        return [TextContent(type="text", text=result)]
    
    async def _handle_save_claude_insight(self, arguments: Dict[str, Any]) -> List[TextContent]:
        """Handle save_claude_insight tool call"""
        insight = arguments.get("insight", "")
        context_info = arguments.get("context", "")
        insight_type = arguments.get("insight_type", "")
        potential_applications = arguments.get("potential_applications", [])
        
        # Create insight content
        content = f"Claude Insight ({insight_type})\n\n"
        content += f"**Context:** {context_info}\n\n"
        content += f"**Insight:**\n{insight}\n"
        
        if potential_applications:
            content += f"\n**Potential Applications:**\n"
            for app in potential_applications:
                content += f"  • {app}\n"
        
        # Insight context
        context = {
            "category": "claude_insight",
            "importance": 0.9,  # Insights are highly valuable
            "tags": ["claude_insight", insight_type, "valuable"],
            "insight_type": insight_type,
            "applications_count": len(potential_applications),
            "claude_type": "insight"
        }
        
        # Save insight
        await self._handle_save_memory({
            "content": content,
            "context": context
        })
        
        result = f"🔮 Claude insight saved!\n"
        result += f"   Type: {insight_type}\n"
        result += f"   Applications: {len(potential_applications)}\n"
        result += f"   Context: {context_info[:50]}{'...' if len(context_info) > 50 else ''}\n"
        
        return [TextContent(type="text", text=result)]


async def main():
    """Main entry point for Claude MCP Server"""
    print("🔮 CLAUDE DESKTOP - TRUE MCP SERVER")
    print("=" * 50)
    print("✅ Implementing standard MCP protocol")
    print("🤖 ML auto-triggers with native optimization")
    print("💬 Conversation and explanation tracking")
    print("📡 Native MCP integration ready")
    
    await run_mcp_server("claude")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Claude MCP Server stopped")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
