#!/usr/bin/env python3
"""
Cursor IDE MCP Server - True MCP Protocol Implementation
Optimized for Cursor IDE with real-time code assistance
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
os.environ.setdefault("CURSOR_MODE", "true")


class CursorMCPServer(MCPMemoryServer):
    """MCP Server optimized for Cursor IDE"""
    
    def __init__(self):
        super().__init__("cursor")
        self.cursor_stats = {
            'code_assists': 0,
            'tab_completions': 0,
            'ai_interactions': 0
        }
        
        # Add Cursor-specific tools
        self._add_cursor_tools()
        
        print("🎯 Cursor MCP Server initialized with IDE optimization")
    
    def _add_cursor_tools(self):
        """Add Cursor-specific MCP tools"""
        
        @self.server.list_tools()
        async def handle_cursor_tools() -> List[Tool]:
            """Extended tool list for Cursor IDE"""
            base_tools = await super(CursorMCPServer, self).server._list_tools_handler()
            
            cursor_tools = [
                Tool(
                    name="cursor_code_assist",
                    description="Log Cursor AI code assistance interactions",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "file_path": {
                                "type": "string",
                                "description": "File being edited"
                            },
                            "user_input": {
                                "type": "string",
                                "description": "User's request or selection"
                            },
                            "ai_suggestion": {
                                "type": "string",
                                "description": "AI's code suggestion"
                            },
                            "accepted": {
                                "type": "boolean",
                                "description": "Whether user accepted the suggestion"
                            },
                            "language": {
                                "type": "string",
                                "description": "Programming language"
                            }
                        },
                        "required": ["user_input", "ai_suggestion", "accepted"]
                    }
                ),
                Tool(
                    name="save_cursor_session",
                    description="Save important Cursor editing session",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "session_summary": {
                                "type": "string",
                                "description": "Summary of what was accomplished"
                            },
                            "files_modified": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": "List of files that were modified"
                            },
                            "key_changes": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": "Key changes made during session"
                            },
                            "ai_assists_used": {
                                "type": "integer",
                                "description": "Number of AI assists used"
                            }
                        },
                        "required": ["session_summary"]
                    }
                )
            ]
            
            return base_tools + cursor_tools
        
        @self.server.call_tool()
        async def handle_cursor_tools(name: str, arguments: Dict[str, Any]) -> List[TextContent]:
            """Handle Cursor-specific tool calls"""
            
            if name == "cursor_code_assist":
                return await self._handle_cursor_code_assist(arguments)
            elif name == "save_cursor_session":
                return await self._handle_save_cursor_session(arguments)
            else:
                # Call parent handler for base tools
                return await super(CursorMCPServer, self).server._call_tool_handler(name, arguments)
    
    async def _handle_cursor_code_assist(self, arguments: Dict[str, Any]) -> List[TextContent]:
        """Handle cursor_code_assist tool call"""
        file_path = arguments.get("file_path", "")
        user_input = arguments.get("user_input", "")
        ai_suggestion = arguments.get("ai_suggestion", "")
        accepted = arguments.get("accepted", False)
        language = arguments.get("language", "")
        
        self.cursor_stats['code_assists'] += 1
        if accepted:
            self.cursor_stats['tab_completions'] += 1
        
        # Create code assist log
        content = f"Cursor AI Code Assistance\n\n"
        if file_path:
            content += f"**File:** {file_path}\n"
        if language:
            content += f"**Language:** {language}\n"
        content += f"**Status:** {'✅ Accepted' if accepted else '❌ Rejected'}\n\n"
        content += f"**User Request:**\n{user_input}\n\n"
        content += f"**AI Suggestion:**\n```{language}\n{ai_suggestion}\n```\n"
        
        # Code assist context
        context = {
            "category": "code_assistance",
            "importance": 0.8 if accepted else 0.4,
            "tags": ["cursor_ai", "code_assist", f"lang_{language}", "accepted" if accepted else "rejected"],
            "file_path": file_path,
            "language": language,
            "accepted": accepted,
            "cursor_type": "code_assistance"
        }
        
        # Save code assist
        await self._handle_save_memory({
            "content": content,
            "context": context
        })
        
        result = f"🎯 Cursor code assist logged!\n"
        result += f"   File: {file_path}\n"
        result += f"   Language: {language}\n"
        result += f"   Status: {'✅ Accepted' if accepted else '❌ Rejected'}\n"
        result += f"   Total assists: {self.cursor_stats['code_assists']}\n"
        
        return [TextContent(type="text", text=result)]
    
    async def _handle_save_cursor_session(self, arguments: Dict[str, Any]) -> List[TextContent]:
        """Handle save_cursor_session tool call"""
        session_summary = arguments.get("session_summary", "")
        files_modified = arguments.get("files_modified", [])
        key_changes = arguments.get("key_changes", [])
        ai_assists_used = arguments.get("ai_assists_used", 0)
        
        # Create session log
        content = f"Cursor Editing Session\n\n"
        content += f"**Summary:** {session_summary}\n\n"
        
        if files_modified:
            content += f"**Files Modified:** ({len(files_modified)})\n"
            for file in files_modified:
                content += f"  • {file}\n"
            content += "\n"
        
        if key_changes:
            content += f"**Key Changes:**\n"
            for change in key_changes:
                content += f"  • {change}\n"
            content += "\n"
        
        if ai_assists_used:
            content += f"**AI Assists Used:** {ai_assists_used}\n"
        
        # Session context
        context = {
            "category": "editing_session",
            "importance": 0.7,
            "tags": ["cursor_session", "editing", "productivity"],
            "files_count": len(files_modified),
            "changes_count": len(key_changes),
            "ai_assists": ai_assists_used,
            "cursor_type": "editing_session"
        }
        
        # Save session
        await self._handle_save_memory({
            "content": content,
            "context": context
        })
        
        result = f"🎯 Cursor session saved!\n"
        result += f"   Files modified: {len(files_modified)}\n"
        result += f"   Key changes: {len(key_changes)}\n"
        result += f"   AI assists: {ai_assists_used}\n"
        
        return [TextContent(type="text", text=result)]


async def main():
    """Main entry point for Cursor MCP Server"""
    print("🎯 CURSOR IDE - TRUE MCP SERVER")
    print("=" * 50)
    print("✅ Implementing standard MCP protocol")
    print("🤖 ML auto-triggers with IDE optimization")
    print("💻 Real-time code assistance tracking")
    print("📡 Native MCP integration ready")
    
    await run_mcp_server("cursor")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Cursor MCP Server stopped")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
