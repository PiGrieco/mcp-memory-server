#!/usr/bin/env python3
"""
Advanced Cursor Integration with Auto-Triggering
Monitors Cursor conversations and automatically triggers memory operations
"""

import asyncio
import json
import time
import threading
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass

from .cursor_integration import CursorMemoryIntegration
from ...src.core.auto_trigger_system import AutoTriggerSystem
from ...src.utils.logging import get_logger, log_performance


logger = get_logger(__name__)


@dataclass
class CursorMessage:
    """Represents a message in Cursor conversation"""
    role: str  # "user", "assistant", "system"
    content: str
    timestamp: datetime
    file_context: Optional[str] = None
    line_number: Optional[int] = None
    project_context: Optional[str] = None


class CursorConversationMonitor:
    """
    Monitors Cursor conversations and triggers automatic memory operations
    """
    
    def __init__(self, integration: CursorMemoryIntegration):
        self.integration = integration
        self.auto_trigger_system = None
        
        # Message tracking
        self.message_buffer = []
        self.last_analysis_time = 0
        self.analysis_interval = 5.0  # seconds
        
        # File monitoring
        self.monitored_files = set()
        self.file_watchers = {}
        
        # Configuration
        self.auto_save_enabled = True
        self.min_conversation_length = 2
        self.max_buffer_size = 50
        
        logger.info("Cursor conversation monitor initialized")
    
    async def initialize(self):
        """Initialize the monitor with auto-trigger system"""
        try:
            # Get auto-trigger system from integration
            if hasattr(self.integration, 'memory_client'):
                from ...src.core.auto_trigger_system import create_auto_trigger_system
                from ...src.services.embedding_service import EmbeddingService
                
                # Create embedding service for auto-trigger
                embedding_service = EmbeddingService()
                await embedding_service.initialize()
                
                self.auto_trigger_system = create_auto_trigger_system(
                    self.integration.memory_client,
                    embedding_service
                )
                
                logger.info("Auto-trigger system initialized for Cursor")
            
        except Exception as e:
            logger.error(f"Failed to initialize auto-trigger system: {e}")
    
    async def add_message(
        self, 
        role: str, 
        content: str, 
        file_context: Optional[str] = None,
        line_number: Optional[int] = None
    ):
        """Add a new message to the conversation buffer"""
        message = CursorMessage(
            role=role,
            content=content,
            timestamp=datetime.now(timezone.utc),
            file_context=file_context,
            line_number=line_number,
            project_context=str(self.integration.workspace_path) if self.integration.workspace_path else None
        )
        
        self.message_buffer.append(message)
        
        # Limit buffer size
        if len(self.message_buffer) > self.max_buffer_size:
            self.message_buffer = self.message_buffer[-self.max_buffer_size:]
        
        # Check if we should trigger analysis
        await self._check_trigger_analysis()
    
    async def _check_trigger_analysis(self):
        """Check if we should trigger automatic analysis"""
        current_time = time.time()
        
        # Check time-based trigger
        if current_time - self.last_analysis_time < self.analysis_interval:
            return
        
        # Check message count trigger
        if len(self.message_buffer) < self.min_conversation_length:
            return
        
        # Trigger analysis
        await self._trigger_automatic_analysis()
        self.last_analysis_time = current_time
    
    async def _trigger_automatic_analysis(self):
        """Trigger automatic analysis of current conversation"""
        if not self.auto_trigger_system or not self.message_buffer:
            return
        
        try:
            # Convert messages to format expected by auto-trigger system
            messages = [
                {
                    "role": msg.role,
                    "content": msg.content,
                    "timestamp": msg.timestamp.isoformat(),
                    "metadata": {
                        "file_context": msg.file_context,
                        "line_number": msg.line_number,
                        "project_context": msg.project_context
                    }
                }
                for msg in self.message_buffer[-10:]  # Last 10 messages
            ]
            
            # Check triggers
            triggered_actions = await self.auto_trigger_system.check_triggers(messages, "cursor")
            
            # Execute triggered actions
            for action, params in triggered_actions:
                await self._execute_triggered_action(action, params)
                
        except Exception as e:
            logger.error(f"Auto-analysis failed: {e}")
    
    async def _execute_triggered_action(self, action: str, params: Dict[str, Any]):
        """Execute a triggered action"""
        try:
            if action == "save_memory":
                # Enhance params with Cursor-specific context
                enhanced_params = await self._enhance_save_params(params)
                
                # Save memory through integration
                result = await self.integration.memory_client.create_memory(
                    content=enhanced_params.get("content"),
                    importance=enhanced_params.get("importance", 0.5),
                    memory_type=enhanced_params.get("memory_type", "conversation"),
                    metadata=enhanced_params.get("metadata", {}),
                    project=enhanced_params.get("project", "default")
                )
                
                if result:
                    logger.info(f"Auto-triggered memory save: {result.get('id')}")
                    
                    # Optionally notify user (could be shown in Cursor UI)
                    await self._notify_user_auto_save(result)
            
            elif action == "search_memories":
                # Search for relevant memories
                memories = await self.integration.search_relevant_memories(
                    query=params.get("query", ""),
                    limit=params.get("limit", 5)
                )
                
                if memories:
                    logger.info(f"Auto-triggered search found {len(memories)} relevant memories")
                    
                    # Could inject memories into Cursor context
                    await self._inject_relevant_memories(memories)
            
            elif action == "get_memory_context":
                # Get context for current conversation
                context = params.get("context", "")
                memories = await self.integration.search_relevant_memories(context, limit=3)
                
                if memories:
                    logger.info(f"Auto-triggered context retrieval: {len(memories)} memories")
            
        except Exception as e:
            logger.error(f"Failed to execute triggered action {action}: {e}")
    
    async def _enhance_save_params(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Enhance save parameters with Cursor-specific context"""
        enhanced = params.copy()
        
        # Add workspace context
        if self.integration.workspace_path:
            enhanced.setdefault("metadata", {})["workspace_path"] = str(self.integration.workspace_path)
        
        # Add current file context if available
        current_file = self._get_current_file_context()
        if current_file:
            enhanced.setdefault("metadata", {})["current_file"] = current_file
        
        # Add project context
        enhanced["project"] = self.integration.integration_config.get("project", "default")
        
        # Enhance memory type based on content
        content = enhanced.get("content", "")
        if any(marker in content.lower() for marker in ["bug", "error", "issue", "problem"]):
            enhanced["memory_type"] = "error_solution"
        elif any(marker in content.lower() for marker in ["how to", "tutorial", "guide"]):
            enhanced["memory_type"] = "knowledge"
        elif "```" in content:
            enhanced["memory_type"] = "code_snippet"
        
        return enhanced
    
    def _get_current_file_context(self) -> Optional[str]:
        """Get current file context from recent messages"""
        for msg in reversed(self.message_buffer[-5:]):
            if msg.file_context:
                return msg.file_context
        return None
    
    async def _notify_user_auto_save(self, result: Dict[str, Any]):
        """Notify user that memory was auto-saved (placeholder)"""
        # This could be implemented to show notifications in Cursor
        # For now, just log
        memory_id = result.get("id", "unknown")
        logger.info(f"💾 Auto-saved memory: {memory_id}")
    
    async def _inject_relevant_memories(self, memories: List[Dict[str, Any]]):
        """Inject relevant memories into Cursor context (placeholder)"""
        # This could be implemented to provide context to Cursor
        # For now, just log
        logger.info(f"🧠 Found {len(memories)} relevant memories for context")
    
    async def force_analysis(self):
        """Force immediate analysis of current conversation"""
        await self._trigger_automatic_analysis()
    
    def get_conversation_summary(self) -> Dict[str, Any]:
        """Get summary of current conversation"""
        if not self.message_buffer:
            return {"message_count": 0, "summary": "No conversation"}
        
        total_length = sum(len(msg.content) for msg in self.message_buffer)
        avg_length = total_length / len(self.message_buffer)
        
        # Get file contexts
        file_contexts = set(msg.file_context for msg in self.message_buffer if msg.file_context)
        
        return {
            "message_count": len(self.message_buffer),
            "avg_message_length": avg_length,
            "total_content_length": total_length,
            "file_contexts": list(file_contexts),
            "time_span": (
                self.message_buffer[-1].timestamp - self.message_buffer[0].timestamp
            ).total_seconds() if len(self.message_buffer) > 1 else 0,
            "last_message_time": self.message_buffer[-1].timestamp.isoformat() if self.message_buffer else None
        }


class CursorAutoIntegration(CursorMemoryIntegration):
    """
    Enhanced Cursor integration with automatic triggering capabilities
    """
    
    def __init__(self, config_override: Optional[Dict] = None):
        super().__init__(config_override)
        
        # Auto-monitoring components
        self.conversation_monitor = None
        self.mcp_server_connection = None
        
        # Configuration for auto-features
        self.auto_config = {
            "conversation_monitoring": True,
            "auto_trigger_enabled": True,
            "file_watching": True,
            "context_injection": True,
            "notification_enabled": True
        }
        self.auto_config.update(self.integration_config.get("auto_features", {}))
    
    async def initialize(self) -> bool:
        """Initialize with auto-monitoring capabilities"""
        success = await super().initialize()
        
        if success and self.auto_config.get("conversation_monitoring", True):
            # Initialize conversation monitor
            self.conversation_monitor = CursorConversationMonitor(self)
            await self.conversation_monitor.initialize()
            
            # Setup MCP server connection for auto-triggering
            await self._setup_mcp_auto_connection()
        
        return success
    
    async def _setup_mcp_auto_connection(self):
        """Setup connection to enhanced MCP server for auto-triggering"""
        try:
            # This would connect to the enhanced MCP server
            # For now, we'll use direct integration
            logger.info("MCP auto-connection setup completed")
            
        except Exception as e:
            logger.warning(f"MCP auto-connection setup failed: {e}")
    
    async def process_cursor_message(
        self, 
        role: str, 
        content: str, 
        file_path: Optional[str] = None,
        line_number: Optional[int] = None
    ):
        """Process a Cursor message with auto-triggering"""
        try:
            # Add to conversation monitor
            if self.conversation_monitor:
                await self.conversation_monitor.add_message(
                    role=role,
                    content=content,
                    file_context=file_path,
                    line_number=line_number
                )
            
            # Process through standard integration
            conversation_data = {
                "messages": [{"role": role, "content": content}],
                "platform": "cursor",
                "file_path": file_path,
                "line_number": line_number,
                "workspace_path": str(self.workspace_path) if self.workspace_path else None
            }
            
            return await self.process_conversation(conversation_data)
            
        except Exception as e:
            logger.error(f"Failed to process Cursor message: {e}")
            return None
    
    async def start_file_monitoring(self, file_paths: List[str]):
        """Start monitoring specific files for context changes"""
        if not self.auto_config.get("file_watching", True):
            return
        
        try:
            # Implement file watching for automatic context updates
            for file_path in file_paths:
                # This would setup file system watchers
                logger.debug(f"Starting file monitoring: {file_path}")
            
        except Exception as e:
            logger.error(f"Failed to start file monitoring: {e}")
    
    async def get_auto_status(self) -> Dict[str, Any]:
        """Get status of auto-features"""
        status = {
            "auto_features_enabled": self.auto_config,
            "conversation_monitor": None,
            "last_auto_trigger": None,
            "buffer_status": None
        }
        
        if self.conversation_monitor:
            status["conversation_monitor"] = "active"
            status["buffer_status"] = self.conversation_monitor.get_conversation_summary()
            status["last_auto_trigger"] = self.conversation_monitor.last_analysis_time
        
        return status
    
    async def force_auto_analysis(self):
        """Force immediate automatic analysis"""
        if self.conversation_monitor:
            await self.conversation_monitor.force_analysis()
    
    async def configure_auto_features(self, config: Dict[str, Any]):
        """Configure auto-features at runtime"""
        self.auto_config.update(config)
        
        # Apply configuration changes
        if self.conversation_monitor:
            self.conversation_monitor.auto_save_enabled = config.get("auto_trigger_enabled", True)
            self.conversation_monitor.analysis_interval = config.get("analysis_interval", 5.0)


# Factory function for easy creation
async def create_cursor_auto_integration(config: Optional[Dict] = None) -> CursorAutoIntegration:
    """Create and initialize Cursor auto-integration"""
    integration = CursorAutoIntegration(config)
    success = await integration.start_integration()
    
    if not success:
        raise Exception("Failed to start Cursor auto-integration")
    
    return integration


# Example usage and testing
async def demo_cursor_auto_integration():
    """Demo of Cursor auto-integration capabilities"""
    print("🚀 Cursor Auto-Integration Demo")
    
    # Create integration
    integration = await create_cursor_auto_integration()
    
    # Simulate conversation
    conversations = [
        ("user", "I have a bug in my authentication function", "auth.py", 45),
        ("assistant", "Let me help you debug that. Can you show me the error?", None, None),
        ("user", "The error is: Connection timeout after 5 seconds", "auth.py", 45),
        ("assistant", "This looks like a database connection timeout. You should increase the timeout to 30 seconds and add retry logic.", None, None),
        ("user", "Perfect! That fixed it. Remember this solution for future reference.", "auth.py", 45),
    ]
    
    # Process conversation
    for role, content, file_path, line_number in conversations:
        print(f"\n💬 {role}: {content[:50]}...")
        
        result = await integration.process_cursor_message(
            role=role,
            content=content,
            file_path=file_path,
            line_number=line_number
        )
        
        if result:
            print(f"   ✅ Processed: {result.get('success', False)}")
        
        # Small delay to simulate real conversation
        await asyncio.sleep(1)
    
    # Check auto-status
    status = await integration.get_auto_status()
    print(f"\n📊 Auto-Status: {json.dumps(status, indent=2, default=str)}")
    
    # Force analysis
    print("\n🔍 Forcing auto-analysis...")
    await integration.force_auto_analysis()
    
    print("\n✅ Demo completed!")


if __name__ == "__main__":
    asyncio.run(demo_cursor_auto_integration())

