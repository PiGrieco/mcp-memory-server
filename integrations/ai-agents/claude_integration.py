#!/usr/bin/env python3
"""
Production-Ready Claude AI Integration for MCP Memory Server
Enhanced with smart context awareness and conversation management
"""

import asyncio
import json
import time
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any

from .base_integration import BaseAIIntegration, ConversationContext, AIIntegrationError
from ...src.utils.logging import get_logger, log_performance


logger = get_logger(__name__)


class ClaudeMemoryIntegration(BaseAIIntegration):
    """Production-ready Claude AI integration with enhanced memory management"""
    
    def __init__(self, config_override: Optional[Dict] = None):
        super().__init__("claude", config_override)
        
        # Claude-specific configuration
        self.claude_config = {
            "auto_context_injection": True,
            "memory_context_limit": 3,
            "conversation_tracking": True,
            "importance_keywords": [
                "remember", "important", "note", "key point", "summarize",
                "action item", "decision", "conclusion", "insight"
            ]
        }
        self.claude_config.update(self.integration_config.get('platform_specific', {}))
        
    async def initialize(self) -> bool:
        """Initialize Claude integration"""
        try:
            self.logger.info("Initializing Claude integration...")
            
            # Setup Claude desktop configuration if available
            await self._setup_claude_desktop_config()
            
            # Initialize conversation tracking
            self.conversation_sessions = {}
            
            self.logger.info("Claude integration initialized successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to initialize Claude integration: {e}")
            return False
    
    async def _setup_claude_desktop_config(self):
        """Setup Claude Desktop configuration for MCP integration"""
        try:
            from pathlib import Path
            import os
            
            # Default Claude config locations
            config_paths = [
                Path.home() / "Library/Application Support/Claude/claude_desktop_config.json",  # macOS
                Path.home() / "AppData/Roaming/Claude/claude_desktop_config.json",  # Windows
                Path.home() / ".config/claude/claude_desktop_config.json"  # Linux
            ]
            
            config_content = {
                "mcpServers": {
                    "mcp-memory-server": {
                        "command": "python",
                        "args": ["-m", "mcp_memory_server"],
                        "env": {
                            "MONGODB_URI": os.getenv("MONGODB_URI", ""),
                            "MONGODB_DATABASE": os.getenv("MONGODB_DATABASE", "mcp_memory"),
                            "EMBEDDING_MODEL": os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")
                        }
                    }
                }
            }
            
            for config_path in config_paths:
                if config_path.parent.exists():
                    try:
                        # Load existing config
                        existing_config = {}
                        if config_path.exists():
                            with open(config_path, 'r') as f:
                                existing_config = json.load(f)
                        
                        # Merge configurations
                        if "mcpServers" not in existing_config:
                            existing_config["mcpServers"] = {}
                        existing_config["mcpServers"].update(config_content["mcpServers"])
                        
                        # Save updated config
                        with open(config_path, 'w') as f:
                            json.dump(existing_config, f, indent=2)
                        
                        self.logger.info(f"Claude desktop config updated: {config_path}")
                        break
                        
                    except Exception as e:
                        self.logger.debug(f"Could not update config at {config_path}: {e}")
            
        except Exception as e:
            self.logger.warning(f"Failed to setup Claude desktop config: {e}")
    
    async def extract_conversation_context(self, data: Dict[str, Any]) -> Optional[ConversationContext]:
        """Extract conversation context from Claude interaction"""
        try:
            conversation_id = data.get('conversation_id') or f"claude_{int(time.time())}"
            
            messages = []
            
            # Handle Claude conversation format
            if 'messages' in data:
                for msg in data['messages'][-10:]:  # Last 10 messages
                    messages.append({
                        'role': msg.get('role', 'user'),
                        'content': msg.get('content', ''),
                        'timestamp': msg.get('timestamp', datetime.now(timezone.utc).isoformat())
                    })
            elif 'human_message' in data and 'assistant_message' in data:
                messages.extend([
                    {
                        'role': 'user',
                        'content': data['human_message'],
                        'timestamp': datetime.now(timezone.utc).isoformat()
                    },
                    {
                        'role': 'assistant', 
                        'content': data['assistant_message'],
                        'timestamp': datetime.now(timezone.utc).isoformat()
                    }
                ])
            
            if not messages:
                return None
            
            # Calculate importance for Claude interactions
            importance = await self._calculate_claude_importance(messages)
            
            metadata = {
                'claude_model': data.get('model', 'claude-3'),
                'conversation_length': len(messages),
                'has_code': any('```' in msg.get('content', '') for msg in messages),
                'has_artifacts': data.get('has_artifacts', False),
                'session_id': data.get('session_id')
            }
            
            return ConversationContext(
                conversation_id=conversation_id,
                platform='claude',
                user_id=data.get('user_id'),
                messages=messages,
                metadata=metadata,
                timestamp=datetime.now(timezone.utc),
                importance_score=importance,
                project=self.integration_config.get('project', 'default')
            )
            
        except Exception as e:
            self.logger.error(f"Failed to extract Claude conversation context: {e}")
            return None
    
    async def _calculate_claude_importance(self, messages: List[Dict]) -> float:
        """Calculate importance for Claude conversations"""
        base_importance = 0.5
        
        # Check for importance keywords
        all_content = ' '.join([msg.get('content', '') for msg in messages]).lower()
        
        keyword_count = sum(1 for keyword in self.claude_config['importance_keywords'] 
                           if keyword in all_content)
        base_importance += min(0.3, keyword_count * 0.1)
        
        # Boost for longer, substantive conversations
        total_length = len(all_content)
        if total_length > 1000:
            base_importance += 0.2
        elif total_length < 200:
            base_importance -= 0.1
        
        # Boost for code or technical content
        if any('```' in msg.get('content', '') for msg in messages):
            base_importance += 0.15
        
        # Boost for Claude's structured responses
        if any(marker in all_content for marker in ['## ', '### ', '1. ', '- ']):
            base_importance += 0.1
        
        return max(0.0, min(1.0, base_importance))
    
    async def format_memory_for_platform(self, memory: Dict[str, Any]) -> str:
        """Format memory content for Claude"""
        try:
            content = memory.get('content', '')
            importance = memory.get('importance', 0.5)
            created_at = memory.get('created_at', '')
            memory_type = memory.get('memory_type', 'conversation')
            
            # Format with Claude-friendly markdown
            importance_stars = '★' * int(importance * 5)
            
            formatted = f"""💭 **Relevant Memory** ({memory_type.title()})
📅 {created_at} | 🌟 {importance_stars}

{content}

---"""
            
            return formatted
            
        except Exception as e:
            self.logger.error(f"Failed to format memory for Claude: {e}")
            return f"Memory: {memory.get('content', 'No content')}"
    
    @log_performance("claude_context_enhancement")
    async def enhance_claude_context(
        self, 
        current_message: str,
        conversation_history: List[Dict] = None
    ) -> str:
        """Enhance Claude context with relevant memories"""
        try:
            if not self.claude_config.get('auto_context_injection', True):
                return current_message
            
            # Search for relevant memories
            relevant_memories = await self.search_relevant_memories(
                current_message,
                limit=self.claude_config.get('memory_context_limit', 3)
            )
            
            if not relevant_memories:
                return current_message
            
            # Format memories for context injection
            memory_context = "\n\n".join([
                await self.format_memory_for_platform(memory) 
                for memory in relevant_memories
            ])
            
            # Inject context at the beginning of the message
            enhanced_message = f"""<context>
The following are relevant memories from our previous conversations:

{memory_context}
</context>

{current_message}"""
            
            self.logger.debug(f"Enhanced Claude context with {len(relevant_memories)} memories")
            return enhanced_message
            
        except Exception as e:
            self.logger.error(f"Failed to enhance Claude context: {e}")
            return current_message
    
    async def create_claude_system_prompt(
        self, 
        base_prompt: str = "",
        include_memory_context: bool = True
    ) -> str:
        """Create a system prompt for Claude with memory integration"""
        try:
            memory_instructions = ""
            
            if include_memory_context:
                memory_instructions = """
You have access to a persistent memory system that stores important information from our conversations. 

When you notice important information that should be remembered for future conversations, you can:
1. Use the create_memory tool to save key insights, decisions, or information
2. Use the search_memories tool to find relevant past information
3. Reference memories naturally in your responses when relevant

The memory system helps maintain context across conversations and provides continuity.
"""
            
            system_prompt = f"""{base_prompt}

{memory_instructions}

Remember to be helpful, harmless, and honest while leveraging the memory system to provide more contextual and personalized assistance.
"""
            
            return system_prompt.strip()
            
        except Exception as e:
            self.logger.error(f"Failed to create Claude system prompt: {e}")
            return base_prompt
    
    async def process_claude_artifacts(self, artifacts: List[Dict]) -> List[Dict]:
        """Process Claude artifacts for memory storage"""
        processed_artifacts = []
        
        try:
            for artifact in artifacts:
                artifact_type = artifact.get('type', 'unknown')
                content = artifact.get('content', '')
                title = artifact.get('title', 'Claude Artifact')
                
                # Create memory for significant artifacts
                if len(content) > 100:  # Only store substantial artifacts
                    memory_content = f"Artifact: {title}\nType: {artifact_type}\n\n{content}"
                    
                    memory_result = await self.memory_client.create_memory(
                        content=memory_content,
                        importance=0.7,  # Artifacts are generally important
                        memory_type='artifact',
                        metadata={
                            'artifact_type': artifact_type,
                            'artifact_title': title,
                            'platform': 'claude',
                            'created_by_integration': True
                        },
                        project=self.integration_config.get('project', 'default')
                    )
                    
                    if memory_result:
                        artifact['memory_id'] = memory_result.get('id')
                        self.logger.info(f"Saved Claude artifact as memory: {title}")
                
                processed_artifacts.append(artifact)
                
        except Exception as e:
            self.logger.error(f"Failed to process Claude artifacts: {e}")
        
        return processed_artifacts


# Standalone utility functions
async def setup_claude_integration(config: Optional[Dict] = None) -> ClaudeMemoryIntegration:
    """Setup Claude integration with optional configuration"""
    integration = ClaudeMemoryIntegration(config)
    
    success = await integration.start_integration()
    if not success:
        raise AIIntegrationError("Failed to setup Claude integration")
    
    return integration


def create_claude_desktop_config(output_path: str = None) -> bool:
    """Create Claude Desktop configuration file"""
    try:
        import os
        from pathlib import Path
        
        if not output_path:
            # Try default Claude config location
            if os.name == 'nt':  # Windows
                output_path = Path.home() / "AppData/Roaming/Claude/claude_desktop_config.json"
            elif os.name == 'posix':
                if Path.home().joinpath("Library").exists():  # macOS
                    output_path = Path.home() / "Library/Application Support/Claude/claude_desktop_config.json"
                else:  # Linux
                    output_path = Path.home() / ".config/claude/claude_desktop_config.json"
        
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
        
        logger.info(f"Claude desktop configuration created at {output_path}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to create Claude desktop config: {e}")
        return False


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "setup":
        async def main():
            try:
                integration = await setup_claude_integration()
                print("✅ Claude integration setup completed!")
                print("🔧 Configuration files updated")
                print("🚀 Restart Claude Desktop to activate integration")
                
            except Exception as e:
                print(f"❌ Setup failed: {e}")
                sys.exit(1)
        
        asyncio.run(main())
    
    elif len(sys.argv) > 1 and sys.argv[1] == "config":
        output_path = sys.argv[2] if len(sys.argv) > 2 else None
        
        if create_claude_desktop_config(output_path):
            print(f"✅ Claude desktop configuration created")
        else:
            print("❌ Failed to create configuration")
            sys.exit(1)
    
    else:
        print("Usage:")
        print("  python claude_integration.py setup")
        print("  python claude_integration.py config [output_path]")
