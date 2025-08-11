#!/usr/bin/env python3
"""
Windsurf IDE MCP Server - True MCP Protocol Implementation
Optimized for Windsurf Cascade AI IDE with code-aware features
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
os.environ.setdefault("WINDSURF_MODE", "true")


class WindsurfMCPServer(MCPMemoryServer):
    """MCP Server optimized for Windsurf Cascade IDE"""
    
    def __init__(self):
        super().__init__("windsurf")
        self.windsurf_stats = {
            'code_snippets_saved': 0,
            'explanations_saved': 0,
            'cascade_interactions': 0
        }
        
        # Add Windsurf-specific tools
        self._add_windsurf_tools()
        
        print("🌪️ Windsurf MCP Server initialized with Cascade AI optimization")
    
    def _add_windsurf_tools(self):
        """Add Windsurf-specific MCP tools"""
        
        @self.server.list_tools()
        async def handle_windsurf_tools() -> List[Tool]:
            """Extended tool list for Windsurf"""
            base_tools = await super(WindsurfMCPServer, self).server._list_tools_handler()
            
            windsurf_tools = [
                Tool(
                    name="save_code_snippet",
                    description="Save code snippets with language and context information",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "code": {
                                "type": "string",
                                "description": "The code snippet to save"
                            },
                            "language": {
                                "type": "string",
                                "description": "Programming language (python, javascript, etc.)"
                            },
                            "description": {
                                "type": "string",
                                "description": "Description of what the code does"
                            },
                            "file_path": {
                                "type": "string",
                                "description": "File path where the code is located"
                            },
                            "tags": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": "Tags for categorization"
                            }
                        },
                        "required": ["code", "language", "description"]
                    }
                ),
                Tool(
                    name="explain_code",
                    description="Get explanations for code patterns from memory",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "code_query": {
                                "type": "string",
                                "description": "Description of the code pattern to explain"
                            },
                            "language": {
                                "type": "string",
                                "description": "Programming language to focus on"
                            }
                        },
                        "required": ["code_query"]
                    }
                ),
                Tool(
                    name="cascade_interaction",
                    description="Log interaction with Windsurf Cascade AI",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "interaction_type": {
                                "type": "string",
                                "enum": ["question", "code_generation", "refactoring", "debugging"],
                                "description": "Type of Cascade interaction"
                            },
                            "content": {
                                "type": "string",
                                "description": "Content of the interaction"
                            },
                            "result": {
                                "type": "string",
                                "description": "Result or outcome of the interaction"
                            }
                        },
                        "required": ["interaction_type", "content"]
                    }
                )
            ]
            
            return base_tools + windsurf_tools
        
        @self.server.call_tool()
        async def handle_windsurf_tools(name: str, arguments: Dict[str, Any]) -> List[TextContent]:
            """Handle Windsurf-specific tool calls"""
            
            if name == "save_code_snippet":
                return await self._handle_save_code_snippet(arguments)
            elif name == "explain_code":
                return await self._handle_explain_code(arguments)
            elif name == "cascade_interaction":
                return await self._handle_cascade_interaction(arguments)
            else:
                # Call parent handler for base tools
                return await super(WindsurfMCPServer, self).server._call_tool_handler(name, arguments)
    
    async def _handle_save_code_snippet(self, arguments: Dict[str, Any]) -> List[TextContent]:
        """Handle save_code_snippet tool call"""
        code = arguments.get("code", "")
        language = arguments.get("language", "")
        description = arguments.get("description", "")
        file_path = arguments.get("file_path", "")
        tags = arguments.get("tags", [])
        
        if not code.strip():
            return [TextContent(type="text", text="❌ Cannot save empty code snippet")]
        
        # Create enriched content
        content = f"Code Snippet ({language}):\n"
        content += f"Description: {description}\n"
        if file_path:
            content += f"File: {file_path}\n"
        content += f"\n```{language}\n{code}\n```"
        
        # Enhanced context for code snippets
        context = {
            "category": "code_snippet",
            "importance": 0.8,  # Code snippets are generally important
            "tags": tags + [f"lang_{language}", "windsurf_code"],
            "language": language,
            "file_path": file_path,
            "windsurf_type": "code_snippet"
        }
        
        # Save using base functionality
        save_result = await self._handle_save_memory({
            "content": content,
            "context": context
        })
        
        self.windsurf_stats['code_snippets_saved'] += 1
        
        result = f"🌪️ Code snippet saved to Windsurf memory!\n"
        result += f"   Language: {language}\n"
        result += f"   Description: {description}\n"
        result += f"   Lines: {len(code.split())}\n"
        result += f"   Tags: {', '.join(tags)}\n"
        
        return [TextContent(type="text", text=result)]
    
    async def _handle_explain_code(self, arguments: Dict[str, Any]) -> List[TextContent]:
        """Handle explain_code tool call"""
        code_query = arguments.get("code_query", "")
        language = arguments.get("language", "")
        
        if not code_query.strip():
            return [TextContent(type="text", text="❌ Cannot search with empty code query")]
        
        # Enhanced search for code explanations
        search_query = f"{code_query} {language} code explanation"
        
        search_result = await self._handle_search_memory({
            "query": search_query,
            "limit": 5,
            "min_similarity": 0.1
        })
        
        # Add Windsurf-specific context
        result = f"🌪️ Windsurf Code Explanation Search:\n"
        result += f"Query: {code_query}\n"
        if language:
            result += f"Language: {language}\n"
        result += "\n" + search_result[0].text
        
        return [TextContent(type="text", text=result)]
    
    async def _handle_cascade_interaction(self, arguments: Dict[str, Any]) -> List[TextContent]:
        """Handle cascade_interaction tool call"""
        interaction_type = arguments.get("interaction_type", "")
        content = arguments.get("content", "")
        result_text = arguments.get("result", "")
        
        self.windsurf_stats['cascade_interactions'] += 1
        
        # Create memory content
        memory_content = f"Windsurf Cascade Interaction ({interaction_type}):\n"
        memory_content += f"Input: {content}\n"
        if result_text:
            memory_content += f"Result: {result_text}\n"
        
        # Save interaction
        context = {
            "category": "cascade_interaction",
            "importance": 0.7,
            "tags": [f"cascade_{interaction_type}", "windsurf_ai", "interaction"],
            "interaction_type": interaction_type,
            "windsurf_type": "cascade_interaction"
        }
        
        await self._handle_save_memory({
            "content": memory_content,
            "context": context
        })
        
        result = f"🌪️ Cascade interaction logged!\n"
        result += f"   Type: {interaction_type}\n"
        result += f"   Content length: {len(content)} chars\n"
        result += f"   Total Cascade interactions: {self.windsurf_stats['cascade_interactions']}\n"
        
        return [TextContent(type="text", text=result)]
    
    def _check_deterministic_triggers(self, message: str) -> Dict:
        """Enhanced deterministic triggers for Windsurf"""
        base_result = super()._check_deterministic_triggers(message)
        
        message_lower = message.lower()
        windsurf_triggers = []
        
        # Code-specific triggers
        code_words = [
            'function', 'class', 'method', 'variable', 'algorithm',
            'pattern', 'refactor', 'optimize', 'debug', 'error',
            'exception', 'syntax', 'logic', 'performance'
        ]
        
        for word in code_words:
            if word in message_lower:
                windsurf_triggers.append(f"code_{word}")
        
        # Windsurf Cascade specific
        cascade_words = ['cascade', 'ai assistant', 'windsurf', 'explain code', 'generate']
        for word in cascade_words:
            if word in message_lower:
                windsurf_triggers.append(f"cascade_{word.replace(' ', '_')}")
        
        # Programming languages
        languages = ['python', 'javascript', 'typescript', 'react', 'vue', 'css', 'html', 'sql', 'java', 'cpp', 'go', 'rust']
        for lang in languages:
            if lang in message_lower:
                windsurf_triggers.append(f"lang_{lang}")
        
        # Combine with base triggers
        all_triggers = base_result['triggers'] + windsurf_triggers
        
        # Enhanced save logic for code content
        should_save = base_result['should_save'] or len(windsurf_triggers) > 0
        
        return {
            "triggers": all_triggers,
            "should_save": should_save,
            "should_search": base_result['should_search'],
            "confidence": 0.9 if all_triggers else 0.1,
            "windsurf_triggers": windsurf_triggers
        }


async def main():
    """Main entry point for Windsurf MCP Server"""
    print("🌪️ WINDSURF CASCADE IDE - TRUE MCP SERVER")
    print("=" * 50)
    print("✅ Implementing standard MCP protocol")
    print("🤖 ML auto-triggers with Cascade AI optimization")
    print("💻 Code-aware memory management")
    print("📡 Native MCP integration ready")
    
    await run_mcp_server("windsurf")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Windsurf MCP Server stopped")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
