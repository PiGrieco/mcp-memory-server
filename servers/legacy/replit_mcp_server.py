#!/usr/bin/env python3
"""
Replit Cloud IDE MCP Server - True MCP Protocol Implementation
Optimized for Replit cloud development with collaboration features
"""

import asyncio
import os
import sys
from pathlib import Path
from typing import Dict, List, Any
from datetime import datetime

# Dynamic path resolution - works from any installation location
SCRIPT_DIR = Path(__file__).parent.absolute()
SRC_DIR = SCRIPT_DIR / "src"

# Add src to path dynamically
sys.path.insert(0, str(SRC_DIR))

# Force environment variables for auto-trigger - ALWAYS enabled
os.environ["AUTO_TRIGGER_ENABLED"] = "true"
os.environ["ML_MODEL_TYPE"] = "huggingface"
os.environ["HUGGINGFACE_MODEL_NAME"] = "PiGrieco/mcp-memory-auto-trigger-model"
os.environ["REPLIT_MODE"] = "true"
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


class ReplitMCPServer(MCPMemoryServer):
    """MCP Server optimized for Replit cloud development environment"""
    
    def __init__(self):
        super().__init__("replit")
        self.replit_stats = {
            'repls_tracked': 0,
            'collaborations_logged': 0,
            'deployments_documented': 0,
            'code_runs_logged': 0
        }
        
        # Auto-trigger configuration
        self.auto_trigger_enabled = True
        self.trigger_keywords = ['ricorda', 'nota', 'importante', 'salva', 'memorizza', 'remember', 'note', 'important', 'save']
        self.solution_patterns = ['risolto', 'solved', 'fixed', 'bug fix', 'solution', 'tutorial', 'come fare', 'how to']
        
        # Add Replit-specific tools
        self._add_replit_tools()
        
        print("⚡ Replit MCP Server initialized with cloud collaboration features")
    
    def _add_replit_tools(self):
        """Add Replit-specific MCP tools"""
        
        @self.server.list_tools()
        async def list_replit_tools() -> List[Tool]:
            """Extended tool list for Replit Cloud IDE"""
            base_tools = await super(ReplitMCPServer, self).server._list_tools_handler()
            
            replit_tools = [
                Tool(
                    name="track_repl",
                    description="Track Replit project development and collaboration",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "repl_name": {
                                "type": "string",
                                "description": "Name of the Repl"
                            },
                            "language": {
                                "type": "string",
                                "description": "Primary programming language"
                            },
                            "description": {
                                "type": "string",
                                "description": "What the Repl does"
                            },
                            "collaborators": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": "List of collaborator usernames"
                            },
                            "progress_update": {
                                "type": "string",
                                "description": "Latest progress or changes made"
                            },
                            "is_public": {
                                "type": "boolean",
                                "description": "Whether the Repl is public"
                            },
                            "packages_used": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": "Packages/dependencies used"
                            }
                        },
                        "required": ["repl_name", "language", "description"]
                    }
                ),
                Tool(
                    name="log_collaboration",
                    description="Log collaboration activities in a Repl",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "repl_name": {
                                "type": "string",
                                "description": "Name of the Repl"
                            },
                            "collaborator": {
                                "type": "string",
                                "description": "Username of the collaborator"
                            },
                            "action": {
                                "type": "string",
                                "enum": ["joined", "left", "edited_file", "ran_code", "added_comment", "merged_changes"],
                                "description": "Type of collaboration action"
                            },
                            "details": {
                                "type": "string",
                                "description": "Details about the action"
                            },
                            "file_path": {
                                "type": "string",
                                "description": "File that was affected (if applicable)"
                            },
                            "timestamp": {
                                "type": "string",
                                "description": "Timestamp of the action"
                            }
                        },
                        "required": ["repl_name", "collaborator", "action"]
                    }
                ),
                Tool(
                    name="save_code_run",
                    description="Save successful code runs and their outputs",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "repl_name": {
                                "type": "string",
                                "description": "Name of the Repl"
                            },
                            "code_snippet": {
                                "type": "string",
                                "description": "Code that was run"
                            },
                            "output": {
                                "type": "string",
                                "description": "Output of the code execution"
                            },
                            "language": {
                                "type": "string",
                                "description": "Programming language"
                            },
                            "execution_time": {
                                "type": "number",
                                "description": "Execution time in seconds"
                            },
                            "success": {
                                "type": "boolean",
                                "description": "Whether the execution was successful"
                            },
                            "error_message": {
                                "type": "string",
                                "description": "Error message if execution failed"
                            }
                        },
                        "required": ["repl_name", "code_snippet", "language", "success"]
                    }
                ),
                Tool(
                    name="document_deployment",
                    description="Document Repl deployment and hosting information",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "repl_name": {
                                "type": "string",
                                "description": "Name of the deployed Repl"
                            },
                            "deployment_url": {
                                "type": "string",
                                "description": "URL where the Repl is deployed"
                            },
                            "deployment_type": {
                                "type": "string",
                                "enum": ["web_app", "api", "bot", "script", "game"],
                                "description": "Type of deployment"
                            },
                            "environment_vars": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": "Environment variables used (names only, not values)"
                            },
                            "custom_domain": {
                                "type": "string",
                                "description": "Custom domain if configured"
                            },
                            "performance_notes": {
                                "type": "string",
                                "description": "Notes about performance or configuration"
                            }
                        },
                        "required": ["repl_name", "deployment_url", "deployment_type"]
                    }
                ),
                Tool(
                    name="search_repl_history",
                    description="Search through Repl development history",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "query": {
                                "type": "string",
                                "description": "Search query"
                            },
                            "repl_name": {
                                "type": "string",
                                "description": "Specific Repl to search in"
                            },
                            "language": {
                                "type": "string",
                                "description": "Filter by programming language"
                            },
                            "activity_type": {
                                "type": "string",
                                "enum": ["code_run", "collaboration", "deployment", "general"],
                                "description": "Type of activity to search for"
                            },
                            "collaborator": {
                                "type": "string",
                                "description": "Filter by specific collaborator"
                            }
                        },
                        "required": ["query"]
                    }
                )
            ]
            
            return base_tools + replit_tools
        
        @self.server.call_tool()
        async def handle_replit_tools(name: str, arguments: Dict[str, Any]) -> List[TextContent]:
            """Handle Replit-specific tool calls"""
            
            if name == "track_repl":
                return await self._handle_track_repl(arguments)
            elif name == "log_collaboration":
                return await self._handle_log_collaboration(arguments)
            elif name == "save_code_run":
                return await self._handle_save_code_run(arguments)
            elif name == "document_deployment":
                return await self._handle_document_deployment(arguments)
            elif name == "search_repl_history":
                return await self._handle_search_repl_history(arguments)
            else:
                # Call parent handler for base tools
                return await super(ReplitMCPServer, self).server._call_tool_handler(name, arguments)
    
    async def _handle_track_repl(self, arguments: Dict[str, Any]) -> List[TextContent]:
        """Handle track_repl tool call"""
        repl_name = arguments.get("repl_name", "")
        language = arguments.get("language", "")
        description = arguments.get("description", "")
        collaborators = arguments.get("collaborators", [])
        progress_update = arguments.get("progress_update", "")
        is_public = arguments.get("is_public", False)
        packages_used = arguments.get("packages_used", [])
        
        if not repl_name.strip():
            return [TextContent(type="text", text="❌ Repl name is required")]
        
        self.replit_stats['repls_tracked'] += 1
        
        # Create Repl tracking content
        content = f"Repl Project: {repl_name}\n\n"
        content += f"**Language:** {language}\n"
        content += f"**Description:** {description}\n"
        content += f"**Visibility:** {'Public' if is_public else 'Private'}\n\n"
        
        if collaborators:
            content += f"**Collaborators:** {', '.join(collaborators)}\n\n"
        
        if packages_used:
            content += "**Packages/Dependencies:**\n"
            for package in packages_used:
                content += f"  • {package}\n"
            content += "\n"
        
        if progress_update:
            content += f"**Latest Update:** {progress_update}\n"
        
        # Repl context
        context = {
            "category": "repl_project",
            "importance": 0.7,
            "tags": ["repl", "project", f"lang_{language}"] + packages_used,
            "repl_name": repl_name,
            "language": language,
            "collaborators": collaborators,
            "replit_type": "repl_project"
        }
        
        # Save Repl info
        await self._handle_save_memory({
            "content": content,
            "context": context
        })
        
        result = "⚡ Repl project tracked!\n"
        result += f"   Name: {repl_name} ({language})\n"
        result += f"   Collaborators: {len(collaborators)}\n"
        result += f"   Packages: {len(packages_used)}\n"
        result += f"   Total Repls tracked: {self.replit_stats['repls_tracked']}\n"
        
        return [TextContent(type="text", text=result)]
    
    async def _handle_log_collaboration(self, arguments: Dict[str, Any]) -> List[TextContent]:
        """Handle log_collaboration tool call"""
        repl_name = arguments.get("repl_name", "")
        collaborator = arguments.get("collaborator", "")
        action = arguments.get("action", "")
        details = arguments.get("details", "")
        file_path = arguments.get("file_path", "")
        timestamp = arguments.get("timestamp", datetime.now().isoformat())
        
        if not repl_name.strip() or not collaborator.strip():
            return [TextContent(type="text", text="❌ Repl name and collaborator are required")]
        
        self.replit_stats['collaborations_logged'] += 1
        
        # Create collaboration log
        content = f"Collaboration Activity in {repl_name}\n\n"
        content += f"**Collaborator:** {collaborator}\n"
        content += f"**Action:** {action}\n"
        content += f"**Timestamp:** {timestamp}\n"
        
        if details:
            content += f"**Details:** {details}\n"
        
        if file_path:
            content += f"**File:** {file_path}\n"
        
        # Collaboration context
        context = {
            "category": "collaboration",
            "importance": 0.6,
            "tags": ["collaboration", "repl", f"action_{action}"],
            "repl_name": repl_name,
            "collaborator": collaborator,
            "action": action,
            "replit_type": "collaboration"
        }
        
        # Save collaboration log
        await self._handle_save_memory({
            "content": content,
            "context": context
        })
        
        result = "⚡ Collaboration activity logged!\n"
        result += f"   Repl: {repl_name}\n"
        result += f"   Collaborator: {collaborator}\n"
        result += f"   Action: {action}\n"
        result += f"   Total collaborations: {self.replit_stats['collaborations_logged']}\n"
        
        return [TextContent(type="text", text=result)]
    
    async def _handle_save_code_run(self, arguments: Dict[str, Any]) -> List[TextContent]:
        """Handle save_code_run tool call"""
        repl_name = arguments.get("repl_name", "")
        code_snippet = arguments.get("code_snippet", "")
        output = arguments.get("output", "")
        language = arguments.get("language", "")
        execution_time = arguments.get("execution_time", 0)
        success = arguments.get("success", False)
        error_message = arguments.get("error_message", "")
        
        if not repl_name.strip() or not code_snippet.strip():
            return [TextContent(type="text", text="❌ Repl name and code snippet are required")]
        
        self.replit_stats['code_runs_logged'] += 1
        
        # Create code run log
        content = f"Code Execution in {repl_name}\n\n"
        content += f"**Language:** {language}\n"
        content += f"**Status:** {'✅ Success' if success else '❌ Failed'}\n"
        
        if execution_time:
            content += f"**Execution Time:** {execution_time:.3f}s\n"
        
        content += f"\n**Code:**\n```{language}\n{code_snippet}\n```\n"
        
        if success and output:
            content += f"\n**Output:**\n```\n{output}\n```\n"
        elif not success and error_message:
            content += f"\n**Error:**\n```\n{error_message}\n```\n"
        
        # Code run context
        context = {
            "category": "code_execution",
            "importance": 0.6 if success else 0.4,
            "tags": ["code_execution", "repl", f"lang_{language}", "success" if success else "error"],
            "repl_name": repl_name,
            "language": language,
            "success": success,
            "replit_type": "code_execution"
        }
        
        # Save code run
        await self._handle_save_memory({
            "content": content,
            "context": context
        })
        
        result = "⚡ Code execution logged!\n"
        result += f"   Repl: {repl_name}\n"
        result += f"   Language: {language}\n"
        result += f"   Status: {'✅ Success' if success else '❌ Failed'}\n"
        result += f"   Code length: {len(code_snippet)} chars\n"
        result += f"   Total runs logged: {self.replit_stats['code_runs_logged']}\n"
        
        return [TextContent(type="text", text=result)]
    
    async def _handle_document_deployment(self, arguments: Dict[str, Any]) -> List[TextContent]:
        """Handle document_deployment tool call"""
        repl_name = arguments.get("repl_name", "")
        deployment_url = arguments.get("deployment_url", "")
        deployment_type = arguments.get("deployment_type", "")
        environment_vars = arguments.get("environment_vars", [])
        custom_domain = arguments.get("custom_domain", "")
        performance_notes = arguments.get("performance_notes", "")
        
        if not repl_name.strip() or not deployment_url.strip():
            return [TextContent(type="text", text="❌ Repl name and deployment URL are required")]
        
        self.replit_stats['deployments_documented'] += 1
        
        # Create deployment documentation
        content = f"Deployment: {repl_name}\n\n"
        content += f"**URL:** {deployment_url}\n"
        content += f"**Type:** {deployment_type}\n"
        content += f"**Deployed:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        
        if custom_domain:
            content += f"**Custom Domain:** {custom_domain}\n\n"
        
        if environment_vars:
            content += "**Environment Variables:**\n"
            for var in environment_vars:
                content += f"  • {var}\n"
            content += "\n"
        
        if performance_notes:
            content += f"**Performance Notes:** {performance_notes}\n"
        
        # Deployment context
        context = {
            "category": "deployment",
            "importance": 0.8,
            "tags": ["deployment", "repl", deployment_type],
            "repl_name": repl_name,
            "deployment_url": deployment_url,
            "deployment_type": deployment_type,
            "replit_type": "deployment"
        }
        
        # Save deployment info
        await self._handle_save_memory({
            "content": content,
            "context": context
        })
        
        result = "⚡ Deployment documented!\n"
        result += f"   Repl: {repl_name}\n"
        result += f"   URL: {deployment_url}\n"
        result += f"   Type: {deployment_type}\n"
        result += f"   Environment vars: {len(environment_vars)}\n"
        result += f"   Total deployments: {self.replit_stats['deployments_documented']}\n"
        
        return [TextContent(type="text", text=result)]
    
    async def _handle_search_repl_history(self, arguments: Dict[str, Any]) -> List[TextContent]:
        """Handle search_repl_history tool call"""
        query = arguments.get("query", "")
        repl_name = arguments.get("repl_name")
        language = arguments.get("language")
        activity_type = arguments.get("activity_type")
        collaborator = arguments.get("collaborator")
        
        if not query.strip():
            return [TextContent(type="text", text="❌ Search query is required")]
        
        # Filter memories by Replit categories
        replit_categories = ["repl_project", "collaboration", "code_execution", "deployment"]
        filtered_memories = [
            memory for memory in self.memories.values()
            if memory.get('context', {}).get('category') in replit_categories
        ]
        
        # Apply filters
        if repl_name:
            filtered_memories = [
                memory for memory in filtered_memories
                if memory.get('context', {}).get('repl_name') == repl_name
            ]
        
        if language:
            filtered_memories = [
                memory for memory in filtered_memories
                if f"lang_{language}" in memory.get('context', {}).get('tags', [])
            ]
        
        if activity_type:
            category_map = {
                "code_run": "code_execution",
                "collaboration": "collaboration",
                "deployment": "deployment",
                "general": ["repl_project"]
            }
            target_categories = category_map.get(activity_type, [activity_type])
            if not isinstance(target_categories, list):
                target_categories = [target_categories]
            
            filtered_memories = [
                memory for memory in filtered_memories
                if memory.get('context', {}).get('category') in target_categories
            ]
        
        if collaborator:
            filtered_memories = [
                memory for memory in filtered_memories
                if memory.get('context', {}).get('collaborator') == collaborator
            ]
        
        # Perform search
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
            return [TextContent(type="text", text=f"⚡ No Repl history found for query: '{query}'")]
        
        result = f"⚡ Found {len(results)} Repl history entries for query: '{query}'\n\n"
        
        for i, item in enumerate(results, 1):
            memory = item['memory']
            score = item['score']
            category = memory.get('context', {}).get('category', 'unknown')
            repl = memory.get('context', {}).get('repl_name', 'Unknown')
            
            result += f"{i}. **{memory['id']}** ({category} in {repl}, score: {score:.3f})\n"
            content_preview = memory['content'][:200] + "..." if len(memory['content']) > 200 else memory['content']
            result += f"   {content_preview}\n\n"
        
        return [TextContent(type="text", text=result)]
    
    def _check_deterministic_triggers(self, message: str) -> Dict:
        """Enhanced deterministic triggers for Replit"""
        base_result = super()._check_deterministic_triggers(message)
        
        message_lower = message.lower()
        replit_triggers = []
        
        # Cloud development triggers
        cloud_words = [
            'repl', 'deploy', 'collaboration', 'share', 'fork',
            'run', 'execute', 'output', 'error', 'debug'
        ]
        
        for word in cloud_words:
            if word in message_lower:
                replit_triggers.append(f"cloud_{word}")
        
        # Programming language triggers
        languages = [
            'python', 'javascript', 'typescript', 'java', 'cpp',
            'go', 'rust', 'html', 'css', 'sql', 'bash'
        ]
        
        for lang in languages:
            if lang in message_lower:
                replit_triggers.append(f"lang_{lang}")
        
        # Collaboration triggers
        collab_words = [
            'team', 'partner', 'together', 'joined', 'invited',
            'multiplayer', 'real-time', 'concurrent'
        ]
        
        for word in collab_words:
            if word in message_lower:
                replit_triggers.append(f"collab_{word}")
        
        # Combine with base triggers
        all_triggers = base_result['triggers'] + replit_triggers
        
        # Enhanced save logic for cloud development
        should_save = base_result['should_save'] or len(replit_triggers) > 0
        
        return {
            "triggers": all_triggers,
            "should_save": should_save,
            "should_search": base_result['should_search'],
            "confidence": 0.9 if all_triggers else 0.1,
            "replit_triggers": replit_triggers
        }


async def main():
    """Main entry point for Replit MCP Server"""
    print("⚡ REPLIT CLOUD IDE - TRUE MCP SERVER")
    print("=" * 50)
    print("✅ Implementing standard MCP protocol")
    print("🤖 ML auto-triggers with cloud optimization")
    print("🤝 Collaboration-aware memory management")
    print("📡 Native MCP integration ready")
    
    await run_mcp_server("replit")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Replit MCP Server stopped")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
