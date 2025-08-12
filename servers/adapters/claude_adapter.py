"""
Claude Desktop adapter for MCP Memory Server
"""

import re
from typing import Dict, Any, List

from .base_adapter import BaseAdapter, PlatformContext


class ClaudeAdapter(BaseAdapter):
    """Adapter for Claude Desktop integration"""
    
    def _get_platform_config(self) -> Dict[str, Any]:
        """Get Claude-specific configuration"""
        return self.settings.platforms.claude
    
    async def process_message(self, content: str, context: PlatformContext) -> Dict[str, Any]:
        """Process a message from Claude Desktop"""
        try:
            # Analyze content for Claude-specific patterns
            analysis = self._analyze_claude_content(content, context)
            
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
                "message": f"Failed to process Claude message: {e}"
            }
    
    async def should_auto_save(self, content: str, context: PlatformContext) -> bool:
        """Determine if content should be auto-saved in Claude context"""
        try:
            # Check if auto-trigger is enabled for Claude
            if not self.platform_config.get("auto_trigger", True):
                return False
            
            # Claude-specific triggers
            claude_triggers = [
                # Conversation triggers
                r"remember\s+that",  # Remember statements
                r"important\s+note",  # Important notes
                r"key\s+point",  # Key points
                r"takeaway",  # Takeaways
                r"summary",  # Summaries
                
                # Knowledge triggers
                r"fact\s+about",  # Facts
                r"information\s+about",  # Information
                r"learned\s+that",  # Learning
                r"discovered\s+that",  # Discoveries
                r"found\s+out",  # Findings
                
                # Decision triggers
                r"decided\s+to",  # Decisions
                r"chose\s+to",  # Choices
                r"opted\s+for",  # Options
                r"selected",  # Selections
                
                # Problem-solving triggers
                r"solution\s+to",  # Solutions
                r"fix\s+for",  # Fixes
                r"workaround",  # Workarounds
                r"resolved",  # Resolutions
                
                # Code and technical triggers
                r"code\s+example",  # Code examples
                r"function\s+to",  # Functions
                r"algorithm",  # Algorithms
                r"pattern",  # Patterns
                r"best\s+practice",  # Best practices
                
                # Error and debugging triggers
                r"error\s+was",  # Errors
                r"bug\s+in",  # Bugs
                r"issue\s+with",  # Issues
                r"problem\s+was",  # Problems
                r"debugging",  # Debugging
            ]
            
            # Check for Claude-specific patterns
            for pattern in claude_triggers:
                if re.search(pattern, content, re.IGNORECASE):
                    return True
            
            # Check for important keywords
            important_keywords = [
                "error", "warning", "bug", "fix", "solution", "problem",
                "decision", "choice", "important", "remember", "note",
                "knowledge", "fact", "information", "learned", "discovered",
                "function", "class", "method", "api", "endpoint", "database",
                "config", "setting", "environment", "deployment", "production",
                "algorithm", "pattern", "best practice", "workaround", "resolution"
            ]
            
            content_lower = content.lower()
            keyword_matches = sum(1 for keyword in important_keywords if keyword in content_lower)
            
            # If multiple important keywords, likely worth saving
            if keyword_matches >= 2:
                return True
            
            # Check context for conversation-specific triggers
            if context.metadata:
                # Long responses (likely contain important information)
                if len(content) > 500:
                    return True
                
                # User questions (responses to questions are often important)
                if context.metadata.get("type") == "response_to_question":
                    return True
                
                # Code explanations
                if context.metadata.get("type") == "code_explanation":
                    return True
                
                # Problem-solving context
                if context.metadata.get("type") == "problem_solving":
                    return True
            
            return False
            
        except Exception as e:
            # Default to not saving if there's an error
            return False
    
    async def get_relevant_memories(self, query: str, context: PlatformContext) -> List[Any]:
        """Get memories relevant to Claude conversation context"""
        try:
            # Build search query based on context
            search_query = query
            
            # Add context-specific terms
            if context.metadata:
                # Add conversation topic to search
                if context.metadata.get("topic"):
                    search_query += f" {context.metadata['topic']}"
                
                # Add conversation type to search
                if context.metadata.get("conversation_type"):
                    search_query += f" {context.metadata['conversation_type']}"
                
                # Add user intent to search
                if context.metadata.get("user_intent"):
                    search_query += f" {context.metadata['user_intent']}"
            
            # If no specific query, use project context
            if not search_query.strip():
                search_query = context.project
            
            # Search memories
            memories = await self.memory_service.search_memories(
                query=search_query,
                project=context.project,
                max_results=15,  # More results for conversation context
                similarity_threshold=0.2  # Lower threshold for conversation context
            )
            
            # Format for Claude conversation
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
                    "type": "claude_memory"
                })
            
            return formatted_memories
            
        except Exception as e:
            return []
    
    def _analyze_claude_content(self, content: str, context: PlatformContext) -> Dict[str, Any]:
        """Analyze content for Claude-specific patterns"""
        analysis = {
            "content_type": "conversation",
            "tone": "neutral",
            "has_code": False,
            "has_explanation": False,
            "has_question": False,
            "has_answer": False,
            "complexity": "medium",
            "length_category": "medium"
        }
        
        try:
            # Detect content type
            if re.search(r"```[\w]*\n|function\s+\w+|def\s+\w+|class\s+\w+", content):
                analysis["content_type"] = "code_explanation"
                analysis["has_code"] = True
            elif re.search(r"\?\s*$|\?\s*\n", content):
                analysis["content_type"] = "question"
                analysis["has_question"] = True
            elif re.search(r"here\s+is|this\s+is|the\s+answer|solution\s+is", content, re.IGNORECASE):
                analysis["content_type"] = "answer"
                analysis["has_answer"] = True
            elif re.search(r"explain|describe|how\s+to|what\s+is", content, re.IGNORECASE):
                analysis["content_type"] = "explanation"
                analysis["has_explanation"] = True
            
            # Detect tone
            if re.search(r"great|excellent|amazing|wonderful", content, re.IGNORECASE):
                analysis["tone"] = "positive"
            elif re.search(r"error|problem|issue|bug|fail", content, re.IGNORECASE):
                analysis["tone"] = "negative"
            elif re.search(r"however|but|although|nevertheless", content, re.IGNORECASE):
                analysis["tone"] = "cautious"
            
            # Assess complexity
            sentences = re.split(r'[.!?]+', content)
            avg_sentence_length = sum(len(s.split()) for s in sentences) / len(sentences) if sentences else 0
            
            if avg_sentence_length > 25:
                analysis["complexity"] = "high"
            elif avg_sentence_length > 15:
                analysis["complexity"] = "medium"
            else:
                analysis["complexity"] = "low"
            
            # Assess length
            word_count = len(content.split())
            if word_count > 500:
                analysis["length_category"] = "long"
            elif word_count > 200:
                analysis["length_category"] = "medium"
            else:
                analysis["length_category"] = "short"
            
            # Add context metadata
            if context.metadata:
                analysis["conversation_type"] = context.metadata.get("conversation_type")
                analysis["user_intent"] = context.metadata.get("user_intent")
                analysis["topic"] = context.metadata.get("topic")
            
        except Exception as e:
            analysis["error"] = str(e)
        
        return analysis
    
    async def get_claude_specific_features(self) -> Dict[str, Any]:
        """Get Claude-specific features and capabilities"""
        return {
            "platform": "claude",
            "features": {
                "auto_trigger": self.platform_config.get("auto_trigger", True),
                "conversation_mode": self.platform_config.get("conversation_mode", True),
                "context_integration": self.platform_config.get("context_integration", True)
            },
            "conversation_types": [
                "general_chat", "code_review", "problem_solving", "learning",
                "decision_making", "troubleshooting", "explanation", "summary"
            ],
            "memory_types": [
                "conversation", "explanation", "solution", "decision",
                "knowledge", "code_example", "best_practice", "workaround"
            ]
        }
    
    async def get_conversation_context(self, context: PlatformContext) -> Dict[str, Any]:
        """Get conversation context for Claude"""
        try:
            # Get recent memories for context
            recent_memories = await self.memory_service.list_memories(
                project=context.project,
                limit=5,
                offset=0
            )
            
            # Get relevant memories based on current context
            relevant_memories = await self.get_relevant_memories("", context)
            
            return {
                "recent_memories": len(recent_memories),
                "relevant_memories": len(relevant_memories),
                "project": context.project,
                "session_id": context.session_id,
                "conversation_history": [
                    {
                        "id": memory.id,
                        "content": memory.content[:200] + "..." if len(memory.content) > 200 else memory.content,
                        "created_at": memory.created_at.isoformat(),
                        "importance": memory.importance
                    }
                    for memory in recent_memories
                ]
            }
            
        except Exception as e:
            return {
                "error": str(e),
                "recent_memories": 0,
                "relevant_memories": 0
            } 