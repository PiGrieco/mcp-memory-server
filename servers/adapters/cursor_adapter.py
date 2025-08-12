"""
Cursor IDE adapter for MCP Memory Server
"""

import re
from typing import Dict, Any, List
from pathlib import Path

from .base_adapter import BaseAdapter, PlatformContext


class CursorAdapter(BaseAdapter):
    """Adapter for Cursor IDE integration"""
    
    def _get_platform_config(self) -> Dict[str, Any]:
        """Get Cursor-specific configuration"""
        return self.settings.platforms.cursor
    
    async def process_message(self, content: str, context: PlatformContext) -> Dict[str, Any]:
        """Process a message from Cursor IDE"""
        try:
            # Analyze content for Cursor-specific patterns
            analysis = self._analyze_cursor_content(content, context)
            
            # Determine if this should be auto-saved
            should_save = await self.should_auto_save(content, context)
            
            if should_save:
                # Auto-save the memory
                result = await self.auto_save_memory(content, context)
                return {
                    "processed": True,
                    "auto_saved": result["saved"],
                    "analysis": analysis,
                    "memory_result": result
                }
            else:
                return {
                    "processed": True,
                    "auto_saved": False,
                    "analysis": analysis,
                    "reason": "Content did not meet auto-save criteria"
                }
                
        except Exception as e:
            return {
                "processed": False,
                "error": str(e),
                "message": f"Failed to process Cursor message: {e}"
            }
    
    async def should_auto_save(self, content: str, context: PlatformContext) -> bool:
        """Determine if content should be auto-saved in Cursor context"""
        try:
            # Check if auto-trigger is enabled for Cursor
            if not self.platform_config.get("auto_trigger", True):
                return False
            
            # Cursor-specific triggers
            cursor_triggers = [
                # Code-related triggers
                r"function\s+\w+\s*\(",  # Function definitions
                r"class\s+\w+",  # Class definitions
                r"def\s+\w+\s*\(",  # Python function definitions
                r"const\s+\w+",  # JavaScript constants
                r"let\s+\w+",  # JavaScript variables
                r"var\s+\w+",  # JavaScript variables
                
                # Error and debugging triggers
                r"console\.log",  # Console logs
                r"print\s*\(",  # Print statements
                r"debugger",  # Debugger statements
                r"TODO:",  # TODO comments
                r"FIXME:",  # FIXME comments
                r"BUG:",  # BUG comments
                
                # Important patterns
                r"remember\s+that",  # Remember statements
                r"important:",  # Important notes
                r"note:",  # Notes
                r"warning:",  # Warnings
                r"error:",  # Errors
                
                # Code patterns
                r"import\s+",  # Import statements
                r"from\s+\w+\s+import",  # From imports
                r"require\s*\(",  # Require statements
                r"export\s+",  # Export statements
            ]
            
            # Check for Cursor-specific patterns
            for pattern in cursor_triggers:
                if re.search(pattern, content, re.IGNORECASE):
                    return True
            
            # Check for important keywords
            important_keywords = [
                "error", "warning", "bug", "fix", "solution", "problem",
                "decision", "choice", "important", "remember", "note",
                "knowledge", "fact", "information", "learned", "discovered",
                "function", "class", "method", "api", "endpoint", "database",
                "config", "setting", "environment", "deployment", "production"
            ]
            
            content_lower = content.lower()
            keyword_matches = sum(1 for keyword in important_keywords if keyword in content_lower)
            
            # If multiple important keywords, likely worth saving
            if keyword_matches >= 2:
                return True
            
            # Check context for IDE-specific triggers
            if context.metadata:
                # File-related triggers
                if context.metadata.get("file_type") in ["py", "js", "ts", "java", "cpp", "c"]:
                    if len(content) > 100:  # Longer code snippets
                        return True
                
                # Error context
                if context.metadata.get("type") == "error":
                    return True
                
                # Debug context
                if context.metadata.get("type") == "debug":
                    return True
            
            return False
            
        except Exception as e:
            # Default to not saving if there's an error
            return False
    
    async def get_relevant_memories(self, query: str, context: PlatformContext) -> List[Any]:
        """Get memories relevant to Cursor IDE context"""
        try:
            # Build search query based on context
            search_query = query
            
            # Add context-specific terms
            if context.metadata:
                # Add file type to search
                if context.metadata.get("file_type"):
                    search_query += f" {context.metadata['file_type']} code"
                
                # Add project name to search
                if context.metadata.get("project_name"):
                    search_query += f" {context.metadata['project_name']}"
                
                # Add language to search
                if context.metadata.get("language"):
                    search_query += f" {context.metadata['language']}"
            
            # If no specific query, use project context
            if not search_query.strip():
                search_query = context.project
            
            # Search memories
            memories = await self.memory_service.search_memories(
                query=search_query,
                project=context.project,
                max_results=10,
                similarity_threshold=0.2  # Lower threshold for IDE context
            )
            
            # Format for Cursor IDE
            formatted_memories = []
            for memory in memories:
                formatted_memories.append({
                    "id": memory.id,
                    "content": memory.content,
                    "project": memory.project,
                    "importance": memory.importance,
                    "similarity": memory.similarity_score,
                    "created_at": memory.created_at.isoformat(),
                    "tags": memory.tags,
                    "type": "cursor_memory"
                })
            
            return formatted_memories
            
        except Exception as e:
            return []
    
    def _analyze_cursor_content(self, content: str, context: PlatformContext) -> Dict[str, Any]:
        """Analyze content for Cursor-specific patterns"""
        analysis = {
            "content_type": "unknown",
            "language": "unknown",
            "has_code": False,
            "has_comments": False,
            "has_errors": False,
            "has_todos": False,
            "complexity": "low"
        }
        
        try:
            # Detect content type
            if re.search(r"function\s+\w+\s*\(|def\s+\w+\s*\(|class\s+\w+", content):
                analysis["content_type"] = "code_definition"
                analysis["has_code"] = True
            elif re.search(r"console\.log|print\s*\(|debugger", content):
                analysis["content_type"] = "debug_statement"
                analysis["has_code"] = True
            elif re.search(r"TODO:|FIXME:|BUG:", content, re.IGNORECASE):
                analysis["content_type"] = "todo_comment"
                analysis["has_todos"] = True
            elif re.search(r"//|#|/\*|\*/", content):
                analysis["content_type"] = "comment"
                analysis["has_comments"] = True
            elif re.search(r"error|warning|exception", content, re.IGNORECASE):
                analysis["content_type"] = "error_message"
                analysis["has_errors"] = True
            
            # Detect language
            if re.search(r"def\s+\w+|import\s+\w+|from\s+\w+", content):
                analysis["language"] = "python"
            elif re.search(r"function\s+\w+|const\s+\w+|let\s+\w+", content):
                analysis["language"] = "javascript"
            elif re.search(r"public\s+class|private\s+\w+|System\.out", content):
                analysis["language"] = "java"
            elif re.search(r"#include|int\s+main|std::", content):
                analysis["language"] = "cpp"
            
            # Assess complexity
            lines = content.split('\n')
            if len(lines) > 20:
                analysis["complexity"] = "high"
            elif len(lines) > 10:
                analysis["complexity"] = "medium"
            
            # Add context metadata
            if context.metadata:
                analysis["file_type"] = context.metadata.get("file_type")
                analysis["project_name"] = context.metadata.get("project_name")
            
        except Exception as e:
            analysis["error"] = str(e)
        
        return analysis
    
    async def get_cursor_specific_features(self) -> Dict[str, Any]:
        """Get Cursor-specific features and capabilities"""
        return {
            "platform": "cursor",
            "features": {
                "auto_trigger": self.platform_config.get("auto_trigger", True),
                "ide_integration": self.platform_config.get("ide_integration", True),
                "code_analysis": self.platform_config.get("code_analysis", True),
                "file_watching": self.platform_config.get("file_watching", True)
            },
            "supported_languages": [
                "python", "javascript", "typescript", "java", "cpp", "c",
                "go", "rust", "php", "ruby", "swift", "kotlin"
            ],
            "memory_types": [
                "code_definition", "debug_statement", "todo_comment",
                "comment", "error_message", "configuration"
            ]
        } 