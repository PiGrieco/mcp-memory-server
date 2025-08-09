#!/usr/bin/env python3
"""
Production-Ready GPT/OpenAI Integration for MCP Memory Server
Enhanced with ChatGPT Plus, API, and custom GPT support
"""

import asyncio
import json
import time
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any

from .base_integration import BaseAIIntegration, ConversationContext, AIIntegrationError
from ...src.utils.logging import get_logger, log_performance


logger = get_logger(__name__)


class GPTMemoryIntegration(BaseAIIntegration):
    """Production-ready GPT integration supporting multiple OpenAI interfaces"""
    
    def __init__(self, config_override: Optional[Dict] = None):
        super().__init__("gpt", config_override)
        
        # GPT-specific configuration
        self.gpt_config = {
            "api_integration": True,
            "chatgpt_web_integration": True,
            "custom_gpt_support": True,
            "memory_injection_format": "structured",
            "max_context_tokens": 8000,
            "importance_boost_keywords": [
                "important", "remember", "note this", "key insight", 
                "action item", "follow up", "decision", "conclusion"
            ]
        }
        self.gpt_config.update(self.integration_config.get('platform_specific', {}))
        
        # OpenAI API configuration
        self.openai_client = None
        
    async def initialize(self) -> bool:
        """Initialize GPT integration"""
        try:
            self.logger.info("Initializing GPT integration...")
            
            # Initialize OpenAI API client if API key available
            await self._setup_openai_api()
            
            # Setup custom GPT instructions
            await self._generate_custom_gpt_instructions()
            
            self.logger.info("GPT integration initialized successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to initialize GPT integration: {e}")
            return False
    
    async def _setup_openai_api(self):
        """Setup OpenAI API client"""
        try:
            import os
            api_key = os.getenv('OPENAI_API_KEY')
            
            if api_key and self.gpt_config.get('api_integration', True):
                try:
                    import openai
                    self.openai_client = openai.AsyncOpenAI(api_key=api_key)
                    self.logger.info("OpenAI API client initialized")
                except ImportError:
                    self.logger.warning("OpenAI library not available, API integration disabled")
            else:
                self.logger.debug("OpenAI API key not configured")
                
        except Exception as e:
            self.logger.warning(f"Failed to setup OpenAI API: {e}")
    
    async def _generate_custom_gpt_instructions(self) -> str:
        """Generate custom GPT instructions for memory integration"""
        instructions = f"""# Custom GPT with Persistent Memory

You are a custom GPT with access to a persistent memory system that remembers important information across conversations.

## Memory System Capabilities
- **Remember**: Save important information, decisions, insights, and context
- **Recall**: Search and retrieve relevant past information
- **Context**: Maintain continuity across multiple conversations
- **Learning**: Build upon previous interactions and knowledge

## How to Use Memory
1. **Automatic Saving**: Important information is automatically saved
2. **Manual Saving**: Use phrases like "remember this" or "note that" for explicit saving
3. **Retrieval**: Relevant memories are automatically surfaced when needed
4. **Reference**: Feel free to reference past conversations and build upon them

## Memory Categories
- Conversations and insights
- Decisions and action items  
- Code snippets and technical solutions
- Personal preferences and context
- Project information and goals

## Best Practices
- Build context from previous conversations
- Reference relevant past discussions
- Maintain continuity in ongoing projects
- Learn from past interactions to provide better assistance

Remember: This memory system helps provide more personalized, contextual, and helpful assistance by building upon our conversation history.
"""
        
        # Save instructions to file for easy copying to Custom GPT
        try:
            from pathlib import Path
            instructions_path = Path.home() / ".mcp_memory" / "gpt_custom_instructions.md"
            instructions_path.parent.mkdir(exist_ok=True)
            
            with open(instructions_path, 'w') as f:
                f.write(instructions)
            
            self.logger.info(f"Custom GPT instructions saved to {instructions_path}")
            
        except Exception as e:
            self.logger.warning(f"Failed to save custom GPT instructions: {e}")
        
        return instructions
    
    async def extract_conversation_context(self, data: Dict[str, Any]) -> Optional[ConversationContext]:
        """Extract conversation context from GPT interaction"""
        try:
            conversation_id = data.get('conversation_id') or f"gpt_{int(time.time())}"
            
            messages = []
            
            # Handle different GPT interaction formats
            if 'messages' in data:
                # API format
                for msg in data['messages'][-12:]:  # Last 12 messages for GPT context
                    messages.append({
                        'role': msg.get('role', 'user'),
                        'content': msg.get('content', ''),
                        'timestamp': msg.get('timestamp', datetime.now(timezone.utc).isoformat())
                    })
            
            elif 'user_message' in data:
                # Simple format
                messages.append({
                    'role': 'user',
                    'content': data['user_message'],
                    'timestamp': datetime.now(timezone.utc).isoformat()
                })
                
                if 'assistant_message' in data:
                    messages.append({
                        'role': 'assistant',
                        'content': data['assistant_message'],
                        'timestamp': datetime.now(timezone.utc).isoformat()
                    })
            
            elif 'chatgpt_conversation' in data:
                # ChatGPT web format
                conv = data['chatgpt_conversation']
                for turn in conv.get('turns', [])[-6:]:
                    if 'user' in turn:
                        messages.append({
                            'role': 'user',
                            'content': turn['user'],
                            'timestamp': datetime.now(timezone.utc).isoformat()
                        })
                    if 'assistant' in turn:
                        messages.append({
                            'role': 'assistant',
                            'content': turn['assistant'],
                            'timestamp': datetime.now(timezone.utc).isoformat()
                        })
            
            if not messages:
                return None
            
            # Calculate importance for GPT conversations
            importance = await self._calculate_gpt_importance(messages, data)
            
            metadata = {
                'gpt_model': data.get('model', 'gpt-4'),
                'interface_type': data.get('interface', 'unknown'),  # api, web, custom_gpt
                'conversation_length': len(messages),
                'has_code': any('```' in msg.get('content', '') for msg in messages),
                'custom_gpt_name': data.get('custom_gpt_name'),
                'temperature': data.get('temperature', 0.7),
                'max_tokens': data.get('max_tokens')
            }
            
            return ConversationContext(
                conversation_id=conversation_id,
                platform='gpt',
                user_id=data.get('user_id'),
                messages=messages,
                metadata=metadata,
                timestamp=datetime.now(timezone.utc),
                importance_score=importance,
                project=self.integration_config.get('project', 'default')
            )
            
        except Exception as e:
            self.logger.error(f"Failed to extract GPT conversation context: {e}")
            return None
    
    async def _calculate_gpt_importance(self, messages: List[Dict], data: Dict) -> float:
        """Calculate importance for GPT conversations"""
        base_importance = 0.5
        
        # Get all content
        all_content = ' '.join([msg.get('content', '') for msg in messages]).lower()
        
        # Boost for importance keywords
        keyword_count = sum(1 for keyword in self.gpt_config['importance_boost_keywords'] 
                           if keyword in all_content)
        base_importance += min(0.3, keyword_count * 0.1)
        
        # Boost for code content
        if any('```' in msg.get('content', '') for msg in messages):
            base_importance += 0.2
        
        # Boost for longer conversations
        total_length = len(all_content)
        if total_length > 1500:
            base_importance += 0.15
        elif total_length < 100:
            base_importance -= 0.15
        
        # Boost for custom GPT interactions
        if data.get('interface') == 'custom_gpt':
            base_importance += 0.1
        
        # Boost for explicit memory requests
        memory_indicators = ['remember', 'save this', 'note this', 'important']
        if any(indicator in all_content for indicator in memory_indicators):
            base_importance += 0.2
        
        return max(0.0, min(1.0, base_importance))
    
    async def format_memory_for_platform(self, memory: Dict[str, Any]) -> str:
        """Format memory content for GPT"""
        try:
            content = memory.get('content', '')
            importance = memory.get('importance', 0.5)
            created_at = memory.get('created_at', '')
            memory_type = memory.get('memory_type', 'conversation')
            
            if self.gpt_config.get('memory_injection_format') == 'structured':
                # Structured format for GPT
                formatted = f"""[MEMORY] {memory_type.upper()}
Date: {created_at}
Importance: {importance:.1f}/1.0

{content}

[/MEMORY]"""
            else:
                # Natural format
                importance_desc = "High" if importance > 0.7 else "Medium" if importance > 0.4 else "Low"
                formatted = f"""Previous context ({importance_desc} importance, {created_at}):
{content}"""
            
            return formatted
            
        except Exception as e:
            self.logger.error(f"Failed to format memory for GPT: {e}")
            return f"Previous conversation: {memory.get('content', 'No content')}"
    
    @log_performance("gpt_api_interaction")
    async def create_gpt_completion_with_memory(
        self,
        messages: List[Dict[str, str]],
        model: str = "gpt-4",
        include_memory_context: bool = True,
        memory_limit: int = 3
    ) -> Optional[str]:
        """Create GPT completion with memory context"""
        try:
            if not self.openai_client:
                self.logger.warning("OpenAI client not available")
                return None
            
            enhanced_messages = messages.copy()
            
            # Add memory context if enabled
            if include_memory_context and len(messages) > 0:
                last_user_message = None
                for msg in reversed(messages):
                    if msg.get('role') == 'user':
                        last_user_message = msg.get('content', '')
                        break
                
                if last_user_message:
                    relevant_memories = await self.search_relevant_memories(
                        last_user_message, 
                        limit=memory_limit
                    )
                    
                    if relevant_memories:
                        memory_context = "\n\n".join([
                            await self.format_memory_for_platform(memory)
                            for memory in relevant_memories
                        ])
                        
                        # Insert memory context before the last user message
                        memory_message = {
                            "role": "system",
                            "content": f"Relevant context from previous conversations:\n\n{memory_context}"
                        }
                        enhanced_messages.insert(-1, memory_message)
            
            # Create completion
            response = await self.openai_client.chat.completions.create(
                model=model,
                messages=enhanced_messages,
                temperature=0.7,
                max_tokens=2000
            )
            
            if response.choices:
                assistant_message = response.choices[0].message.content
                
                # Save this interaction as memory if significant
                conversation_data = {
                    'messages': enhanced_messages + [{'role': 'assistant', 'content': assistant_message}],
                    'model': model,
                    'interface': 'api'
                }
                
                await self.process_conversation(conversation_data)
                
                return assistant_message
            
        except Exception as e:
            self.logger.error(f"GPT API completion failed: {e}")
        
        return None
    
    async def enhance_custom_gpt_context(self, user_input: str) -> str:
        """Enhance user input for custom GPT with memory context"""
        try:
            if not self.gpt_config.get('custom_gpt_support', True):
                return user_input
            
            # Search for relevant memories
            relevant_memories = await self.search_relevant_memories(user_input, limit=2)
            
            if not relevant_memories:
                return user_input
            
            # Format memories for context
            memory_context = "\n".join([
                await self.format_memory_for_platform(memory)
                for memory in relevant_memories
            ])
            
            # Create enhanced input
            enhanced_input = f"""Context from our previous conversations:
{memory_context}

Current question/request:
{user_input}"""
            
            return enhanced_input
            
        except Exception as e:
            self.logger.error(f"Failed to enhance custom GPT context: {e}")
            return user_input
    
    async def process_chatgpt_conversation(self, conversation_data: Dict) -> Optional[Dict]:
        """Process ChatGPT web conversation"""
        try:
            # Extract conversation from web format
            formatted_data = {
                'chatgpt_conversation': conversation_data,
                'interface': 'web',
                'model': conversation_data.get('model', 'gpt-4')
            }
            
            return await self.process_conversation(formatted_data)
            
        except Exception as e:
            self.logger.error(f"Failed to process ChatGPT conversation: {e}")
            return None
    
    async def create_function_calling_memory(
        self,
        function_calls: List[Dict],
        conversation_context: str
    ) -> Optional[Dict]:
        """Create memory for GPT function calling interactions"""
        try:
            # Format function calls for memory
            function_summary = []
            for call in function_calls:
                func_name = call.get('name', 'unknown')
                func_args = call.get('arguments', {})
                func_result = call.get('result', 'No result')
                
                function_summary.append(f"Function: {func_name}")
                function_summary.append(f"Arguments: {json.dumps(func_args, indent=2)}")
                function_summary.append(f"Result: {func_result}")
                function_summary.append("---")
            
            memory_content = f"""Conversation Context:
{conversation_context}

Function Calls Made:
{chr(10).join(function_summary)}"""
            
            return await self.memory_client.create_memory(
                content=memory_content,
                importance=0.8,  # Function calls are generally important
                memory_type='function_call',
                metadata={
                    'platform': 'gpt',
                    'function_count': len(function_calls),
                    'functions_used': [call.get('name') for call in function_calls],
                    'created_by_integration': True
                },
                project=self.integration_config.get('project', 'default')
            )
            
        except Exception as e:
            self.logger.error(f"Failed to create function calling memory: {e}")
            return None


# Standalone utility functions
async def setup_gpt_integration(config: Optional[Dict] = None) -> GPTMemoryIntegration:
    """Setup GPT integration with optional configuration"""
    integration = GPTMemoryIntegration(config)
    
    success = await integration.start_integration()
    if not success:
        raise AIIntegrationError("Failed to setup GPT integration")
    
    return integration


def generate_gpt_custom_instructions() -> str:
    """Generate custom GPT instructions for memory integration"""
    return """# GPT with Persistent Memory

You are an AI assistant with access to a persistent memory system that remembers important information across conversations.

## Key Features:
- **Persistent Memory**: Important information is automatically saved and can be recalled in future conversations
- **Context Continuity**: Build upon previous conversations and maintain long-term context
- **Smart Recall**: Relevant past information is automatically surfaced when needed
- **Learning**: Improve responses based on past interactions and user preferences

## How It Works:
1. Important information from our conversations is automatically saved
2. When you receive a query, relevant past context is provided
3. You can reference previous conversations naturally
4. User preferences and context build up over time

## Best Practices:
- Reference relevant past conversations when helpful
- Build upon previous discussions and decisions
- Maintain consistency with past preferences and context
- Ask clarifying questions that build on known context

## Memory Categories:
- Personal preferences and context
- Project information and decisions
- Code solutions and technical details
- Insights and important conclusions
- Action items and follow-ups

This memory system enables more personalized, contextual, and helpful assistance by maintaining continuity across all our interactions.
"""


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "setup":
        async def main():
            try:
                integration = await setup_gpt_integration()
                instructions = generate_gpt_custom_instructions()
                
                print("✅ GPT integration setup completed!")
                print("\n📋 Custom GPT Instructions:")
                print("=" * 50)
                print(instructions)
                print("=" * 50)
                print("\n📝 Copy the above instructions to your Custom GPT configuration")
                
            except Exception as e:
                print(f"❌ Setup failed: {e}")
                sys.exit(1)
        
        asyncio.run(main())
    
    elif len(sys.argv) > 1 and sys.argv[1] == "instructions":
        print(generate_gpt_custom_instructions())
    
    else:
        print("Usage:")
        print("  python gpt_integration.py setup")
        print("  python gpt_integration.py instructions")
