#!/usr/bin/env python3
"""
Production-Ready Cursor IDE Integration for MCP Memory Server
Based on the successful .cursor/mcp.json configuration pattern
"""

import asyncio
import json
import os
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional, Any

from .base_integration import BaseAIIntegration, ConversationContext, AIIntegrationError
from ...src.utils.logging import get_logger, log_performance
from ...src.utils.exceptions import MCPMemoryError


logger = get_logger(__name__)


class CursorMemoryIntegration(BaseAIIntegration):
    """
    Production-ready Cursor IDE integration
    Follows the MCP protocol for seamless integration
    """
    
    def __init__(self, config_override: Optional[Dict] = None):
        super().__init__("cursor", config_override)
        
        # Cursor-specific configuration
        self.cursor_config_path = Path(".cursor/mcp.json")
        self.server_config = {
            "mcpServers": {
                "mcp-memory-server": {
                    "command": "python",
                    "args": ["-m", "mcp_memory_server"],
                    "env": {
                        "MONGODB_URI": os.getenv("MONGODB_URI", ""),
                        "MONGODB_DATABASE": os.getenv("MONGODB_DATABASE", "mcp_memory"),
                        "EMBEDDING_MODEL": os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2"),
                        "LOG_LEVEL": os.getenv("LOG_LEVEL", "INFO")
                    }
                }
            }
        }
        
        # MCP tools that will be available in Cursor
        self.available_tools = [
            "create_memory",
            "search_memories", 
            "list_memories",
            "update_memory",
            "delete_memory",
            "get_memory_stats"
        ]
        
        # Session tracking
        self.active_context = None
        self.workspace_path = None
        
    async def initialize(self) -> bool:
        """Initialize Cursor integration"""
        try:
            self.logger.info("Initializing Cursor MCP integration...")
            
            # Detect workspace
            self.workspace_path = await self._detect_workspace()
            if not self.workspace_path:
                self.logger.warning("No workspace detected, using current directory")
                self.workspace_path = Path.cwd()
            
            # Setup MCP configuration
            await self._setup_mcp_configuration()
            
            # Validate server availability
            server_available = await self._validate_server()
            if not server_available:
                self.logger.warning("MCP server not immediately available, will retry")
            
            # Setup workspace monitoring if enabled
            if self.integration_config.get('monitor_workspace', True):
                await self._setup_workspace_monitoring()
            
            self.logger.info("Cursor integration initialized successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to initialize Cursor integration: {e}")
            return False
    
    async def _detect_workspace(self) -> Optional[Path]:
        """Detect current Cursor workspace"""
        # Look for common workspace indicators
        current_dir = Path.cwd()
        workspace_indicators = [
            '.cursor',
            '.vscode', 
            '.git',
            'package.json',
            'pyproject.toml',
            'Cargo.toml',
            'go.mod'
        ]
        
        # Check current directory and parents
        for path in [current_dir] + list(current_dir.parents):
            for indicator in workspace_indicators:
                if (path / indicator).exists():
                    self.logger.debug(f"Detected workspace: {path}")
                    return path
        
        return None
    
    async def _setup_mcp_configuration(self):
        """Setup MCP configuration for Cursor"""
        try:
            cursor_dir = self.workspace_path / ".cursor"
            cursor_dir.mkdir(exist_ok=True)
            
            mcp_config_path = cursor_dir / "mcp.json"
            
            # Load existing config if present
            existing_config = {}
            if mcp_config_path.exists():
                try:
                    with open(mcp_config_path, 'r') as f:
                        existing_config = json.load(f)
                except Exception as e:
                    self.logger.warning(f"Failed to load existing MCP config: {e}")
            
            # Merge with our server configuration
            merged_config = existing_config.copy()
            if "mcpServers" not in merged_config:
                merged_config["mcpServers"] = {}
            
            merged_config["mcpServers"]["mcp-memory-server"] = self.server_config["mcpServers"]["mcp-memory-server"]
            
            # Save configuration
            with open(mcp_config_path, 'w') as f:
                json.dump(merged_config, f, indent=2)
            
            self.logger.info(f"MCP configuration saved to {mcp_config_path}")
            
            # Also create settings.json for enhanced integration
            await self._setup_cursor_settings(cursor_dir)
            
        except Exception as e:
            self.logger.error(f"Failed to setup MCP configuration: {e}")
            raise
    
    async def _setup_cursor_settings(self, cursor_dir: Path):
        """Setup additional Cursor settings for better integration"""
        settings_path = cursor_dir / "settings.json"
        
        memory_settings = {
            "mcp.memory.autoSave": True,
            "mcp.memory.contextAwareness": True,
            "mcp.memory.showSuggestions": True,
            "mcp.memory.importanceThreshold": 0.5,
            "mcp.memory.project": self.integration_config.get('project', 'default')
        }
        
        # Load existing settings
        existing_settings = {}
        if settings_path.exists():
            try:
                with open(settings_path, 'r') as f:
                    existing_settings = json.load(f)
            except Exception as e:
                self.logger.debug(f"No existing settings file: {e}")
        
        # Merge settings
        existing_settings.update(memory_settings)
        
        # Save settings
        with open(settings_path, 'w') as f:
            json.dump(existing_settings, f, indent=2)
        
        self.logger.debug(f"Cursor settings updated at {settings_path}")
    
    async def _validate_server(self) -> bool:
        """Validate that MCP server is available"""
        try:
            # Try to import and test the server
            from ...main import main as server_main
            
            # Test basic functionality
            if self.memory_client:
                test_result = await self.memory_client.search_memories(
                    query="test", limit=1
                )
                self.logger.debug("MCP server validation successful")
                return True
            
            return False
            
        except Exception as e:
            self.logger.warning(f"MCP server validation failed: {e}")
            return False
    
    async def _setup_workspace_monitoring(self):
        """Setup monitoring for workspace changes"""
        # This would implement file watching for automatic memory creation
        # from code changes, comments, etc.
        self.logger.debug("Workspace monitoring setup (placeholder)")
        pass
    
    async def extract_conversation_context(self, data: Dict[str, Any]) -> Optional[ConversationContext]:
        """Extract conversation context from Cursor interaction"""
        try:
            # Cursor typically provides context through MCP tools calls
            conversation_id = data.get('conversation_id') or f"cursor_{int(time.time())}"
            
            # Extract messages from the interaction
            messages = []
            
            # Handle different types of Cursor interactions
            if 'user_input' in data:
                messages.append({
                    'role': 'user',
                    'content': data['user_input'],
                    'timestamp': datetime.now(timezone.utc).isoformat()
                })
            
            if 'ai_response' in data:
                messages.append({
                    'role': 'assistant', 
                    'content': data['ai_response'],
                    'timestamp': datetime.now(timezone.utc).isoformat()
                })
            
            if 'code_context' in data:
                messages.append({
                    'role': 'system',
                    'content': f"Code context: {data['code_context']}",
                    'timestamp': datetime.now(timezone.utc).isoformat()
                })
            
            if not messages:
                return None
            
            # Calculate importance based on interaction type
            importance = await self._calculate_cursor_importance(data)
            
            # Extract metadata
            metadata = {
                'workspace_path': str(self.workspace_path) if self.workspace_path else None,
                'file_path': data.get('file_path'),
                'line_number': data.get('line_number'),
                'interaction_type': data.get('interaction_type', 'chat'),
                'language': data.get('language'),
                'cursor_version': data.get('cursor_version')
            }
            
            return ConversationContext(
                conversation_id=conversation_id,
                platform='cursor',
                user_id=data.get('user_id'),
                messages=messages,
                metadata=metadata,
                timestamp=datetime.now(timezone.utc),
                importance_score=importance,
                project=self.integration_config.get('project', 'default')
            )
            
        except Exception as e:
            self.logger.error(f"Failed to extract conversation context: {e}")
            return None
    
    async def _calculate_cursor_importance(self, data: Dict[str, Any]) -> float:
        """Calculate importance score for Cursor interactions"""
        base_importance = 0.5
        
        # Increase importance for code-related interactions
        if data.get('interaction_type') in ['code_generation', 'debugging', 'refactoring']:
            base_importance += 0.2
        
        # Increase importance for error/problem solving
        content = ' '.join([
            data.get('user_input', ''),
            data.get('ai_response', ''),
            data.get('code_context', '')
        ]).lower()
        
        importance_indicators = {
            'error': 0.3,
            'bug': 0.3,
            'fix': 0.2,
            'implement': 0.2,
            'optimize': 0.15,
            'refactor': 0.15,
            'important': 0.2,
            'todo': 0.1,
            'note': 0.1
        }
        
        for indicator, boost in importance_indicators.items():
            if indicator in content:
                base_importance += boost
                break
        
        # Increase importance for longer interactions
        total_length = len(content)
        if total_length > 500:
            base_importance += 0.1
        elif total_length < 100:
            base_importance -= 0.1
        
        return max(0.0, min(1.0, base_importance))
    
    async def format_memory_for_platform(self, memory: Dict[str, Any]) -> str:
        """Format memory for display in Cursor"""
        try:
            content = memory.get('content', '')
            title = memory.get('title', 'Memory')
            created_at = memory.get('created_at', '')
            importance = memory.get('importance', 0.5)
            
            # Format for Cursor's markdown support
            formatted = f"""### {title}
**Created:** {created_at}  
**Importance:** {'★' * int(importance * 5)}  

{content}

---
*Memory ID: {memory.get('id', 'unknown')}*
"""
            
            return formatted
            
        except Exception as e:
            self.logger.error(f"Failed to format memory for Cursor: {e}")
            return f"Memory: {memory.get('content', 'No content')}"
    
    @log_performance("cursor_code_context_analysis")
    async def analyze_code_context(self, file_path: str, line_number: int = None) -> Dict[str, Any]:
        """Analyze code context for memory relevance"""
        try:
            if not Path(file_path).exists():
                return {}
            
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Basic analysis - could be enhanced with AST parsing
            lines = content.split('\n')
            
            context = {
                'file_path': file_path,
                'total_lines': len(lines),
                'language': self._detect_language(file_path),
                'relevant_memories': []
            }
            
            # If line number specified, extract surrounding context
            if line_number and 1 <= line_number <= len(lines):
                start = max(0, line_number - 5)
                end = min(len(lines), line_number + 5)
                context['surrounding_code'] = '\n'.join(lines[start:end])
                context['current_line'] = lines[line_number - 1] if line_number > 0 else ''
            
            # Search for relevant memories based on file content
            search_query = self._extract_search_terms(content)
            if search_query:
                relevant_memories = await self.search_relevant_memories(search_query, limit=3)
                context['relevant_memories'] = relevant_memories
            
            return context
            
        except Exception as e:
            self.logger.error(f"Failed to analyze code context: {e}")
            return {}
    
    def _detect_language(self, file_path: str) -> str:
        """Detect programming language from file extension"""
        extension_map = {
            '.py': 'python',
            '.js': 'javascript', 
            '.ts': 'typescript',
            '.jsx': 'javascript',
            '.tsx': 'typescript',
            '.java': 'java',
            '.cpp': 'cpp',
            '.c': 'c',
            '.cs': 'csharp',
            '.go': 'go',
            '.rs': 'rust',
            '.php': 'php',
            '.rb': 'ruby',
            '.swift': 'swift',
            '.kt': 'kotlin',
            '.scala': 'scala',
            '.clj': 'clojure',
            '.hs': 'haskell',
            '.ml': 'ocaml',
            '.fs': 'fsharp',
            '.elm': 'elm',
            '.dart': 'dart',
            '.r': 'r',
            '.m': 'matlab',
            '.sh': 'bash',
            '.ps1': 'powershell',
            '.sql': 'sql',
            '.html': 'html',
            '.css': 'css',
            '.scss': 'scss',
            '.less': 'less',
            '.xml': 'xml',
            '.yaml': 'yaml',
            '.yml': 'yaml',
            '.json': 'json',
            '.md': 'markdown',
            '.tex': 'latex'
        }
        
        extension = Path(file_path).suffix.lower()
        return extension_map.get(extension, 'text')
    
    def _extract_search_terms(self, content: str) -> str:
        """Extract meaningful search terms from code content"""
        # Simple extraction - could be enhanced with NLP
        lines = content.split('\n')
        
        search_terms = []
        
        # Look for comments
        for line in lines:
            line = line.strip()
            if line.startswith('#') or line.startswith('//') or line.startswith('/*'):
                comment = line.lstrip('#//* ').strip()
                if len(comment) > 10:  # Meaningful comments
                    search_terms.append(comment)
        
        # Look for function/class names (basic pattern matching)
        import re
        function_pattern = r'(?:def|function|class|interface)\s+(\w+)'
        matches = re.findall(function_pattern, content, re.IGNORECASE)
        search_terms.extend(matches)
        
        # Return first few terms as search query
        return ' '.join(search_terms[:3])
    
    async def create_workspace_memory(
        self, 
        content: str,
        memory_type: str = "workspace",
        importance: float = 0.6,
        metadata: Dict[str, Any] = None
    ) -> Optional[Dict[str, Any]]:
        """Create a memory specifically for workspace context"""
        try:
            enhanced_metadata = {
                'workspace_path': str(self.workspace_path) if self.workspace_path else None,
                'created_by': 'cursor_integration',
                'memory_category': 'workspace',
                **(metadata or {})
            }
            
            result = await self.memory_client.create_memory(
                content=content,
                importance=importance,
                memory_type=memory_type,
                metadata=enhanced_metadata,
                project=self.integration_config.get('project', 'default')
            )
            
            if result:
                self.logger.info(f"Workspace memory created: {result.get('id')}")
            
            return result
            
        except Exception as e:
            self.logger.error(f"Failed to create workspace memory: {e}")
            return None
    
    async def get_workspace_memories(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get memories specific to current workspace"""
        try:
            if not self.workspace_path:
                return []
            
            # Search for memories related to this workspace
            search_query = f"workspace:{self.workspace_path.name}"
            memories = await self.search_relevant_memories(search_query, limit=limit)
            
            # Filter by workspace path in metadata
            workspace_memories = []
            for memory in memories:
                metadata = memory.get('metadata', {})
                if metadata.get('workspace_path') == str(self.workspace_path):
                    workspace_memories.append(memory)
            
            return workspace_memories
            
        except Exception as e:
            self.logger.error(f"Failed to get workspace memories: {e}")
            return []
    
    async def export_cursor_config(self, output_path: Optional[str] = None) -> str:
        """Export current Cursor MCP configuration"""
        try:
            if not output_path:
                output_path = "cursor_mcp_config.json"
            
            config = {
                'integration_info': {
                    'platform': self.platform_name,
                    'version': '1.0.0',
                    'workspace_path': str(self.workspace_path) if self.workspace_path else None,
                    'exported_at': datetime.now(timezone.utc).isoformat()
                },
                'mcp_configuration': self.server_config,
                'integration_settings': self.integration_config,
                'available_tools': self.available_tools
            }
            
            with open(output_path, 'w') as f:
                json.dump(config, f, indent=2)
            
            self.logger.info(f"Cursor configuration exported to {output_path}")
            return output_path
            
        except Exception as e:
            self.logger.error(f"Failed to export Cursor config: {e}")
            raise


# Standalone functions for Cursor integration
async def setup_cursor_integration(workspace_path: Optional[str] = None) -> CursorMemoryIntegration:
    """Setup Cursor integration in current or specified workspace"""
    integration = CursorMemoryIntegration()
    
    if workspace_path:
        integration.workspace_path = Path(workspace_path)
    
    success = await integration.start_integration()
    if not success:
        raise AIIntegrationError("Failed to setup Cursor integration")
    
    return integration


def create_cursor_mcp_config(output_path: str = ".cursor/mcp.json") -> bool:
    """Create basic Cursor MCP configuration file"""
    try:
        config = {
            "mcpServers": {
                "mcp-memory-server": {
                    "command": "python",
                    "args": ["-m", "mcp_memory_server"],
                    "env": {
                        "MONGODB_URI": "${MONGODB_URI}",
                        "MONGODB_DATABASE": "${MONGODB_DATABASE:-mcp_memory}",
                        "EMBEDDING_MODEL": "${EMBEDDING_MODEL:-all-MiniLM-L6-v2}",
                        "LOG_LEVEL": "${LOG_LEVEL:-INFO}"
                    }
                }
            }
        }
        
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_file, 'w') as f:
            json.dump(config, f, indent=2)
        
        logger.info(f"Cursor MCP configuration created at {output_path}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to create Cursor MCP config: {e}")
        return False


if __name__ == "__main__":
    # Quick setup script
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "setup":
        workspace = sys.argv[2] if len(sys.argv) > 2 else None
        
        async def main():
            try:
                integration = await setup_cursor_integration(workspace)
                print("✅ Cursor integration setup completed successfully!")
                print(f"📁 Workspace: {integration.workspace_path}")
                print("🔧 MCP configuration created in .cursor/mcp.json")
                print("🚀 Restart Cursor to activate the integration")
                
            except Exception as e:
                print(f"❌ Setup failed: {e}")
                sys.exit(1)
        
        asyncio.run(main())
    
    elif len(sys.argv) > 1 and sys.argv[1] == "config":
        output_path = sys.argv[2] if len(sys.argv) > 2 else ".cursor/mcp.json"
        
        if create_cursor_mcp_config(output_path):
            print(f"✅ MCP configuration created at {output_path}")
        else:
            print("❌ Failed to create MCP configuration")
            sys.exit(1)
    
    else:
        print("Usage:")
        print("  python cursor_integration.py setup [workspace_path]")
        print("  python cursor_integration.py config [output_path]")
