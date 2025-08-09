#!/usr/bin/env python3
"""
Base AI Integration Class for MCP Memory Server
Production-ready foundation for all AI agent integrations
"""

import asyncio
import json
import logging
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any, Callable
from pathlib import Path

from ...src.config.settings import get_config
from ...src.utils.logging import get_logger, log_performance
from ...src.utils.exceptions import MCPMemoryError
from ...src.utils.retry import retry_async
from ...src.utils.validation import validate_email


logger = get_logger(__name__)


@dataclass
class ConversationContext:
    """Enhanced conversation context structure"""
    conversation_id: str
    platform: str
    user_id: Optional[str]
    messages: List[Dict[str, Any]]
    metadata: Dict[str, Any]
    timestamp: datetime
    importance_score: float = 0.5
    project: str = "default"
    
    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data['timestamp'] = self.timestamp.isoformat()
        return data


@dataclass
class MemoryTrigger:
    """Memory trigger configuration"""
    trigger_type: str  # auto, manual, keyword, importance
    threshold: float = 0.7
    keywords: List[str] = None
    cooldown_seconds: int = 30
    max_memories_per_session: int = 10
    
    def __post_init__(self):
        if self.keywords is None:
            self.keywords = []


class AIIntegrationError(MCPMemoryError):
    """Error in AI integration"""
    pass


class BaseAIIntegration(ABC):
    """
    Base class for AI agent integrations with MCP Memory Server
    Provides common functionality for all AI platforms
    """
    
    def __init__(
        self, 
        platform_name: str,
        config_override: Optional[Dict] = None,
        custom_logger: Optional[logging.Logger] = None
    ):
        self.platform_name = platform_name
        self.config = get_config()
        self.logger = custom_logger or get_logger(f"{__name__}.{platform_name}")
        
        # Integration configuration
        self.integration_config = self._load_integration_config(config_override)
        
        # Memory management
        self.memory_client = None
        self.conversation_cache = {}
        self.trigger_config = MemoryTrigger(**self.integration_config.get('triggers', {}))
        
        # Session tracking
        self.session_memory_count = 0
        self.last_memory_time = 0
        self.active_conversations = set()
        
        # Hooks and callbacks
        self.hooks = {
            'pre_save': [],
            'post_save': [],
            'pre_search': [],
            'post_search': [],
            'conversation_start': [],
            'conversation_end': []
        }
        
        self.logger.info(f"Initialized {platform_name} integration")
    
    def _load_integration_config(self, config_override: Optional[Dict] = None) -> Dict:
        """Load platform-specific configuration"""
        default_config = {
            'auto_save_enabled': True,
            'importance_threshold': 0.5,
            'max_context_length': 4000,
            'memory_search_limit': 5,
            'triggers': {
                'trigger_type': 'auto',
                'threshold': 0.7,
                'cooldown_seconds': 30,
                'max_memories_per_session': 10
            },
            'platform_specific': {}
        }
        
        # Load from config file if exists
        config_path = Path.home() / f".mcp_memory/integrations/{self.platform_name}.json"
        if config_path.exists():
            try:
                with open(config_path, 'r') as f:
                    file_config = json.load(f)
                default_config.update(file_config)
            except Exception as e:
                self.logger.warning(f"Failed to load config from {config_path}: {e}")
        
        # Apply override
        if config_override:
            default_config.update(config_override)
        
        return default_config
    
    @abstractmethod
    async def initialize(self) -> bool:
        """Initialize the AI integration"""
        pass
    
    @abstractmethod
    async def extract_conversation_context(self, data: Dict[str, Any]) -> Optional[ConversationContext]:
        """Extract conversation context from platform-specific data"""
        pass
    
    @abstractmethod
    async def format_memory_for_platform(self, memory: Dict[str, Any]) -> str:
        """Format memory content for the specific AI platform"""
        pass
    
    async def start_integration(self) -> bool:
        """Start the AI integration service"""
        try:
            self.logger.info(f"Starting {self.platform_name} integration...")
            
            # Initialize memory client
            await self._initialize_memory_client()
            
            # Platform-specific initialization
            success = await self.initialize()
            
            if success:
                self.logger.info(f"{self.platform_name} integration started successfully")
                await self._trigger_hook('integration_start')
            else:
                self.logger.error(f"Failed to start {self.platform_name} integration")
            
            return success
            
        except Exception as e:
            self.logger.error(f"Error starting {self.platform_name} integration: {e}")
            raise AIIntegrationError(f"Integration startup failed: {e}")
    
    async def _initialize_memory_client(self):
        """Initialize MCP memory client"""
        try:
            # Import here to avoid circular imports
            from ...src.services.memory_service import MemoryService
            from ...src.services.database_service import DatabaseService
            from ...src.services.embedding_service import EmbeddingService
            
            # Initialize services
            db_service = DatabaseService()
            await db_service.initialize()
            
            embedding_service = EmbeddingService()
            await embedding_service.initialize()
            
            self.memory_client = MemoryService(db_service, embedding_service)
            
            self.logger.debug("Memory client initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize memory client: {e}")
            raise
    
    @log_performance("conversation_processing")
    async def process_conversation(
        self, 
        conversation_data: Dict[str, Any],
        force_save: bool = False
    ) -> Optional[Dict[str, Any]]:
        """
        Process a conversation and potentially save it as memory
        """
        try:
            # Extract context
            context = await self.extract_conversation_context(conversation_data)
            if not context:
                self.logger.debug("No valid conversation context extracted")
                return None
            
            # Trigger hooks
            await self._trigger_hook('pre_save', context)
            
            # Check if should save
            if await self._should_save_memory(context, force_save):
                memory = await self._create_memory_from_context(context)
                if memory:
                    # Save memory
                    result = await self.memory_client.create_memory(
                        content=memory['content'],
                        importance=memory['importance'],
                        memory_type=memory['memory_type'],
                        metadata=memory['metadata'],
                        project=memory['project']
                    )
                    
                    if result:
                        self.session_memory_count += 1
                        self.last_memory_time = time.time()
                        
                        self.logger.info(f"Memory saved: {result.get('id')}")
                        await self._trigger_hook('post_save', result)
                        
                        return result
            
            return None
            
        except Exception as e:
            self.logger.error(f"Error processing conversation: {e}")
            return None
    
    @log_performance("memory_search")
    async def search_relevant_memories(
        self, 
        query: str,
        limit: int = None,
        threshold: float = None
    ) -> List[Dict[str, Any]]:
        """Search for relevant memories"""
        try:
            if not self.memory_client:
                return []
            
            # Use config defaults if not specified
            limit = limit or self.integration_config.get('memory_search_limit', 5)
            threshold = threshold or self.integration_config.get('importance_threshold', 0.3)
            
            await self._trigger_hook('pre_search', {'query': query, 'limit': limit})
            
            memories = await self.memory_client.search_memories(
                query=query,
                limit=limit,
                similarity_threshold=threshold,
                project=self.integration_config.get('project', 'default')
            )
            
            await self._trigger_hook('post_search', {'query': query, 'results': memories})
            
            return memories
            
        except Exception as e:
            self.logger.error(f"Memory search failed: {e}")
            return []
    
    async def get_memory_suggestions(
        self, 
        current_context: str,
        conversation_id: Optional[str] = None
    ) -> List[str]:
        """Get formatted memory suggestions for current context"""
        try:
            memories = await self.search_relevant_memories(current_context)
            
            suggestions = []
            for memory in memories:
                formatted = await self.format_memory_for_platform(memory)
                if formatted:
                    suggestions.append(formatted)
            
            return suggestions
            
        except Exception as e:
            self.logger.error(f"Failed to get memory suggestions: {e}")
            return []
    
    async def _should_save_memory(self, context: ConversationContext, force: bool = False) -> bool:
        """Determine if conversation should be saved as memory"""
        if force:
            return True
        
        if not self.integration_config.get('auto_save_enabled', True):
            return False
        
        # Check cooldown
        if time.time() - self.last_memory_time < self.trigger_config.cooldown_seconds:
            return False
        
        # Check session limits
        if self.session_memory_count >= self.trigger_config.max_memories_per_session:
            return False
        
        # Check importance threshold
        if context.importance_score < self.trigger_config.threshold:
            return False
        
        # Check content length
        total_content = ' '.join([msg.get('content', '') for msg in context.messages])
        if len(total_content.strip()) < 50:  # Minimum content length
            return False
        
        return True
    
    async def _create_memory_from_context(self, context: ConversationContext) -> Optional[Dict[str, Any]]:
        """Create memory object from conversation context"""
        try:
            # Generate memory content
            content = await self._generate_memory_content(context)
            if not content:
                return None
            
            # Calculate importance
            importance = await self._calculate_importance(context)
            
            # Determine memory type
            memory_type = await self._determine_memory_type(context)
            
            return {
                'content': content,
                'importance': importance,
                'memory_type': memory_type,
                'metadata': {
                    'platform': self.platform_name,
                    'conversation_id': context.conversation_id,
                    'user_id': context.user_id,
                    'message_count': len(context.messages),
                    'integration_version': self.__class__.__module__ + '.' + self.__class__.__name__,
                    'created_by_integration': True,
                    **context.metadata
                },
                'project': context.project
            }
            
        except Exception as e:
            self.logger.error(f"Failed to create memory from context: {e}")
            return None
    
    async def _generate_memory_content(self, context: ConversationContext) -> str:
        """Generate memory content from conversation context"""
        if not context.messages:
            return ""
        
        # Format conversation
        content_parts = []
        for msg in context.messages[-6:]:  # Last 6 messages
            role = msg.get('role', 'unknown')
            content = msg.get('content', '').strip()
            
            if content:
                content_parts.append(f"{role.title()}: {content}")
        
        content = '\n\n'.join(content_parts)
        
        # Truncate if too long
        max_length = self.integration_config.get('max_context_length', 4000)
        if len(content) > max_length:
            content = content[:max_length] + "..."
        
        return content
    
    async def _calculate_importance(self, context: ConversationContext) -> float:
        """Calculate importance score for conversation"""
        base_importance = context.importance_score
        
        # Adjust based on conversation length
        message_count = len(context.messages)
        if message_count > 10:
            base_importance += 0.1
        elif message_count < 3:
            base_importance -= 0.1
        
        # Adjust based on keywords
        content = ' '.join([msg.get('content', '') for msg in context.messages])
        important_keywords = ['important', 'remember', 'note', 'task', 'todo', 'deadline']
        
        for keyword in important_keywords:
            if keyword.lower() in content.lower():
                base_importance += 0.1
                break
        
        # Clamp between 0 and 1
        return max(0.0, min(1.0, base_importance))
    
    async def _determine_memory_type(self, context: ConversationContext) -> str:
        """Determine memory type based on context"""
        content = ' '.join([msg.get('content', '') for msg in context.messages]).lower()
        
        if any(word in content for word in ['function', 'code', 'method', 'class']):
            return 'function'
        elif any(word in content for word in ['task', 'todo', 'deadline', 'schedule']):
            return 'task'
        elif any(word in content for word in ['error', 'bug', 'issue', 'problem']):
            return 'error'
        elif any(word in content for word in ['knowledge', 'fact', 'information', 'learn']):
            return 'knowledge'
        else:
            return 'conversation'
    
    def add_hook(self, event: str, callback: Callable):
        """Add event hook"""
        if event in self.hooks:
            self.hooks[event].append(callback)
    
    async def _trigger_hook(self, event: str, data: Any = None):
        """Trigger event hooks"""
        if event in self.hooks:
            for callback in self.hooks[event]:
                try:
                    if asyncio.iscoroutinefunction(callback):
                        await callback(data)
                    else:
                        callback(data)
                except Exception as e:
                    self.logger.warning(f"Hook {event} callback failed: {e}")
    
    async def get_integration_stats(self) -> Dict[str, Any]:
        """Get integration statistics"""
        return {
            'platform': self.platform_name,
            'session_memory_count': self.session_memory_count,
            'active_conversations': len(self.active_conversations),
            'last_memory_time': self.last_memory_time,
            'config': self.integration_config,
            'memory_client_available': self.memory_client is not None
        }
    
    async def reset_session(self):
        """Reset session counters"""
        self.session_memory_count = 0
        self.last_memory_time = 0
        self.active_conversations.clear()
        self.logger.info(f"Reset {self.platform_name} integration session")
    
    async def shutdown(self):
        """Shutdown the integration"""
        try:
            await self._trigger_hook('integration_shutdown')
            
            if self.memory_client:
                # Close any connections
                if hasattr(self.memory_client, 'close'):
                    await self.memory_client.close()
            
            self.logger.info(f"{self.platform_name} integration shutdown complete")
            
        except Exception as e:
            self.logger.error(f"Error during {self.platform_name} integration shutdown: {e}")


# Utility functions for integration development
def create_integration_config_template(platform_name: str) -> Dict[str, Any]:
    """Create a configuration template for a new integration"""
    return {
        'platform_name': platform_name,
        'auto_save_enabled': True,
        'importance_threshold': 0.5,
        'max_context_length': 4000,
        'memory_search_limit': 5,
        'triggers': {
            'trigger_type': 'auto',
            'threshold': 0.7,
            'cooldown_seconds': 30,
            'max_memories_per_session': 10
        },
        'platform_specific': {
            # Platform-specific configuration goes here
        }
    }


def save_integration_config(platform_name: str, config: Dict[str, Any]):
    """Save integration configuration to file"""
    config_dir = Path.home() / ".mcp_memory/integrations"
    config_dir.mkdir(parents=True, exist_ok=True)
    
    config_path = config_dir / f"{platform_name}.json"
    with open(config_path, 'w') as f:
        json.dump(config, f, indent=2)
    
    logger.info(f"Saved {platform_name} integration config to {config_path}")
