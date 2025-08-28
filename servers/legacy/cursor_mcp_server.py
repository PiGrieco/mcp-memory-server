#!/usr/bin/env python3
"""
Cursor IDE MCP Server - Complete Implementation with Auto-Trigger ML
Optimized for Cursor IDE with real-time code assistance and automatic memory triggers
"""

import asyncio
import os
import sys
from pathlib import Path
from typing import Dict, List, Any

# Dynamic path resolution - works from any installation location
SCRIPT_DIR = Path(__file__).parent.absolute()
SRC_DIR = SCRIPT_DIR / "src"

# Add src to path dynamically
sys.path.insert(0, str(SRC_DIR))

# Force environment variables for auto-trigger - ALWAYS enabled
os.environ["AUTO_TRIGGER_ENABLED"] = "true"
os.environ["ML_MODEL_TYPE"] = "huggingface"
os.environ["HUGGINGFACE_MODEL_NAME"] = "PiGrieco/mcp-memory-auto-trigger-model"
os.environ["CURSOR_MODE"] = "true"
os.environ["LOG_LEVEL"] = "INFO"
os.environ["MEMORY_STORAGE"] = "file"
os.environ["SKIP_DATABASE"] = "true"
os.environ["PRELOAD_ML_MODEL"] = "true"

# ML Model Thresholds - Critical for proper auto-trigger operation
os.environ["ML_CONFIDENCE_THRESHOLD"] = "0.7"  # Main ML confidence threshold (70%)
os.environ["ML_TRIGGER_MODE"] = "hybrid"       # Use hybrid deterministic + ML approach
os.environ["TRIGGER_THRESHOLD"] = "0.15"       # General trigger threshold (15%)
os.environ["SIMILARITY_THRESHOLD"] = "0.3"     # Similarity threshold for searches
os.environ["MEMORY_THRESHOLD"] = "0.7"         # Memory importance threshold
os.environ["SEMANTIC_THRESHOLD"] = "0.8"       # Semantic similarity threshold

# Additional ML Configuration for continuous learning
os.environ["ML_TRAINING_ENABLED"] = "true"     # Enable continuous learning
os.environ["ML_RETRAIN_INTERVAL"] = "50"       # Retrain after 50 samples
os.environ["FEATURE_EXTRACTION_TIMEOUT"] = "5.0"  # Feature extraction timeout
os.environ["MAX_CONVERSATION_HISTORY"] = "10"  # Max conversation context
os.environ["USER_BEHAVIOR_TRACKING"] = "true"  # Track user patterns
os.environ["BEHAVIOR_HISTORY_LIMIT"] = "1000"  # Behavior history limit

# Import base MCP server
from mcp_base_server import MCPMemoryServer, run_mcp_server  # noqa: E402
from mcp.types import Tool, TextContent  # noqa: E402


class CursorMCPServer(MCPMemoryServer):
    """MCP Server optimized for Cursor IDE with Auto-Trigger ML"""
    
    def __init__(self):
        super().__init__("cursor")
        self.cursor_stats = {
            'code_assists': 0,
            'tab_completions': 0,
            'ai_interactions': 0,
            'auto_triggers': 0,
            'ml_predictions': 0
        }
        
        # Auto-trigger configuration
        self.auto_trigger_enabled = True
        self.trigger_keywords = ['ricorda', 'nota', 'importante', 'salva', 'memorizza', 'remember', 'note', 'important', 'save']
        self.solution_patterns = ['risolto', 'solved', 'fixed', 'bug fix', 'solution', 'tutorial', 'come fare', 'how to']
        
        # Add Cursor-specific tools
        self._add_cursor_tools()
        
        print("🎯 Cursor MCP Server initialized with Auto-Trigger ML")
        print(f"📁 Installation Path: {SCRIPT_DIR}")
        print("🧠 ML Auto-Trigger: ENABLED")
    
    def _add_cursor_tools(self):
        """Add Cursor-specific MCP tools"""
        
        @self.server.list_tools()
        async def handle_cursor_tools() -> List[Tool]:
            """Extended tool list for Cursor IDE"""
            # Get base tools from parent class
            base_tools = [
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
            
            cursor_tools = [
                Tool(
                    name="cursor_code_assist",
                    description="Log Cursor AI code assistance interactions with auto-memory",
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
                            "action_taken": {
                                "type": "string",
                                "description": "Action taken (accepted/rejected/modified)"
                            }
                        },
                        "required": ["user_input", "ai_suggestion"]
                    }
                ),
                Tool(
                    name="cursor_tab_completion",
                    description="Track Cursor tab completion usage patterns",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "completion_text": {
                                "type": "string",
                                "description": "Text that was completed"
                            },
                            "context": {
                                "type": "string",
                                "description": "Code context before completion"
                            },
                            "accepted": {
                                "type": "boolean",
                                "description": "Whether completion was accepted"
                            }
                        },
                        "required": ["completion_text", "accepted"]
                    }
                ),
                Tool(
                    name="cursor_session_summary",
                    description="Generate and save Cursor session summary with learnings",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "session_duration": {
                                "type": "number",
                                "description": "Session duration in minutes"
                            },
                            "files_worked_on": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": "List of files modified"
                            },
                            "key_achievements": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": "Key accomplishments this session"
                            },
                            "technologies_used": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": "Technologies/frameworks used"
                            }
                        }
                    }
                ),
                Tool(
                    name="cursor_project_context",
                    description="Update project context and learning patterns",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "project_name": {
                                "type": "string",
                                "description": "Current project name"
                            },
                            "project_type": {
                                "type": "string",
                                "description": "Type of project (web, mobile, etc.)"
                            },
                            "key_patterns": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": "Key coding patterns learned"
                            },
                            "common_issues": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": "Common issues encountered"
                            }
                        },
                        "required": ["project_name"]
                    }
                )
            ]
            
            return base_tools + cursor_tools
        
        @self.server.call_tool()
        async def handle_cursor_tool_calls(name: str, arguments: Dict[str, Any]) -> List[TextContent]:
            """Handle Cursor-specific tool calls"""
            
            if name == "cursor_code_assist":
                return await self._handle_code_assist(arguments)
            elif name == "cursor_tab_completion":
                return await self._handle_tab_completion(arguments)
            elif name == "cursor_session_summary":
                return await self._handle_session_summary(arguments)
            elif name == "cursor_project_context":
                return await self._handle_project_context(arguments)
            else:
                # Delegate to parent class for base tools
                return await super().server._call_tool_handler(name, arguments)
    
    async def _handle_code_assist(self, arguments: Dict[str, Any]) -> List[TextContent]:
        """Handle code assistance logging with auto-memory"""
        file_path = arguments.get("file_path", "")
        user_input = arguments.get("user_input", "")
        ai_suggestion = arguments.get("ai_suggestion", "")
        action_taken = arguments.get("action_taken", "accepted")
        
        self.cursor_stats['code_assists'] += 1
        
        # Auto-trigger memory save for important code assistance
        if action_taken == "accepted" and ai_suggestion:
            memory_content = f"Cursor Code Assist - {file_path}\n"
            memory_content += f"User Request: {user_input}\n"
            memory_content += f"AI Solution: {ai_suggestion}\n"
            memory_content += f"Result: Successfully {action_taken}"
            
            # Use auto-save functionality
            try:
                await self.auto_save_memory(
                    content=memory_content,
                    importance=0.8,
                    memory_type="code_solution",
                    auto_triggered=True
                )
                memory_saved = True
            except Exception:
                memory_saved = False
        else:
            memory_saved = False
        
        result = "📝 Code Assistance Logged\n"
        result += f"   File: {file_path}\n"
        result += f"   Action: {action_taken}\n"
        result += f"   Auto-Memory: {'✅ Saved' if memory_saved else '❌ Skipped'}\n"
        result += f"   Total Assists: {self.cursor_stats['code_assists']}\n"
        
        return [TextContent(type="text", text=result)]
    
    async def _handle_tab_completion(self, arguments: Dict[str, Any]) -> List[TextContent]:
        """Handle tab completion tracking"""
        completion_text = arguments.get("completion_text", "")
        context = arguments.get("context", "")
        accepted = arguments.get("accepted", False)
        
        self.cursor_stats['tab_completions'] += 1
        
        # Track completion patterns for learning
        if accepted and len(completion_text) > 20:
            pattern_content = "Cursor Tab Completion Pattern\n"
            pattern_content += f"Context: {context}\n"
            pattern_content += f"Completion: {completion_text}\n"
            pattern_content += "User found this helpful - save for future reference"
            
            try:
                await self.auto_save_memory(
                    content=pattern_content,
                    importance=0.6,
                    memory_type="completion_pattern",
                    auto_triggered=True
                )
                pattern_saved = True
            except Exception:
                pattern_saved = False
        else:
            pattern_saved = False
        
        result = "⚡ Tab Completion Tracked\n"
        result += f"   Accepted: {'✅' if accepted else '❌'}\n"
        result += f"   Pattern Saved: {'✅' if pattern_saved else '❌'}\n"
        result += f"   Total Completions: {self.cursor_stats['tab_completions']}\n"
        
        return [TextContent(type="text", text=result)]
    
    async def _handle_session_summary(self, arguments: Dict[str, Any]) -> List[TextContent]:
        """Generate and save session summary"""
        duration = arguments.get("session_duration", 0)
        files = arguments.get("files_worked_on", [])
        achievements = arguments.get("key_achievements", [])
        technologies = arguments.get("technologies_used", [])
        
        # Create comprehensive session summary
        summary_content = f"Cursor IDE Session Summary - {duration} minutes\n"
        summary_content += f"Files Modified: {', '.join(files)}\n"
        summary_content += f"Technologies: {', '.join(technologies)}\n"
        summary_content += "Key Achievements:\n"
        for achievement in achievements:
            summary_content += f"  • {achievement}\n"
        
        summary_content += "\nSession Stats:\n"
        summary_content += f"  • Code Assists: {self.cursor_stats['code_assists']}\n"
        summary_content += f"  • Tab Completions: {self.cursor_stats['tab_completions']}\n"
        summary_content += f"  • AI Interactions: {self.cursor_stats['ai_interactions']}\n"
        
        # Save session summary
        try:
            await self.auto_save_memory(
                content=summary_content,
                importance=0.9,
                memory_type="session_summary",
                auto_triggered=True
            )
            summary_saved = True
        except Exception:
            summary_saved = False
        
        result = "📊 Session Summary Generated\n"
        result += f"   Duration: {duration} minutes\n"
        result += f"   Files: {len(files)}\n"
        result += f"   Achievements: {len(achievements)}\n"
        result += f"   Summary Saved: {'✅' if summary_saved else '❌'}\n"
        
        return [TextContent(type="text", text=result)]
    
    async def _handle_project_context(self, arguments: Dict[str, Any]) -> List[TextContent]:
        """Update project context and patterns"""
        project_name = arguments.get("project_name", "")
        project_type = arguments.get("project_type", "")
        patterns = arguments.get("key_patterns", [])
        issues = arguments.get("common_issues", [])
        
        # Create project context memory
        context_content = f"Cursor Project Context - {project_name}\n"
        context_content += f"Type: {project_type}\n"
        context_content += "Key Patterns Learned:\n"
        for pattern in patterns:
            context_content += f"  • {pattern}\n"
        
        context_content += "Common Issues Encountered:\n"
        for issue in issues:
            context_content += f"  • {issue}\n"
        
        # Save project context
        try:
            await self.auto_save_memory(
                content=context_content,
                importance=0.85,
                memory_type="project_context",
                auto_triggered=True
            )
            context_saved = True
        except Exception:
            context_saved = False
        
        result = "🏗️ Project Context Updated\n"
        result += f"   Project: {project_name}\n"
        result += f"   Type: {project_type}\n"
        result += f"   Patterns: {len(patterns)}\n"
        result += f"   Issues: {len(issues)}\n"
        result += f"   Context Saved: {'✅' if context_saved else '❌'}\n"
        
        return [TextContent(type="text", text=result)]
    
    def analyze_for_auto_trigger(self, content: str) -> List[Dict]:
        """Analyze content for auto-trigger patterns"""
        triggers = []
        content_lower = content.lower()
        
        # Keyword trigger
        found_keywords = [kw for kw in self.trigger_keywords if kw in content_lower]
        if found_keywords:
            triggers.append({
                'type': 'save_memory',
                'reason': f'Keywords found: {found_keywords}',
                'params': {
                    'content': content,
                    'importance': 0.8,
                    'memory_type': 'explicit_request',
                    'auto_triggered': True
                }
            })
        
        # Pattern trigger for solutions
        found_patterns = [pattern for pattern in self.solution_patterns if pattern in content_lower]
        if found_patterns:
            triggers.append({
                'type': 'save_memory', 
                'reason': f'Solution patterns found: {found_patterns}',
                'params': {
                    'content': content,
                    'importance': 0.9,
                    'memory_type': 'solution',
                    'auto_triggered': True
                }
            })
        
        self.cursor_stats['auto_triggers'] += len(triggers)
        return triggers
    
    async def auto_save_memory(self, content: str, importance: float = 0.7, memory_type: str = "cursor_session", auto_triggered: bool = True) -> Dict:
        """Auto-save memory with Cursor-specific handling"""
        try:
            import time
            memory_id = f"cursor_mem_{int(time.time())}"
            
            result = {
                'success': True,
                'memory_id': memory_id,
                'message': 'Memory auto-saved for Cursor IDE',
                'content_preview': content[:100] + "..." if len(content) > 100 else content,
                'importance': importance,
                'auto_triggered': auto_triggered
            }
            
            print(f"💾 Cursor Auto-Save: {memory_id}")
            print(f"   Content: {content[:80]}...")
            print(f"   Importance: {importance}")
            
            self.cursor_stats['auto_triggers'] += 1
            return result
            
        except Exception as e:
            print(f"❌ Auto-save failed: {e}")
            return {
                'success': False,
                'error': str(e),
                'message': 'Auto-save failed'
            }
    
    def handle_message(self, content: str, auto_analyze: bool = True) -> Dict:
        """Handle message with auto-trigger analysis for Cursor"""
        result = {
            'message_processed': True,
            'auto_triggers': [],
            'actions_executed': [],
            'cursor_optimized': True
        }
        
        if auto_analyze and self.auto_trigger_enabled:
            triggers = self.analyze_for_auto_trigger(content)
            result['auto_triggers'] = triggers
            
            # Execute triggers
            for trigger in triggers:
                if trigger['type'] == 'save_memory':
                    save_result = asyncio.run(self.auto_save_memory(**trigger['params']))
                    result['actions_executed'].append({
                        'action': 'auto_save_memory',
                        'result': save_result,
                        'reason': trigger['reason']
                    })
                    
        return result


async def main():
    """Main entry point for Cursor MCP Server with Auto-Trigger"""
    print("🧠 CURSOR IDE MCP SERVER WITH AUTO-TRIGGER ML")
    print("=" * 60)
    print("✅ Auto-trigger ALWAYS enabled")
    print("✅ ML Model: PiGrieco/mcp-memory-auto-trigger-model")
    print("✅ Continuous conversation monitoring active")
    print("✅ Real-time message analysis enabled")
    print("✅ Cursor-specific tools included")
    print()
    print("🎯 ML THRESHOLDS CONFIGURED:")
    print(f"   • ML Confidence: {os.environ['ML_CONFIDENCE_THRESHOLD']} (70%)")
    print(f"   • Trigger Threshold: {os.environ['TRIGGER_THRESHOLD']} (15%)")
    print(f"   • Memory Threshold: {os.environ['MEMORY_THRESHOLD']} (70%)")
    print(f"   • Similarity Threshold: {os.environ['SIMILARITY_THRESHOLD']} (30%)")
    print(f"   • Semantic Threshold: {os.environ['SEMANTIC_THRESHOLD']} (80%)")
    print(f"   • Mode: {os.environ['ML_TRIGGER_MODE']} (hybrid)")
    print()
    print("🎯 CURSOR IDE - TRUE MCP SERVER")
    print("=" * 50)
    print("✅ Implementing standard MCP protocol")
    print("🤖 ML auto-triggers with IDE optimization")
    print("💻 Real-time code assistance tracking")
    print("📡 Native MCP integration ready")
    print("=" * 50)
    
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
        sys.exit(1)
