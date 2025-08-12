#!/usr/bin/env python3
"""
Lovable Platform MCP Server - True MCP Protocol Implementation
Optimized for Lovable AI-powered development platform with design focus
"""

import asyncio
import os
import sys
from pathlib import Path
import time
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
os.environ["LOVABLE_MODE"] = "true"
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
from mcp_base_server import MCPMemoryServer, run_mcp_server
from mcp.types import Tool, TextContent


class LovableMCPServer(MCPMemoryServer):
    """MCP Server optimized for Lovable AI development platform"""
    
    def __init__(self):
        super().__init__("lovable")
        self.lovable_stats = {
            'projects_tracked': 0,
            'designs_saved': 0,
            'features_documented': 0,
            'auto_triggers': 0,
            'ml_predictions': 0,
            'ui_components_saved': 0
        }
        
        # Auto-trigger configuration
        self.auto_trigger_enabled = True
        self.trigger_keywords = ['ricorda', 'nota', 'importante', 'salva', 'memorizza', 'remember', 'note', 'important', 'save']
        self.solution_patterns = ['risolto', 'solved', 'fixed', 'bug fix', 'solution', 'tutorial', 'come fare', 'how to']
        
        # Add Lovable-specific tools
        self._add_lovable_tools()
        
        print("💙 Lovable MCP Server initialized with AI platform optimization")
    
    def _add_lovable_tools(self):
        """Add Lovable-specific MCP tools"""
        
        @self.server.list_tools()
        async def handle_lovable_tools() -> List[Tool]:
            """Extended tool list for Lovable Platform"""
            base_tools = await super(LovableMCPServer, self).server._list_tools_handler()
            
            lovable_tools = [
                Tool(
                    name="save_design_pattern",
                    description="Save UI/UX design patterns and components",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "pattern_name": {
                                "type": "string",
                                "description": "Name of the design pattern"
                            },
                            "description": {
                                "type": "string",
                                "description": "Description of the design pattern"
                            },
                            "technology_stack": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": "Technologies used (React, Tailwind, etc.)"
                            },
                            "use_cases": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": "When to use this pattern"
                            },
                            "code_example": {
                                "type": "string",
                                "description": "Code example implementing the pattern"
                            },
                            "screenshot_url": {
                                "type": "string",
                                "description": "URL to screenshot or design mockup"
                            }
                        },
                        "required": ["pattern_name", "description"]
                    }
                ),
                Tool(
                    name="track_project",
                    description="Track Lovable project development progress",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "project_name": {
                                "type": "string",
                                "description": "Name of the Lovable project"
                            },
                            "project_type": {
                                "type": "string",
                                "enum": ["web_app", "mobile_app", "landing_page", "dashboard", "e_commerce"],
                                "description": "Type of project being built"
                            },
                            "progress_update": {
                                "type": "string",
                                "description": "Description of progress made"
                            },
                            "features_completed": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": "List of completed features"
                            },
                            "next_steps": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": "Planned next steps"
                            },
                            "tech_stack": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": "Technology stack being used"
                            }
                        },
                        "required": ["project_name", "project_type", "progress_update"]
                    }
                ),
                Tool(
                    name="save_ui_component",
                    description="Save reusable UI components for Lovable projects",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "component_name": {
                                "type": "string",
                                "description": "Name of the UI component"
                            },
                            "component_type": {
                                "type": "string",
                                "enum": ["button", "form", "navigation", "modal", "card", "layout", "input", "other"],
                                "description": "Type of UI component"
                            },
                            "description": {
                                "type": "string",
                                "description": "What the component does"
                            },
                            "props": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": "Component props/parameters"
                            },
                            "styling_framework": {
                                "type": "string",
                                "description": "CSS framework used (Tailwind, CSS Modules, etc.)"
                            },
                            "code": {
                                "type": "string",
                                "description": "Component code"
                            },
                            "usage_example": {
                                "type": "string",
                                "description": "Example of how to use the component"
                            }
                        },
                        "required": ["component_name", "component_type", "description"]
                    }
                ),
                Tool(
                    name="search_design_patterns",
                    description="Search for design patterns and UI components",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "query": {
                                "type": "string",
                                "description": "Search query for design patterns"
                            },
                            "pattern_type": {
                                "type": "string",
                                "enum": ["ui_component", "design_pattern", "layout", "navigation", "form", "animation"],
                                "description": "Type of pattern to search for"
                            },
                            "technology": {
                                "type": "string",
                                "description": "Specific technology to filter by"
                            }
                        },
                        "required": ["query"]
                    }
                )
            ]
            
            return base_tools + lovable_tools
        
        @self.server.call_tool()
        async def handle_lovable_tools(name: str, arguments: Dict[str, Any]) -> List[TextContent]:
            """Handle Lovable-specific tool calls"""
            
            if name == "save_design_pattern":
                return await self._handle_save_design_pattern(arguments)
            elif name == "track_project":
                return await self._handle_track_project(arguments)
            elif name == "save_ui_component":
                return await self._handle_save_ui_component(arguments)
            elif name == "search_design_patterns":
                return await self._handle_search_design_patterns(arguments)
            else:
                # Call parent handler for base tools
                return await super(LovableMCPServer, self).server._call_tool_handler(name, arguments)
    
    async def _handle_save_design_pattern(self, arguments: Dict[str, Any]) -> List[TextContent]:
        """Handle save_design_pattern tool call"""
        pattern_name = arguments.get("pattern_name", "")
        description = arguments.get("description", "")
        technology_stack = arguments.get("technology_stack", [])
        use_cases = arguments.get("use_cases", [])
        code_example = arguments.get("code_example", "")
        screenshot_url = arguments.get("screenshot_url", "")
        
        if not pattern_name.strip():
            return [TextContent(type="text", text="❌ Pattern name is required")]
        
        # Create design pattern content
        content = f"Design Pattern: {pattern_name}\n\n"
        content += f"**Description:** {description}\n\n"
        
        if technology_stack:
            content += f"**Technology Stack:** {', '.join(technology_stack)}\n\n"
        
        if use_cases:
            content += f"**Use Cases:**\n"
            for use_case in use_cases:
                content += f"  • {use_case}\n"
            content += "\n"
        
        if code_example:
            content += f"**Code Example:**\n```\n{code_example}\n```\n\n"
        
        if screenshot_url:
            content += f"**Screenshot:** {screenshot_url}\n"
        
        # Enhanced context for design patterns
        context = {
            "category": "design_pattern",
            "importance": 0.8,
            "tags": ["design_pattern", "lovable"] + technology_stack,
            "pattern_name": pattern_name,
            "technology_stack": technology_stack,
            "lovable_type": "design_pattern"
        }
        
        # Save using base functionality
        await self._handle_save_memory({
            "content": content,
            "context": context
        })
        
        self.lovable_stats['designs_saved'] += 1
        
        result = f"💙 Design pattern saved to Lovable memory!\n"
        result += f"   Pattern: {pattern_name}\n"
        result += f"   Technologies: {', '.join(technology_stack)}\n"
        result += f"   Use cases: {len(use_cases)}\n"
        result += f"   Has code example: {'✅' if code_example else '❌'}\n"
        
        return [TextContent(type="text", text=result)]
    
    async def _handle_track_project(self, arguments: Dict[str, Any]) -> List[TextContent]:
        """Handle track_project tool call"""
        project_name = arguments.get("project_name", "")
        project_type = arguments.get("project_type", "")
        progress_update = arguments.get("progress_update", "")
        features_completed = arguments.get("features_completed", [])
        next_steps = arguments.get("next_steps", [])
        tech_stack = arguments.get("tech_stack", [])
        
        if not project_name.strip():
            return [TextContent(type="text", text="❌ Project name is required")]
        
        self.lovable_stats['projects_tracked'] += 1
        if features_completed:
            self.lovable_stats['features_documented'] += len(features_completed)
        
        # Create project update content
        content = f"Lovable Project Update: {project_name}\n\n"
        content += f"**Project Type:** {project_type}\n"
        content += f"**Progress:** {progress_update}\n\n"
        
        if tech_stack:
            content += f"**Tech Stack:** {', '.join(tech_stack)}\n\n"
        
        if features_completed:
            content += f"**Completed Features:**\n"
            for feature in features_completed:
                content += f"  ✅ {feature}\n"
            content += "\n"
        
        if next_steps:
            content += f"**Next Steps:**\n"
            for step in next_steps:
                content += f"  📋 {step}\n"
        
        # Project context
        context = {
            "category": "project_update",
            "importance": 0.7,
            "tags": ["project_update", "lovable", project_type] + tech_stack,
            "project_name": project_name,
            "project_type": project_type,
            "lovable_type": "project_update"
        }
        
        # Save project update
        await self._handle_save_memory({
            "content": content,
            "context": context
        })
        
        result = f"💙 Project progress tracked!\n"
        result += f"   Project: {project_name} ({project_type})\n"
        result += f"   Features completed: {len(features_completed)}\n"
        result += f"   Next steps: {len(next_steps)}\n"
        result += f"   Total projects tracked: {self.lovable_stats['projects_tracked']}\n"
        
        return [TextContent(type="text", text=result)]
    
    async def _handle_save_ui_component(self, arguments: Dict[str, Any]) -> List[TextContent]:
        """Handle save_ui_component tool call"""
        component_name = arguments.get("component_name", "")
        component_type = arguments.get("component_type", "")
        description = arguments.get("description", "")
        props = arguments.get("props", [])
        styling_framework = arguments.get("styling_framework", "")
        code = arguments.get("code", "")
        usage_example = arguments.get("usage_example", "")
        
        if not component_name.strip():
            return [TextContent(type="text", text="❌ Component name is required")]
        
        self.lovable_stats['ui_components_saved'] += 1
        
        # Create UI component content
        content = f"UI Component: {component_name}\n\n"
        content += f"**Type:** {component_type}\n"
        content += f"**Description:** {description}\n\n"
        
        if props:
            content += f"**Props:**\n"
            for prop in props:
                content += f"  • {prop}\n"
            content += "\n"
        
        if styling_framework:
            content += f"**Styling:** {styling_framework}\n\n"
        
        if code:
            content += f"**Code:**\n```jsx\n{code}\n```\n\n"
        
        if usage_example:
            content += f"**Usage Example:**\n```jsx\n{usage_example}\n```\n"
        
        # Component context
        context = {
            "category": "ui_component",
            "importance": 0.8,
            "tags": ["ui_component", "lovable", component_type, styling_framework],
            "component_name": component_name,
            "component_type": component_type,
            "lovable_type": "ui_component"
        }
        
        # Save component
        await self._handle_save_memory({
            "content": content,
            "context": context
        })
        
        result = f"💙 UI component saved!\n"
        result += f"   Component: {component_name} ({component_type})\n"
        result += f"   Props: {len(props)}\n"
        result += f"   Has code: {'✅' if code else '❌'}\n"
        result += f"   Total components: {self.lovable_stats['ui_components_saved']}\n"
        
        return [TextContent(type="text", text=result)]
    
    async def _handle_search_design_patterns(self, arguments: Dict[str, Any]) -> List[TextContent]:
        """Handle search_design_patterns tool call"""
        query = arguments.get("query", "")
        pattern_type = arguments.get("pattern_type")
        technology = arguments.get("technology")
        
        if not query.strip():
            return [TextContent(type="text", text="❌ Search query is required")]
        
        # Filter memories by design-related categories
        design_categories = ["design_pattern", "ui_component", "project_update"]
        filtered_memories = [
            memory for memory in self.memories.values()
            if memory.get('context', {}).get('category') in design_categories
        ]
        
        # Apply additional filters
        if pattern_type:
            filtered_memories = [
                memory for memory in filtered_memories
                if pattern_type in memory.get('context', {}).get('tags', [])
            ]
        
        if technology:
            filtered_memories = [
                memory for memory in filtered_memories
                if technology.lower() in ' '.join(memory.get('context', {}).get('tags', [])).lower()
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
            return [TextContent(type="text", text=f"💙 No design patterns found for query: '{query}'")]
        
        result = f"💙 Found {len(results)} design patterns for query: '{query}'\n\n"
        
        for i, item in enumerate(results, 1):
            memory = item['memory']
            score = item['score']
            category = memory.get('context', {}).get('category', 'unknown')
            
            result += f"{i}. **{memory['id']}** ({category}, score: {score:.3f})\n"
            content_preview = memory['content'][:200] + "..." if len(memory['content']) > 200 else memory['content']
            result += f"   {content_preview}\n\n"
        
        return [TextContent(type="text", text=result)]
    
    def _check_deterministic_triggers(self, message: str) -> Dict:
        """Enhanced deterministic triggers for Lovable"""
        base_result = super()._check_deterministic_triggers(message)
        
        message_lower = message.lower()
        lovable_triggers = []
        
        # Design and development triggers
        design_words = [
            'design', 'ui', 'ux', 'component', 'layout', 'pattern',
            'style', 'css', 'responsive', 'mobile', 'desktop',
            'wireframe', 'mockup', 'prototype'
        ]
        
        for word in design_words:
            if word in message_lower:
                lovable_triggers.append(f"design_{word}")
        
        # Technology triggers
        tech_words = [
            'react', 'vue', 'angular', 'tailwind', 'bootstrap',
            'javascript', 'typescript', 'html', 'css', 'sass',
            'next.js', 'nuxt', 'gatsby'
        ]
        
        for word in tech_words:
            if word in message_lower:
                lovable_triggers.append(f"tech_{word.replace('.', '_')}")
        
        # Project management triggers
        project_words = [
            'feature', 'milestone', 'progress', 'update', 'project',
            'deployment', 'launch', 'release', 'version'
        ]
        
        for word in project_words:
            if word in message_lower:
                lovable_triggers.append(f"project_{word}")
        
        # Combine with base triggers
        all_triggers = base_result['triggers'] + lovable_triggers
        
        # Enhanced save logic for design content
        should_save = base_result['should_save'] or len(lovable_triggers) > 0
        
        return {
            "triggers": all_triggers,
            "should_save": should_save,
            "should_search": base_result['should_search'],
            "confidence": 0.9 if all_triggers else 0.1,
            "lovable_triggers": lovable_triggers
        }


async def main():
    """Main entry point for Lovable MCP Server"""
    print("💙 LOVABLE AI PLATFORM - TRUE MCP SERVER")
    print("=" * 50)
    print("✅ Implementing standard MCP protocol")
    print("🤖 ML auto-triggers with design optimization")
    print("🎨 UI/UX pattern management")
    print("📡 Native MCP integration ready")
    
    await run_mcp_server("lovable")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Lovable MCP Server stopped")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
